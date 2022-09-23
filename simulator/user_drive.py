#initialize the screen
import pygame, math, sys, time
from pygame.locals import *
import cv2 as cv # Just for you Ashton
import numpy as np


def level1():
    pygame.init()
    track = cv.imread("images/oval_track_v1.png", cv.IMREAD_GRAYSCALE)
    screen = pygame.display.set_mode((track.shape[1], track.shape[0]))
    #GAME CLOCK
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 75)
    win_font = pygame.font.Font(None, 50)
    win_condition = None
    win_text = font.render('', True, (0, 255, 0))
    loss_text = font.render('', True, (255, 0, 0))
    t0 = time.time()
    bg = pygame.image.load("images/oval_track_v1.png")
    
    def check_collision(car, track):
        mask_array = track[car.rect[1]:car.rect[1]+car.rect[3],car.rect[0]:car.rect[0]+car.rect[2]]
        num_zeroes = np.count_nonzero(mask_array==0)
        if num_zeroes > np.prod(mask_array.shape)*0.25:
        # if 0 in mask_array:
            return True
        else:
            return False
    
    def laser_scan(car, track, side):
        # 0 is left, 1 is right
        # Direction is counter clockwise
        step_size = 1
        if side == 0:
            angle = (car.direction+90) % 360
            angle = np.deg2rad(angle)
        elif side == 1:
            angle = (car.direction-90) % 360
            angle = np.deg2rad(angle)
        else:
            print("Error: side must be 0 or 1")
            return None

        laser = [car.position[0], car.position[1]]
        while True:
            if track[int(laser[1]), int(laser[0])] == 0:
                break
            laser[0] -= (math.sin(angle) * step_size)
            laser[1] -= (math.cos(angle) * step_size)
        dist = np.linalg.norm(np.array(car.position) - np.array(laser))
        return laser, dist

    class CarSprite(pygame.sprite.Sprite):
        MAX_FORWARD_SPEED = 10
        MAX_REVERSE_SPEED = 10
        ACCELERATION = 2
        TURN_SPEED = 10

        def __init__(self, image, position):
            pygame.sprite.Sprite.__init__(self)
            track = cv.imread("images/oval_track_v1.png", cv.IMREAD_GRAYSCALE)

            self.src_image = pygame.image.load(image)
            self.position = position
            self.speed = self.direction = 0
            self.k_left = self.k_right = self.k_down = self.k_up = 0
        
        def update(self, deltat):
            #SIMULATION
            self.speed += (self.k_up + self.k_down)
            if self.speed > self.MAX_FORWARD_SPEED:
                self.speed = self.MAX_FORWARD_SPEED
            if self.speed < -self.MAX_REVERSE_SPEED:
                self.speed = -self.MAX_REVERSE_SPEED
            self.direction += (self.k_right + self.k_left)
            x, y = (self.position)
            rad = self.direction * math.pi / 180
            x += -self.speed*math.sin(rad)
            y += -self.speed*math.cos(rad)
            self.position = (x, y)
            self.image = pygame.transform.rotate(self.src_image, self.direction)
            self.rect = self.image.get_rect()
            self.rect.center = self.position

    # CREATE A CAR AND RUN
    rect = screen.get_rect()
    car = CarSprite('images/car_orientation1.png', (80, track.shape[0]/2))
    car_group = pygame.sprite.RenderPlain(car)

    #THE GAME LOOP
    while 1:
        #USER INPUT
        t1 = time.time()
        dt = t1-t0

        deltat = clock.tick(30)
        for event in pygame.event.get():
            if not hasattr(event, 'key'): continue
            down = event.type == KEYDOWN 
            if win_condition == None: 
                if event.key == K_RIGHT: car.k_right = down * -5 
                elif event.key == K_LEFT: car.k_left = down * 5
                elif event.key == K_UP: car.k_up = down * 2
                elif event.key == K_DOWN: car.k_down = down * -2 
                elif event.key == K_ESCAPE: sys.exit(0) # quit the game
            elif win_condition == False and event.key == K_SPACE: 
                level1()
                t0 = t1
            elif event.key == K_ESCAPE: sys.exit(0)    
      
        #RENDERING
        screen.blit(bg, (0, 0))
        # screen.fill((0,0,0))
        car_group.update(deltat)
        # collisions = pygame.sprite.groupcollide(car_group, pad_group, False, False, collided = None)
        
        collisions = check_collision(car, track)
        
        if collisions == True:
            win_condition = False
            timer_text = font.render("Crash!", True, (255,0,0))
            car.image = pygame.image.load('images/collision.png')
            loss_text = win_font.render('Press Space to Retry', True, (255,0,0))
            seconds = 0
            car.MAX_FORWARD_SPEED = 0
            car.MAX_REVERSE_SPEED = 0
            car.k_right = 0
            car.k_left = 0

        left_hit, left_range = laser_scan(car, track, 0)
        right_hit, right_range = laser_scan(car, track, 1)
        # print(round(left_range,0), round(right_range,0))
        pygame.draw.line(screen, (255, 0, 0), (left_hit[0], left_hit[1]), (right_hit[0], right_hit[1]), width=3)
        car_group.draw(screen)
        screen.blit(win_text, (250, 700))
        screen.blit(loss_text, (250, 700))
        pygame.display.flip()

if __name__ == '__main__': 
    level1()