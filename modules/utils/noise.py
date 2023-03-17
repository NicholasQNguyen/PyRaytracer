"""
Author: Liz Matthews, Geoff Matthews
Noise manager class
"""
import numpy as np
from enum import Enum

from .vector import smerp, lerp
from .definitions import COLORS


class Axes(Enum):
    """Each axis it the tree can rotate around."""
    X = 0
    Y = 1
    Z = 2


class NoiseMachine:
    def __init__(self,
                 noctaves=5,
                 octaveDilation=2,
                 minimum=0,
                 maximum=1,
                 nvalues=256,
                 seed=1234):
        self.noctaves = noctaves
        self.octaveDilation = octaveDilation
        self.nvalues = nvalues
        self.values = np.linspace(minimum, maximum, nvalues)
        self.permutations = np.arange(0, nvalues, 1)
        np.random.seed(seed)
        np.random.shuffle(self.values)
        np.random.shuffle(self.permutations)

    # One-dimensional noise
    def intNoise(self, i):
        return self.values[int(i) % self.nvalues]

    def smerpNoise(self, x):
        a = self.intNoise(np.floor(x))
        b = self.intNoise(np.ceil(x))
        xFrac = x - np.floor(x)
        return smerp(a, b, xFrac)

    def noise(self, x):
        s = 0.0
        for i in range(self.noctaves):
            s += self.smerpNoise(x*self.octaveDilation**i)/2**i
        return s*0.5

    # Two-dimensional noise
    def intNoise2d(self, i, j):
        """Given i and j, return a pseudo-random value.
        Uses permutations to shift i/j."""
        a = self.permutations[j % self.nvalues]
        b = self.permutations[(i + a) % self.nvalues]
        return self.values[b % self.nvalues]

    # Two-dimensional noise
    def intNoise3d(self, i, j, k):
        """Given i, j, and k, return a pseudo-random value.
        Uses permutations to shift i/j/k."""
        a = self.permutations[j % self.nvalues]
        b = self.permutations[(i + a) % self.nvalues]
        c = self.permutations[(i + b) % self.nvalues]
        return self.values[c % self.nvalues]

    def smerpNoise2d(self, x, y):
        """Smoothly interpolate given two dimensional points."""
        i = int(np.floor(x))
        j = int(np.floor(y))
        xFrac = x-i
        yFrac = y-j
        # randoms at four corners:
        n00 = self.intNoise2d(i, j)
        n10 = self.intNoise2d(i+1, j)
        n01 = self.intNoise2d(i, j+1)
        n11 = self.intNoise2d(i+1, j+1)
        # smerp along x
        nx0 = smerp(n00, n10, xFrac)
        nx1 = smerp(n01, n11, xFrac)
        # smerp along y
        return smerp(nx0, nx1, yFrac)

    def smerpNoise3d(self, x, y, z):
        """Smoothly interpolate given three dimensional points."""
        i = int(np.floor(x))
        j = int(np.floor(y))
        k = int(np.floor(z))
        xFrac = x - i
        yFrac = y - j
        zFrac = z - k
        # randoms at 6 corners:
        # 15 Slides, slide 34
        # Smerp on x
        # Back side
        n000 = self.intNoise3d(i, j, k)
        n100 = self.intNoise3d(i+1, j, k)
        nx00 = smerp(n000, n100, xFrac)
        n010 = self.intNoise3d(i, j+1, k)
        n110 = self.intNoise3d(i+1, j + 1, k)
        nx10 = smerp(n010, n110, xFrac)
        # Front corners
        n001 = self.intNoise3d(i, j, k+1)
        n101 = self.intNoise3d(i+1, j, k+1)
        nx00 = smerp(n001, n101, xFrac)
        n011 = self.intNoise3d(i, j+1, k+1)
        n111 = self.intNoise3d(i+1, j+1, k+1)
        nx01 = smerp(n011, n111, xFrac)
        # Smerp on y
        nxy0 = smerp(nx10, nx00, yFrac)
        nxy1 = smerp(nx00, nx01, yFrac)
        # Smerp on z
        return smerp(nxy0, nxy1, zFrac)

    def noise2d(self, x, y):
        """Cumulative noise at x and y using smerp."""
        s = 0.0
        for i in range(self.noctaves):
            s += self.smerpNoise2d(x*self.octaveDilation**i,
                                   y*self.octaveDilation**i)/2**i
        return s*0.5

    def noise3d(self, x, y, z):
        """Cumulative noise at x, y, and zusing smerp."""
        s = 0.0
        for i in range(self.noctaves):
            s += self.smerpNoise3d(x*self.octaveDilation**i,
                                   y*self.octaveDilation**i,
                                   z*self.octaveDilation**i)/2**i
        return s*0.5

    def noise2dTiled(self, x, y, xMod, yMod):
        """Cumulative noise at x and y using smerp, tilable."""
        s = 0.0
        for i in range(self.noctaves):
            s += self.smerpNoise2dTiled(x*self.octaveDilation**i,
                                        y*self.octaveDilation**i,
                                        xMod*self.octaveDilation**i,
                                        yMod*self.octaveDilation**i)/2**i
        return s*0.5

    def smerpNoise2dTiled(self, x, y, xMod, yMod):
        """Smoothly interpolate given two dimensional points, tilable."""
        i = int(np.floor(x))
        j = int(np.floor(y))
        xFrac = x-i
        yFrac = y-j

        # randoms at four corners:
        n00 = self.intNoise2d(i % xMod, j % yMod)
        n10 = self.intNoise2d((i+1) % xMod, j % yMod)
        n01 = self.intNoise2d(i % xMod, (j+1) % yMod)
        n11 = self.intNoise2d((i+1) % xMod, (j+1) % yMod)

        # smerp along x
        nx0 = smerp(n00, n10, xFrac)
        nx1 = smerp(n01, n11, xFrac)
        # smerp along y
        return smerp(nx0, nx1, yFrac)


class NoisePatterns(object):
    _instance = None

    @classmethod
    def getInstance(cls):
        if cls._instance is None:
            cls._instance = NoisePatterns()
        return cls._instance

    def __init__(self):
        self.noiseId = 0
        self.scale = 50
        self.nms = [NoiseMachine(seed=i) for i in range(5)]

    def next(self):
        self.noiseId += 1
        self.noiseId %= len(self.nms)

    def previous(self):
        self.noiseId -= 1
        self.noiseId %= len(self.nms)

    def clouds(self, x, y,
               c1=COLORS["blue"], c2=COLORS["white"]):
        noise = self.nms[self.noiseId].noise2d(x, y)
        return lerp(c1, c2, noise)

    def tiledClouds(self, x, y,
                    xMod=2,
                    yMod=2,
                    c1=COLORS["blue"],
                    c2=COLORS["white"]):
        noise = self.nms[self.noiseId].noise2dTiled(x, y, xMod, yMod)
        return lerp(c1, c2, noise)

    def marble(self, x, y,
               c1=COLORS["marble1"],
               c2=COLORS["marble2"],
               noiseStrength=0.2):
        noise = self.nms[self.noiseId].noise2d(x, y)
        value = np.sin(x + y + noise * noiseStrength * self.scale)
        # Adjust from [-1, 1] to [0, 1]
        value = (value + 1) / 2
        return lerp(c1, c2, value)

    def wood(self, x, y,
             c1=COLORS["wood1"],
             c2=COLORS["wood2"],
             noiseStrength=0.2):
        noise = self.nms[self.noiseId].noise2d(x, y)
        radius = np.sqrt(x**2 + y**2) * 10
        value = np.sin(radius + noise * noiseStrength * self.scale)
        # Adjust from [-1, 1] to [0, 1]
        value = (value + 1) / 2
        return lerp(c1, c2, value)

    def fire(self, x, y,
             c1=COLORS["red"],
             c2=COLORS["yellow"],
             noiseStrength=0.6):
        y /= 2
        xMiddle = 4
        yMiddle = 3
        noise = self.nms[self.noiseId].noise2d(x*2, y*2)
        color = lerp(c1, c2, noise)
        radius = np.sqrt((x-xMiddle)**2 + (y-yMiddle)**2)/4
        noise2 = self.nms[self.noiseId].noise2d(x + np.sin(y*2) * 0.5, y)
        radius += (noise2 - 0.5) * noiseStrength
        s = 1.0 - smerp(0.1, 1.0, radius)
        return color * s

    def clouds3D(self, x, y, z,
                 c1=COLORS["blue"], c2=COLORS["white"]):
        noise = self.nms[self.noiseId].noise3d(x, y, z)
        return lerp(c1, c2, noise)

    def marble3D(self, x, y, z,
                 c1=COLORS["marble1"],
                 c2=COLORS["marble2"],
                 noiseStrength=0.2):
        noise = self.nms[self.noiseId].noise3d(x, y, z)
        value = np.sin(x + y + z + noise * noiseStrength * self.scale)
        # Adjust from [-1, 1] to [0, 1]
        value = (value + 1) / 2
        return lerp(c1, c2, value)

    def wood3D(self, x, y, z,
               c1=COLORS["wood1"],
               c2=COLORS["wood2"],
               axis=Axes.Z,
               noiseStrength=0.2):
        noise = self.nms[self.noiseId].noise3d(x, y, z)
        radius = np.sqrt(x**2 + y**2) * 10
        value = np.sin(radius + noise * noiseStrength * self.scale)
        # Adjust from [-1, 1] to [0, 1]
        value = (value + 1) / 2
        return lerp(c1, c2, value)
