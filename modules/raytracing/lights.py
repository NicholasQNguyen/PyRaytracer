import numpy as np

from abc import ABC, abstractmethod
from ..utils.vector import vec, normalize, magnitude


class AbstractLight(ABC):
    def __init__(self, color, position):
        self.color = color
        self.position = position

    def getColor(self):
        """Returns the color of the light"""
        return self.color

    @abstractmethod
    def getVectorToLight(self, point):
        """Returns a vector pointing towards the light"""
        pass

    @abstractmethod
    def getDistance(self, point):
        """Returns the distance to the light"""
        pass


class PointLight(AbstractLight):
    def __init__(self, color, position=vec(0, 0, 0)):
        super().__init__(color, position)

    def getVectorToLight(self, point):
        """Returns a normalized vector pointing towards the light"""
        return normalize(self.position - point)

    def getDistance(self, point):
        """Returns the distance to the light"""
        return magnitude(self.position - point)

    def __repr__(self):
        return "Point Light"


class DirectionalLight(AbstractLight):
    def __init__(self, color, position=vec(0, 0, 0), lightVector=vec(0, 0, 0)):
        super().__init__(color, position)
        self.lightVector = lightVector

    def getVectorToLight(self, point):
        """Returns a vector pointing towards the light"""
        return self.lightVector

    def getDistance(self, point):
        """Returns the distance to the light"""
        return np.inf

    def __repr__(self):
        return "Directional Light"
