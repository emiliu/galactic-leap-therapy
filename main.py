from common.core import BaseWidget, run, lookup
from common.gfxutil import (
    topleft_label,
    Cursor3D,
    AnimGroup,
    KFAnim,
    scale_point,
    CEllipse,
    CRectangle,
)
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

from gesture import GestureWidget
from graphics import Rocket, NoteRoads, Laser
from sounds import NoteCluster, NoteSequencer


SF_PATH = "data/FluidR3_GM.sf2"


class MainWidget(BaseWidget):
    def __init__(self):
        super(MainWidget, self).__init__()

        self.label = topleft_label()
        self.add_widget(self.label)

        with self.canvas:
            # set background image
            self.bg = Rectangle(
                source="images/maxresdefault.jpg", pos=self.pos, size=self.size
            )

        self.bind(pos=self.update_bg)
        self.bind(size=self.update_bg)
        # bind background to size of window

        self.audio = Audio(2)
        self.synth = Synth(SF_PATH)
        self.audio.set_generator(self.synth)

        self.notes = NoteSequencer(
            self.synth,
            [
                69,
                72,
                76,
                81,
                [83, 68],
                76,
                72,
                83,
                [84, 67],
                76,
                72,
                84,
                [78, 66],
                74,
                69,
                74,
                [76, 65],
                72,
                69,
                72,
                [76, 65],
                72,
                69,
                [71, 50],
                [72, 45],
                [72, 45],
            ],
        )

        self.objects = AnimGroup()

        # add rockets to screen
        self.rockets = []
        num_inter = 4
        for i in range(num_inter):
            x = 200  # near left edge of screen
            y = np.interp((i), (0, num_inter), (200, int(Window.height * 0.8)))

            hue = np.interp((i), (0, num_inter), (0, 255))
            color = (hue, 0.5, 0.5)
            pos = (x, y)

            rocket = Rocket(
                pos, (200, 100), color, self.add_widget
            )  # add_widget is the callback
            self.rockets.append(rocket)  # index corresponds to finger gesture
            self.objects.add(rocket)

        self.canvas.add(self.objects)

        kMargin = Window.width * 0.005
        kCursorAreaSize = (
            Window.width / 4 - 2 * kMargin,
            Window.height / 4 - 2 * kMargin,
        )
        kCursorAreaPos = Window.width - kCursorAreaSize[0] - kMargin, kMargin
        self.gesture = GestureWidget(
            cursor_area_pos=kCursorAreaPos,
            cursor_area_size=kCursorAreaSize,
            size_range=(1, 5),
        )
        self.canvas.add(self.gesture)

        self.touching = False
        self.TOUCH = 10

    def on_update(self):

        self.audio.on_update()
        self.gesture.on_update()
        self.gesture.check_touch()

        touch = self.gesture.get_any_touch_state()
        if touch:
            if not self.touching:
                self.notes.noteon(self.TOUCH)
                self.touching = True
        else:
            if self.touching:
                self.notes.noteoff(self.TOUCH)
                self.touching = False

    # proxy while we work on gesture detection
    def on_key_down(self, keycode, modifiers):

        gesture_proxy = lookup(keycode[1], "qwer", (1, 2, 3, 4))
        if gesture_proxy:
            # make rocket shoot
            # pass
            print("keypress")

            self.rockets[gesture_proxy - 1].flame_on()
            self.notes.noteon(keycode[1])

    def on_key_up(self, keycode):

        gesture_proxy = lookup(keycode[1], "qwer", (1, 2, 3, 4))
        if gesture_proxy:
            # stop rocket shooting
            self.rockets[gesture_proxy - 1].flame_off()
            self.notes.noteoff(keycode[1])

    def update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size


if __name__ == "__main__":
    run(MainWidget)
