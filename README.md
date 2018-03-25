# pykeman3d
Built-for-fun, incredibly derpy Python 3D game engine (built with deprecated immediate mode OpenGL)

Pykeman3d is my side project/academic exercise to learn and derp around with 3d rendering. I'm using immediate mode because it's easy to iterate over when adding features. I'm using Python for the same reason. Do not use this for anything serious!

## Purpose

I built Pykeman3d for an easy way to render procedurally generated content. 

## Dependencies

Pykeman3d uses [PyOpenGL](http://pyopengl.sourceforge.net/) and [Pygame](https://www.pygame.org/news) for rendering. 

## Architecture

Pykeman3d consists of three primary components:
- Renderer
- Controller
- Shapes

The renderer is used to do the ctual drawing as well as intercepting user input signals. The controller is provided by the program using pykeman3d by subclassing the provided controller class and overriding its functions. The controller is responsible for providing the renderer with data from a game model to render, and act on user signals to mutate the game model over time. Shape objects are the pre-defined low poly models a controller can instuct the renderer to draw.

Pykeman3d assumes the map is a grid, with the renderer calling the controller for each integer, 3d coordinate and collecting lists of Shapes to draw there. The renderer will use the controller's provided limits in each of the three axes to determine how far out to render.

## Rendering 

Pykeman3d uses the quads and triangles from OpenGL for rendering. For now, the only way for the controller to define which of these to draw is to use pre-defined Shapes. Going forward, there will be ways to construct Shapes programatically as well as more easily write Shape definition files. Today, Shapes are defined as a list of 3d points, then a list of tris and quads using those points and a reference to a texture to paint the tri/quad with.

With the camera left at the origin and no translations, scaling, or rotations applied, the view first rendered is down the negative z axis, with the positive y axis as the up direction, and the positive x axis extending to the right.
