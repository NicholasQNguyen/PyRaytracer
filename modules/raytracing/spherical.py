import numpy as np

from .objects import Object3D
from ..utils.vector import normalize, magnitude


class Spherical(Object3D):
    def quadraticFormula(self, a, b, c):
        """Calulates the quadratic formula.
           Returns a tuple with -b plus and minus
           in the 0th and 1st index respectively."""
        plusB = (-b + np.sqrt(self.getDiscriminant(a, b, c))) / (2 * a)
        minusB = (-b - np.sqrt(self.getDiscriminant(a, b, c))) / (2 * a)
        return (plusB, minusB)

    def getDiscriminant(self, a, b, c):
        """Calulates the discriminent (term under the
           sqrt in the quadratic formula).
           Returns a float."""
        return b ** 2 - 4 * a * c

    def getNormal(self, surfacePoint, intersection=None):
        """Find the unit normal."""
        # https://www.scratchapixel.com/lessons/3d-basic-rendering/introduction-to-shading/shading-normals.html
        return normalize(surfacePoint - self.position)

    def getA(self, vector):
        """Returns the dot product of a vector by itself."""
        return 1 if magnitude(vector) == 1 else np.dot(vector, vector)

    def getB(self, vector1, vector2):
        """Expects normalized vectors.
           Returns the dot product of 2 vectors times 2."""
        return np.dot(vector1, vector2) * 2

    def getC(self, vector, subtractedTerm):
        """Returns the dot product of a vector by itself
           minus a term."""
        return np.dot(vector, vector) - subtractedTerm


class Sphere(Spherical):
    def __init__(self, radius, position, baseColor, ambient,
                 diffuse, specular, shininess, specCoeff,
                 reflective, image, refractiveIndex,
                 noiseFunction):
        super().__init__(position, baseColor, ambient,
                         diffuse, specular, shininess,
                         specCoeff, reflective, image,
                         refractiveIndex, noiseFunction)
        self.radius = radius

    def getRadius(self):
        """Returns the radius of the circle."""
        return self.radius

    def intersect(self, ray):
        """Find the intersection for the sphere.
           Returns either a float representing the distance
           to the sphere (t) or infinity if it misses"""
        # 06 Slides, slide 43
        q = ray.position - self.position
        # 1 b/c normalized
        a = self.getA(ray.direction)
        b = self.getB(q, ray.direction)
        c = self.getC(q, self.radius ** 2)
        # https://www.csee.umbc.edu/~olano/class/435-02-8/ray-sphere.html
        # We miss if discriminent is negative
        return np.inf if self.getDiscriminant(a, b, c) < 0 else \
            self.positiveOnly(min(self.quadraticFormula(a, b, c)))

    def getDistance(self):
        return 2 * self.radius

    def __repr__(self):
        return str(self.getBaseColor()) + " Sphere"


class Ellipsoid(Spherical):
    def __init__(self, a, b, c, position, baseColor, ambient,
                 diffuse, specular, shininess, specCoeff,
                 reflective, image, refractiveIndex,
                 noiseFunction):
        super().__init__(position, baseColor, ambient,
                         diffuse, specular, shininess, specCoeff,
                         reflective, image, refractiveIndex,
                         noiseFunction)
        self.a = a
        self.b = b
        self.c = c

    def intersect(self, ray):
        """Find the intersection for the ellipsoid.
           Returns either a float representing the distance
           to the ellipsoid (t) or infinity if it misses"""
        # 10 Slides, Slide 22
        q = ray.position - self.position
        s = (self.a, self.b, self.c)
        vOverS = ray.direction / s
        qOverS = q / s
        a = self.getA(vOverS)
        b = self.getB(vOverS, qOverS)
        c = self.getC(qOverS, 1)
        return np.inf if self.getDiscriminant(a, b, c) < 0 else \
            self.positiveOnly(min(self.quadraticFormula(a, b, c)))

    # TODO Do the rotation stuff
    """
    def rotateX(self, x, y, z):
        (x,
         y * np.cos(theta) - z * np.sin(theta),
         y * np.sin(theta) + z * np.cos(theta))

    def rotateY(self, x, y, z):
        (x,
         y * np.cos(theta) - z * np.sin(theta),
         y * np.sin(theta) + z * np.cos(theta))

    def rotateZ(self, x, y, z):
        (x,
         y * np.cos(theta) - z * np.sin(theta),
         y * np.sin(theta) + z * np.cos(theta))
    """
    def getDistance(self):
        return np.sqrt(self.a ** 2 + self.b ** 2 + self.c ** 2)

    def __repr__(self):
        return str(self.getBaseColor()) + " Ellipsoid"
