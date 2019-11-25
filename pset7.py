#pset7.py


import sys
#sys.path.append('..')
from common.core import BaseWidget, run, lookup
from common.audio import Audio
from common.gfxutil import CEllipse, CRectangle, topleft_label
from common.mixer import Mixer
from common.wavegen import WaveGenerator
from common.wavesrc import WaveBuffer, WaveFile, make_wave_buffers

from kivy.core.window import Window
from kivy.core.image import Image
from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.graphics import PushMatrix, PopMatrix, Translate

import numpy as np


FRAME_RATE = 44100

WIDTH = Window.width
HEIGHT = Window.height
MEASURE = HEIGHT * 0.2
NOW_BAR = HEIGHT * 0.25

SLOP = 0.1 * FRAME_RATE

class MainWidget(BaseWidget) :
    def __init__(self):
        super(MainWidget, self).__init__()

        self.bg = Rectangle(
            source="images/vzmpv432havx.jpg", pos=self.pos, size=Window.size
        )
        self.canvas.add(self.bg)

        self.data = SongData()
        self.data.read_data('data/solo.csv', 'data/beats.csv')

        self.beats = BeatMatchDisplay(self.data)
        self.canvas.add(self.beats)
        self.audio = AudioController(('data/YouGotAnotherThingComin_LD4.wav', 'data/YouGotAnotherThingComin_TRKS4.wav', 'miss.wav'))
        self.player = Player(self.data, self.beats, self.audio)

        self.score = topleft_label()
        self.add_widget(self.score)

    def on_key_down(self, keycode, modifiers):
        # play / pause toggle
        if keycode[1] == 'p':
            self.audio.toggle()

        # button down
        button_idx = lookup(keycode[1], '12345', (0,1,2,3,4))
        if button_idx is not None:
            self.player.on_button_down(button_idx)

    def on_key_up(self, keycode):
        # button up
        button_idx = lookup(keycode[1], '12345', (0,1,2,3,4))
        if button_idx is not None:
            self.player.on_button_up(button_idx)

    def on_update(self):
        # update game based on audio frame
        frame = self.audio.solo.frame
        self.beats.on_update(frame)
        self.audio.on_update()
        self.player.on_update(frame)

        self.score.text = 'Score: %d\n' % self.player.score
        self.score.text += 'Streak: %d' % self.player.streak


# creates the Audio driver
# load solo and bg audio tracks
# creates snippets for audio sound fx
class AudioController(object):
    def __init__(self, song_path):
        super(AudioController, self).__init__()
        self.audio = Audio(2)
        self.mixer = Mixer()

        self.solo = WaveGenerator(WaveFile(song_path[0]))
        self.bg = WaveGenerator(WaveFile(song_path[1]))
        self.miss_file = None #WaveFile(song_path[2])

        self.mixer.add(self.solo)
        self.mixer.add(self.bg)
        self.audio.set_generator(self.mixer)

    # start / stop the song
    def toggle(self):
        self.solo.play_toggle()
        self.bg.play_toggle()

    # mute / unmute the solo track
    def set_mute(self, mute):
        if mute:
            self.solo.set_gain(0.0)
        else:
            self.solo.set_gain(1.0)

    # play a sound-fx (miss sound)
    def play_sfx(self):
        pass
        #self.mixer.add(WaveGenerator(self.miss_file))

    # needed to update audio
    def on_update(self):
        self.audio.on_update()


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
                split = line.strip().split(',')
                #self.solo.append((round(float(split[0]) * FRAME_RATE), self.solo[-1][1], False))
                self.solo[-1].append(round(float(split[0]) * FRAME_RATE))
                self.solo.append([round(float(split[0]) * FRAME_RATE), int(split[1])-1])

        # store bar lines as the frame locations
        with open(bg_path) as f:
            self.bg = [round(float(line.split(',')[0]) * FRAME_RATE) for line in f.readlines()]



class GemBarDisplay(InstructionGroup):
    def __init__(self, pos, size, color=None):
        super(GemBarDisplay, self).__init__()
        self.color = color
        self.add(self.color)
        self.add(Rectangle(pos=pos, size=size))

    # change to display this gem being hit
    def on_hit(self):
        print('hit')

    # change to display this gem being hit
    def on_hit(self):
        self.color.rgb = (0.0824, 0.498, 0.1216)

    # change to display a passed gem
    def on_pass(self):
        self.color.rgb = (0.1137, 0.149, 0.2314)

    # useful if gem is to animate
    def on_update(self, dt):
        pass


# display for a single gem at a position with a color (if desired)
class GemDisplay(InstructionGroup):
    def __init__(self, pos, color, texture):
        super(GemDisplay, self).__init__()
        # gem background
        self.color = color
        self.add(self.color)
        self.add(CEllipse(cpos=pos, csize=(50, 50)))
        # gem texture
        self.add(Color(1, 1, 1))
        self.add(CEllipse(cpos=pos, csize=(50, 50), texture=texture))

    # change to display this gem being hit
    def on_hit(self):
        self.color.rgb = (0.0824, 0.498, 0.1216)

    # change to display a passed gem
    def on_pass(self):
        self.color.rgb = (0.1137, 0.149, 0.2314)

    # useful if gem is to animate
    def on_update(self, dt):
        pass


# Displays one button on the nowbar
class ButtonDisplay(InstructionGroup):
    def __init__(self, pos, color, texture):
        super(ButtonDisplay, self).__init__()

        self.color = color
        self.add(self.color)
        self.add(CEllipse(cpos=pos, csize=(50, 50)))
        self.texture_color = Color(0, 0, 0, 0)
        self.add(self.texture_color)
        self.add(CEllipse(cpos=pos, csize=(50, 50), texture=texture))

        self.add(Color(1,1,1,1))
        self.size = (40,40)
        self.pos = pos
        self.shape = CRectangle(
            csize=self.size,
            cpos=pos,
            segments=4,
            source="images/redship.png"
        )
        self.add(self.shape)

    # displays when button is down (and if it hit a gem)
    def on_down(self, hit):
        if hit:
            self.texture_color.a = 1
        else:
            self.color.a = 0.8

    # back to normal state
    def on_up(self):
        self.color.a = 1
        self.texture_color.a = 0


# Displays and controls all game elements: Nowbar, Buttons, BarLines, Gems.
class BeatMatchDisplay(InstructionGroup):
    def __init__(self, gem_data):
        super(BeatMatchDisplay, self).__init__()
        self.gem_data = gem_data

        # TODO make these instance variables
        global MEASURE, NOW_BAR

        WIDTH = Window.width
        HEIGHT = Window.height
        MEASURE = HEIGHT * 0.2
        NOW_BAR = HEIGHT * 0.25
        print(WIDTH, HEIGHT)

        # collection of lane colors
        self.colors = ((1.000, 0.651, 0.188),
                       (0.843, 0.910, 0.729),
                       (0.302, 0.631, 0.663),
                       (0.180, 0.314, 0.467),
                       (0.380, 0.110, 0.208))

        offset = WIDTH / 8
        diff = (WIDTH - 2 * offset) / 4

        # translate object
        self.trans = Translate()

        # bar lines
        self.add(PushMatrix())
        self.add(self.trans)
        self.add(Color(1, 1, 1))
        for bar in self.gem_data.bg:
            self.add(Line(points=[0, bar/FRAME_RATE * MEASURE, WIDTH, bar/FRAME_RATE * MEASURE], width=2))
        self.add(PopMatrix())

        # now bar
        self.add(Color(0.5, 0.5, 0.5))
        self.add(Line(points=[0, NOW_BAR, WIDTH, NOW_BAR], width=10))

        # buttons
        self.buttons = []
        btn_texture = None # Image('cardboard.png').texture
        for i in range(5):
            button = ButtonDisplay((i*diff+offset, NOW_BAR), Color(*self.colors[i]), texture=btn_texture)
            self.buttons.append(button)
            self.add(button)

        # gems
        self.add(PushMatrix())
        self.add(self.trans)
        self.gems = []
        gem_width_half = 25
        gem_texture = None #Image('texture.png').texture
        for gem in self.gem_data.solo:
            if len(gem) < 3:
                continue
            #gem_obj = GemDisplay((gem[1]*diff+offset, gem[0]/FRAME_RATE * MEASURE), Color(*self.colors[gem[1]]), texture=gem_texture)
            gem_obj = GemBarDisplay((gem[1]*diff+offset - gem_width_half, gem[0]/FRAME_RATE * MEASURE),
                                    (2 * gem_width_half, (gem[2] - gem[0])/FRAME_RATE * MEASURE), Color(*self.colors[gem[1]]))
            self.gems.append(gem_obj)
            self.add(gem_obj)
        self.add(PopMatrix())


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
        self.trans.y = -1 * frame/FRAME_RATE * MEASURE + NOW_BAR



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

            if self.gem_data.solo[self.gem_idx + 1][0] - SLOP <= self.frame <= self.gem_data.solo[self.gem_idx + 1][2] + SLOP:
                self.gem_idx += 1
            # check if next gem is within slop window
            if self.gem_data.solo[self.gem_idx][0] - SLOP <= self.frame <= self.gem_data.solo[self.gem_idx][2] + SLOP:
            #if abs(self.gem_data.solo[self.gem_idx][0] - self.frame) <= SLOP:

                # if lane matches, then we have a hit
                if self.gem_data.solo[self.gem_idx][1] == lane:
                    self.display.gem_hit(self.gem_idx)
                    hit = True
                    self.score += 1
                    self.streak += 1

                # this gem is used
                self.gem_idx += 1

        self.display.on_button_down(lane, hit)
        self.audio_ctrl.set_mute(not hit)

        # miss handling
        if not hit:
            self.audio_ctrl.play_sfx()

            # reset streak
            if self.streak > 1: self.score += self.streak
            self.streak = 0

    # called by MainWidget
    def on_button_up(self, lane):
        self.display.on_button_up(lane)

    # needed to check for pass gems (ie, went past the slop window)
    def on_update(self, frame):
        self.frame = frame

        # if gems still exist, check for pass gems
        while self.gem_idx < len(self.gem_data.solo) and self.gem_data.solo[self.gem_idx][2] < self.frame - SLOP:
            # only enter the loop if there are pass gems
            self.display.gem_pass(self.gem_idx)
            self.gem_idx += 1
            self.audio_ctrl.set_mute(True)
            if self.streak > 1: self.score += self.streak
            self.streak = 0

if __name__ == "__main__":
    run(MainWidget)
