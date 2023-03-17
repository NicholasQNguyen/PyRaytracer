"""
Author: Liz Matthews, Geoff Matthews
"""
from ..utils.vector import vec


class Material(object):
    """A class to contain all properties of a material.
       Contains ambient, diffuse, specular colors.
       Contains shininess property.
       Contains specular coefficient."""
    def __init__(self, baseColor, ambient, diffuse, specular,
                 shine=100, specCoeff=1.0, reflective=False,
                 image=None, refractiveIndex=1.0):
        self.baseColor = vec(*baseColor)
        self.ambient = vec(*ambient)
        self.diffuse = vec(*diffuse)
        self.specular = vec(*specular)
        self.shine = shine
        self.specCoeff = specCoeff
        self.reflective = reflective
        self.image = image
        self.refractiveIndex = refractiveIndex

    def getBaseColor(self):
        """Getter method for ambient color."""
        return self.baseColor

    def getAmbient(self):
        """Getter method for ambient color."""
        return self.ambient

    def getDiffuse(self):
        """Getter method for diffuse color."""
        return self.diffuse

    def getSpecular(self):
        """Getter method for specular color."""
        return self.specular

    def getShine(self):
        """Getter method for shininess factor."""
        return self.shine

    def getSpecularCoefficient(self):
        """Getter method for specular coefficient."""
        return self.specCoeff

    def getReflective(self):
        """Getter method for reflective."""
        return self.reflective

    def getImage(self):
        """Getter method for image"""
        return self.image

    def getRefractiveIndex(self):
        """Getter method for refractive index"""
        return self.refractiveIndex

    def getNoiseFunction(self):
        return None


class NoiseMaterial(Material):
    def __init__(self, baseColor, ambient, diffuse, specular,
                 shine=100, specCoeff=1.0, reflective=False,
                 image=None, refractiveIndex=1.0,
                 noiseFunction=None):
        super().__init__(baseColor, ambient, diffuse, specular,
                         shine=100, specCoeff=1.0, reflective=False,
                         image=None, refractiveIndex=1.0)
        self.noiseFunction = noiseFunction

    def getNoiseFunction(self):
        return self.noiseFunction
