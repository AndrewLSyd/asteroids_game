# Spaceship game

try:
    import simplegui
except ImportError:
    import SimpleGUICS2Pygame.simpleguics2pygame as simplegui
import math
import random

# sound assets purchased from sounddogs.com, please do not redistribute
soundtrack = simplegui.load_sound(
    "http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/soundtrack.mp3")
missile_sound = simplegui.load_sound(
    "http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/missile.mp3")
missile_sound.set_volume(.5)
ship_thrust_sound = simplegui.load_sound(
    "http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/thrust.mp3")
explosion_sound = simplegui.load_sound(
    "http://commondatastorage.googleapis.com/codeskulptor-assets/sounddogs/explosion.mp3")

#  __      _____ _       _           _     
# /_ |    / ____| |     | |         | |    
#  | |   | |  __| | ___ | |__   __ _| |___ 
#  | |   | | |_ | |/ _ \| '_ \ / _` | / __|
#  | |_  | |__| | | (_) | |_) | (_| | \__ \
#  |_(_)  \_____|_|\___/|_.__/ \__,_|_|___/


WIDTH = 800
HEIGHT = 600
started = False
score = 0
lives = 3
time = 0
rock_group = set([])
missile_group = set([])
explosion_group = set([])

#  ___      _    _      _                    __                  _   _                 
# |__ \    | |  | |    | |                  / _|                | | (_)                
#    ) |   | |__| | ___| |_ __   ___ _ __  | |_ _   _ _ __   ___| |_ _  ___  _ __  ___ 
#   / /    |  __  |/ _ \ | '_ \ / _ \ '__| |  _| | | | '_ \ / __| __| |/ _ \| '_ \/ __|
#  / /_ _  | |  | |  __/ | |_) |  __/ |    | | | |_| | | | | (__| |_| | (_) | | | \__ \
# |____(_) |_|  |_|\___|_| .__/ \___|_|    |_|  \__,_|_| |_|\___|\__|_|\___/|_| |_|___/
#                        | |                                                           
#                        |_|                                                           

def angle_to_vector(ang):
    return [math.cos(ang), math.sin(ang)]


def dist(p, q):
    return math.sqrt((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2)

def process_sprite_group(a_set, a_canvas):
    copy_of_set = set(a_set)
    for i in copy_of_set:
        if i.update():
            a_set.remove(i)
        i.draw(a_canvas)

        
def group_collide(group, other_object):
    global explosion_group, an_explosion
    for i in set(group):
        if i.collide(other_object):
            group.remove(i)
            
            print("EXPLODES!")
            explosion_sound.rewind()
            explosion_sound.play()
            
            pos = i.get_pos()
            vel = [0, 0]
            angle = random.uniform(-math.pi, math.pi)
            angle_vel = 0
            
            an_explosion = Sprite(pos, vel, angle, angle_vel, explosion_image, explosion_info)
            explosion_group.add(an_explosion)
            return True
        else:
            return False
        
def group_group_collide(rock_group, missile_group):
    """ checks for collisions between a rock group and missile group """
    collisions = 0
    for i in missile_group:
        if group_collide(rock_group, i):
            collisions += 1
    return collisions
    

#  ____      _____ _                         
# |___ \    / ____| |                        
#   __) |  | |    | | __ _ ___ ___  ___  ___ 
#  |__ <   | |    | |/ _` / __/ __|/ _ \/ __|
#  ___) |  | |____| | (_| \__ \__ \  __/\__ \
# |____(_)  \_____|_|\__,_|___/___/\___||___/


class ImageInfo:
    def __init__(self, center, size, radius=0, lifespan=None, animated=False):
        self.center = center
        self.size = size
        self.radius = radius
        if lifespan:
            self.lifespan = lifespan
        else:
            self.lifespan = float('inf')
        self.animated = animated

    def get_center(self):
        return self.center

    def get_size(self):
        return self.size

    def get_radius(self):
        return self.radius

    def get_lifespan(self):
        return self.lifespan

    def get_animated(self):
        return self.animated


# Ship class
class Ship:
    def __init__(self, pos, vel, angle, image, info):
        self.pos = [pos[0], pos[1]]
        self.vel = [vel[0], vel[1]]
        self.thrust = False
        self.angle = angle
        self.angle_vel = 0
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.friction = 0.075
        self.accel = angle_to_vector(self.angle)

    def draw(self, canvas):
        # canvas.draw_circle(self.pos, self.radius, 1, "White", "White")
        if self.thrust:
            canvas.draw_image(ship_image, ship_thrust_info.center, ship_thrust_info.size, self.pos, ship_thrust_info.size,
                          self.angle)
        else:
            canvas.draw_image(ship_image, ship_info.center, ship_info.size, self.pos, ship_info.size,
                          self.angle)         
            
    def update(self):
        self.pos[0] += self.vel[0]
        self.pos[0] = self.pos[0] % WIDTH
        self.pos[1] += self.vel[1]
        self.pos[1] = self.pos[1] % WIDTH
        self.angle += self.angle_vel
        
        self.accel = angle_to_vector(self.angle)
        
        # friction
        self.vel[0] -= self.friction * self.vel[0]
        self.vel[1] -= self.friction * self.vel[1]
        
        if self.thrust:
            self.vel[0] += self.accel[0] * 0.75
            self.vel[1] += self.accel[1] * 0.75
            

    def rotate_left(self):
        self.angle_vel -= math.pi * 2 / 60

    def rotate_right(self):
        self.angle_vel += math.pi * 2 / 60
        
    def thrust_on(self):
        self.thrust = True
    
    def thrust_off(self):
        self.thrust = False
    
    def shoot(self):
        global missile_group, a_missile
        pos = [self.pos[0] + self.accel[0] * ship_info.size[0] / 2, self.pos[1] + self.accel[1] * ship_info.size[0] / 2]
        vel = [self.vel[0] + self.accel[0] * 5, self.vel[1] + self.accel[1] * 5]
        a_missile = Sprite(pos, vel, 0, 0, missile_image, missile_info, missile_sound)
        missile_group.add(a_missile)
        print("missile added to missile_group")
    
    def get_pos(self):
        return self.pos
    
    
    def get_radius(self):
        return self.radius

# Sprite class
class Sprite:
    def __init__(self, pos, vel, ang, ang_vel, image, info, sound=None):
        self.pos = [pos[0], pos[1]]
        self.vel = [vel[0], vel[1]]
        self.angle = ang
        self.angle_vel = ang_vel
        self.image = image
        self.image_center = info.get_center()
        self.image_size = info.get_size()
        self.radius = info.get_radius()
        self.lifespan = info.get_lifespan()
        self.animated = info.get_animated()
        self.age = 0
        if sound:
            sound.rewind()
            sound.play()

    def draw(self, canvas):
        if self.animated:
            shift = self.age * self.image_size[0]
            canvas.draw_image(self.image, [self.image_center[0] + shift, self.image_center[1]], self.image_size, self.pos, self.image_size,
                              self.angle)   
        else:
            canvas.draw_image(self.image, self.image_center, self.image_size, self.pos, self.image_size,
                              self.angle)                   

    def update(self):
        self.pos[0] += self.vel[0]
        self.pos[0] = self.pos[0] % WIDTH
        self.pos[1] += self.vel[1]
        self.pos[1] = self.pos[1] % WIDTH
        self.angle += self.angle_vel
        self.age += 1
#        print(self.age)
#        print(self.lifespan)
        if self.age >= self.lifespan:
            return True
        else:
            return False
        
    
    def collide(self, other_object):
        distance = dist(self.pos, other_object.get_pos())
        radii = self.radius + other_object.get_radius()
        
        return distance < radii


    def get_pos(self):
        return self.pos
    
    
    def get_radius(self):
        return self.radius

    
# art assets created by Kim Lathrop, may be freely re-used in non-commercial projects, please credit Kim

# debris images - debris1_brown.png, debris2_brown.png, debris3_brown.png, debris4_brown.png
#                 debris1_blue.png, debris2_blue.png, debris3_blue.png, debris4_blue.png, debris_blend.png
debris_info = ImageInfo([320, 240], [640, 480])
debris_image = simplegui.load_image(
    "http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/debris2_blue.png")

# nebula images - nebula_brown.png, nebula_blue.png
nebula_info = ImageInfo([400, 300], [800, 600])
nebula_image = simplegui.load_image(
    "http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/nebula_blue.f2014.png")

# splash image
splash_info = ImageInfo([200, 150], [400, 300])
splash_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/splash.png")

# ship image
ship_info = ImageInfo([45, 45], [90, 90], 35)
ship_thrust_info = ImageInfo([45 + 90, 45], [90, 90], 35)
ship_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/double_ship.png")

# missile image - shot1.png, shot2.png, shot3.png
missile_info = ImageInfo([5, 5], [10, 10], 3, 50)
missile_image = simplegui.load_image("http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/shot2.png")

# asteroid images - asteroid_blue.png, asteroid_brown.png, asteroid_blend.png
asteroid_info = ImageInfo([45, 45], [90, 90], 40)
asteroid_image = simplegui.load_image(
    "http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/asteroid_blue.png")

# animated explosion - explosion_orange.png, explosion_blue.png, explosion_blue2.png, explosion_alpha.png
explosion_info = ImageInfo([64, 64], [128, 128], 17, 24, True)
explosion_image = simplegui.load_image(
    "http://commondatastorage.googleapis.com/codeskulptor-assets/lathrop/explosion_alpha.png")



# alternative upbeat soundtrack by composer and former IIPP student Emiel Stopler
# please do not redistribute without permission from Emiel at http://www.filmcomposer.nl
# soundtrack = simplegui.load_sound("https://storage.googleapis.com/codeskulptor-assets/ricerocks_theme.mp3")


#  _  _     _____        __   ______               _     _    _                 _ _               
# | || |   |  __ \      / _| |  ____|             | |   | |  | |               | | |              
# | || |_  | |  | | ___| |_  | |____   _____ _ __ | |_  | |__| | __ _ _ __   __| | | ___ _ __ ___ 
# |__   _| | |  | |/ _ \  _| |  __\ \ / / _ \ '_ \| __| |  __  |/ _` | '_ \ / _` | |/ _ \ '__/ __|
#    | |_  | |__| |  __/ |   | |___\ V /  __/ | | | |_  | |  | | (_| | | | | (_| | |  __/ |  \__ \
#    |_(_) |_____/ \___|_|   |______\_/ \___|_| |_|\__| |_|  |_|\__,_|_| |_|\__,_|_|\___|_|  |___/


# mouseclick handlers that reset UI and conditions whether splash image is drawn
def click(pos):
    global started, lives, score
    center = [WIDTH / 2, HEIGHT / 2]
    size = splash_info.get_size()
    inwidth = (center[0] - size[0] / 2) < pos[0] < (center[0] + size[0] / 2)
    inheight = (center[1] - size[1] / 2) < pos[1] < (center[1] + size[1] / 2)
    if (not started) and inwidth and inheight:
        started = True
        lives = 3
        score = 0
        soundtrack.rewind()
        soundtrack.play()



def draw(canvas):
    global time, lives, score, started, rock_group

    if lives < 1:
        started = False
        rock_group = set([])

    # animiate background
    time += 1
    wtime = (time / 4) % WIDTH
    center = debris_info.get_center()
    size = debris_info.get_size()
    canvas.draw_image(nebula_image, nebula_info.get_center(), nebula_info.get_size(), [WIDTH / 2, HEIGHT / 2],
                      [WIDTH, HEIGHT])
    canvas.draw_image(debris_image, center, size, (wtime - WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))
    canvas.draw_image(debris_image, center, size, (wtime + WIDTH / 2, HEIGHT / 2), (WIDTH, HEIGHT))

    # draw ship and sprites
    my_ship.draw(canvas)
#    a_rock.draw(canvas)
#    a_missile.draw(canvas)
    # update ship and sprites
    my_ship.update()
#    a_rock.update()
#    a_missile.update()
    
    process_sprite_group(rock_group, canvas)
    process_sprite_group(missile_group, canvas)
    process_sprite_group(explosion_group, canvas)
    
    # lives and score
    canvas.draw_text("LIVES:", [25, 25], 24, "white")
    canvas.draw_text(str(lives), [125, 25], 24, "white")
    canvas.draw_text("SCORE:", [25, 50], 24, "white")
    canvas.draw_text(str(score), [125, 50], 24, "white")
    
    # draw splash screen if not started
    if not started:
        canvas.draw_image(splash_image, splash_info.get_center(), 
                          splash_info.get_size(), [WIDTH / 2, HEIGHT / 2], 
                          splash_info.get_size())

        
    # check if ship collides with rocks
    if group_collide(rock_group, my_ship):
        print("my_ship hit a rock")
        lives -= 1

    score += group_group_collide(rock_group, missile_group)

# timer handler that spawns a rock
def rock_spawner():
    global rock_group
    pos = [random.randrange(0, WIDTH), random.randrange(0, HEIGHT)]
    vel = [(score ** 0.15) * random.uniform(-10 / 5, 10 / 5), (score **  0.15) * random.uniform(-10 / 5, 10 / 5)]
    angle = random.uniform(-math.pi, math.pi)
    angle_vel = random.uniform(-math.pi / 60, math.pi / 60)
    print(missile_info.get_lifespan())
    
    if len(rock_group) < 12 and started:
        a_rock = Sprite(pos, vel, angle, angle_vel, asteroid_image, asteroid_info)
        if dist(a_rock.get_pos(), my_ship.get_pos()) > 100:
            rock_group.add(a_rock)
        print("rock added to rock_group")


# keyboard responses
def rotate_left():
    print("left")
    my_ship.rotate_left()

def rotate_right():
    print("right")
    my_ship.rotate_right()


def thrust_on():
    my_ship.thrust_on()
    ship_thrust_sound.play()
    
def thrust_off():
    my_ship.thrust_off()
    ship_thrust_sound.pause()
    ship_thrust_sound.rewind()

def shoot():
    my_ship.shoot()

# keyboard handler
keydown_inputs = {"left":rotate_left, "right":rotate_right, "up":thrust_on, "space":shoot}
keyup_inputs = {"left":rotate_right, "right":rotate_left, "up":thrust_off}


def keydown_handler(key):
    for i in keydown_inputs:
        if key == simplegui.KEY_MAP[i]:
            keydown_inputs[i]()
            
def keyup_handler(key):
    for i in keyup_inputs:
        if key == simplegui.KEY_MAP[i]:
            keyup_inputs[i]()

#  _____    _____       _ _   _       _ _            ______                        
# | ____|  |_   _|     (_) | (_)     | (_)          |  ____|                       
# | |__      | |  _ __  _| |_ _  __ _| |_ ___  ___  | |__ _ __ __ _ _ __ ___   ___ 
# |___ \     | | | '_ \| | __| |/ _` | | / __|/ _ \ |  __| '__/ _` | '_ ` _ \ / _ \
#  ___) |   _| |_| | | | | |_| | (_| | | \__ \  __/ | |  | | | (_| | | | | | |  __/
# |____(_) |_____|_| |_|_|\__|_|\__,_|_|_|___/\___| |_|  |_|  \__,_|_| |_| |_|\___|

frame = simplegui.create_frame("Asteroids", WIDTH, HEIGHT)

# initialize ship and two sprites
my_ship = Ship([WIDTH / 2, HEIGHT / 2], [0, 0], 0, ship_image, ship_info)
# my_ship.angle_vel = 10
# a_rock = Sprite([WIDTH / 2, HEIGHT / 2], [0.5, 0.25], 0, 0, asteroid_image, asteroid_info)
# a_missile = Sprite([2 * WIDTH / 3, 2 * HEIGHT / 3], [-1, 1], 0, 0, missile_image, missile_info, missile_sound)

#    __     _____            _     _              ______               _   
#   / /    |  __ \          (_)   | |            |  ____|             | |  
#  / /_    | |__) |___  __ _ _ ___| |_ ___ _ __  | |____   _____ _ __ | |_ 
# | '_ \   |  _  // _ \/ _` | / __| __/ _ \ '__| |  __\ \ / / _ \ '_ \| __|
# | (_) |  | | \ \  __/ (_| | \__ \ ||  __/ |    | |___\ V /  __/ | | | |_ 
#  \___(_) |_|  \_\___|\__, |_|___/\__\___|_|    |______\_/ \___|_| |_|\__|
#          | |  | |     __/ |     | | |                                    
#          | |__| | __ |___/_   __| | | ___ _ __ ___                       
#          |  __  |/ _` | '_ \ / _` | |/ _ \ '__/ __|                      
#          | |  | | (_| | | | | (_| | |  __/ |  \__ \                      
#          |_|  |_|\__,_|_| |_|\__,_|_|\___|_|  |___/                      

frame.set_draw_handler(draw)
frame.set_keydown_handler(keydown_handler)
frame.set_keyup_handler(keyup_handler)
frame.set_mouseclick_handler(click)


timer = simplegui.create_timer(1000.0, rock_spawner)

#  ______    _____ _             _      __                          
# |____  |  / ____| |           | |    / _|                         
#     / /  | (___ | |_ __ _ _ __| |_  | |_ _ __ __ _ _ __ ___   ___ 
#    / /    \___ \| __/ _` | '__| __| |  _| '__/ _` | '_ ` _ \ / _ \
#   / /     ____) | || (_| | |  | |_  | | | | | (_| | | | | | |  __/
#  /_(_)   |_____/ \__\__,_|_|  _\__| |_| |_|  \__,_|_| |_| |_|\___|
#                          | | | | (_)                              
#            __ _ _ __   __| | | |_ _ _ __ ___   ___ _ __ ___       
#           / _` | '_ \ / _` | | __| | '_ ` _ \ / _ \ '__/ __|      
#          | (_| | | | | (_| | | |_| | | | | | |  __/ |  \__ \      
#           \__,_|_| |_|\__,_|  \__|_|_| |_| |_|\___|_|  |___/      

timer.start()
frame.start()
soundtrack.play()
