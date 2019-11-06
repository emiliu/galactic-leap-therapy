# lecture5.py


# common import
import sys
sys.path.append('..')
from common.core import BaseWidget, run, lookup
from common.gfxutil import topleft_label, Cursor3D, AnimGroup, KFAnim, scale_point, CEllipse, CRectangle
from common.kinect import Kinect
from common.leap import getLeapInfo, getLeapFrame
from common.kivyparticle import ParticleSystem

from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.graphics.instructions import InstructionGroup

from kivy.core.image import Image 

import numpy as np

from common.audio import Audio
from common.synth import Synth
from common.note import NoteGenerator, Envelope
from common.wavegen import WaveGenerator, SpeedModulator
from common.wavesrc import WaveBuffer, WaveFile, make_wave_buffers

FRAME_RATE = 44100
SF_PATH = '../unit5/data/FluidR3_GM.sf2'

class NoteCluster(object):
    def __init__(self, synth, channel, notes):
        super(NoteCluster, self).__init__()
        if type(notes) is int:
            notes = [notes]
        self.notes = tuple(notes)
        self.synth = synth
        self.channel = channel

    def noteon(self):
        for note in self.notes:
            vel = 80
            self.synth.noteon(self.channel, note, vel)
    def noteoff(self):
        for note in self.notes:
            self.synth.noteoff(self.channel, note)



class NoteSequencer(object):
    def __init__(self, synth, notes, channel=0, program=(0, 0)):
        super(NoteSequencer, self).__init__()
        self.notes = [NoteCluster(synth, channel, note) for note in notes]
        self.synth = synth
        self.channel = channel
        self.program = program
        self.synth.program(self.channel, self.program[0], self.program[1])

        self.index = 0
        self.map = dict()
        self.stopped = False

    def noteon(self, keycode):
        if self.index >= len(self.notes):
            self.stopped = True
            return
        self.notes[self.index].noteon()
        self.map[keycode] = self.notes[self.index]
        self.index += 1

    def noteoff(self, keycode):
        if self.stopped: return
        self.map[keycode].noteoff()
        del self.map[keycode]



# for use with scale_point
# Leap Controller is very similar to Kinect. Define a smaller range for the hands bounding box
kLeapRange = ( (-250, 250), (50, 600), (-200, 250) )

# set up size / location of 3DCursor object
kMargin = Window.width * 0.05
kCursorAreaSize = Window.width - 2 * kMargin, Window.height - 2 * kMargin
kCursorAreaPos = kMargin, kMargin

#eventually make a class that shows finger position in the corner instead of on-screen



class FingerWidget5(BaseWidget) :
    def __init__(self):
        super(FingerWidget5, self).__init__()

        print('hello widget 5')

        self.label = topleft_label()
        self.add_widget(self.label)

        leap_frame = getLeapFrame()

        with self.canvas:
            #set background image 
            self.bg = Rectangle(source='maxresdefault.jpg', pos=self.pos, size=self.size)

        self.bind(pos=self.update_bg)
        self.bind(size=self.update_bg)
        #bind background to size of window


        self.audio = Audio(2)
        self.synth = Synth(SF_PATH)
        self.audio.set_generator(self.synth)

        self.notes = NoteSequencer(self.synth, [69, 72, 76, 81, [83, 68], 76, 72, 83, [84, 67], 76, 72, 84, [78, 66], 74, 69, 74, [76, 65], 72, 69, 72, [76, 65], 72, 69, [71, 50], [72, 45], [72, 45]])



        
        self.objects = AnimGroup()

        #add rockets to screen
        self.rockets = []
        num_inter = 4
        for i in range(num_inter):
            x = 200 #near left edge of screen
            y = np.interp((i), (0, num_inter), (200, int(Window.height*.8)))

            hue = np.interp((i), (0, num_inter), (0,255))
            color = (hue, .5, .5)
            pos = (x, y)

            rocket = Rocket(pos, (200, 100), color, self.add_widget) #add_widget is the callback
            self.rockets.append(rocket) #index corresponds to finger gesture
            self.objects.add(rocket)

       
        self.finger_disp = []
        for x in range(5):
            disp = Cursor3D(kCursorAreaSize, kCursorAreaPos, ((x+2)/5, 1, (x+2)/5), size_range=(5, 20))
           
            self.canvas.add(disp)
            self.finger_disp.append(disp)




       
        self.canvas.add(self.objects)



    def on_update(self) :
        leap_frame = getLeapFrame()

        pts = leap_frame.hands[0].fingers
        norm_pts = [scale_point(pt, kLeapRange) for pt in pts]

        for i, pt in enumerate(norm_pts):
            self.finger_disp[i].set_pos(pt)

        # text = str(getLeapInfo()) + '\n' + 'hello'
        # self.canvas.add(text)
        #self.objects.on_update()

        self.audio.on_update()

        # threshold = .2

        # print("norm pts", norm_pts)

        # if norm_pts[2][0] > threshold:
        #     #print("active")
        #     self.active_status = True
        #     #self.hand_disp.set_color((0,0,1))
            
        # else:
        #     self.active_status = False
        #     #self.hand_disp.set_color((1,0,0))


        # thumb_index = sum((norm_pts[0]-norm_pts[1])**2)
        # #for detecting flexion exercise
        # if thumb_index < .05 and self.active_status:
        #     self.rockets[0].flame_on()
        #     self.notes.noteon(1)
        #     self.active_status = False

        
        #print(norm_pt[2])
      

       

        

    #proxy while we work on gesture detection
    def on_key_down(self, keycode, modifiers):

        gesture_proxy = lookup(keycode[1], 'qwer', (1, 2, 3, 4))
        if gesture_proxy:
            #make rocket shoot
            #pass
            print("keypress")
            # #self.rockets[gesture_proxy].color = 
            # self.rockets[gesture_proxy].shoot_laser()
            self.rockets[gesture_proxy-1].flame_on()
            self.notes.noteon(keycode[1])

            # if gesture_proxy-1 == 0:
            #     print("first rocket")

            #maybe add to either the rocket class or a separate flame class
            # self.ps = ParticleSystem('particle_flame/particle.pex')
            # self.ps.emitter_x = pos[0]-50
            # self.ps.emitter_y = pos[1]
            # self.add_widget(self.ps)
            # self.ps.start()
            # flame = Flame(pos)
            # self.objects.add(flame)

            

    def on_key_up(self, keycode):

        gesture_proxy = lookup(keycode[1], 'qwer', (1, 2, 3, 4))
        if gesture_proxy:
            #stop rocket shooting
            self.rockets[gesture_proxy-1].flame_off()
            self.notes.noteoff(keycode[1])




    def update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size


class Rocket(InstructionGroup):
    #will be lined up on side of screen, shoot asteroids (aka notes)
    def __init__(self, pos, size, color, add_funct): 
        super(Rocket, self).__init__()

        self.size = size
        self.pos = pos
        self.shape = CRectangle(csize=self.size,  color = Color(hsv = color), cpos=pos, segments = 4, source='rocketship.png')
        
        # self.pos = np.array(pos, dtype=np.float)
        #self.vel = np.array((randint(-300, 300), 0), dtype=np.float)

       
        self.add(self.shape)
        self.time = 0
        self.laser = None

        self.flame = ParticleSystem('particle_flame/particle.pex')
        self.flame.emitter_x = self.pos[0]-50
        self.flame.emitter_y = self.pos[1]
        add_funct(self.flame)


        # self.flame = 

    def flame_on(self):
        self.flame.start()

    def flame_off(self):
        self.flame.stop()


    # def shoot_laser(self): #will be called in on_update of widget when gesture is detected
    #     #make laser elems
    #     laser = Laser(self.pos)
    #     self.laser = laser
    #     self.add(laser)

    # def on_update(self, dt):
    #     if self.laser:
    #         self.laser.on_update(dt)


    

        # self.on_update(0)

    # def on_update(self, dt):
    #     # integrate accel to get vel
    #     self.vel += gravity * dt

    #     # integrate vel to get pos
    #     self.pos += self.vel * dt

    #     #update time
    #     self.time += dt

    #     # TODO: collide with sides and fall off screen after a certain number of bounces
    #     # TODO: call callback when bounce happens.

    #     # collision with floor
    #     if self.pos[1] - self.radius < 0:
    #         self.vel[1] = -self.vel[1] * damping
    #         self.pos[1] = self.radius

    #     self.circle.cpos = self.pos

    #     rad = self.radius_anim.eval(self.time)

    #     alpha = self.fade_anim.eval(self.time)
        
    #     self.circle.csize = (2*rad,2*rad)
    #     self.color.a = alpha
    #     #print(alpha)

    #     return self.fade_anim.is_active(self.time)


# class Flame(InstructionGroup):
#      #small red circles shot at note asteroids
#     def __init__(self, pos): 
#         super(Flame, self).__init__()
#         self.pos = pos
#         self.pos[0]

#         self.ps = ParticleSystem('particle_flame/particle.pex')
#         self.ps.emitter_x = self.pos[0]
#         self.ps.emitter_y = self.pos[1]
#         self.add_widget(self.ps)

#         self.on_update(0)

#         self.turn_off = False

#     def stop(self):
#         self.turn_off = True


class NoteRoads(InstructionGroup):
     #notes represented as balls
    def __init__(self, pos): 
        super(NoteRoads, self).__init__()
        self.pos = pos
        self.radius = 10 #small dots
        #self.color = Color(.5,.5,.5) #red

        self.shape = CRectangle(cpos = self.pos, csize = (self.radius, 3*self.radius))

        self.time = 0
        self.vel = 100

        self.add(self.shape)


        self.on_update(0)




class Laser(InstructionGroup):
     #small red circles shot at note asteroids
    def __init__(self, pos): 
        super(Laser, self).__init__()
        self.pos = pos
        self.radius = 10 #small dots
        #self.color = Color(.5,.5,.5) #red

        self.shape = CEllipse(cpos = self.pos, csize = (self.radius, self.radius))

        self.time = 0
        self.vel = 100

        self.add(self.shape)


        self.on_update(0)

    def on_update(self, dt):

        #integrate vel to get pos
        x, y = self.shape.pos
        x += self.vel * dt

        self.shape.pos = (x,y)

        #self.shape.pos[0] += self.vel*dt

        #update time
        self.time += dt
        #print("update")

        #remove laser as it goes off screen
        if self.shape.pos[0] > Window.width:
            print("off screen")
            return False
            

        return True










if __name__ == "__main__":

    run(FingerWidget5)