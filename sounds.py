from common.core import BaseWidget, run

from common.audio import Audio
from common.synth import Synth
from common.note import NoteGenerator, Envelope
from common.wavegen import WaveGenerator, SpeedModulator
from common.wavesrc import WaveBuffer, WaveFile, make_wave_buffers

FRAME_RATE = 44100
SF_PATH = "./data/FluidR3_GM.sf2"


class NoteCluster(object):
    def __init__(self, synth, channel, notes):
        super(NoteCluster, self).__init__()
        if type(notes) is int:
            notes = [notes]
        self.notes = tuple(notes)
        self.synth = synth
        self.channel = channel

    def noteon(self):
        for note in self.notes:
            vel = 80
            self.synth.noteon(self.channel, note, vel)

    def noteoff(self):
        for note in self.notes:
            self.synth.noteoff(self.channel, note)


class NoteSequencer(object):
    def __init__(self, synth, notes, channel=0, program=(0, 0)):
        super(NoteSequencer, self).__init__()
        self.notes = [NoteCluster(synth, channel, note) for note in notes]
        self.synth = synth
        self.channel = channel
        self.program = program
        self.synth.program(self.channel, self.program[0], self.program[1])

        self.index = 0
        self.map = dict()
        self.stopped = False

    def noteon(self, keycode):
        if self.index >= len(self.notes):
            self.stopped = True
            return
        self.notes[self.index].noteon()
        self.map[keycode] = self.notes[self.index]
        self.index += 1

    def noteoff(self, keycode):
        if self.stopped:
            return
        self.map[keycode].noteoff()
        del self.map[keycode]


class MainWidget(BaseWidget):
    def __init__(self):
        super(MainWidget, self).__init__()

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

    def on_update(self):
        self.audio.on_update()

    def on_key_down(self, keycode, modifiers):
        self.notes.noteon(keycode[1])

    def on_key_up(self, keycode):
        self.notes.noteoff(keycode[1])


if __name__ == "__main__":
    run(MainWidget)
