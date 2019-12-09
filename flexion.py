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
import scipy.interpolate

from audio import AudioController
from gesture import GestureWidget
from graphics import FlexShip, TileDisplay, ProgressBar
from sounds import NoteCluster, NoteSequencer
from opposition import SongData


class MainWidget(BaseWidget):
    def __init__(self):

        super(MainWidget, self).__init__()

        # add background
        self.bg = Rectangle(
            source="./images/vaporwav.jpg", pos=self.pos, size=Window.size
        )
        self.canvas.add(self.bg)

        # load song data
        # data_manager = SongData()
        # gem_data, bar_data = data_manager.read_data(
        #    "songs/annot_test.txt", "songs/annot_barlines.txt"
        # )
        self.data = SongData()
        self.data.read_data("data/solo.csv", "data/beats.csv")
        self.audio = AudioController(
            [
                "data/YouGotAnotherThingComin_LD4.wav",
                "data/YouGotAnotherThingComin_TRKS4.wav",
            ],
            # ["songs/MoreThanAFeeling_solo.wav", "songs/MoreThanAFeeling_bg.wav",],
            use_miss_sound=False,
        )

        # create game
        self.display = BeatMatchDisplay(self.data)
        self.player = Player(self.data, self.display, self.audio)
        self.canvas.add(self.display)

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

        self.label = topleft_label()
        self.add_widget(self.label)

    def on_key_down(self, keycode, modifiers):
        # play / pause toggle
        if keycode[1] == "p":
            self.audio.toggle()

    def on_update(self):
        # use x-axis wrist angle
        AXIS = 0

        # update things based on current song time
        self.audio.on_update()
        time = self.audio.get_time()
        self.display.on_update(time)
        self.player.on_update(time)

        # handle rocket movemement
        self.gesture.on_update()
        wrist_angle = self.gesture.get_wrist_angle(AXIS)

        # option 1: set absolute position
        pos = wrist_angle / (np.pi / 2) * Window.width + (Window.width / 2)
        self.player.set_position(pos)

        # option 2: move incrementally
        # delta = wrist_angle * 10
        # self.player.move_position(delta)

        self.label.text = ""
        # self.label.text += "\nScore: %.2f\n" % self.player.score
        self.label.text += "Time: %.2f\n" % time

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


"""
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
"""


# Displays and controls all game elements: Nowbar, Buttons, BarLines, Gems.
class BeatMatchDisplay(InstructionGroup):
    NOW_BAR = Window.height * 0.25
    BARLINE_WIDTH = 2
    HEIGHT_PER_SECOND = Window.height * 0.2
    TILES_PER_SECOND = 5
    TILE_WIDTH = Window.width * 0.25

    def __init__(self, song_data):
        super(BeatMatchDisplay, self).__init__()

        self.song_data = song_data
        song_solo_len = song_data.solo[-1][0]
        song_bg_len = song_data.bg[-1]

        # bar lines
        self.lines = []
        self.line_colors = []
        for bar in self.song_data.bg:
            y = bar * self.HEIGHT_PER_SECOND + self.NOW_BAR
            line = Line(points=[0, y, Window.width, y], width=self.BARLINE_WIDTH,)
            line_color = Color(1, 1, 1)
            self.lines.append(line)
            self.line_colors.append(line_color)
            self.add(line_color)
            self.add(line)

        # "follow the path" tiles
        n_tiles = 1 + round(max(song_solo_len, song_bg_len) * self.TILES_PER_SECOND)
        self.tiles = np.zeros(n_tiles)
        self.tile_has_note = np.full(n_tiles, False)

        for gem in reversed(self.song_data.solo):
            gem_time = gem[0]
            gem_lane = gem[1]

            # get closest tile to the note
            tile_index = round(gem_time * self.TILES_PER_SECOND)

            # get normalized x-position
            norm_x = 0.1 + gem_lane * 0.2
            self.tiles[tile_index] = norm_x
            self.tile_has_note[tile_index] = True

        # smoothly fill in tiles without notes by cubic spline interpolation
        zero_indices = self.tiles == 0
        x = np.arange(len(self.tiles))
        self.tiles[zero_indices] = scipy.interpolate.pchip_interpolate(
            x[~zero_indices], self.tiles[~zero_indices], x[zero_indices],
        )

        # create the actual tile graphics
        self.tile_display = []
        for i in range(len(self.tiles)):
            pos = (
                self.tiles[i] * Window.width,
                i / self.TILES_PER_SECOND * self.HEIGHT_PER_SECOND + self.NOW_BAR,
            )
            if self.tile_has_note[i]:
                color = Color(1, 0, 0.5)
            else:
                color = Color(0.20, 0.93, 0.48)

            # depending on the "slope" of the path,
            # widen the tiles to make it easier
            if i > 0 and i < len(self.tiles) - 1:
                width_scale = 1 / np.cos(
                    np.arctan(
                        (self.tiles[i + 1] - self.tiles[i - 1])
                        / (
                            2
                            * self.HEIGHT_PER_SECOND
                            / self.TILES_PER_SECOND
                            / Window.height
                        )
                    )
                )
                # width_scale = 1 + 10 * np.abs(self.tiles[i+1] - self.tiles[i-1])
            else:
                width_scale = 1

            td = TileDisplay(
                pos,
                color,
                width_scale * self.TILE_WIDTH,
                self.HEIGHT_PER_SECOND / self.TILES_PER_SECOND,
                self.fake_3d,
            )
            self.tile_display.append(td)
            self.add(td)

        # rocket
        pos = (Window.width / 2, self.NOW_BAR)
        self.rocket = FlexShip(pos)
        self.add(self.rocket)

        # progress bar
        self.progress = ProgressBar(
            (Window.width, 0), (Window.width, Window.height), Color(0.2, 0.93, 0.48)
        )
        self.progress.set_total(max(song_solo_len, song_bg_len))
        self.add(self.progress)

    # call every frame to handle animation needs
    def on_update(self, time):
        trans_y = -1 * self.HEIGHT_PER_SECOND * time

        # move bar lines
        for i in range(len(self.song_data.bg)):
            bar = self.song_data.bg[i]

            # compute line endpoint locations
            y = bar * self.HEIGHT_PER_SECOND + self.NOW_BAR + trans_y
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

        # move tiles
        for i in range(len(self.tiles)):
            pos = np.array(
                [
                    self.tiles[i] * Window.width,
                    i / self.TILES_PER_SECOND * self.HEIGHT_PER_SECOND
                    + self.NOW_BAR
                    + trans_y,
                ]
            )
            if pos[1] > -0.1 * Window.height and pos[1] < 2 * Window.height:
                self.tile_display[i].set_position(pos)
                self.tile_display[i].on_update()

        # update progress bar
        self.progress.on_update(time)

    def set_rocket_position(self, pos):
        self.rocket.set_position(pos)

    def move_rocket_position(self, delta):
        self.rocket.move_position(delta)

    def get_tile(self, time):
        index = round(time * self.TILES_PER_SECOND)
        return (
            self.tile_display[index].pos,
            (self.tile_display[index].width, self.tile_display[index].height),
        )

    # apply a fake 3d effect to the given point
    def fake_3d(self, pt):
        (in_x, in_y) = pt

        # point at "infinity"
        # roughly center of screen
        (c_x, c_y) = (Window.width / 2, Window.height * 0.425)

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

    # needed to check for pass gems (ie, went past the slop window)
    def on_update(self, time):
        self.time = time

    # tell the game logic the current position of the rocket
    def set_position(self, pos):
        self.display.set_rocket_position(pos)
        self.check_path(pos)

    def move_position(self, delta):
        self.display.move_rocket_position(delta)
        pos = self.display.rocket.get_position()
        self.check_path(pos)

    # check if the player is following the path or not
    def check_path(self, player_pos):
        # find the current tile and check distance to player
        (t_pos, t_size) = self.display.get_tile(self.time)
        x_dist = np.abs(player_pos - t_pos[0])

        if x_dist < t_size[0] / 2:
            # on the current tile
            self.audio_ctrl.set_speed(1)
        else:
            # not on the current tile
            # slow down the song smoothly
            speed = 1 - np.arctan(5 * (x_dist - t_size[0] / 2) / Window.width)
            self.audio_ctrl.set_speed(np.clip(speed, 0.2, 1))


if __name__ == "__main__":
    run(MainWidget)
    # run(MainWidget, fullscreen=True)
