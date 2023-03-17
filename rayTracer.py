# textures on planes,
""" Author: Liz Matthews, Geoff Matthews """
import numpy as np
import pygame as pg

from render import ProgressiveRenderer, ShowTypes
# from quilt import QuiltRenderer
# from reverseQuilt import RQuiltRenderer
from modules.raytracing.scene import Scene
from modules.raytracing.spherical import Sphere, Ellipsoid
from modules.raytracing.planar import Plane
from modules.raytracing.ray import Ray
from modules.utils.vector import vec, normalize, lerp
from modules.utils.definitions import twoFiftyFiveToOnePointO

SCREEN_MULTIPLIER = 1/16
WIDTH = 10800
HEIGHT = 7200
MAX_RECURSION_DEPTH = 5
X = 0
Y = 1
Z = 2
AIR = None


class RayTracer(ProgressiveRenderer):
    def __init__(self,
                 width=int(WIDTH * SCREEN_MULTIPLIER),
                 height=int(HEIGHT * SCREEN_MULTIPLIER),
                 show=ShowTypes.PerColumn,
                 samplePerPixel=1,
                 file=None):
        super().__init__(width, height, show=show,
                         samplePerPixel=samplePerPixel,
                         file=file)
        self.fog = vec(0.7, 0.9, 1.0)
        self.scene = Scene(aspect=width/height, fov=45)
        print("Camera Position:", self.scene.camera.getPosition())
        for obj in self.scene.objects:
            print(repr(obj) + " Position: " + str(obj.position))
        for light in self.scene.lights:
            print(repr(light) + " Position: " + str(light.position))

    def getBetweenAngle(self, vector1, vector2):
        """Returns an angle that is
           between vector1 and vector2.
           Expects normalized vectors."""
        # 03 Slides, Slide 32
        # https://www.cuemath.com/geometry/angle-between-vectors/
        return np.arccos(np.dot(vector1, vector2))

    def getReflectionAngle(self, vector1, vector2):
        """Returns an angle that is
           the reflection of vector1 and vector2.
           Expects normalized vectors."""
        # 03 Slides, Slide 32
        # https://www.cuemath.com/geometry/angle-between-vectors/
        return np.dot(vector1, vector2)

    def getReflectionVector(self, vector, normal):
        """Returns the vector that is the reflection
           of the vector off of a surface.
           Expects normalized vectors."""
        # 03 Slides, Slide 32
        # https://www.cuemath.com/geometry/angle-between-vectors/
        return normalize(-(i := (np.dot(vector, normal) * normal)) +
                         (vector - i))

    def snellsLaw(self, transmitting=AIR, external=AIR):
        # 13 Slides, slide 7
        if transmitting is not AIR and external is not AIR:
            external.getRefractiveIndex() / transmitting.getRefractiveIndex()
        # Exiting
        elif transmitting is AIR:
            return 1
        # Entering
        elif external is AIR:
            return 1/transmitting.getRefractiveIndex()

    def getRefractiveVector(self, vector, normal, ratio):
        """Returns the position where a ray would start
           when refracting."""
        # 13 Slides, slide 12
        dotProduct = np.dot(-vector, normal)
        return (ratio * dotProduct -
                np.sqrt(1 - (ratio ** 2) * (1 - dotProduct ** 2))
                ) * normal + ratio * vector

    def getReflectance(self, obj, origin=AIR):
        """Returns a float of the reflectance.
           Entering from the origin into the obj."""
        # 13 Slides, slide 26
        etaObj = obj.getRefractiveIndex()
        etaOrigin = 1.0 if origin is AIR else origin.getRefractiveIndex()
        return ((etaObj - etaOrigin)/(etaObj + etaOrigin)) ** 2

    def schlick(self, reflectance, theta):
        """Returns a float. The angle by which things
           change when entering a refractive object."""
        # 13 Slides, slide 27
        return reflectance + (1 - reflectance) * (1 - np.cos(theta)) ** 5

    def returnImage(self, obj, surfaceHitPoint):
        """Returns the color of the image we hit."""
        # 11 Slides, Slide 20
        if type(obj) is Sphere or \
           type(obj) is Ellipsoid:
            # 11 Slides, Slide 49
            d = normalize(obj.getPosition() - surfaceHitPoint)
            u = 0.5 + (np.arctan2(d[Z], d[X]) / (2 * np.pi))
            v = np.arccos(d[Y]) / np.pi
            # 11 Slides, Slide 21
            px = int(u * obj.getImage().get_width()) % \
                obj.getImage().get_width()
            py = int(v * obj.getImage().get_height()) % \
                obj.getImage().get_height()
            return twoFiftyFiveToOnePointO(obj.getImage().get_at((px, py)))
        # TODO get working for cubes
        elif type(obj) is Plane:
            normal = obj.getNormal()
            forward = self.scene.camera.getForward()
            u = np.cross(normal, forward)
            v = np.cross(normal, u)
            # 11 Slides, Slide 24
            p = normalize(surfaceHitPoint - obj.getPosition())
            coordinateU = int(np.dot(u, p)) % obj.getImage().get_width()
            coordinateV = int(np.dot(v, p)) % obj.getImage().get_height()
            return twoFiftyFiveToOnePointO(obj.getImage().get_at(
                (coordinateU, coordinateV)))

    def getDiffuse(self, vectorToLight, normal):
        """Gets the diffuse. Expects normalized vectors"""
        return max(0, self.getReflectionAngle(vectorToLight, normal))

    def getSpecularAngle(self, vectorToLight, normal,
                         cameraRay, obj):
        # 07 Slides, slide 30
        halfwayVector = normalize(-vectorToLight + cameraRay.direction)
        # 07 Slides, Slide 24 + Slide 27
        return self.getReflectionAngle(normal, halfwayVector) ** \
            obj.getShine() * \
            obj.getSpecularCoefficient()

    def getSpecularColor(self, specularAngle, objectSpecularColor):
        # 07 Slides, Slide 20
        return specularColor if \
            (specularColor := specularAngle * objectSpecularColor)[X] > 0 \
            else vec(0, 0, 0)  # Prevent black specular spots

    def recur(self, ray, value, recursionCount):
        return self.getColorR(ray, recursionCount + 1) * value \
               if value != 0 and recursionCount < MAX_RECURSION_DEPTH \
               else np.zeros(3)

    def getColorR(self, ray, recursionCount=0):
        """Returns color with diffuse and specualr attached.
           Expects a normalized ray."""
        color = np.zeros(3)
        nearestObject, minDist = self.scene.nearestObject(ray)
        # We hit nothing
        if nearestObject is None:
            return self.fog
        surfaceHitPoint = ray.getPositionAt(minDist)
        normal = nearestObject.getNormal(surfaceHitPoint)
        # Reflect if it's reflective
        reflectionRay = Ray(surfaceHitPoint,
                            self.getReflectionVector(ray.direction,
                                                     normal))
        reflectiveColor = self.recur(reflectionRay,
                                     nearestObject.getReflective(),
                                     recursionCount)
        # Refractive stuff
        exitOrEnterCheck = np.dot(ray.direction, normal)
        # Entering
        if exitOrEnterCheck < 0 and nearestObject.getRefractiveIndex() != 0:
            ratio = self.snellsLaw(transmitting=nearestObject)
            refractiveRay = Ray(surfaceHitPoint,
                                self.getRefractiveVector(ray.direction,
                                                         normal,
                                                         ratio))
            oppSide = refractiveRay.getPositionAt(nearestObject.getDistance())
            exitingRay = Ray(oppSide,
                             self.getRefractiveVector(refractiveRay.direction,
                                                      normal,
                                                      ratio))
            refractiveColor = self.recur(exitingRay,
                                         nearestObject.getRefractiveIndex(),
                                         recursionCount)
        # Exiting
        elif exitOrEnterCheck > 0 and nearestObject.getRefractiveIndex() != 0:
            ratio = self.snellsLaw(external=nearestObject)
            refractiveRay = Ray(self.getRefractiveVector(ray.direction,
                                                         normal,
                                                         ratio),
                                -ray.direction)
            oppSide = refractiveRay.getPositionAt(nearestObject.getDistance())
            exitingRay = Ray(oppSide,
                             self.getRefractiveVector(refractiveRay.direction,
                                                      normal,
                                                      ratio))
            refractiveColor = self.recur(exitingRay,
                                         nearestObject.getRefractiveIndex(),
                                         recursionCount)
        else:
            refractiveColor = vec(1, 1, 1)
        # Fresnal
        R0 = self.getReflectance(nearestObject)
        RTheta = self.schlick(R0, self.getBetweenAngle(ray.direction, normal))
        # TODO Do i normlize this?
        reflectAndRefractColor = normalize(lerp(reflectiveColor,
                                                refractiveColor,
                                                RTheta))
        color = color + reflectAndRefractColor
        if nearestObject.getImage() is not None:
            color = self.returnImage(nearestObject, surfaceHitPoint)
        # use the noise function if we got one
        elif nearestObject.getNoiseFunction() is not None:
            color = nearestObject.getNoiseFunction()(surfaceHitPoint[X],
                                                     surfaceHitPoint[Y],
                                                     surfaceHitPoint[Z])
        else:
            # Start with base color of object + ambient difference
            color = color + nearestObject.getBaseColor() - \
                nearestObject.getAmbient()  # 07 Slides, Slide 16
        for light in self.scene.lights:
            vectorToLight = light.getVectorToLight(surfaceHitPoint)
            # Check if shadowed
            shadowedObject, _ = self.scene.nearestObject(Ray(
                                                             surfaceHitPoint,
                                                             vectorToLight),
                                                         nearestObject)
            if shadowedObject is not None:
                return nearestObject.getAmbient()
            # 07 Slides, Slide 16
            color = color * \
                self.getDiffuse(vectorToLight, normal) + \
                nearestObject.getAmbient() + \
                self.getSpecularColor(self.getSpecularAngle(  # Slide 23
                                                            vectorToLight,
                                                            normal,
                                                            ray,
                                                            nearestObject),
                                      nearestObject.getSpecular())
        return color

    def getColor(self, x, y, samplePerPixel=1):
        totalColor = np.zeros(3)
        for i in range(samplePerPixel ** 2):
            # Hit the center of the pixel
            shift = 1 / ((samplePerPixel + 1) * (i + 1))
            # Get the color based on the ray
            cameraRay = self.scene.camera.getRay(
                                                    (x + shift) / self.width,
                                                    (y + shift) / self.height
                                                )
            # Fixing any NaNs in numpy, clipping to 0, 1.
            totalColor = totalColor + np.nan_to_num(np.clip(
                self.getColorR(cameraRay, 0), 0, 1), 0)
        return totalColor / (samplePerPixel ** 2)


# Calls the 'main' function when this script is executed
if __name__ == '__main__':
    RayTracer.main("Ray Tracer Basics")
    pg.quit()
