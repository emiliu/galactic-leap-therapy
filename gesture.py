import sys
import numpy as np

sys.path.append("..")

from common.core import BaseWidget, run
from common.gfxutil import (
    topleft_label,
    Cursor3D,
    AnimGroup,
    KFAnim,
    scale_point,
    CEllipse,
)
from common.kinect import Kinect
from common.leap import getLeapInfo, getLeapFrame

from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line
from kivy.graphics.instructions import InstructionGroup


class GestureWidget(InstructionGroup):
    # set up size / location of 3DCursor object
    kLeapRange = ((-250, 250), (50, 600), (-200, 250))
    kMargin = Window.width * 0.05
    kCursorAreaSize = Window.width - 2 * kMargin, Window.height - 2 * kMargin
    kCursorAreaPos = kMargin, kMargin

    # constants
    NUM_FINGERS = 5

    def __init__(
        self,
        leap_range=None,
        cursor_area_pos=None,
        cursor_area_size=None,
        size_range=None,
        display_trailing_cursors=True,
    ):
        super(GestureWidget, self).__init__()

        # leap size/bounding box setup
        self.leap_range = leap_range or self.kLeapRange
        cursor_area_pos = cursor_area_pos or self.kCursorAreaPos
        cursor_area_size = cursor_area_size or self.kCursorAreaSize
        size_range = size_range or (5, 20)

        # past positions
        self.POSITION_HISTORY = 10
        self.palm_pts = np.zeros((self.POSITION_HISTORY, 3))
        self.finger_pts = np.zeros((self.POSITION_HISTORY, self.NUM_FINGERS, 3))

        # fingertip touch detection
        self.touch_states = [False] * self.NUM_FINGERS

        # set up cursors for fingertips
        self.finger_cursors = []
        for i in range(0, self.NUM_FINGERS):
            self.finger_cursors.append(
                Cursor3D(
                    cursor_area_size,
                    cursor_area_pos,
                    (0.2, 0.6, 0.2),
                    size_range=size_range,
                )
            )

        self.finger_cursors_1 = None
        if display_trailing_cursors:
            self.finger_cursors_1 = []
            for i in range(0, self.NUM_FINGERS):
                self.finger_cursors_1.append(
                    Cursor3D(
                        cursor_area_size,
                        cursor_area_pos,
                        (0.1, 0.3, 0.1),
                        size_range=size_range,
                    )
                )

        # cursor for palm
        self.palm_cursor = Cursor3D(
            cursor_area_size, cursor_area_pos, (1, 1, 1), size_range=size_range
        )
        self.palm_cursor_1 = None
        if display_trailing_cursors:
            self.palm_cursor_1 = Cursor3D(
                cursor_area_size,
                cursor_area_pos,
                (0.5, 0.5, 0.5),
                size_range=size_range,
            )

        # lines between palm and fingertips
        self.finger_lines = []
        for i in range(self.NUM_FINGERS):
            self.finger_lines.append(Line(points=[0, 0, 0, 0], width=2))

        # add to canvas
        self.add(Color(1, 1, 1))
        for fl in self.finger_lines:
            self.add(fl)

        if display_trailing_cursors:
            self.add(self.palm_cursor_1)
            for fc in self.finger_cursors_1:
                self.add(fc)

        self.add(self.palm_cursor)
        for fc in self.finger_cursors:
            self.add(fc)

    def on_update(self):
        leap_frame = getLeapFrame()

        if leap_frame.valid and np.all(leap_frame.hands[0].palm_pos != [0, 0, 0]):
            # get and store new palm position
            palm_pt = leap_frame.hands[0].palm_pos
            palm_pt_norm = scale_point(palm_pt, self.leap_range)
            self.palm_pts = np.concatenate((np.array([palm_pt]), self.palm_pts[:-1]))

            # get and store new fingertip positions
            finger_pts = leap_frame.hands[0].fingers
            finger_pts_norm = [scale_point(pt, self.leap_range) for pt in finger_pts]
            self.finger_pts = np.concatenate(
                (np.array([finger_pts]), self.finger_pts[:-1])
            )

            self.update_graphics(palm_pt_norm, finger_pts_norm)

    def resize_display(self, cursor_area_pos=None, cursor_area_size=None):
        cursor_area_pos = cursor_area_pos or self.kCursorAreaPos
        cursor_area_size = cursor_area_size or self.kCursorAreaSize

        self.palm_cursor.resize(cursor_area_pos, cursor_area_size)
        for c in self.finger_cursors:
            c.resize(cursor_area_pos, cursor_area_size)

        if self.palm_cursor_1 is not None:
            self.palm_cursor_1.resize(cursor_area_pos, cursor_area_size)
            for c in self.finger_cursors_1:
                c.resize(cursor_area_pos, cursor_area_size)

    # return all fingers that have just touched in this instant,
    # or False if there are none
    def check_touch(self):
        detected_fingers = []
        for f in range(1, self.NUM_FINGERS):
            if self.check_touch_for_finger(f):
                detected_fingers.append(f)

        if len(detected_fingers) == 0:
            return False
        return detected_fingers

    # return (target_finger_touched, other_fingers_touched)
    # e.g. (True, [1, 2, 4])
    def check_touch_with_preference(self, target_finger):
        target_finger_touched = self.check_touch_for_finger(target_finger)

        other_fingers_touched = []
        for f in range(1, self.NUM_FINGERS):
            if self.check_touch_for_finger(f):
                other_fingers_touched.append(f)

        return (target_finger_touched, other_fingers_touched)

    # check if a given finger has just touched at this moment
    def check_touch_for_finger(self, target_finger):
        assert target_finger > 0 and target_finger < self.NUM_FINGERS, target_finger

        DETECTION_DISTANCE_MIN = 40
        DETECTION_DISTANCE_MAX = 60

        # logic to detect a touch or a release
        touched = False
        released = False

        # check distance
        distance = np.linalg.norm(
            self.finger_pts[0, target_finger] - self.finger_pts[0, 0]
        )
        touched = touched or (distance < DETECTION_DISTANCE_MIN)
        released = released or (distance > DETECTION_DISTANCE_MAX)

        # only return true on the first moment of touch
        if touched and not self.touch_states[target_finger]:
            self.touch_states[target_finger] = True
            return True

        # reset state upon detecting release
        if released and self.touch_states[target_finger]:
            self.touch_states[target_finger] = False

        return False

    # return whether a finger is touched or not
    def get_touch_state(self, finger):
        return self.touch_states[finger]

    # return fingers touched
    def get_touch_states(self):
        return self.touch_states

    # return whether any fingers are currently touched
    def get_any_touch_state(self):
        return any(self.touch_states)

    # called by on_update
    def update_graphics(self, palm_pt_norm, finger_pts_norm):
        # set palm and fingertip positions
        if self.palm_cursor_1 is not None:
            self.palm_cursor_1.set_pos(
                self._flip_y_z(scale_point(self.palm_pts[-1], self.leap_range))
            )
            for i, pt in enumerate(
                [scale_point(p, self.leap_range) for p in self.finger_pts[-1]]
            ):
                self.finger_cursors_1[i].set_pos(self._flip_y_z(pt))

        # set palm and fingertip positions
        self.palm_cursor.set_pos(self._flip_y_z(palm_pt_norm))
        for i, pt in enumerate(finger_pts_norm):
            self.finger_cursors[i].set_pos(self._flip_y_z(pt))

        # set fingertip colors for non-thumb fingers
        for i in range(1, self.NUM_FINGERS):
            if self.touch_states[i]:
                self.finger_cursors[i].set_color((0.6, 0.2, 0.2))
            else:
                self.finger_cursors[i].set_color((0.2, 0.6, 0.2))

        # set line positions
        for i in range(self.NUM_FINGERS):
            (palm_x, palm_y) = self.palm_cursor.get_screen_xy()
            (finger_x, finger_y) = self.finger_cursors[i].get_screen_xy()
            self.finger_lines[i].points = [palm_x, palm_y, finger_x, finger_y]

    def _flip_y_z(self, pt):
        assert len(pt) == 3
        return np.array([pt[0], 1 - pt[2], 1 - pt[1]])

    # computes palm to middle finger angle in radians
    def get_wrist_angle(self, axis):
        # 0 axis is x/-z, 1 axis is y/-z
        # middle finger to palm vectors
        vector_pm = self.finger_pts[0, 2] - self.palm_pts[0]

        if vector_pm[2] == 0:
            return 0
        return np.arctan(vector_pm[axis] / -vector_pm[2])

    # detect whether the left or right hand is in use
    def get_hand(self):
        index = self.finger_pts[0, 1]
        pinky = self.finger_pts[0, 4]

        # check x coordinate
        if index[0] < pinky[0]:
            return "right"
        elif index[0] > pinky[0]:
            return "left"
        return None


class MainWidget(BaseWidget):
    def __init__(self):
        super(MainWidget, self).__init__()
        self.label = topleft_label()
        self.add_widget(self.label)
        self.gesture = GestureWidget()
        self.canvas.add(self.gesture)

    def on_update(self):
        self.gesture.on_update()
        self.label.text = str(getLeapInfo()) + "\n"

        touch_fingers = self.gesture.check_touch()
        if touch_fingers:
            print(touch_fingers)

        wrist_pos = self.gesture.get_relative_wrist_position(0)
        if np.abs(wrist_pos) > 1:
            print(wrist_pos)


if __name__ == "__main__":
    run(MainWidget)
