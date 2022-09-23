import os
import pygame
from math import sin, radians, degrees, copysign, cos
import numpy as np
from pygame.math import Vector2
import cv2 as cv


class Car:
    def __init__(self, x, y, angle=0.0, length=4, max_steering=30, max_acceleration=5.0):
        self.position = Vector2(x, y)
        self.velocity = Vector2(0.0, 0.0)
        self.angle = angle
        self.length = length
        self.max_acceleration = max_acceleration
        self.max_steering = max_steering
        self.max_velocity = 100
        self.brake_deceleration = 10
        self.free_deceleration = 2

        self.acceleration = 0.0
        self.steering = 0.0

    def update(self, dt):
        # self.velocity += (self.acceleration * dt, 0)
        self.velocity.x = max(-self.max_velocity, min(self.velocity.x, self.max_velocity))

        if self.steering:
            turning_radius = self.length / sin(radians(self.steering))
            angular_velocity = self.velocity.x / turning_radius
        else:
            angular_velocity = 0

        self.position += self.velocity.rotate(-self.angle) * dt
        self.angle += degrees(angular_velocity) * dt


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Car tutorial")
        # width = 1280
        # height = 720
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.track = cv.imread(os.path.join(current_dir,"images", "oval_track_v1.png"), cv.IMREAD_GRAYSCALE)
        self.bg = pygame.image.load(os.path.join(current_dir,"images", "oval_track_v1.png"))
        self.screen = pygame.display.set_mode((self.track.shape[1], self.track.shape[0]))
        # self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.ticks = 60
        self.exit = False

    def check_collision(self,car, track):
        carx, cary = car.position
        return track[int(cary), int(carx)] == 0
        
        # mask_array = track[car.rect[1]:car.rect[1]+car.rect[3],car.rect[0]:car.rect[0]+car.rect[2]]
        # num_zeroes = np.count_nonzero(mask_array==0)
        # if num_zeroes > np.prod(mask_array.shape)*0.25:
        # # if 0 in mask_array:
        #     return True
        # else:
        #     return False
        
    
    def laser_scan(self,car, track, side):
        # 0 is left, 1 is right
        # Direction is counter clockwise
        step_size = 1
        if side == 0:
            angle = (car.angle) % 360
            angle = np.deg2rad(angle)
        elif side == 1:
            angle = (car.angle-180) % 360
            angle = np.deg2rad(angle)
        else:
            print("Error: side must be 0 or 1")
            return None

        laser = [car.position[0], car.position[1]]
        while True:
            if track[int(laser[1]), int(laser[0])] == 0:
                break
            laser[0] -= (sin(angle) * step_size)
            laser[1] -= (cos(angle) * step_size)
        dist = np.linalg.norm(np.array(car.position) - np.array(laser))
        return laser, dist

    def run(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(current_dir, os.path.join("images", "car.png"))
        
        # screen = pygame.display.set_mode((track.shape[1], track.shape[0]))
        car_image = pygame.image.load(image_path)
        car = Car(80,self.track.shape[0]/2,length=20,max_acceleration=.5,angle=90)
        car.velocity = Vector2(100,0)
        print("creating car:", image_path)
        ppu = 1

        while not self.exit:
            dt = self.clock.get_time() / 1000
            
            # Event queue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit = True

            # User input
            pressed = pygame.key.get_pressed()

            # if pressed[pygame.K_UP]:
            #     if car.velocity.x < 0:
            #         car.acceleration = car.brake_deceleration
            #     else:
            #         car.acceleration += 1 * dt
            # elif pressed[pygame.K_DOWN]:
            #     if car.velocity.x > 0:
            #         car.acceleration = -car.brake_deceleration
            #     else:
            #         car.acceleration -= 1 * dt
            # elif pressed[pygame.K_SPACE]:
            #     if abs(car.velocity.x) > dt * car.brake_deceleration:
            #         car.acceleration = -copysign(car.brake_deceleration, car.velocity.x)
            #     else:
            #         car.acceleration = -car.velocity.x / dt
            # else:
            #     if abs(car.velocity.x) > dt * car.free_deceleration:
            #         car.acceleration = -copysign(car.free_deceleration, car.velocity.x)
            #     else:
            #         if dt != 0:
            #             car.acceleration = -car.velocity.x / dt
            # car.acceleration = max(-car.max_acceleration, min(car.acceleration, car.max_acceleration))

            if pressed[pygame.K_RIGHT]:
                car.steering -= 30 * dt
            elif pressed[pygame.K_LEFT]:
                car.steering += 30 * dt
            else:
                car.steering = 0
            car.steering = max(-car.max_steering, min(car.steering, car.max_steering))

            # Logic
            car.update(dt)

            collisions = self.check_collision(car, self.track)
            
            if collisions == True:
                win_condition = False
                # timer_text = font.render("Crash!", True, (255,0,0))
                car.image = pygame.image.load(os.path.join('images', 'collision.png'))
                # loss_text = win_font.render('Press Space to Retry', True, (255,0,0))
                self.exit= True
                print("crashed")
                car.velocity.x = 0

            left_hit, left_range = self.laser_scan(car, self.track, 0)
            right_hit, right_range = self.laser_scan(car, self.track, 1)


            # Drawing
            self.screen.blit(self.bg, (0, 0))
            # self.screen.fill((0, 0, 0))
            # print(car.position)
            pygame.draw.line(self.screen, (255, 0, 0), (left_hit[0], left_hit[1]), (right_hit[0], right_hit[1]), width=5)
            rotated = pygame.transform.rotate(car_image, car.angle)
            rect = rotated.get_rect()
            self.screen.blit(rotated, car.position * ppu - (rect.width / 2, rect.height / 2))
            pygame.display.flip()

            self.clock.tick(self.ticks)
        pygame.quit()


if __name__ == '__main__':
    game = Game()
    game.run()