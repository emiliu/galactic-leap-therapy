from common.core import BaseWidget, run, lookup
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
from common.gfxutil import CRectangle
from common.synth import Synth
from common.note import NoteGenerator, Envelope
from common.wavegen import WaveGenerator, SpeedModulator
from common.wavesrc import WaveBuffer, WaveFile, make_wave_buffers


class Rocket(InstructionGroup):
    def __init__(self, pos, size, color, add_funct):
        super(Rocket, self).__init__()

        self.size = size
        self.pos = pos
        self.shape = CRectangle(
            csize=self.size,
            color=Color(hsv=color),
            cpos=pos,
            segments=4,
            source="images/ufo2.png",
        )

        self.add(self.shape)
        self.time = 0
        self.laser = None

        self.flame = ParticleSystem("images/particle_flame/particle.pex")
        self.flame.emitter_x = self.pos[0] - 50
        self.flame.emitter_y = self.pos[1]
        add_funct(self.flame)

    def flame_on(self):
        self.flame.start()

    def flame_off(self):
        self.flame.stop()


class NoteRoads(InstructionGroup):
    # notes represented as balls
    def __init__(self, pos):
        super(NoteRoads, self).__init__()
        self.pos = pos
        self.radius = 10  # small dots

        self.shape = CRectangle(cpos=self.pos, csize=(self.radius, 3 * self.radius))

        self.time = 0
        self.vel = 100

        self.add(self.shape)

        self.on_update(0)


class Laser(InstructionGroup):
    # small red circles shot at note asteroids
    def __init__(self, pos):
        super(Laser, self).__init__()
        self.pos = pos
        self.radius = 10  # small dots
        # self.color = Color(.5,.5,.5) #red

        self.shape = CEllipse(cpos=self.pos, csize=(self.radius, self.radius))

        self.time = 0
        self.vel = 100

        self.add(self.shape)

        self.on_update(0)

    def on_update(self, dt):

        # integrate vel to get pos
        x, y = self.shape.pos
        x += self.vel * dt

        self.shape.pos = (x, y)

        # self.shape.pos[0] += self.vel*dt

        # update time
        self.time += dt
        # print("update")

        # remove laser as it goes off screen
        if self.shape.pos[0] > Window.width:
            print("off screen")
            return False

        return True


class FlexShip(InstructionGroup):
    def __init__(self, pos):
        super(FlexShip, self).__init__()

        self.size = (80,80)
        self.pos = pos
        self.shape = CRectangle(
            csize=self.size,
            cpos=pos,
            segments=4,
            source="images/redship.png",
        )

        self.add(self.shape)

        self.flame = ParticleSystem("images/particle_flame/particle.pex")
        self.flame.emitter_x = self.pos[0] - 50
        self.flame.emitter_y = self.pos[1]
        self.flame.start()

    def move_display(self, inc, axis):
        #move rocket increment along axis (x=0, y=1)
        if axis == 0:
            pos = (self.shape.pos[axis]+inc, self.shape.pos[1])
        else:
            pos = (self.shape.pos[0], self.shape.pos[axis]+inc)

        if pos[0] > 0 and pos[0] < Window.width-100:
            if pos[1] > 0 and pos[1] < Window.height:
        
                self.shape.pos = pos




class MainWidget(BaseWidget):
    def __init__(self):
        super(MainWidget).__init__()

if __name__ == '__main__':
    run(MainWidget)