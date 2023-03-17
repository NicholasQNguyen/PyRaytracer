import numpy as np
from enum import Enum

from .objects import Object3D
from ..utils.vector import normalize


class Side(Enum):
    """Each side of the cube."""
    Top = 0
    Bottom = 1
    Right = 2
    Left = 3
    Front = 4
    Back = 5


class Plane(Object3D):
    def __init__(self, normal, position, baseColor,
                 ambient, diffuse, specular,
                 shininess, specCoeff, reflective,
                 image, refractiveIndex,
                 noiseFunction=None):
        super().__init__(position, baseColor, ambient,
                         diffuse, specular, shininess,
                         specCoeff, reflective, image,
                         refractiveIndex, noiseFunction)
        self.normal = normalize(normal)

    def getNormal(self, intersection=None):
        """Find the normal for the given object. Must override."""
        return self.normal

    def intersect(self, ray):
        """Find the intersection for the plane.
           Returns a t only if it's positive."""
        return self.positiveOnly(self.signedIntersect(ray))

    def signedIntersect(self, ray):
        """Find the intersection for the plane.
           Returns a t if positive or negative.
           For use in Cube class."""
        # 10 Slides, slide 16
        return np.inf if \
            (denom := np.dot(ray.direction, self.normal)) == 0 else \
            np.dot(self.position - ray.position, self.normal) / denom

    def getDistance(self):
        return 0

    def __repr__(self):
        # return str(self.getBaseColor()) + " Plane"
        return str(self.getBaseColor()) + " Plane"


class Cube(Object3D):
    def __init__(self, length, top, forward, position, baseColor, ambient,
                 diffuse, specular, shininess, specCoeff,
                 reflective, image, refractiveIndex,
                 noiseFunction):
        super().__init__(position, baseColor, ambient,
                         diffuse, specular, shininess,
                         specCoeff, reflective, image,
                         refractiveIndex, noiseFunction)
        self.length = length
        self.sides = []
        self.top = top
        self.forward = forward
        self.lastIntersectedPlane = None
        self.setSides()

    def setSides(self):
        for side in [Side.Top, Side.Bottom, Side.Right,
                     Side.Left, Side.Front, Side.Back]:
            self.sides.append(self.generateSide(side))

    def generateSide(self, side):
        distance = self.length / 2
        if side is Side.Top:
            normal = self.top
        elif side is Side.Bottom:
            normal = -self.top
        elif side is Side.Right:
            normal = np.cross(self.forward, self.top)
        elif side is Side.Left:
            normal = np.cross(self.top, self.forward)
        elif side is Side.Front:
            normal = self.forward
        elif side is Side.Back:
            normal = -self.forward
        else:
            raise Exception("We messed up somewhere \
                            in the cube side generation.")
        return Plane(normal=normal,
                     position=self.position + distance * normal,
                     baseColor=self.getBaseColor(),
                     ambient=self.getAmbient(),
                     diffuse=self.getDiffuse(),
                     specular=self.getSpecular(),
                     shininess=self.getShine(),
                     specCoeff=self.getSpecularCoefficient(),
                     reflective=self.getReflective(),
                     image=self.getImage(),
                     refractiveIndex=self.getRefractiveIndex())

    def intersect(self, ray):
        """Find the intersection for the cube."""
        maxEnter = 0
        minExit = np.inf
        intersections = [side.signedIntersect(ray) for side in self.sides]
        for i, side in enumerate(self.sides):
            # Is an enter
            if np.dot(ray.direction, side.getNormal()) < 0 \
              and intersections[i] > maxEnter:
                maxEnter = intersections[i]
                self.lastIntersectedPlane = side
            # Is an exit
            elif np.dot(ray.direction, side.getNormal()) > 0 \
              and intersections[i] < minExit:
                minExit = intersections[i]
        return maxEnter if maxEnter < minExit else np.inf

    def getNormal(self, intersection):
        """Find the normal for the given object. Must override."""
        return normalize(self.lastIntersectedPlane.getNormal())

    def getLength(self):
        """Find the normal for the given object. Must override."""
        return self.length

    def getDistance(self):
        return self.length

    def __repr__(self):
        return str(self.getBaseColor()) + " Cube"
