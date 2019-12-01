from common.audio import Audio
from common.mixer import Mixer
from common.wavegen import WaveGenerator, SpeedModulator
from common.wavesrc import WaveBuffer, WaveFile, make_wave_buffers

# creates the Audio driver
# load solo and bg audio tracks
# creates snippets for audio sound fx
class AudioController(object):
    def __init__(self, song_path, use_miss_sound=True):
        super(AudioController, self).__init__()
        self.audio = Audio(2)
        self.mixer = Mixer()
        self.speed_mod = SpeedModulator(self.mixer)

        self.solo = WaveGenerator(WaveFile(song_path[0]))
        self.bg = WaveGenerator(WaveFile(song_path[1]))
        if use_miss_sound:
            self.miss_file = WaveFile(song_path[2])
        else:
            self.miss_file = None

        self.mixer.add(self.solo)
        self.mixer.add(self.bg)
        self.audio.set_generator(self.speed_mod)

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
        if self.miss_file is not None:
            self.mixer.add(WaveGenerator(self.miss_file))

    # needed to update audio
    def on_update(self):
        self.audio.on_update()

    # get the current song playback position in seconds
    def get_time(self):
        return self.bg.frame / Audio.sample_rate

    # change the playback speed
    def set_speed(self, speed=1):
        self.speed_mod.set_speed(speed)
