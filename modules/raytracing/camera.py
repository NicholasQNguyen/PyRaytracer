"""
Author: Liz Matthews, Geoff Matthews
"""
import numpy as np

from ..utils.vector import vec, lerp, normalize
from .ray import Ray


class Camera(object):
    """Camera object for raytracing.
    Initialization camera pointing
    at an arbitrary plane focus. Can get position
    and obtain a ray based on a percentage along
    the x and y of the focus plane."""

    def set(self,
            focus=vec(0, 0, 0),
            fwd=vec(0, 0, -1),
            up=vec(0, 1, 0),
            fov=90.0,
            distance=2.5,
            aspect=4/3):
        """Sets up the camera given the parameters.
           Calculates position, ul, ur, ll, and lr."""
        # 08 Slides, Slide 17
        self.fwd = normalize(fwd)
        self.up = normalize(up)
        self.right = np.cross(self.fwd, self.up)
        self.right = normalize(self.right)
        self.up = np.cross(self.right, self.fwd)
        self.up = normalize(self.up)
        # 08 Slides, Slides 28
        self.width = 2 * distance * np.tan(fov/2)
        self.height = np.reciprocal(aspect) * self.width
        self.position = focus - fwd * distance
        self.ul = focus + \
            (self.up * (self.height / 2)) - \
            (self.right * (self.width / 2))
        self.ur = focus + \
            (self.up * (self.height / 2)) + \
            (self.right * (self.width / 2))
        self.ll = focus - \
            (self.up * (self.height / 2)) - \
            (self.right * (self.width / 2))
        self.lr = focus - \
            (self.up * (self.height / 2)) + \
            (self.right * (self.width / 2))

    def __init__(self,
                 focus=vec(0, 0, 0),
                 fwd=vec(0, 0, -1),
                 up=vec(0, 1, 0),
                 fov=45.0,
                 distance=2.5,
                 aspect=4/3):
        self.set(focus, fwd, up, fov, distance, aspect)

    def getRay(self, xPercent, yPercent):
        """Returns a ray based on a percentage for the x and y coordinate."""
        p0 = lerp(self.ul, self.ur, xPercent)
        p1 = lerp(self.ll, self.lr, xPercent)
        worldPos = lerp(p0, p1, yPercent)
        return Ray(self.position, worldPos - self.position)

    def getPosition(self):
        """Getter method for position."""
        return self.position

    def getDistanceToFocus(self, point):
        """Getter method for distance from
           the given point to the center of focus."""
        focus = (self.ul + self.ur + self.ll + self.lr) / 4
        return np.linalg.norm(point - focus)

    def getForward(self):
        """Getter method for position."""
        return self.fwd
