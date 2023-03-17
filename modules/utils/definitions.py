import pygame as pg
import numpy as np

EPSILON = 1e-11
SHIFT_EPSILON = EPSILON * 100000


def twoFiftyFiveToOnePointO(color):
    """Expects a 4-tuple with RGB Alpha.
       Returns a numpy array without alpha
       in 1.0 mode."""
    return np.array(color[:-1]) / 255


def makeColor(name):
    return twoFiftyFiveToOnePointO(pg.Color(name))


def safeMultiply(self, vector, multiplier):
    newVector = vector * multiplier
    for index in range(len(newVector)):
        self[index] = max(0, min(1.0, newVector[index]))
    return newVector


COLORS = {
    "blue": makeColor("blue"),
    "white": makeColor("white"),
    "black": makeColor("black"),
    "red": makeColor("red"),
    "green": makeColor("green"),
    "yellow": makeColor("yellow"),
    "marble1": makeColor("seagreen1"),
    "marble2": makeColor("seagreen4"),
    "wood1": makeColor("sienna1"),
    "wood2": makeColor("sienna4"),
    "gray": makeColor("gray")
}
