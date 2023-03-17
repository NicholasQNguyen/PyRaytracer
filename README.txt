To Run:
python3 rayTracer.py -f [FILE_NAME] -sh [ShowType] -s [Sample per Pixel]
or 
make run

Flags:
-f -> File Name: Name of file if you save it.

-sh -> Show Type: Type of show to do (PerColumn, PerPixel, NoShow, etc.)
NOTE: if -sh is set to NoShow, -f must also be set or an exception will raise

-s -> Sample: Sample per pixel for the anti aliasing.

To Adjust the Scene:
Go to modules/raytracing/scene
In there, you can change which shapes appear
