import pygame, OpenGL
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import random
import time
import sys

def start(controller, debug=False):
    view = Pykeman3d()
    view.start(controller, debug)

class Pykeman3d:
    
    def __init__(self):
        pygame.init()
        pygame.display.set_mode((600,600), DOUBLEBUF|OPENGL)
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glTexEnvf(GL_TEXTURE_ENV,GL_TEXTURE_ENV_MODE,GL_MODULATE)
        glTexEnvf(GL_TEXTURE_ENV,GL_COMBINE_RGB,GL_MODULATE)
        glTexEnvf(GL_TEXTURE_ENV,GL_COMBINE_ALPHA,GL_MODULATE)
        self.lastspiralcenter = None
        
    def process_input(self, ctrl):
        mousex, mousey = pygame.mouse.get_rel()
        ctrl.input_axis('mouseX', mousex)
        ctrl.input_axis('mouseY', mousey)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                ctrl.input_button('quit', True)
            if event.type == pygame.KEYDOWN and 97<=event.key<=122:
                ctrl.input_button(chr(event.key), True)
            if event.type == pygame.KEYUP and 97<=event.key<=122:
                ctrl.input_button(chr(event.key), False)
    
    def spiral_range(self, dists, center_x, center_y, center_z):
        if self.lastspiralcenter == (center_x, center_y, center_z):
            return self.lastspiral
        coords = []
        ys = [center_y] if dists[1]==0 else [a for b in [[center_y+tmp,center_y-tmp] for tmp in range(dists[1],0,-1)] for a in b]+[center_y]
        radius = max(dists[0], dists[2])
        for y in ys:
            x = center_x+dists[0]
            z = center_z+dists[2]
            f = -1
            for o in range(radius*2,0,-1):
                for _ in range(o):
                    x += f
                    coords.append((x,y,z))
                for _ in range(o):
                    z += f
                    coords.append((x,y,z))
                f *= -1
        self.lastspiralcenter = (center_x, center_y, center_z)
        self.lastspiral = coords
        return coords
        
    def register_shape_list(self, i, shape):
        glNewList(i, GL_COMPILE)
        glBegin(GL_QUADS)
        for quad in shape.quads():
            glTexCoord2f(self.texsize*quad.texture()+0.5,0)
            glVertex3f(*quad.vertices()[0])
            glTexCoord2f(self.texsize*(1+quad.texture())-0.5,0)
            glVertex3f(*quad.vertices()[1])
            glTexCoord2f(self.texsize*(1+quad.texture())-0.5,1)
            glVertex3f(*quad.vertices()[2])
            glTexCoord2f(self.texsize*quad.texture()+0.5,1)
            glVertex3f(*quad.vertices()[3])
        glEnd()
        glBegin(GL_TRIANGLES)
        for tri in shape.tris():
            glTexCoord2f(self.texsize*tri.texture()+0.5,0)
            glVertex3f(*tri.vertices()[0])
            glTexCoord2f(self.texsize*tri.texture()+0.5,1)
            glVertex3f(*tri.vertices()[1])
            glTexCoord2f(self.texsize*(1+tri.texture())-0.5,1)
            glVertex3f(*tri.vertices()[2])
        glEnd()
        glEndList()
    
    def load_texture(self, img):
        textureData = pygame.image.tostring(img, "RGBA", 1)
        width = img.get_width()
        height = img.get_height()
        im = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, im)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, textureData)
        glEnable(GL_TEXTURE_2D)
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT )
        glTexParameteri( GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT ) 
        return im
    
    def compile_textures(self, controller):
        textures, self.texsize, self.texcount = controller.load_textures()
        self.texture = pygame.image.fromstring(bytes([0 for _ in range(self.texcount*4*(self.texsize**2))]), (self.texsize*self.texcount,self.texsize), 'RGBA')
        for t in range(len(textures)):
            self.texture.blit(textures[t], (self.texsize*t, 0), special_flags=0)
        tt = self.load_texture(self.texture)
        glBindTexture(GL_TEXTURE_2D, tt)
    
    def start(self, controller, debug=False):
        self.compile_textures(controller)
        glMatrixMode(GL_TEXTURE)
        glScalef(1.0/(self.texsize*self.texcount), 1.0, 1.0)
        glMatrixMode(GL_MODELVIEW)
        self.shapes = controller.shape_definitions()
        self.shapelists = {}
        self.shapelistoffset = glGenLists(len(self.shapes))
        self.shape_polycounts = {}
        i = 0
        for s in self.shapes:
            self.shapelists[s] = self.shapelistoffset+i
            self.shape_polycounts[s] = self.shapes[s].polygon_count()
            self.register_shape_list(self.shapelistoffset+i, self.shapes[s])
            i += 1
        self.camerainfo = controller.camera_setup()
        self.cache = {}
        lastframe = time.time()
        t = -1
        secstart = time.time()
        frame_count = 0
        while True:
            t += 1
            #
            #  gather input
            #
            self.process_input(controller)
            #
            #  update model
            #
            thisframe = time.time()
            controller.update(thisframe-lastframe)
            lastframe = thisframe
            #
            #  refresh drawing cache
            #
            draw_dist = controller.draw_distances()
            camera_pos = controller.camera_pos()
            thetaH = controller.camera_angle_horizontal()
            thetaV = controller.camera_angle_vertical()
            camera_tile = [math.floor(x) for x in camera_pos]
            coords = self.spiral_range(draw_dist, *camera_tile)
            for c in coords:
                if (c not in self.cache) or (controller.stale_at_coord(*c)):
                    self.cache[c] = controller.shapes_at_coord(*c)
            for c in set(self.cache.keys()).difference(set(coords)):
                self.cache.pop(c)
            #
            #  draw the cache
            #
            
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            gluPerspective(*controller.camera_setup())
            glRotatef(thetaH, 0.0, 1.0, 0.0)
            glRotatef(-thetaV, math.cos(math.radians(thetaH)), 0.0, math.sin(math.radians(thetaH)))
            glTranslatef(-camera_pos[0], -camera_pos[1], -camera_pos[2])
            glClearColor(*controller.bg_color())
            glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
            
            glMatrixMode(GL_MODELVIEW)
            visible_coords = coords
            shape_count = 0
            for coord in visible_coords:
                glPushMatrix()
                glTranslate(coord[0], coord[1], coord[2])
                for shape in self.cache[coord]:
                    glCallList(self.shapelists[shape])
                    shape_count += self.shape_polycounts[shape]
                glPopMatrix()
            
            frame_count += 1
            if debug and time.time() >= secstart+1:
                print('{0}\t{1}\t{2}'.format(frame_count, shape_count, '({0:.2f}, {1:.2f}, {2:.2f})'.format(*camera_pos)))
                secstart = time.time()
                frame_count = 0
            pygame.display.flip()