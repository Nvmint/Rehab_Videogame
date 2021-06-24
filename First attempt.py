# -*- coding: utf-8 -*-
"""
Created on Tue Jun 22 23:55:19 2021

@author: diana
"""
import numpy as np
import cv2 as cv
import pygame as py
import mediapipe as mp
py.font.init()

movement = 0
WIDHT, HEIGHT = 900, 600
screen = py.display.set_mode([WIDHT,HEIGHT])
py.display.set_caption("Rehab Videogame")
back_image = py.image.load("sea3.jpg")
back_image = py.transform.scale(back_image,(900,600))
bubble_dimesion = 30
axo_dimension = 100
axo_image = py.image.load('axolote1.png')
axo_image = py.transform.flip(py.transform.scale(axo_image,(axo_dimension,axo_dimension)),True,False)
bubble_image = py.image.load('buble2.png')
bubble_image = py.transform.scale(bubble_image,(bubble_dimesion,bubble_dimesion))


def angle_calculate(a,b,c):
    
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    
    radians = np.arctan2(c[1]-b[1],c[0]-b[0]) - np.arctan2(a[1]-b[1],a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    
    if angle > 180.0:
        angle=360-angle
    
    return angle   

def process(frame,mp_drawing,mp_holistic,holistic):
    stage = None
    #cambios de color y aplicar módulo holistic
    image = cv.cvtColor(frame,cv.COLOR_RGB2BGR)
    result = holistic.process(image)
    image = cv.cvtColor(image,cv.COLOR_BGR2RGB)
            
    #Landmarks
    try: 
            landmarks = result.pose_landmarks.landmark
            
            #coordenadas de brazo izq
            shoulder = [landmarks[mp_holistic.PoseLandmark.LEFT_SHOULDER.value].x,
                      landmarks[mp_holistic.PoseLandmark.LEFT_SHOULDER.value].y]
            elbow = [landmarks[mp_holistic.PoseLandmark.LEFT_ELBOW.value].x,
                      landmarks[mp_holistic.PoseLandmark.LEFT_ELBOW.value].y]
            wrist = [landmarks[mp_holistic.PoseLandmark.LEFT_WRIST.value].x,
                      landmarks[mp_holistic.PoseLandmark.LEFT_WRIST.value].y]
            
            #calculate angle
            angle = angle_calculate(shoulder,elbow,wrist)
            
            #look angle
            cv.putText(image,str(angle),
                       tuple(np.multiply(elbow,[640,480]).astype(int)),
                             cv.FONT_HERSHEY_SIMPLEX,0.5,(255,255,255),2,cv.LINE_AA)
            
            #repetitions
            if angle>120:
                stage = 0
            elif angle <=60:
                stage = 1
            
    except:
        pass
                  
    #dibujar las articulaciones en la imagen
    mp_drawing.draw_landmarks(image, result.pose_landmarks,mp_holistic.POSE_CONNECTIONS,
                              mp_drawing.DrawingSpec(color = (102,31,208),thickness = 2,circle_radius = 2),
                              mp_drawing.DrawingSpec(color = (103,249,237),thickness = 2,circle_radius = 2))
            
    return image,stage
            

class axolote:

    def __init__(self):
    
        self.img = axo_image
        self.velocity = 30
        self.pos_x = 100
        self.pos_y = 100
        self.mask = py.mask.from_surface(self.img)
        
    def update(self,user_movement):
        if user_movement == 1 and self.pos_y - self.velocity > 0:
            self.pos_y -= self.velocity
        elif user_movement == 0 and self.pos_y + self.velocity + axo_dimension < HEIGHT:
            self.pos_y += self.velocity
        
    def draw (self,screen):
        screen.blit(self.img, (self.pos_x,self.pos_y))
        py.display.update() 
        
class bubble:
    def __init__(self):
        self.imag = bubble_image
        self.pos_x = WIDHT+np.random.randint(10,600)
        self.pos_y = np.random.randint(10, 600 - bubble_dimesion)
        self.mask = py.mask.from_surface(self.imag)
        
    def update(self):
        self.pos_x -=10
        if self.pos_x < - bubble_dimesion:
            self.pos_x = WIDHT + np.random.randint(10, 900)
            self.pos_y =np.random.randint(10, 600)
    
    def draw(self,screen):
        screen.blit(self.imag, (self.pos_x,self.pos_y))
    
    def collision(self,obj):
        return collide(self,obj)
        
def collide(obj1, obj2):
    offset_x = obj2.pos_x - obj1.pos_x
    offset_y = obj2.pos_y - obj1.pos_y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


def main():
    fps = 60
    bubbles = []
    player = axolote()
    score = 0
    
    main_font = py.font.SysFont("comicsans", 50)
    
    for i in range(4): bubbles.append(bubble())
    clock=py.time.Clock()
    run = True
    
    capture =cv.VideoCapture(0)
    
    mp_drawing = mp.solutions.drawing_utils
    mp_holistic = mp.solutions.holistic
    
    def redraw(score):
        screen.blit(back_image,(0,0))
        score_label = main_font.render(f"Score: {score} ",1,(255,255,255))
        
        screen.blit(score_label,(WIDHT-score_label.get_width()-10,10))
        
        for i in range(4): 
                bubbles[i].draw(screen)
                bubbles[i].update()
                if bubbles[i].collision(player):
                    score += 1
    
        player.draw(screen) 
        player.update(stage)
        
        
    with mp_holistic.Holistic(min_detection_confidence=0.8,min_tracking_confidence=0.8) as holistic:
        while run: 
            
            clock.tick(fps)
            data,frame = capture.read()
            imag,stage = process(frame,mp_drawing,mp_holistic,holistic)
            
            redraw(score)
                
            cv.imshow('camera',imag)
            
            for event in py.event.get():
                if event.type == py.QUIT:
                    run = False
            
            if cv.waitKey(2) == ord('q'):
                break
                
    capture.release()
    cv.destroyAllWindows()       
    py.quit()

  
if __name__=="__main__":
    main()