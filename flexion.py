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


SF_PATH = "data/FluidR3_GM.sf2"



class MainWidget(BaseWidget):
	def __init__(self):
		super(MainWidget, self).__init__()
		

		self.bg = Rectangle(
			source="./images/horizon_bh.jpg", pos=self.pos, size=Window.size
		)
		self.canvas.add(self.bg)

		self.audio = Audio(2)
		self.synth = Synth(SF_PATH)
		self.audio.set_generator(self.synth)

		self.objects = AnimGroup()

		# add rockets to screen
		pos = (Window.width/2, 300)

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

		self.touching = False
		self.TOUCH = 10

		self.label = topleft_label()
		self.add_widget(self.label)

	def on_update(self):
		axis = 1
		thresh = 1
		
		self.audio.on_update()
		self.gesture.on_update()

		
		dist = self.gesture.get_directionality(axis, thresh)
		self.rocket.move_display(dist, axis)
		

		self.label.text = ""
		self.label.text += str(getLeapInfo())

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

	# proxy while we work on gesture detection
	def on_key_down(self, keycode, modifiers):
		gesture_proxy = lookup(keycode[1], "qwer", (1, 2, 3, 4))
		if gesture_proxy:
			# make rocket shoot
			# pass
			print("keypress")


	def on_key_up(self, keycode):
		gesture_proxy = lookup(keycode[1], "qwer", (1, 2, 3, 4))
		if gesture_proxy:
			# stop rocket shooting
			pass



if __name__ == "__main__":
	run(MainWidget)
	# run(MainWidget, fullscreen=True)
