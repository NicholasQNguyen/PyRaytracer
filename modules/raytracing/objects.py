"""
Author: Liz Matthews, Geoff Matthews
"""
from abc import ABC, abstractmethod
import numpy as np

from .materials import Material, NoiseMaterial


class Object3D(ABC):
    """Abstract base class for all objects in the raytraced scene.
       Has a position, material.
       Has getter methods for all material properties.
       Has abstract methods intersect and getNormal."""
    def __init__(self, position, baseColor, ambient,
                 diffuse, specular, shininess, specCoeff,
                 reflective, image, refractiveIndex,
                 noiseFunction=None):
        self.position = np.array(position)
        self.material = Material(baseColor,
                                 ambient,
                                 diffuse,
                                 specular,
                                 shininess,
                                 specCoeff,
                                 reflective,
                                 image,
                                 refractiveIndex) \
                        if noiseFunction is None else \
                        NoiseMaterial(baseColor,
                                      ambient,
                                      diffuse,
                                      specular,
                                      shininess,
                                      specCoeff,
                                      reflective,
                                      image,
                                      refractiveIndex,
                                      noiseFunction)

    def getMaterial(self):
        return self.material

    def getPosition(self):
        return self.position

    def getBaseColor(self):
        """Getter method for the material's color."""
        return self.material.getBaseColor()

    def getAmbient(self, intersection=None):
        """Getter method for the material's ambient color.
           Intersection parameter is unused for Ray Tracing Basics."""
        return self.material.getAmbient()

    def getDiffuse(self, intersection=None):
        """Getter method for the material's diffuse color.
           Intersection parameter is unused for Ray Tracing Basics."""
        return self.material.getDiffuse()

    def getSpecular(self, intersection=None):
        """Getter method for the material's specular color.
           Intersection parameter is unused for Ray Tracing Basics."""
        return self.material.getSpecular()

    def getShine(self):
        """Getter method for the material's shininess factor."""
        return self.material.getShine()

    def getSpecularCoefficient(self, intersection=None):
        """Getter method for the material's specular coefficient.
           Intersection parameter is unused for Ray Tracing Basics."""
        return self.material.getSpecularCoefficient()

    def getReflective(self):
        """Getter method for the material's color."""
        return self.material.getReflective()

    def getImage(self):
        """Getter method for the material's image."""
        return self.material.getImage()

    def getRefractiveIndex(self):
        """Getter method for the material's refractive index."""
        return self.material.getRefractiveIndex()

    def getNoiseFunction(self):
        """Getter method for the material's refractive index."""
        return self.material.getNoiseFunction()

    @abstractmethod
    def intersect(self, ray):
        """Find the intersection for the given object. Must override."""
        pass

    @abstractmethod
    def getNormal(self, intersection=None):
        """Find the normal for the given object. Must override."""
        pass

    @abstractmethod
    def getDistance(self, intersection=None):
        """Find the distance from one end to another
           for the given object. Must override."""
        pass

    def positiveOnly(self, t):
        """Returns t or infinity if t is negative."""
        return t if t >= 0 else np.inf
