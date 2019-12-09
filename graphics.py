import numpy as np

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.core.image import Image
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line, Rectangle, Triangle
from kivy.graphics.instructions import InstructionGroup

from common.audio import Audio
from common.gfxutil import CRectangle, CEllipse
from common.core import BaseWidget, run, lookup
from common.kivyparticle import ParticleSystem


class Rocket(InstructionGroup):
    def __init__(self, pos, size, color, add_funct):
        super(Rocket, self).__init__()

        self.size = size
        self.pos = pos
        self.shape = CRectangle(
            csize=self.size,
            color=Color(hsv=color),
            cpos=pos,
            segments=4,
            source="images/rocketship.png",
        )

        self.add(self.shape)
        self.time = 0
        self.laser = None

        self.flame = ParticleSystem("images/particle_flame/particle.pex")
        self.flame.emitter_x = self.pos[0] - 50
        self.flame.emitter_y = self.pos[1]
        add_funct(self.flame)

    def flame_on(self):
        # self.flame.start()
        self.shape.source = "images/green_ship.png"

    def flame_off(self):
        # self.flame.stop()
        self.shape.source = "images/rocketship.png"


class NoteRoads(InstructionGroup):
    # notes represented as balls
    def __init__(self, pos):
        super(NoteRoads, self).__init__()
        self.pos = pos
        # self.radius = 10  # small dots
        self.radius = Window.width / 40  # small dots

        self.shape = CRectangle(cpos=self.pos, csize=(self.radius, 3 * self.radius))

        self.time = 0
        self.vel = 100

        self.add(self.shape)

        self.on_update(0)


class Laser(InstructionGroup):
    # small red circles shot at note asteroids
    def __init__(self, pos):
        super(Laser, self).__init__()
        self.pos = pos
        # self.radius = 10  # small dots
        self.radius = Window.width / 40  # small dots
        # self.color = Color(.5,.5,.5) #red

        self.shape = CEllipse(cpos=self.pos, csize=(self.radius, self.radius))

        self.time = 0
        self.vel = 100

        self.add(self.shape)

        self.on_update(0)

    def on_update(self, dt):

        # integrate vel to get pos
        x, y = self.shape.pos
        x += self.vel * dt

        self.shape.pos = (x, y)

        # self.shape.pos[0] += self.vel*dt

        # update time
        self.time += dt
        # print("update")

        # remove laser as it goes off screen
        if self.shape.pos[0] > Window.width:
            print("off screen")
            return False

        return True


class FlexShip(InstructionGroup):
    def __init__(self, pos):
        super(FlexShip, self).__init__()

        self.size = np.array([80, 80])
        # self.pos = pos
        self.shape = CRectangle(
            csize=self.size, cpos=pos, segments=4, source="images/ufo.png",
        )

        self.add(Color(1, 1, 1))
        self.add(self.shape)

        self.flame = ParticleSystem("images/particle_flame/particle.pex")
        self.flame.emitter_x = pos[0] - 50
        self.flame.emitter_y = pos[1]
        self.flame.start()

    def set_position(self, pos, axis=0):
        new_pos = np.array(self.shape.get_cpos())
        new_pos[axis] = pos
        self.shape.set_cpos(
            np.clip(new_pos, self.size / 2, Window.size - self.size / 2)
        )

    def move_position(self, delta, axis=0):
        new_pos = np.array(self.shape.get_cpos())
        new_pos[axis] += delta
        self.shape.set_cpos(
            np.clip(new_pos, self.size / 2, Window.size - self.size / 2)
        )

    def get_position(self):
        return self.shape.get_cpos()


class GemBarDisplay(InstructionGroup):
    def __init__(self, pos, size, color=None):
        super(GemBarDisplay, self).__init__()
        self.color = color
        self.add(self.color)
        self.add(Rectangle(pos=pos, size=size))

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
    SIZE = Window.width / 12

    def __init__(self, pos, color, texture=None):
        super(GemDisplay, self).__init__()
        self.pos = pos
        self.color = color
        # self.texture = texture

        # gem background
        # self.add(self.color)
        self.ellipse1 = CEllipse(cpos=pos, csize=(self.SIZE, self.SIZE))
        # self.add(self.ellipse1)
        # gem texture
        if texture is not None:
            self.add(Color(1, 1, 1, 1))
            self.ellipse2 = CEllipse(
                cpos=pos, csize=(self.SIZE, self.SIZE), texture=texture
            )
            self.add(self.ellipse2)
        else:
            self.ellipse2 = None

    def set_pos(self, pos):
        self.pos = pos
        self.ellipse1.set_cpos(pos)
        if self.ellipse2 is not None:
            self.ellipse2.set_cpos(pos)

    def set_size_scale(self, scale):
        self.ellipse1.set_csize((scale * self.SIZE, scale * self.SIZE))
        if self.ellipse2 is not None:
            self.ellipse2.set_csize((scale * self.SIZE, scale * self.SIZE))

    # change to display this gem being hit
    def on_hit(self):
        self.color.rgb = (0.0824, 0.498, 0.1216)
        if self.ellipse2:
            self.remove(self.ellipse2)

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

        SIZE = Window.width / 18

        self.color = color
        # self.add(self.color)
        # self.add(CEllipse(cpos=pos, csize=(SIZE, SIZE)))

        self.texture_color = Color(1, 1, 1, 1)
        self.add(self.texture_color)
        self.add(CEllipse(cpos=pos, csize=(SIZE, SIZE), texture=texture))

        # self.add(Color(1, 1, 1, 1))
        # self.size = (40, 40)
        # self.pos = pos
        # self.shape = CRectangle(
        #    csize=self.size, cpos=pos, segments=4, source="images/rocketship.png"
        # )
        # self.add(self.shape)

    # displays when button is down (and if it hit a gem)
    def on_down(self, hit):
        pass
        # if hit:
        # self.texture_color.a = 1
        # else:
        # self.color.a = 0.8

    # back to normal state
    def on_up(self):
        self.color.a = 1
        self.texture_color.a = 0


class TileDisplay(InstructionGroup):
    def __init__(self, pos, color, width, height, transform_callback=None):
        super(TileDisplay, self).__init__()
        self.pos = np.array(pos)
        self.color = color
        self.original_color = np.array(color.rgb)
        self.width = width
        self.height = height
        self.transform = transform_callback

        # each tile is two triangles to form a rectangle
        self.t0 = Triangle(points=[0, 0, 0, 0, 0, 0])
        self.t1 = Triangle(points=[0, 0, 0, 0, 0, 0])
        self.set_position(pos)

        self.add(self.color)
        self.add(self.t0)
        self.add(self.t1)

    def set_position(self, pos):
        pos = np.array(pos)
        v0 = pos + (self.width / 2, self.height / 2)
        v1 = pos + (-self.width / 2, self.height / 2)
        v2 = pos + (-self.width / 2, -self.height / 2)
        v3 = pos + (self.width / 2, -self.height / 2)

        if self.transform is not None:
            (v0, _) = self.transform(v0)
            (v1, _) = self.transform(v1)
            (v2, _) = self.transform(v2)
            (v3, _) = self.transform(v3)

        self.t0.points = [*v0, *v1, *v2]
        self.t1.points = [*v0, *v2, *v3]

    def on_update(self):
        y = self.t0.points[1]
        c_scale = 1 - np.clip(y / Window.height, 0, 1)
        self.color.rgb = c_scale * self.original_color


class MainWidget(BaseWidget):
    def __init__(self):
        super(MainWidget).__init__()


if __name__ == "__main__":
    run(MainWidget)
