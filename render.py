# -*- coding: utf-8 -*-
"""
Authors: Liz Matthews, Geoff Matthews

Code to progressively render an image with smaller and smaller pixels.
To use for a different project, extend ProgressivePixelRenderer and
override getColor().
"""

import os
import pygame
import time
import numpy as np
import pygame as pg
from enum import Enum
from abc import ABC, abstractmethod
import argparse


SHOW_TYPES_STRINGS = ("PerPixel",
                      "PerColumn",
                      "PerImage",
                      "FinalShow",
                      "NoShow")

FILE_EXTENSIONS = (".png", ".jpg")


class ShowTypes(Enum):
    """Control for how the progressive pixel renderer shows images.
    More showing will be slower, NoShow doesn't show the image until
    done."""
    PerPixel = 0
    PerColumn = 1
    PerImage = 2
    FinalShow = 3
    NoShow = 4


class ProgressiveRenderer(ABC):
    """Abstract base class for renderers."""
    @classmethod
    def main(cls, caption="Renderer"):
        """General main loop for the progressive renderer.
        Sets up pygame and everything necessary."""
        # Initialize Pygame
        pygame.init()
        # Get command line arguments
        parser = argparse.ArgumentParser()
        parser.add_argument("-sh", "--show", help="Show")
        parser.add_argument("-s", "--sample", help="Sample", type=int)
        parser.add_argument("-f", "--file", help="File")
        args = parser.parse_args()
        fileName = args.file
        if fileName is not None:
            if (not (fileName[-4:] in FILE_EXTENSIONS)):
                raise Exception("File name must end in \".jpg\" or \".png\".")
            show = ShowTypes.NoShow
        else:
            if (args.show is not None) and \
              (not (args.show in SHOW_TYPES_STRINGS)):
                raise Exception("-sh flag must be one of the following: \n \
1) PerPixel \n \
2) PerColumn \n \
3) PerImage \n \
4) FinalShow \n \
5) NoShow")
            show = ShowTypes[args.show] if args.show is not None else None
        sample = args.sample if args.sample is not None else 1
        # Set up renderer
        cls.renderer = cls(show=show,
                           samplePerPixel=sample,
                           file=fileName)
        cls.renderer.startPygame(caption)
        cls.stepper = cls.renderer.render()
        # Main loop
        while cls.renderer.isRunning():
            # If the renderer has work to do, let it
            if not cls.renderer.done:
                next(cls.stepper)

    @classmethod
    def restart(cls):
        cls.stepper.close()
        cls.renderer.restartRender()
        cls.stepper = cls.renderer.render()

    def __init__(self, width=640, height=480,
                 showTime=True,
                 show=ShowTypes.PerColumn,
                 minimumPixel=0,
                 startPixelSize=256,
                 samplePerPixel=1,
                 file=None):
        self.width = width
        self.height = height
        self.showTime = showTime
        self.minimumPixel = minimumPixel
        self.screen = None
        self.fillColor = (64, 128, 255)
        if show is not None:
            self.show = show
        else:
            self.show = ShowTypes.PerColumn
        self.samplePerPixel = samplePerPixel

        if self.show in [ShowTypes.NoShow, ShowTypes.FinalShow]:
            self.startPixelSize = max(1, minimumPixel * 2)
        else:
            self.startPixelSize = startPixelSize
        if self.show == ShowTypes.NoShow:
            self.fileName = file
        else:
            self.fileName = None

    @abstractmethod
    def getColor(self, x, y):
        """Must return a color in a np.array()"""
        return np.array((0, 0, 255))

    def handleExitInput(self, event):
        """For exiting the program."""
        if event.type == pg.QUIT:
            return True
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                return True
        return False

    def handleSaveInput(self, event):
        """The key s will save the file."""
        if event.type == pg.KEYDOWN and event.key == pg.K_s:
            self.save()

    def handleOtherInput(self, event):
        """For handling other inputs, override for new behaviors"""
        pass

    def handleInput(self):
        """Checks the event queue."""
        for event in pygame.event.get():
            exitRender = self.handleExitInput(event)
            if exitRender:
                return True
            self.handleSaveInput(event)
            self.handleOtherInput(event)

    def save(self):
        pygame.event.set_blocked(pg.KEYDOWN | pg.KEYUP)
        fname = input("File name?:  ")
        pygame.event.set_blocked(0)
        pygame.image.save(self.image, os.path.join("images", fname))

    def startPygame(self, caption):
        if self.show != ShowTypes.NoShow:
            self.screen = pygame.display.set_mode((self.width, self.height))
            pygame.display.set_caption(caption)

        else:
            self.screen = None
        # Create the image
        self.image = pygame.Surface((self.width,
                                     self.height))
        self.image.fill(self.fillColor)
        # Prepare Game Objects
        self.clock = pygame.time.Clock()
        # Start rendering
        self.restartRender()

    def isRunning(self):
        return not self.handleInput() and \
               not (self.done and self.show == ShowTypes.NoShow)

    def restartRender(self):
        self.pixelSize = self.startPixelSize
        self.done = False

    def showProgress(self, fps=60):
        """Method to draw the background to the screen and flip."""
        # Let the clock tick
        self.clock.tick(fps)
        if self.show != ShowTypes.NoShow:
            # Draw background into screen and show
            self.screen.blit(self.image, (0, 0))
            pygame.display.flip()

    def render(self):
        """The main loop of rendering the image.
        Will create pixels of progressively smaller sizes. Stops rendering
        when the pixel size is 0."""
        startTime = time.time()
        # First progress is to fill entire image with one color
        color = self.getColor(0, 0)
        self.image.fill(color, ((0, 0), (self.width, self.height)))
        # Show the progress
        self.showProgress()
        yield
        # Until the pixel size gets too small
        while self.pixelSize > self.minimumPixel:
            print(f"Pixel Size: {self.pixelSize:3}")
            # For each pixel in the image, jumping by pixel size
            for x in range(0, self.width, self.pixelSize):
                for y in range(0, self.height, self.pixelSize):
                    # Get color
                    # Only anti-alias if down to 1 pixel
                    color = self.getColor(x, y, 1) * 255 if \
                        self.pixelSize > 1 else \
                        self.getColor(x, y, self.samplePerPixel) * 255
                    self.image.fill(color, ((x, y), (self.pixelSize,
                                                     self.pixelSize)))
                    if self.show == ShowTypes.PerPixel:
                        self.showProgress(256 * 60 // self.pixelSize)
                    yield
                if self.show == ShowTypes.PerColumn:
                    self.showProgress(60)
            # Reduce pixel size
            self.pixelSize //= 2
            if self.show == ShowTypes.PerImage:
                self.showProgress(30)
        # Done rendering
        self.done = True
        endTime = time.time()
        print()
        print(f"Completed in {(endTime - startTime):.4f} seconds", flush=True)
        if self.show == ShowTypes.FinalShow:
            self.showProgress(30)
        elif self.show == ShowTypes.NoShow:
            pygame.image.save(self.image,
                              os.path.join("images", self.fileName))
        yield
