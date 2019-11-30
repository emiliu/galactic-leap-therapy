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
from common.kivyparticle import ParticleSystem

from kivy.core.window import Window
from kivy.core.image import Image
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.graphics import PushMatrix, PopMatrix, Translate
from kivy.graphics.instructions import InstructionGroup

import numpy as np

from audio import AudioController
from gesture import GestureWidget
from graphics import FlexShip, GemDisplay
from sounds import NoteCluster, NoteSequencer


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

        self.audio = AudioController(
            ["songs/MoreThanAFeeling_solo.wav", "songs/MoreThanAFeeling_bg.wav",],
            use_miss_sound=False,
        )
        self.display = BeatMatchDisplay(gem_data, bar_data)
        self.player = Player(gem_data, self.display, self.audio)

        # add rockets to screen
        pos = (Window.width / 2, Window.height / 4)
        self.rocket = FlexShip(pos)
        self.canvas.add(self.rocket)

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
            self.audio.toggle()

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
        self.label.text += "\nScore: %.2f\n" % self.player.score
        self.label.text += "Time: %.2f\n" % self.audio.get_time()

        self.audio.on_update()
        time = self.audio.get_time()
        self.display.on_update(time)
        self.player.on_update(time)

    def on_layout(self, window_size):
        # resize background
        ASPECT = 16 / 9
        width = max(Window.width, Window.height * ASPECT)
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
            Window.width - kCursorAreaSize[0] - kMargin,
            kMargin,
        )
        self.gesture.resize_display(kCursorAreaPos, kCursorAreaSize)

        # resize label
        resize_topleft_label(self.label)


# holds data for gems and barlines.
class SongData(object):
    def __init__(self):
        super(SongData, self).__init__()

    # read the gems and song data. You may want to add a secondary filepath
    # argument if your barline data is stored in a different txt file.
    def read_data(self, filepath_gems, filepath_barline):
        # based on functions from lab2
        def lines_from_file(filename):
            newfile = open(filename)
            strlist = newfile.readlines()
            return strlist

        def tokens_from_line(line):
            nline = line.strip()
            return nline.split("\t")

        def gems_from_file(filename):
            lines = lines_from_file(filename)
            out = []
            for l in lines:
                elems = tokens_from_line(l)
                gtype = int(float(elems[1]) * 10 % 10)
                time = float(elems[0])
                out.append((time, gtype))

            return out

        def bars_from_file(filename):
            lines = lines_from_file(filename)
            out = []
            for l in lines:
                elems = tokens_from_line(l)
                time = float(elems[0])
                out.append(time)

            return out

        gem_data = gems_from_file(filepath_gems)  # list of (time, type) tuple
        barlines = bars_from_file(filepath_barline)

        return (gem_data, barlines)


# Displays and controls all game elements: Nowbar, Buttons, BarLines, Gems.
class BeatMatchDisplay(InstructionGroup):
    def __init__(self, gem_data, bar_data):
        super(BeatMatchDisplay, self).__init__()
        self.time = 0
        # barlines separate every n beats
        # gems represent notes
        # go through and fix them later\

        self.gem_data = gem_data
        self.bar_data = bar_data
        self.gems = []

        # self.nowbar = NowBar()
        # self.add(self.nowbar)

        self.trans = Translate()
        self.time_dist = 200

        self.now_y = 300
        self.load_gems_bars()

    def load_gems_bars(self):
        self.add(PushMatrix())
        self.add(self.trans)

        # for barline in self.bar_data:
        # 	pos = (Window.width*.2, int(barline*self.time_dist+self.now_y))

        # 	self.add(BarlineDisplay(pos = pos))
        for gem in self.gem_data:
            color = Color(hsv=(1, 1, 1))

            x = np.interp((gem[1]), (1, 5), (200, Window.width - 200))
            pos = (60 + x, int(gem[0] * self.time_dist + self.now_y))
            gem = GemDisplay(pos=pos, color=color)
            self.gems.append(gem)
            self.add(gem)

        self.add(PopMatrix())

        self.gem_to_remove = None

    def get_gem_y_loc(self, gem_idx):
        gem = self.gems[gem_idx]

        return gem.pos[1] - self.time * self.time_dist

    # called by Player. Causes the right thing to happen
    def gem_hit(self, gem_idx):
        self.gems[gem_idx].on_hit()

        self.gem_to_remove = (self.time, self.gems[gem_idx])

    # called by Player. Causes the right thing to happen
    def gem_pass(self, gem_idx):
        self.gems[gem_idx].on_pass()

    # call every frame to handle animation needs
    def on_update(self, time):
        # pass

        # tracking time manually
        # dt = self.kivyClock.frametime
        self.time = time

        self.trans.y = -time * self.time_dist

        if self.gem_to_remove is not None:

            if self.time > self.gem_to_remove[0] + 0.2:
                self.remove(self.gem_to_remove[1])

        # put ~gems appearing code~ here, according to the time
        # potentially put this code into another

        # call note off for synth stuff


# Handles game logic and keeps score.
# Controls the display and the audio
class Player(object):
    def __init__(self, gem_data, display, audio_ctrl):
        super(Player, self).__init__()
        self.gem_data = gem_data
        self.display = display
        self.audio_ctrl = audio_ctrl

        self.score = 0
        self.current_idx = 0
        self.mute_len = 50
        self.slop = [0, 0]

    # called by MainWidget
    """
    def on_button_down(self, lane):
        # check if there is a gem hit, pass value to display
        # check if a gem is in the correct area
        value = self.is_gem_hit(lane)
        print(value)
        if value == True:
            hit = True

        else:
            hit = False
            if value == "lane":  # lane miss
                self.audio_ctrl.play_sfx()
                self.audio_ctrl.temp_mute(0)
                self.display.gem_pass(self.current_idx)
                self.current_idx += 1
            else:  # temporal miss
                self.audio_ctrl.play_sfx()
                self.audio_ctrl.temp_mute(0)

        self.display.on_button_down(lane, hit)
    """

    # returns True if gem hit, ow returns type of miss
    def is_gem_hit(self, lane):
        if (
            self.display.get_gem_y_loc(self.current_idx) > self.slop[1]
            and self.display.get_gem_y_loc(self.current_idx) < self.slop[0]
        ):
            print(self.gem_data[self.current_idx][1], lane + 1)
            if self.gem_data[self.current_idx][1] == lane + 1:
                self.display.gem_hit(self.current_idx)
                self.current_idx += 1
                print("gem hit")
                self.score += 1
                return True
            else:

                return "lane"
        else:

            return "temporal"

    # needed to check for pass gems (ie, went past the slop window)
    def on_update(self, time):
        # print(self.display.get_gem_y_loc(self.current_idx))
        if self.display.get_gem_y_loc(self.current_idx) < self.slop[1]:
            self.display.gems[self.current_idx].on_pass()
            print("passed gem")
            self.current_idx += 1

        self.time = time


if __name__ == "__main__":
    run(MainWidget)
    # run(MainWidget, fullscreen=True)
