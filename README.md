# pykeman3d
Built-for-fun, incredibly derpy Python 3D game engine (built with deprecated immediate mode OpenGL)

Pykeman3d is my side project/academic exercise to learn and derp around with 3d rendering. I'm forcing myself to move beyond imemdiate mode from deprecated OpenGL APIs, made mcuh easier by the [ModernGL](https://github.com/cprogrammer1994/ModernGL) repo.

## Purpose

I built Pykeman3d for an easy way to render my procedurally generated content, as well as just have fun. It assumes terrain as a first-class concept, so it's ideal for RPGs and the like, but poorly suited for true 3D environments such as space.

## Dependencies

Pykeman3d uses [ModernGL](https://github.com/cprogrammer1994/ModernGL) and [Pygame](https://www.pygame.org/news) for rendering. 

## Architecture

Pykeman3d consists of three primary components:
- Renderer
- Controller
- Shapes

The renderer is used to do the actual drawing as well as intercepting user input signals. The controller is provided by the program using pykeman3d by subclassing the provided controller class and overriding its functions. The controller is responsible for providing the renderer with data from a game model to render, and act on user signals to mutate the game model over time. Shape objects are the pre-defined low poly models a controller can instuct the renderer to draw.

Pykeman3d assumes the map is a grid, with the renderer calling the controller for each integer, 2d coordinate and collecting lists of Shapes to draw there as well as terrain height and type. The renderer will use the controller's provided limits to determine how far out to render.

## Rendering 

Pykeman3d uses the quads and triangles from OpenGL for rendering. For now, the only way for the controller to define which of these to draw is to use pre-defined Shapes (or the terrain, which generated triangles as needed to match the provided height points). Going forward, there will be ways to construct Shapes programatically as well as more easily write Shape definition files. Today, Shapes are defined as a list of 3d points, then a list of tris and quads using those points and a reference to a texture to paint the tri/quad with.

With the camera left at the origin and no translations, scaling, or rotations applied, the view first rendered is down the negative z axis, with the positive y axis as the up direction, and the positive x axis extending to the right.
