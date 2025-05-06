import pygame
import math
from math import sqrt
from pyautogui import size
import random
pygame.init()
pygame.mixer.init()


width,height = size()
height = height -100 
screen = pygame.display.set_mode((width,height))
clock = pygame.time.Clock()
pygame.mixer.music.load('assets/sounds/bg_music.wav')
pygame.mixer.music.set_volume(0.1)

music_play = False
sword_swing = pygame.mixer.Sound('assets/sounds/sword_swing.wav')
sword_swing.set_volume(0.5)

lost_sound = pygame.mixer.Sound('assets/sounds/lost_sound.wav')
lost_sound.set_volume(0.5)
player_lost = False
# pygame.mixer.Sound.set_volume(0.5)

# music_time = False
class Player():
    def __init__(self,screen,width,height):
        self.screen = screen
        self.width = width
        self.height = height 
        self.total_hp = 5
        self.font = pygame.font.Font('assets/fonts/Pixeltype.ttf',60)
        self.dash_sound = pygame.mixer.Sound('assets/sounds/hero_dash.wav')

        self.idle_right = []
        self.idle_left = []
        self.walking_right_images = []
        self.walking_left_images = []

        self.state = 'idle_right'
        self.last_direction = 'right'

        self.current_image = 0
        self.animation_speed = 0.4
        self.squezed_size = 6
        self.x = 400
        self.y = 400
        self.player_speed = 12

        self.dash_condition = False
        self.movement_x = None

        self.moved = False

        self.load_images()
        
        self.image = self.idle_right[0]
        self.rect = self.image.get_rect(center = (self.x,self.y))
        self.player_hitbox_surface = pygame.Surface((30,50))
        self.player_hitbox_rect = self.player_hitbox_surface.get_rect(center = (self.x,self.y))

    def update(self):
        # self.screen.fill('red')
        self.screen.blit(self.image,self.rect)
        self.player_hitbox_surface.fill('red')
        # self.screen.blit(self.player_hitbox_surface,self.player_hitbox_rect)

    def health(self):
        font= self.font.render(f'Total HP: {self.total_hp}',False,'blue')
        self.screen.blit(font,(self.width-200,20))
        
    def load_images(self):
        for i in range(10):
            image = pygame.image.load(f'assets/Player/Idle_right/Idle_right{i}.png').convert_alpha()
            width,height = image.get_size()
            image = pygame.transform.scale(image,(width/self.squezed_size,height/self.squezed_size))
            self.idle_right.append(image)   

        for i in range(17):
            image = pygame.image.load(f'assets/Player/Idle_left/Idle_left{i}.png').convert_alpha()
            width,height = image.get_size()
            image = pygame.transform.scale(image,(width/self.squezed_size,height/self.squezed_size))
            self.idle_left.append(image)  

        for i in range(15):
            image = pygame.image.load(f'assets/Player/Walking_left/W_left_{i}.png').convert_alpha()
            width,height = image.get_size()
            image = pygame.transform.scale(image,(width/self.squezed_size,height/self.squezed_size))
            self.walking_left_images.append(image)  

        for i in range(15):
            image = pygame.image.load(f'assets/Player/Walking_right/W_right{i}.png').convert_alpha()
            width,height = image.get_size()
            image = pygame.transform.scale(image,(width/self.squezed_size,height/self.squezed_size))
            self.walking_right_images.append(image)      

    def animations(self):
        self.current_image += self.animation_speed

        if self.state == 'idle_right':
            if self.current_image >= len(self.idle_right):
                self.current_image = 0
            self.image = self.idle_right[int(self.current_image)]
        
        if self.state == 'idle_left':
            if self.current_image >= len(self.idle_left):
                self.current_image = 0
            self.image = self.idle_left[int(self.current_image)]
        
        if self.state == 'left':
            if self.current_image >= len(self.walking_left_images):
                self.current_image = 0
            self.image = self.walking_left_images[int(self.current_image)]
        
        if self.state == 'right' :
            if self.current_image >= len(self.walking_right_images):
                self.current_image = 0
            self.image = self.walking_right_images[int(self.current_image)]

        if self.state == 'up':
            if self.current_image >= len(self.idle_right):
                self.current_image = 0
            
            if self.last_direction == 'right':
                self.image = self.walking_right_images[int(self.current_image)]

            else:
                self.image = self.walking_left_images[int(self.current_image)]
                
        if self.state == 'down':
            if self.current_image >= len(self.idle_right):
                self.current_image = 0

            if self.last_direction == 'right':
                self.image = self.walking_right_images[int(self.current_image)]
            
            else:self.image = self.walking_left_images[int(self.current_image)]

    def movement(self,keys):
            moved = False
            if keys[pygame.K_a]:
                self.x -= self.player_speed
                if self.x <=25:
                    self.x = 25


                self.state = 'left'
                self.last_direction = 'left'
                moved = True

            if keys[pygame.K_d]:
                self.x += self.player_speed
                self.state = 'right'
                self.last_direction = 'right'
                moved = True
                if self.x >= self.width -25:
                    self.x = self.width -25

            if keys[pygame.K_w]:
                self.y -= self.player_speed
                self.state = 'up'
                moved = True
                if self.y <=45:
                    self.y = 45

            if keys[pygame.K_s]:
                self.y += self.player_speed
                self.state = 'down'
                moved = True
                if self.y >= self.height - 45:
                    self.y = self.height - 45

            if not moved:
                if self.last_direction == 'left':
                    self.state = 'idle_left'

                if self.last_direction == 'right':
                    self.state = 'idle_right'

            self.rect.center = (self.x,self.y)
            self.player_hitbox_rect.center = (self.x,self.y)       

    def dash(self):
        if not self.dash_condition:
            return 

        if self.movement_x is None:
            self.movement_x = self.x

        dash_speed = 100
        dash_distance = 300

        if self.state == 'idle_left' or self.state == 'left' or self.last_direction == 'left':
            self.x -= dash_speed
            if self.x <= self.movement_x - dash_distance:
                self.dash_condition = False
                self.movement_x = None
                if self.x <=25:
                    self.x  = 25
        else:   
            self.x += dash_speed
            if self.x >= self.movement_x + dash_distance:
                self.dash_condition = False
                self.movement_x = None

        self.rect.center = (self.x,self.y)

        # print(f"x: {self.x}, movement_x: {self.movement_x}, dash_condition: {self.dash_condition}")
            
class Blade():
    def __init__(self,player):
        self.player = player
        self.all_nails = []
        self.load_nails()
        self.image = self.all_nails[0]
        self.rect = None
        self.attacking = False
        self.horizontal_attack_hitbox_rect = 0
        self.vertical_attack_hitbox_rect = 0
             
    def load_nails(self):
        nail_right = pygame.image.load('assets/Player/weapon_swing/nail_right.png').convert_alpha()
        self.all_nails.append(nail_right)

        nail_left = pygame.image.load('assets/Player/weapon_swing/nail_left.png').convert_alpha()
        self.all_nails.append(nail_left)
          
        nail_up = pygame.image.load('assets/Player/weapon_swing/nail_up.png').convert_alpha()
        self.all_nails.append(nail_up)
        
        nail_down = pygame.image.load('assets/Player/weapon_swing/nail_down.png').convert_alpha()
        self.all_nails.append(nail_down)

    def draw_nails(self,x,y):
        
        if self.player.state == 'right' or self.player.state == 'idle_right':
            self.image = self.all_nails[0]

        if self.player.state == 'left' or self.player.state =='idle_left':
            self.image = self.all_nails[1]

        if self.player.state == 'up':
            self.image = self.all_nails[2]

        if self.player.state == 'down' :
            self.image = self.all_nails[3]

        self.rect = self.image.get_rect(center = (x,y))
        self.player.screen.blit(self.image,self.rect)

    def Blade_hitboxes(self,x,y):
        horizontal_attack_hitbox = pygame.Surface((30,60))
        vertical_attack_hitbox =pygame.Surface((60,30))
        horizontal_attack_hitbox.fill('red')
        vertical_attack_hitbox.fill('red')
        self.horizontal_attack_hitbox_rect = horizontal_attack_hitbox.get_rect(center = (x,y))
        self.vertical_attack_hitbox_rect = vertical_attack_hitbox.get_rect(center =(x,y))
        # if self.player.state == 'right' or self.player.state == 'left' or self.player.state == 'idle_left' or self.player.state == 'idle_right':
        #     self.player.screen.blit(horizontal_attack_hitbox,self.horizontal_attack_hitbox_rect)
        # else:self.player.screen.blit(vertical_attack_hitbox,self.vertical_attack_hitbox_rect)

class Enemies():
    enemy_left_images = []
    enemy_right_images =[]
    enemy_disappearing_images = []
    image_loaded = False  

    def __init__(self,player,blade,x,y):
        self.player = player
        self.blade = blade
        self.x = x
        self.y = y
        self.enemy_speed = random.uniform(1.00,3.00)
        self.squezed_size = 6
        self.animation_speed = 0.2
        self.current_image = 0
        
        
        if not Enemies.image_loaded and not  Enemies.enemy_disappearing_images:
            self.load_images(self.squezed_size)
            for i in range(1,8):
                img = pygame.image.load(f'assets/Enemy/disappearing_animation/no_{i}.png').convert_alpha()
                wi,hei = img.get_size()
                img = pygame.transform.scale(img,(wi * 4,hei*4))
                Enemies.enemy_disappearing_images.append(img)
            Enemies.image_loaded = True

        self.image = self.enemy_right_images[int(self.current_image)]
        self.rect = self.image.get_rect(center = (self.x,self.y))
        self.enemy_hitbox_surface = pygame.Surface((30,50))
        self.enemy_hitbox_surface_rect = self.enemy_hitbox_surface.get_rect(center = (self.x,self.y))

    @classmethod
    def load_images(cls,squeeze):
        for i in range(1,25):
            image = pygame.image.load(f'assets/Enemy/Walking_left/walking_left.{i}.png').convert_alpha()
            width,height = image.get_size()
            image = pygame.transform.scale(image,(width/squeeze,height/squeeze))
            Enemies.enemy_left_images.append(image)

        for i in range(1,25):
            image = pygame.image.load(f'assets/Enemy/Walking_right/walk_right{i}.png').convert_alpha()
            width,height = image.get_size()
            image = pygame.transform.scale(image,(width/squeeze,height/squeeze))
            Enemies.enemy_right_images.append(image)
   
    def enemy_disappear(self):
        complete_loop = False
        if not complete_loop:
            enemy_disappearing_animation_speed = 0.001
            current_image = 0
            current_image += enemy_disappearing_animation_speed
            if current_image >= 7:
                complete_loop = True

        image = Enemies.enemy_disappearing_images[int(current_image)]
        rect = image.get_rect(center = (self.x,self.y))
        self.player.screen.blit(image,rect)

    def update(self):
        self.player.screen.blit(self.image,self.rect)
        self.enemy_hitbox_surface.fill('green')
        # self.player.screen.blit(self.enemy_hitbox_surface,self.enemy_hitbox_surface_rect)

    def movement(self):
        self.current_image += self.animation_speed
        if self.current_image >=24:
            self.current_image = 0 

        if self.player.x < self.x:
            self.image = Enemies.enemy_left_images[int(self.current_image)]

        else:
            self.image = Enemies.enemy_right_images[int(self.current_image)]

    def algorithm(self):

        # Homing A.I
        dx = self.player.x - self.x
        dy = self.player.y - self.y
        hyp = sqrt((dx**2)+(dy**2))
        if hyp !=0:
            dx /= hyp
            dy /= hyp
            self.x += dx * self.enemy_speed + random.uniform(-0.5,0.5)
            self.y += dy * self.enemy_speed + random.uniform(-0.5,0.5)

        self.rect.center = (self.x,self.y)
        self.enemy_hitbox_surface_rect.center = (self.x,self.y)

class Decoration():
    def __init__(self,screen,width,height,player):
        self.game_start = False
        self.screen = screen
        self.height = height
        self.width = width
        self.player = player
        self.x = self.width / 2
        self.y = self.height / 2
        self.player_won = False
        self.player_loose = False
        self.phase = 0
        self.bg_img = pygame.transform.scale(pygame.image.load('assets/deco/ground.png'),(1920,2000))
        self.bg_img_rect = self.bg_img.get_rect(center = (self.x,self.y))
        
   
    def bg(self):
        screen.blit(self.bg_img,self.bg_img_rect)

    def main_screen(self):
        
        image = pygame.image.load('assets/deco/main_screen.png').convert_alpha()
        image = pygame.transform.scale(image,(1920,1000))
        self.screen.blit(image,(0,0))

    def loose_screen(self):
        image = pygame.image.load('assets/deco/you_loose.png').convert_alpha()
        image = pygame.transform.scale(image,(1920,1000))
        
        self.screen.blit(image,(0,0))
    
    def you_win_screen(self):
        image = pygame.image.load('assets/deco/you_win.png').convert_alpha()
        image = pygame.transform.scale(image,(1920,1000))
        
        self.screen.blit(image,(0,0))

    def fonts(self):
        font = self.player.font.render(f'Phase: {self.phase}',False,'blue')
        self.player.screen.blit(font,(700,20))

  

player = Player(screen,width,height)
deco = Decoration(screen,width,height,player)
blade = Blade(player)

#Blade delay for every swing

swing_delay = 500
time1 = 0
enemies = []
i = 0

def append_enemies():
    for _ in range(i):
        direction = random.choice(['left', 'right', 'up', 'down'])
        if direction == 'left':
            x = random.randint(width - (width+600), 0)
            y = random.randint(0, height)
        elif direction == 'right':
            x = random.randint(width, width + 600)
            y = random.randint(0, height)
        elif direction == 'up':
            x = random.randint(0, width)
            y = random.randint(width - (width+600), 0)
        elif direction == 'down':
            x = random.randint(0, width)
            y = random.randint(height, height + 600)

        enemy = Enemies(player, blade, x, y)
        enemies.append(enemy)

def enemy_hit():
    for enemy in enemies[:]:
        random_distance = random.randint(400,600)
        if enemy.x >= player.x and enemy.y >= player.y :
            enemy.x = enemy.x + random_distance
            enemy.y += random_distance
        else:
            enemy.x = enemy.x - random_distance
            enemy.y -= random_distance
        
        player.x = width/2
        player.y = height/2

while True:
    if deco.game_start:
        #BG image
        deco.bg()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()

        if event.type == pygame.KEYDOWN:
            if not deco.game_start:
                if event.key == pygame.K_SPACE:
                    deco.game_start = True
                    music_play = False
                    i = 0
                    enemies.clear()
                    player.total_hp = 3
                    deco.phase = 0
                    deco.player_loose = False
                    deco.player_won = False
        if deco.game_start:


            if event.type == pygame.MOUSEBUTTONDOWN :
                if event.button == 1:
                    time2 = pygame.time.get_ticks()
                    blade.attacking = True

                    if time2 - time1 >= swing_delay:
                        time1 = time2
                        sword_swing.play()
                        if player.state == 'left' or player.state == 'idle_left':
                            blade.draw_nails(player.x - 100, player.y)
                            blade.Blade_hitboxes(player.x - 130, player.y)

                        if player.state == 'right' or player.state == 'idle_right':
                            blade.draw_nails(player.x + 100, player.y)
                            blade.Blade_hitboxes(player.x + 130, player.y)


                        if player.state == 'up':
                            blade.draw_nails(player.x , player.y - 100)
                            blade.Blade_hitboxes(player.x, player.y - 130)

                        if player.state == 'down':
                            blade.draw_nails(player.x, player.y + 100)
                            blade.Blade_hitboxes(player.x, player.y + 130)

                else:
                    blade.attacking = False
                
                if event.button == 3:
                    player.dash_condition = True
                    player.movement_x = None

              
    
    if deco.game_start:
        if not music_play:
                pygame.mixer.music.play(-1, 0.0)  # Start playing the music loop
                music_play = True
                if player.dash_condition:
                    player.dash_sound.play()

        keys = pygame.key.get_pressed()
        player.update()
        blade.player.animations()
        if not player.dash_condition:
            player.movement(keys)
        player.health()
        deco.fonts()
        
        for enemy in enemies:
            enemy.update()
            enemy.movement()
            enemy.algorithm()

        if player.dash_condition:
            player.dash()
            player.dash_sound.play()


        if len(enemies) <=0:
            i += 5
            deco.phase += 1
            append_enemies()
        if deco.phase>20:
            deco.player_won = True
            deco.game_start = False

        for enemy in enemies[:]:
            if blade.rect != None and blade.attacking and (blade.horizontal_attack_hitbox_rect.colliderect(enemy.enemy_hitbox_surface_rect) or blade.vertical_attack_hitbox_rect.colliderect(enemy.enemy_hitbox_surface_rect)):
                enemies.remove(enemy)
                blade.attacking = False
                enemy.enemy_disappear()
            # enemy.enemy_disappear()
                break
          
            
            if enemy.enemy_hitbox_surface_rect.colliderect(player.player_hitbox_rect):
                enemy_hit()
                player.total_hp-=1
                if player.total_hp <=0:
                    deco.game_start = False
                    deco.player_loose = True

    else:
        pygame.mixer.music.stop()
        if deco.player_won:
            deco.you_win_screen()
        elif deco.player_loose:
            lost_sound.play()
            deco.loose_screen()
        else:
            deco.main_screen()
        

    pygame.display.flip()
    clock.tick(60)

pygame.quit()