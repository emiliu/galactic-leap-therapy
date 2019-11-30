# pset7.py


import sys
import numpy as np

# sys.path.append('..')

from common.core import BaseWidget, run, lookup
from common.gfxutil import CEllipse, CRectangle, topleft_label

from kivy.core.window import Window
from kivy.core.image import Image
from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.graphics import PushMatrix, PopMatrix, Translate

from audio import AudioController
from gesture import GestureWidget
from graphics import ButtonDisplay, GemDisplay

FRAME_RATE = 44100

WIDTH = Window.width
HEIGHT = Window.height

SLOP = 0.1 * FRAME_RATE


class MainWidget(BaseWidget):
    def __init__(self):
        super(MainWidget, self).__init__()

        self.bg = Rectangle(
            source="images/vzmpv432havx.jpg", pos=self.pos, size=Window.size
        )
        self.canvas.add(self.bg)

        self.data = SongData()
        self.data.read_data("data/solo.csv", "data/beats.csv")

        self.beats = BeatMatchDisplay(self.data)
        self.canvas.add(self.beats)
        self.audio = AudioController(
            [
                "data/YouGotAnotherThingComin_LD4.wav",
                "data/YouGotAnotherThingComin_TRKS4.wav",
                "miss.wav",
            ],
            use_miss_sound=False,
        )
        self.player = Player(self.data, self.beats, self.audio)

        self.score = topleft_label()
        self.add_widget(self.score)

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

        # self.touching = False
        # self.TOUCH = 10

        self.audio.toggle()

    def on_key_down(self, keycode, modifiers):
        # play / pause toggle
        if keycode[1] == "p":
            self.audio.toggle()

        # button down
        button_idx = lookup(keycode[1], "12345", (0, 1, 2, 3, 4))
        if button_idx is not None:
            self.player.on_button_down(button_idx)

    def on_key_up(self, keycode):
        # button up
        button_idx = lookup(keycode[1], "12345", (0, 1, 2, 3, 4))
        if button_idx is not None:
            self.player.on_button_up(button_idx)

    def on_update(self):
        # update game based on audio frame
        frame = self.audio.solo.frame
        self.beats.on_update(frame)
        self.audio.on_update()
        self.player.on_update(frame)

        self.score.text = "Score: %d\n" % self.player.score
        self.score.text += "Streak: %d" % self.player.streak

        self.gesture.on_update()

        touches = self.gesture.get_touch_states()
        for finger in range(4):
            touch = self.gesture.check_touch_for_finger(finger + 1)
            if touch:
                self.player.on_button_down(finger)
            # elif not touches[finger]:
            # elf.player.on_button_up(finger)

        """
        self.gesture.check_touch()

        #touch = self.gesture.get_any_touch_state()
        #print(touch)
        if any(touch):
            if not self.touching:
                #self.notes.noteon(self.TOUCH)
                for i in range(len(touch)):
                    if touch[i]:
                        self.player.on_button_down(i)
                self.touching = True
        else:
            if self.touching:
                #self.notes.noteoff(self.TOUCH)
                self.player.on_button_up(touch)
                self.touching = False
        """


# holds data for gems and barlines.
class SongData(object):
    def __init__(self):
        super(SongData, self).__init__()
        self.solo = [[0, 0, True]]
        self.bg = []

    # read the gems and song data
    def read_data(self, solo_path, bg_path):

        # store solo as pairs of (sound frame, lane index)
        with open(solo_path) as f:
            for line in f.readlines():
                split = line.strip().split(",")
                # self.solo.append((round(float(split[0]) * FRAME_RATE), self.solo[-1][1], False))
                self.solo[-1].append(round(float(split[0]) * FRAME_RATE))
                self.solo.append(
                    [round(float(split[0]) * FRAME_RATE), min(int(split[1]) - 1, 3)]
                )

        # store bar lines as the frame locations
        with open(bg_path) as f:
            self.bg = [
                round(float(line.split(",")[0]) * FRAME_RATE) for line in f.readlines()
            ]


# Displays and controls all game elements: Nowbar, Buttons, BarLines, Gems.
class BeatMatchDisplay(InstructionGroup):
    MEASURE = HEIGHT * 0.2
    NOW_BAR = HEIGHT * 0.25
    BARLINE_WIDTH = 2
    NOWBAR_WIDTH = 8

    def __init__(self, gem_data):
        super(BeatMatchDisplay, self).__init__()
        self.gem_data = gem_data

        WIDTH = Window.width
        HEIGHT = Window.height

        # collection of lane colors
        self.colors = (
            (1.000, 0.651, 0.188),
            (0.843, 0.910, 0.729),
            (0.302, 0.631, 0.663),
            (0.180, 0.314, 0.467),
            (0.380, 0.110, 0.208),
        )

        offset = WIDTH / 8
        diff = (WIDTH - 2 * offset) / 3

        # translate object
        self.trans = Translate()

        # bar lines
        self.add(Color(1, 1, 1))
        self.lines = []
        for bar in self.gem_data.bg:
            line = Line(
                points=[
                    0,
                    bar / FRAME_RATE * self.MEASURE,
                    WIDTH,
                    bar / FRAME_RATE * self.MEASURE,
                ],
                width=self.BARLINE_WIDTH,
            )
            self.lines.append(line)
            self.add(line)

        # now bar
        self.add(Color(0.5, 0.5, 0.5))
        self.add(
            Line(points=[0, self.NOW_BAR, WIDTH, self.NOW_BAR], width=self.NOWBAR_WIDTH)
        )

        # buttons
        self.buttons = []
        # btn_texture = None
        btn_texture = Image("images/yellowship.png").texture
        for i in range(4):
            button = ButtonDisplay(
                (i * diff + offset, self.NOW_BAR),
                Color(*self.colors[i]),
                texture=btn_texture,
            )
            self.buttons.append(button)
            self.add(button)

        # gems
        self.gems = []
        gem_width_half = 25
        gem_texture = None  # Image('texture.png').texture
        print(self.gem_data.solo[1])
        for gem in self.gem_data.solo:
            if len(gem) < 3:
                continue
            gem_obj = GemDisplay(
                (gem[1] * diff + offset, gem[0] / FRAME_RATE * self.MEASURE),
                Color(*self.colors[gem[1]]),
                texture=gem_texture,
            )
            # gem_obj = GemBarDisplay(
            #    (
            #        gem[1] * diff + offset - gem_width_half,
            #        gem[0] / FRAME_RATE * self.MEASURE,
            #    ),
            #    (2 * gem_width_half, (gem[2] - gem[0]) / FRAME_RATE * self.MEASURE),
            #    Color(*self.colors[gem[1]]),
            # )
            self.gems.append(gem_obj)
            self.add(gem_obj)

    # called by Player. Causes the right thing to happen
    def gem_hit(self, gem_idx):
        self.gems[gem_idx].on_hit()

    # called by Player. Causes the right thing to happen
    def gem_pass(self, gem_idx):
        self.gems[gem_idx].on_pass()

    # called by Player. Causes the right thing to happen
    def on_button_down(self, lane, hit):
        self.buttons[lane].on_down(hit)

    # called by Player. Causes the right thing to happen
    def on_button_up(self, lane):
        self.buttons[lane].on_up()

    # call every frame to handle animation needs
    def on_update(self, frame):
        offset = Window.width / 8
        diff = (Window.width - 2 * offset) / 3
        trans_y = -1 * frame / FRAME_RATE * self.MEASURE + self.NOW_BAR

        # update bar lines
        for i in range(len(self.gem_data.bg)):
            bar = self.gem_data.bg[i]

            # compute line endpoint locations
            real_pt0 = (0, bar / FRAME_RATE * self.MEASURE + trans_y)
            real_pt1 = (Window.width, bar / FRAME_RATE * self.MEASURE + trans_y)
            (fake_pt0, size_scale) = self.fake_3d(real_pt0)
            (fake_pt1, size_scale) = self.fake_3d(real_pt1)

            # set the new locations
            self.lines[i].points = [*fake_pt0, *fake_pt1]
            self.lines[i].width = size_scale * self.BARLINE_WIDTH

        # update gems
        gem_count = 0
        for gem in self.gem_data.solo:
            if len(gem) < 3:
                continue

            # apply translation for real position
            # apply 3d effect for effective "fake" position
            gem_obj = self.gems[gem_count]
            real_pos = (
                gem[1] * diff + offset,
                gem[0] / FRAME_RATE * self.MEASURE + trans_y,
            )
            (fake_pos, size_scale) = self.fake_3d(real_pos)

            # set the new values
            gem_obj.set_pos(fake_pos)
            gem_obj.set_size_scale(size_scale)
            gem_count += 1

    # apply a fake 3d effect to the given point
    def fake_3d(self, pt):
        (in_x, in_y) = pt

        # point at "infinity"
        # roughly center of screen
        (c_x, c_y) = (Window.width / 2, Window.height * 0.475)

        # compute the scaling constant
        c = np.tan(self.NOW_BAR / c_y * (np.pi / 2)) / self.NOW_BAR

        # scale y coordinate
        out_y = np.arctan(in_y * c) / (np.pi / 2) * c_y

        # x coordinate lies on intersection of out_y with
        # the line from (in_x, self.NOW_BAR) to center of screen
        m = (in_x - c_x) / (self.NOW_BAR - c_y)
        out_x = c_x + m * (out_y - c_y)

        # scaling factor for object size
        size_scale = (out_y - c_y) / (self.NOW_BAR - c_y)

        return ((out_x, out_y), size_scale)


# Handles game logic and keeps score.
# Controls the display and the audio
class Player(object):
    def __init__(self, gem_data, display, audio_ctrl):
        super(Player, self).__init__()
        self.gem_data = gem_data
        self.display = display
        self.audio_ctrl = audio_ctrl

        self.frame = 0
        self.gem_idx = 0
        self.score = 0
        self.streak = 0

    # called by MainWidget
    def on_button_down(self, lane):
        hit = False

        # if solo hasn't ended
        if self.gem_idx < len(self.gem_data.solo):

            if (
                self.gem_data.solo[self.gem_idx + 1][0] - SLOP
                <= self.frame
                <= self.gem_data.solo[self.gem_idx + 1][2] + SLOP
            ):
                self.gem_idx += 1
            # check if next gem is within slop window
            if (
                self.gem_data.solo[self.gem_idx][0] - SLOP
                <= self.frame
                <= self.gem_data.solo[self.gem_idx][2] + SLOP
            ):
                # if abs(self.gem_data.solo[self.gem_idx][0] - self.frame) <= SLOP:

                # if lane matches, then we have a hit
                if self.gem_data.solo[self.gem_idx][1] == lane:
                    self.display.gem_hit(self.gem_idx)
                    hit = True
                    self.score += 1
                    self.streak += 1
                    self.audio_ctrl.set_mute(False)

                # this gem is used
                self.gem_idx += 1

        self.display.on_button_down(lane, hit)
        # self.audio_ctrl.set_mute(not hit)

        # miss handling
        if not hit:
            self.audio_ctrl.play_sfx()

            # reset streak
            if self.streak > 1:
                self.score += self.streak
            self.streak = 0

    # called by MainWidget
    def on_button_up(self, lane):
        self.display.on_button_up(lane)

    # needed to check for pass gems (ie, went past the slop window)
    def on_update(self, frame):
        self.frame = frame

        # if gems still exist, check for pass gems
        while (
            self.gem_idx < len(self.gem_data.solo)
            and self.gem_data.solo[self.gem_idx][2] < self.frame - SLOP
        ):
            # only enter the loop if there are pass gems
            self.display.gem_pass(self.gem_idx)
            self.gem_idx += 1
            self.audio_ctrl.set_mute(True)
            if self.streak > 1:
                self.score += self.streak
            self.streak = 0


if __name__ == "__main__":
    run(MainWidget)
