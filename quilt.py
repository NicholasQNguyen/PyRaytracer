import pygame
import os
import time
import platform
import psutil
import argparse

from render import ProgressiveRenderer, ShowTypes

try:
    if platform.system() == "Windows":
        proc = psutil.Process(os.getpid())
        proc.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    else:
        niceness = os.nice(0)
        if niceness < 19:
            os.nice(19)
except Exception as e:
    print("Unable to adjust priority of process.")
    print(e)

QUILT_SUBFOLDER = "quilt"


def stitch(folderName):
    path = os.path.join(QUILT_SUBFOLDER, folderName)
    info = open(os.path.join(path, "info.txt"), "r")
    width, height = [int(x) for x in info.read().split()]
    finalImage = pygame.Surface((width, height))
    images = [x for x in os.listdir(path) if x.endswith(".png")]
    total = len(images)
    percent = 0.1
    printAt = [int(x * percent * total) for x in range(1, int(1/percent))]
    print("Starting...")
    for i in range(total):
        imageName = images[i]
        imageSurface = pygame.image.load(os.path.join(path, imageName))
        trim = imageName.split(".")[0]
        coords = [int(x) for x in trim.split("_")]
        finalImage.blit(imageSurface, coords)
        if i in printAt:
            print(f"{(printAt.index(i)+1)*percent*100:2.0f}% completed!")
    pygame.image.save(finalImage, path + "_FINISHED.png")
    print("All done!")


class QuiltRenderer(ProgressiveRenderer):
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
        filename = args.file if args.file is not None else "quilt"
        if args.show is not None and args.show != "NoShow":
            raise Exception("QuiltRenderer may only take \
                            NoShow as the showType)")
        sample = args.sample if args.sample is not None else 1
        # Set up renderer
        cls.renderer = cls(samplePerPixel=sample,
                           file=filename)
        cls.renderer.startPygame(caption)
        cls.stepper = cls.renderer.render()

    def __init__(self, width=None, height=None,
                 show=None,
                 showTime=True,
                 startPixelSize=1,
                 chunkSize=100,
                 displayUpdates=True,
                 samplePerPixel=1,
                 file=None):
        print("Enter a folder name for the QuiltRenderer")
        super().__init__(width,
                         height,
                         showTime,
                         ShowTypes.NoShow,
                         minimumPixel=startPixelSize // 2,
                         startPixelSize=startPixelSize,
                         samplePerPixel=samplePerPixel,
                         file=None)
        self.displayUpdates = displayUpdates
        self.chunkSize = chunkSize
        self.chunkStartX = 0
        self.chunkStartY = 0
        self.chunkEndX = self.width
        self.chunkEndY = self.height
        if not os.path.exists(QUILT_SUBFOLDER):
            os.mkdir(QUILT_SUBFOLDER)
        self.quiltFolder = os.path.join(QUILT_SUBFOLDER,
                                        file)
        if not os.path.exists(self.quiltFolder):
            os.mkdir(self.quiltFolder)

    def setChunkStart(self, x, y):
        self.chunkStartX = x
        self.chunkStartY = y

    def setChunkEnd(self, x, y):
        self.chunkEndX = x
        self.chunkEndY = y

    def render(self):
        """The main loop of rendering the image.
        Will create pixels of progressively smaller sizes. Stops rendering
        when the pixel size is 0."""
        startTime = time.time()
        # First progress is to fill entire image with one color
        color = self.getColor(0, 0)
        self.image.fill(color, ((0, 0), (self.width, self.height)))
        info = open(os.path.join(self.quiltFolder, "info.txt"), "w")
        info.write(f"{self.width} {self.height}")
        info.close()
        # For each pixel in the image, jumping by pixel size
        for x in range(self.chunkStartX, self.chunkEndX, self.chunkSize):
            for y in range(self.chunkStartY, self.chunkEndY, self.chunkSize):
                chunkWidth = min(self.width - x, self.chunkSize)
                chunkHeight = min(self.height - y, self.chunkSize)
                chunkImage = pygame.Surface((chunkWidth,
                                             chunkHeight))
                chunkFileName = f"{x}_{y}.png"
                if self.displayUpdates:
                    print(f"{chunkFileName} starting.")
                if os.path.isfile(os.path.join(self.quiltFolder,
                                               chunkFileName)):
                    print(f"{chunkFileName} already generated. Skipping.")
                    print("===============================")
                    continue
                for ix in range(x, x+self.chunkSize):
                    for iy in range(y, y+self.chunkSize):
                        # Get color
                        color = self.getColor(ix, iy, self.samplePerPixel) * \
                                255
                        chunkImage.fill(color, ((ix - x, iy - y), (1, 1)))
                pygame.image.save(chunkImage, os.path.join(self.quiltFolder,
                                                           chunkFileName))
                if self.displayUpdates:
                    print(f"{chunkFileName} completed.")
                    print("===============================")
        # Done rendering
        self.done = True
        endTime = time.time()
        if self.displayUpdates:
            print()
            print(f"Completed in {(endTime - startTime):.4f} seconds",
                  flush=True)


if __name__ == '__main__':
    folder = input("Enter folder name to stitch: ")
    stitch(folder)
