import sys
sys.path.append('..')
from common.core import BaseWidget, run, lookup
from common.gfxutil import topleft_label, Cursor3D, AnimGroup, KFAnim, scale_point, CEllipse, CRectangle
from common.kinect import Kinect
from common.leap import getLeapInfo, getLeapFrame
from common.kivyparticle import ParticleSystem

from kivy.core.window import Window
from kivy.core.image import Image 
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.graphics.instructions import InstructionGroup



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



kLeapRange = ( (-250, 250), (50, 600), (-200, 250) )

kMargin = Window.width * 0.05
kCursorAreaSize = Window.width - 2 * kMargin, Window.height - 2 * kMargin
kCursorAreaPos = kMargin, kMargin




class FingerWidget5(BaseWidget) :
    def __init__(self):
        super(FingerWidget5, self).__init__()

        print('hello widget 5')

        self.label = topleft_label()
        self.add_widget(self.label)

        leap_frame = getLeapFrame()

        with self.canvas:
            #set background image 
            self.bg = Rectangle(source='images/maxresdefault.jpg', pos=self.pos, size=self.size)

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

       

        self.audio.on_update()


       

        

    #proxy while we work on gesture detection
    def on_key_down(self, keycode, modifiers):

        gesture_proxy = lookup(keycode[1], 'qwer', (1, 2, 3, 4))
        if gesture_proxy:
            #make rocket shoot
            #pass
            print("keypress")

            self.rockets[gesture_proxy-1].flame_on()
            self.notes.noteon(keycode[1])


            

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
    def __init__(self, pos, size, color, add_funct): 
        super(Rocket, self).__init__()

        self.size = size
        self.pos = pos
        self.shape = CRectangle(csize=self.size,  color = Color(hsv = color), cpos=pos, segments = 4, source='images/rocketship.png')
       

       
        self.add(self.shape)
        self.time = 0
        self.laser = None

        self.flame = ParticleSystem('images/particle_flame/particle.pex')
        self.flame.emitter_x = self.pos[0]-50
        self.flame.emitter_y = self.pos[1]
        add_funct(self.flame)


        # self.flame = 

    def flame_on(self):
        self.flame.start()

    def flame_off(self):
        self.flame.stop()


 



class NoteRoads(InstructionGroup):
     #notes represented as balls
    def __init__(self, pos): 
        super(NoteRoads, self).__init__()
        self.pos = pos
        self.radius = 10 #small dots
        

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