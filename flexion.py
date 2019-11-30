from common.core import BaseWidget, run, lookup
from common.gfxutil import (
    topleft_label,
    resize_topleft_label,
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
from graphics import Rocket, NoteRoads, Laser, FlexShip
from sounds import NoteCluster, NoteSequencer

from guitarhero import AudioController, SongData, BeatMatchDisplay, Player


SF_PATH = "data/FluidR3_GM.sf2"


class MainWidget(BaseWidget):
    def __init__(self):

        super(MainWidget, self).__init__()

        self.bg = Rectangle(
            source="./images/vaporwav.jpg", pos=self.pos, size=Window.size
        )
        self.canvas.add(self.bg)

        data_manager = SongData()
        gem_data, bar_data = data_manager.read_data(
            "songs/annot_test.txt", "songs/annot_barlines.txt"
        )

        self.audio_player = AudioController()
        self.display = BeatMatchDisplay(gem_data, bar_data, self.audio_player.get_time)

        self.player = Player(gem_data, self.display, self.audio_player)

        self.objects = AnimGroup()

        # add rockets to screen
        pos = (Window.width / 2, Window.height / 4)

        self.rocket = FlexShip(pos)
        self.objects.add(self.rocket)

        self.canvas.add(self.objects)

        kMargin = Window.width * 0.005
        kCursorAreaSize = (
            Window.width / 4 - 2 * kMargin,
            Window.height / 4 - 2 * kMargin,
        )
        kCursorAreaPos = (
            Window.width - kCursorAreaSize[0] - kMargin,
            kMargin,
        )

        self.gesture = GestureWidget(
            cursor_area_pos=kCursorAreaPos,
            cursor_area_size=kCursorAreaSize,
            size_range=(1, 5),
            display_trailing_cursors=False,
        )

        self.canvas.add(self.gesture)
        self.canvas.add(self.display)

        self.touching = False
        self.TOUCH = 10

        self.label = topleft_label()
        self.add_widget(self.label)

    def on_key_down(self, keycode, modifiers):
        # play / pause toggle
        if keycode[1] == "p":
            self.audio_player.toggle()

    def on_update(self):
        axis = 0
        thresh = 0.05

        self.gesture.on_update()
        wrist_angle = self.gesture.get_wrist_angle(axis)

        # option 1: set absolute position
        pos = wrist_angle / (np.pi / 2) * Window.width + (Window.width / 2)
        self.rocket.set_position(pos, axis)

        # option 2: move incrementally
        # delta = wrist_angle * 10
        # self.rocket.move_position(delta, axis)

        self.label.text = ""
        self.label.text += str(getLeapInfo())
        self.label.text += "\nScore: %.2f\n" % self.player.score
        self.label.text += "Time: %.2f\n" % self.audio_player.get_time()

        self.audio_player.on_update()
        self.display.on_update()
        self.player.on_update()

    def on_layout(self, window_size):
        # resize background
        ASPECT = 16 / 9
        width = min(Window.width, Window.height * ASPECT)
        height = width / ASPECT
        bg_size = np.array([width, height])
        bg_pos = (np.array([Window.width, Window.height]) - bg_size) / 2
        self.bg.pos = bg_pos
        self.bg.size = bg_size

        # resize gesture widget
        kMargin = width * 0.005
        kCursorAreaSize = (
            width / 4 - 2 * kMargin,
            height / 4 - 2 * kMargin,
        )
        kCursorAreaPos = (
            bg_pos[0] + width - kCursorAreaSize[0] - kMargin,
            bg_pos[1] + kMargin,
        )
        self.gesture.resize_display(kCursorAreaPos, kCursorAreaSize)

        # resize label
        resize_topleft_label(self.label)


if __name__ == "__main__":
    run(MainWidget)
    # run(MainWidget, fullscreen=True)
