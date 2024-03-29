import sys
import numpy as np

from common.core import BaseWidget, run, lookup
from common.kivyparticle import ParticleSystem

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.core.image import Image
from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color, Line, Rectangle
from kivy.uix.widget import Widget

from audio import AudioController
from gesture import GestureWidget
from graphics import ButtonDisplay, GemDisplay, ProgressBar, TopLeftLabel


# slop window in seconds
SLOP = 0.1


class MainWidget(BaseWidget):
    def __init__(self):
        super(MainWidget, self).__init__()

        # add background
        self.bg = Rectangle(
            source="images/vzmpv432havx.jpg", pos=self.pos, size=Window.size
        )
        self.canvas.add(self.bg)

        # load song data
        self.data = SongData()
        self.data.read_data("data/solo.csv", "data/beats.csv")
        self.audio = AudioController(
            [
                "data/YouGotAnotherThingComin_LD4.wav",
                "data/YouGotAnotherThingComin_TRKS4.wav",
                "miss.wav",
            ],
            use_miss_sound=False,
        )

        # create game
        self.explosions = ExplosionsWidget(size=Window.size)
        self.display = BeatMatchDisplay(self.data)
        self.player = Player(self.data, self.display, self.audio, self.explosions)
        self.canvas.add(self.display)

        self.score = TopLeftLabel(7, 4)
        self.add_widget(self.score)

        # add gesture widget
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

        # self.audio.toggle()
        # self.opp = self.player.score  # number of opp exc completed in time

        self.add_widget(self.explosions)

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

    def get_score(self):
        return self.player.score

    def on_update(self):
        # update game based on audio time
        self.audio.on_update()
        time = self.audio.get_time()
        self.display.on_update(time)
        self.player.on_update(time)

        score_text =  "Score: %d\n" % self.player.score
        score_text += "Streak: %d\n" % self.player.streak

        # get current gesture status
        self.gesture.on_update()
        touches = self.gesture.get_touch_states()
        hand = self.gesture.get_hand()
        score_text += "Hand: " + str(hand)

        self.score.set_text(score_text)

        # update game logic depending on which hand is in use
        for finger in range(4):
            touch = False

            if hand == "left":
                touch = self.gesture.check_touch_for_finger(4 - finger)
            if hand == "right":
                touch = self.gesture.check_touch_for_finger(finger + 1)

            if touch:
                self.player.on_button_down(finger)
            elif hand == "left" and not touches[4 - finger] or hand == "right" and not touches[finger + 1]:
                self.player.on_button_up(finger)

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
        kMargin = Window.width * 0.005
        kCursorAreaSize = (
            Window.width / 4 - 2 * kMargin,
            Window.height / 4 - 2 * kMargin,
        )
        kCursorAreaPos = (
            Window.width - kCursorAreaSize[0] - kMargin,
            kMargin,
        )
        self.gesture.resize_display(kCursorAreaPos, kCursorAreaSize)

        # resize label
        self.score.resize()


class ExplosionsWidget(Widget):
    def __init__(self, *args, **kwargs):
        super(ExplosionsWidget, self).__init__()
        self.explosions = []
        self.explosions_copy = []

    def add_explosion(self, pos, duration):
        # Explosion(pos, duration)
        ps = ParticleSystem("images/particle_explosion/particle.pex")
        ps.emitter_x = pos[0]
        ps.emitter_y = pos[1]
        ps.start()
        self.add_widget(ps)
        self.explosions.append(ps)
        self.explosions_copy.append(ps)
        Clock.schedule_once(self.stop_explosion, duration)

    def stop_explosion(self, *args):
        ps = self.explosions.pop(0)
        ps.stop()
        Clock.schedule_once(self.remove_explosion, 1)

    def remove_explosion(self, *args):
        ps = self.explosions_copy.pop(0)
        self.remove_widget(ps)


# holds data for gems and barlines.
class SongData(object):
    def __init__(self):
        super(SongData, self).__init__()
        self.solo = [[0, 0, True]]
        self.bg = []

    # read the gems and song data
    def read_data(self, solo_path, bg_path):

        # store solo as pairs of (sound time, lane index)
        with open(solo_path) as f:
            for line in f.readlines():
                split = line.strip().split(",")
                # self.solo.append((round(float(split[0])), self.solo[-1][1], False))
                self.solo[-1].append(float(split[0]))
                self.solo.append([float(split[0]), min(int(split[1]) - 1, 3)])

        # store bar lines as the time locations
        with open(bg_path) as f:
            self.bg = [float(line.split(",")[0]) for line in f.readlines()]


# Displays and controls all game elements: Nowbar, Buttons, BarLines, Gems.
class BeatMatchDisplay(InstructionGroup):
    MEASURE = Window.height * 0.2
    NOW_BAR = Window.height * 0.25
    BARLINE_WIDTH = 2
    NOWBAR_WIDTH = 8

    def __init__(self, song_data):
        super(BeatMatchDisplay, self).__init__()
        self.song_data = song_data
        song_solo_len = song_data.solo[-1][0]
        song_bg_len = song_data.bg[-1]

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

        self.offset = WIDTH / 8
        self.diff = (WIDTH - 2 * self.offset) / 3

        # bar lines
        self.lines = []
        self.line_colors = []
        for bar in self.song_data.bg:
            y = bar * self.MEASURE
            line = Line(points=[0, y, WIDTH, y], width=self.BARLINE_WIDTH,)
            line_color = Color(1, 1, 1)
            self.lines.append(line)
            self.line_colors.append(line_color)
            self.add(line_color)
            self.add(line)

        # now bar
        # self.add(Color(0.5, 0.5, 0.5))
        # self.add(
            # Line(points=[0, self.NOW_BAR, WIDTH, self.NOW_BAR], width=self.NOWBAR_WIDTH)
        # )

        # buttons
        self.buttons = []
        btn_texture = Image("images/purpleship.png").texture
        btn_pressed_texture = Image("images/yellowship.png").texture
        for i in range(4):
            button = ButtonDisplay(
                (i * self.diff + self.offset, self.NOW_BAR),
                Color(*self.colors[i]),
                texture=btn_texture,
                pressed_texture=btn_pressed_texture,
            )
            self.buttons.append(button)
            self.add(button)

        # gems
        self.gems = []
        # gem_width_half = Window.width / 50
        gem_texture = Image("images/asteroid.png").texture
        for gem in self.song_data.solo:
            if len(gem) < 3:
                continue
            gem_obj = GemDisplay(
                (gem[1] * self.diff + self.offset, gem[0] * self.MEASURE),
                Color(*self.colors[gem[1]]),
                texture=gem_texture,
            )
            # gem_obj = GemBarDisplay(
            #    (
            #        gem[1] * diff + offset - gem_width_half,
            #        gem[0] * self.MEASURE,
            #    ),
            #    (2 * gem_width_half, (gem[2] - gem[0]) * self.MEASURE),
            #    Color(*self.colors[gem[1]]),
            # )
            self.gems.append(gem_obj)
            self.add(gem_obj)

        # progress bar
        self.progress = ProgressBar(
            (Window.width, 0), (Window.width, Window.height), Color(0.2, 0.93, 0.48)
        )
        self.progress.set_total(max(song_solo_len, song_bg_len))
        self.add(self.progress)

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
    def on_update(self, time):
        offset = Window.width / 8
        diff = (Window.width - 2 * offset) / 3
        trans_y = -1 * time * self.MEASURE + self.NOW_BAR

        # update bar lines
        for i in range(len(self.song_data.bg)):
            bar = self.song_data.bg[i]

            # compute line endpoint locations
            y = bar * self.MEASURE + trans_y
            real_pt0 = (0, y)
            real_pt1 = (Window.width, y)
            (fake_pt0, size_scale) = self.fake_3d(real_pt0)
            (fake_pt1, size_scale) = self.fake_3d(real_pt1)

            # set the new locations
            self.lines[i].points = [*fake_pt0, *fake_pt1]
            self.lines[i].width = size_scale * self.BARLINE_WIDTH

            # set new color
            yc = 1 - np.clip(0.5 * (y - self.NOW_BAR) / Window.height, 0, 0.75)
            self.line_colors[i].rgb = (yc, yc, yc)

        # update gems
        gem_count = 0
        for gem in self.song_data.solo:
            if len(gem) < 3:
                continue

            # apply translation for real position
            # apply 3d effect for effective "fake" position
            gem_obj = self.gems[gem_count]
            real_pos = (
                gem[1] * diff + offset,
                gem[0] * self.MEASURE + trans_y,
            )
            (fake_pos, size_scale) = self.fake_3d(real_pos)

            # set the new values
            gem_obj.set_pos(fake_pos)
            gem_obj.set_size_scale(size_scale)
            gem_count += 1

        # update progress bar
        self.progress.on_update(time)

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
    def __init__(self, song_data, display, audio_ctrl, explosions):
        super(Player, self).__init__()
        self.song_data = song_data
        self.display = display
        self.audio_ctrl = audio_ctrl
        self.explosions = explosions

        self.time = 0
        self.gem_idx = 0
        self.score = 0
        self.streak = 0

    # called by MainWidget
    def on_button_down(self, lane):
        hit = False

        # if solo hasn't ended
        if self.gem_idx < len(self.song_data.solo):

            if (
                self.song_data.solo[self.gem_idx + 1][0] - SLOP
                <= self.time
                <= self.song_data.solo[self.gem_idx + 1][2] + SLOP
            ):
                self.gem_idx += 1
            # check if next gem is within slop window
            if (
                self.song_data.solo[self.gem_idx][0] - SLOP
                <= self.time
                <= self.song_data.solo[self.gem_idx][2] + SLOP
            ):
                # if abs(self.song_data.solo[self.gem_idx][0] - self.time) <= SLOP:

                # if lane matches, then we have a hit
                if self.song_data.solo[self.gem_idx][1] == lane:
                    self.display.gem_hit(self.gem_idx)
                    pos = (
                        lane * self.display.diff + self.display.offset,
                        self.display.NOW_BAR - Window.width / 20,
                    )
                    # self.display.NOW_BAR
                    self.explosions.add_explosion(pos, 0.5)
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
    def on_update(self, time):
        self.time = time

        # if gems still exist, check for pass gems
        while (
            self.gem_idx < len(self.song_data.solo)
            and self.song_data.solo[self.gem_idx][2] < self.time - SLOP
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
