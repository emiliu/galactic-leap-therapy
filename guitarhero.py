#guitar hero classes

#from pset7.py


import sys
sys.path.append('..')
from common.core import BaseWidget, run, lookup
from common.audio import Audio
from common.mixer import Mixer
from common.wavegen import WaveGenerator
from common.wavesrc import WaveBuffer, WaveFile, make_wave_buffers
from common.gfxutil import topleft_label

from kivy.graphics.instructions import InstructionGroup
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.graphics import PushMatrix, PopMatrix, Translate
from kivy.clock import Clock as kivyClock
from kivy.core.window import Window

import numpy as np


# creates the Audio driver
# load solo and bg audio tracks
# creates snippets for audio sound fx
class AudioController(object):
	def __init__(self):
		super(AudioController, self).__init__()
		self.audio = Audio(2)
		self.mixer = Mixer()

		self.audio.set_generator(self.mixer)

		self.solo_generator = WaveGenerator(WaveFile("songs/MoreThanAFeeling_solo.wav"))
		self.bg_generator = WaveGenerator(WaveFile("songs/MoreThanAFeeling_bg.wav"))
		self.sfx_generator = WaveGenerator(WaveFile("songs/cs_error.wav"))


		self.mixer.add(self.solo_generator)
		self.mixer.add(self.bg_generator)
		self.mixer.add(self.sfx_generator)
		
		self.solo_generator.reset()
		self.bg_generator.reset()
		self.sfx_generator.reset()
		self.muted = None

	# start / stop the song
	def toggle(self):
		self.solo_generator.play_toggle()
		self.bg_generator.play_toggle()
		print("toggle play state")
		print(self.solo_generator.frame, self.bg_generator.frame)

	# mute / unmute the solo track
	def set_mute(self, mute): #mute is 1 or 0 value
			
		self.solo_generator.set_gain(mute*.5)

	def temp_mute(self, mute):
		self.set_mute(0)

		self.muted = self.get_time()

	# play a sound-fx (miss sound)
	def play_sfx(self):
		self.sfx_generator.reset()
		self.sfx_generator.set_gain(1)
		self.sfx_generator.play()
		
		print("sound effect")


	def get_time(self):
		time = self.bg_generator.frame/Audio.sample_rate
		return time


	# needed to update audio
	def on_update(self):
		self.audio.on_update()

		if self.muted is not None:
			if self.get_time() > self.muted+.2:
				self.set_mute(1)
				





# holds data for gems and barlines.
class SongData(object):
	def __init__(self):
		super(SongData, self).__init__()

	# read the gems and song data. You may want to add a secondary filepath
	# argument if your barline data is stored in a different txt file.
	def read_data(self, filepath_gems, filepath_barline):
			#based on functions from lab2
		def lines_from_file(filename):
			newfile = open(filename)
			strlist =  newfile.readlines()
			return strlist

		def tokens_from_line(line):
			nline = line.strip()
			return nline.split('\t')


		def gems_from_file(filename):
			lines = lines_from_file(filename)
			out = []
			for l in lines:
				elems = tokens_from_line(l)
				gtype = int(float(elems[1])*10 % 10)
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


		gem_data = gems_from_file(filepath_gems) #list of (time, type) tuple
		barlines = bars_from_file(filepath_barline)
		
		return(gem_data, barlines)		
	# store data in this class
	# TODO: figure out how gem and barline data should be accessed...



# display for a single gem at a position with a color (if desired)
class GemDisplay(InstructionGroup):
	def __init__(self, pos, color):
		super(GemDisplay, self).__init__()

		self.pos = pos
		self.color = color
		
		self.shape = Rectangle(pos = pos, size = (150,800))
		self.add(self.shape)
	

	# change to display this gem being hit
	def on_hit(self):

		self.shape.source = "burst.png"

		if self.shape.pos[1] < 300:
			self.remove(self.shape)

	# change to display a passed gem
	def on_pass(self):
		self.shape.size = (50,50) #make it small

	# useful if gem is to animate
	def on_update(self, dt):
		pass
		


# display for a single barline
class BarlineDisplay(InstructionGroup):
	def __init__(self, pos):
		super(BarlineDisplay, self).__init__()

		self.pos = pos
		
		self.shape = Rectangle(pos = self.pos, size = (1000,10))
		self.add(self.shape)
		

	
		
		


# Displays one button on the nowbar
class ButtonDisplay(InstructionGroup):
	def __init__(self, pos, color):
		super(ButtonDisplay, self).__init__()
		self.color = Color(hsv = color)
		self.add(self.color)

		

	# displays when button is down (and if it hit a gem)
	def on_down(self, hit):
		self.shape.size = (250,250)

	# back to normal state
	def on_up(self):
		self.shape.size = (200,200)



# Displays a rectangle to represent the now bar
class NowBar(InstructionGroup):
	def __init__(self):
		super(NowBar, self).__init__()


		self.now_y = 300
		

		#buttons
		num_inter = 4
		self.buttons = []
		for i in range(num_inter):
			y = 200 #near left edge of screen
			x = np.interp((i), (0, num_inter), (200, int(Window.width)))

			hue = np.interp((i), (0, num_inter), (0,.8))

			color = (hue, 1, 1)
			button = ButtonDisplay(pos = (x,y), color = color)
			self.buttons.append(button)
			self.add(button)

	def get_slop_window(self):
		return (self.now_y+100, self.now_y-100)


# Displays and controls all game elements: Nowbar, Buttons, BarLines, Gems.
class BeatMatchDisplay(InstructionGroup):
	def __init__(self, gem_data, bar_data, time_keep_callback):
		super(BeatMatchDisplay, self).__init__()
		self.t = 0
		#barlines separate every n beats
		#gems represent notes
		#go through and fix them later\

		self.gem_data = gem_data
		self.bar_data = bar_data
		self.gems = []

		self.nowbar = NowBar()
		self.add(self.nowbar)


		self.timer_funct = time_keep_callback

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
			color = Color(hsv = (1,1,1))

			x = np.interp((gem[1]), (1, 5), (200, Window.width-200))
			pos = (60+x, int(gem[0]*self.time_dist+self.now_y))
			gem = GemDisplay(pos = pos, color = color)
			self.gems.append(gem)
			self.add(gem)

		self.add(PopMatrix())

		self.gem_to_remove = None


	def get_gem_y_loc(self, gem_idx):
		gem = self.gems[gem_idx]

		return gem.pos[1]-self.t*self.time_dist

		
		
	def slop_window(self):
		return self.nowbar.get_slop_window()

	# called by Player. Causes the right thing to happen
	def gem_hit(self, gem_idx):
		self.gems[gem_idx].on_hit()

		self.gem_to_remove = (self.t, self.gems[gem_idx])
		

	# called by Player. Causes the right thing to happen
	def gem_pass(self, gem_idx):
		self.gems[gem_idx].on_pass()

	# called by Player. Causes the right thing to happen
	def on_button_down(self, lane, hit):
		self.nowbar.buttons[lane].on_down(hit)



	# called by Player. Causes the right thing to happen
	def on_button_up(self, lane):
		self.nowbar.buttons[lane].on_up()


	# call every frame to handle animation needs
	def on_update(self) :
		#pass

		#tracking time manually
		#dt = self.kivyClock.frametime
		dt = self.timer_funct()
		self.t = dt

		self.trans.y = -self.t*self.time_dist
		#print(self.t)
		# dt = self.

		if self.gem_to_remove is not None:
			
			if self.t > self.gem_to_remove[0] + .2:
				self.remove(self.gem_to_remove[1])





		#put ~gems appearing code~ here, according to the time 
		#potentially put this code into another 
		

		#call note off for synth stuff



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

		self.slop = self.display.slop_window()
		self.mute_len = 50
		#print("slop", self.slop)

	# called by MainWidget
	def on_button_down(self, lane):
		#check if there is a gem hit, pass value to display
		#check if a gem is in the correct area 
		value = self.is_gem_hit(lane)
		print(value)
		if value == True:
			hit = True

		else:
			hit = False
			if value == "lane": #lane miss
				self.audio_ctrl.play_sfx()
				self.audio_ctrl.temp_mute(0)
				self.display.gem_pass(self.current_idx) 
				self.current_idx += 1
			else: #temporal miss
				self.audio_ctrl.play_sfx()
				self.audio_ctrl.temp_mute(0)

				
		self.display.on_button_down(lane, hit)


		
	#returns True if gem hit, ow returns type of miss
	def is_gem_hit(self, lane):
		if  self.display.get_gem_y_loc(self.current_idx) > self.slop[1] and self.display.get_gem_y_loc(self.current_idx) < self.slop[0]:
			print(self.gem_data[self.current_idx][1],lane+1)
			if self.gem_data[self.current_idx][1] == lane+1:
				self.display.gem_hit(self.current_idx)
				self.current_idx += 1
				print("gem hit")
				self.score += 1
				return True
			else:

				return "lane"
		else:

			return "temporal"
		

	# called by MainWidget
	def on_button_up(self, lane):
		self.display.on_button_up(lane)


	# needed to check for pass gems (ie, went past the slop window)
	def on_update(self):
		#print(self.display.get_gem_y_loc(self.current_idx))
		if self.display.get_gem_y_loc(self.current_idx) < self.slop[1]:
			self.display.gems[self.current_idx].on_pass()
			print("passed gem")
			self.current_idx += 1

		dt = self.display.timer_funct()
		self.t = dt