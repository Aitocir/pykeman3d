import struct
import math
import random
import time
import sys
import opensimplex

import pygame
from pygame.locals import *
import moderngl

import tilemaker

class Pykeman3d:
    
    def __init__(self):
        #  pygame init
        pygame.init()
        pygame.display.set_mode((600,600), DOUBLEBUF|OPENGL)
        pygame.mouse.set_visible(False)
        pygame.event.set_grab(True)
        #  ModernGL init
        self.ctx = moderngl.create_context()
        self.ctx.enable(moderngl.DEPTH_TEST)
        self.prog = self.ctx.program(vertex_shader='''
            #version 330
            
            in vec3 in_vert;
            in vec3 in_norm;
            in vec2 in_text;
            out vec3 v_vert;
            out vec3 v_norm;
            out vec2 v_text;

            uniform float znear;
            uniform float zfar;
            uniform float fovy;
            uniform float ratio;

            uniform vec3 center;
            uniform vec3 eye;
            uniform vec3 up;
            

            mat4 perspective() {
                float zmul = (-2.0 * znear * zfar) / (zfar - znear);
                float ymul = 1.0 / tan(fovy * 3.14159265 / 360);
                float xmul = ymul / ratio;

                return mat4(
                    xmul, 0.0, 0.0, 0.0,
                    0.0, ymul, 0.0, 0.0,
                    0.0, 0.0, -1.0, -1.0,
                    0.0, 0.0, zmul, 0.0
                );
            }

            mat4 lookat() {
                vec3 forward = normalize(center - eye);
                vec3 side = normalize(cross(forward, up));
                vec3 upward = cross(side, forward);
                return mat4(
                    side.x, upward.x, -forward.x, 0,
                    side.y, upward.y, -forward.y, 0,
                    side.z, upward.z, -forward.z, 0,
                    -dot(eye, side), -dot(eye, upward), dot(eye, forward), 1
                );
            }

            void main() {
                v_text = in_text;
                v_norm = in_norm;
                gl_Position = perspective() * lookat() * vec4(in_vert, 1.0);
                v_vert = in_vert;
            }
        ''', fragment_shader='''
            #version 330

            uniform vec3 Color;
            uniform vec3 Light;
            uniform sampler2D img;
            
            in vec3 v_vert;
            in vec3 v_norm;
            in vec2 v_text;
            
            out vec4 o_color;

            void main() {
                float lum = clamp(dot(normalize(Light - v_vert), normalize(v_norm)), 0.0, 1.0) * 0.5 + 0.5;
                //o_color = vec4(texture(img, vec2(overt[0]*0.2, overt[2]*0.2)).rgb, 1.0);
                o_color = vec4(texture(img, v_text).rgb*lum, 1.0);
            }
        ''')
           
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
    def norm(self, a, b, c):
        # https://math.stackexchange.com/questions/305642/how-to-find-surface-normal-of-a-triangle
        vx = b[0]-a[0]
        vy = b[1]-a[1]
        vz = b[2]-a[2]
        wx = c[0]-a[0]
        wy = c[1]-a[1]
        wz = c[2]-a[2]
        nx = (vy*wz) - (vz*wy)
        ny = (vz*wx) - (vx*wz)
        nz = (vx*wy) - (vy*wx)
        return (nx, ny, nz)
    
    def start(self, controller, debug=False):
        cam_info = controller.camera_setup()
        self.prog['znear'].value = cam_info[2]
        self.prog['zfar'].value = cam_info[3]
        self.prog['ratio'].value = cam_info[1]
        self.prog['fovy'].value = cam_info[0]
        
        pos = tuple(controller.camera_pos())
        self.prog['center'].value = (pos[0]+2, pos[1], pos[2])
        self.prog['eye'].value = pos
        self.prog['up'].value = (0, 1, 0)
        
        grids = {}
        gsize = 20
        gs = gsize//2
        grounds = {}
        for i in range(-gs, gs):
            for j in range(-gs, gs):
                grounds[(i,j)] = tuple(controller.ground_at_coord(i, j))
        for i in range(-gs, gs-1):
            for j in range(-gs, gs-1):
                
                ca = grounds[(i,j)][1]
                cb = grounds[(i+1,j)][1]
                cc = grounds[(i,j+1)][1]
                cd = grounds[(i+1,j+1)][1]
                
                if len(set([ca,cb,cc,cd])) in [1,4]:
                    caa = ca
                    cbb = cb
                    ccc = cc
                    cdd = cd
                else:
                    caa = cb if cb==cc else ca
                    cbb = ca if ca==cd else cb
                    ccc = cd if ca==cd else cc
                    cdd = cc if cb==cc else cd
                
                H = []
                H.append( (i,grounds[(i,j)][0],j) )
                H.append( (i+0.5,(grounds[(i,j)][0]+grounds[(i+1,j)][0])/2,j) )
                H.append( (i+1,grounds[(i+1,j)][0],j) )
                H.append( (i,(grounds[(i,j)][0]+grounds[(i,j+1)][0])/2,j+0.5) )
                H.append( (i+0.5,(grounds[(i,j)][0]+grounds[(i+1,j)][0]+grounds[(i,j+1)][0]+grounds[(i+1,j+1)][0])/4,j+0.5) )
                H.append( (i+1,(grounds[(i+1,j)][0]+grounds[(i+1,j+1)][0])/2,j+0.5) )
                H.append( (i,grounds[(i,j+1)][0],j+1) )
                H.append( (i+0.5,(grounds[(i,j+1)][0]+grounds[(i+1,j+1)][0])/2,j+1) )
                H.append( (i+1,grounds[(i+1,j+1)][0],j+1) )
                
                N = []
                N.append([*self.norm(H[0],H[3],H[1])])
                N.append([*self.norm(H[1],H[5],H[2])])
                N.append([*self.norm(H[3],H[6],H[7])])
                N.append([*self.norm(H[5],H[7],H[8])])
                N.append([*self.norm(H[4],H[1],H[3])])
                N.append([*self.norm(H[4],H[5],H[1])])
                N.append([*self.norm(H[4],H[3],H[7])])
                N.append([*self.norm(H[4],H[7],H[5])])
                
                T = []
                T.append([0,0])
                T.append([0.5,0])
                T.append([1,0])       
                T.append([0,0.5])
                T.append([0.5,0.5])
                T.append([1,0.5])
                T.append([0,1])
                T.append([0.5,1])
                T.append([1,1])
                for c in set([ca,cb,cc,cd,caa,cbb,ccc,cdd]):
                    if c not in grids:
                        grids[c] = bytes()
                grids[ca] += struct.pack('24f', *H[0],*N[0],*T[0],  *H[1],*N[0],*T[1],  *H[3],*N[0],*T[3])
                grids[cb] += struct.pack('24f', *H[1],*N[1],*T[1],  *H[2],*N[1],*T[2],  *H[5],*N[1],*T[5])
                grids[cc] += struct.pack('24f', *H[3],*N[2],*T[3],  *H[7],*N[2],*T[7],  *H[6],*N[2],*T[6])
                grids[cd] += struct.pack('24f', *H[5],*N[3],*T[5],  *H[7],*N[3],*T[7],  *H[8],*N[3],*T[8])
                grids[caa] += struct.pack('24f', *H[4],*N[4],*T[4],  *H[1],*N[4],*T[1],  *H[3],*N[4],*T[3])
                grids[cbb] += struct.pack('24f', *H[4],*N[5],*T[4],  *H[1],*N[5],*T[1],  *H[5],*N[5],*T[5])
                grids[ccc] += struct.pack('24f', *H[4],*N[6],*T[4],  *H[7],*N[6],*T[7],  *H[3],*N[6],*T[3])
                grids[cdd] += struct.pack('24f', *H[4],*N[7],*T[4],  *H[7],*N[7],*T[7],  *H[5],*N[7],*T[5])
        
        imgs = controller.load_textures()
        textures = []
        for i in imgs:
            textures.append(self.ctx.texture(i.get_size(), 3, pygame.image.tostring(i, 'RGB')))
            textures[-1].build_mipmaps()
            textures[-1].use(len(textures)-1)
        
        vaos = {}
        for g in grids:
            vbo = self.ctx.buffer(grids[g])
            vaos[g] = self.ctx.simple_vertex_array(self.prog, vbo, 'in_vert', 'in_norm', 'in_text')
            #vaos[g] = self.ctx.simple_vertex_array(self.prog, vbo, 'vert')

        lastframe = time.time()
        self.prog['Light'].value = (0,25,0)
        while True:
            #
            #  Update
            #
            self.process_input(controller)
            thisframe = time.time()
            controller.update(thisframe-lastframe)
            lastframe = thisframe
            pos = tuple(controller.camera_pos())
            self.prog['Light'].value = (pos[0], pos[1]+2, pos[2])
            roth = controller.camera_angle_horizontal()
            rotv = controller.camera_angle_vertical()
            self.prog['center'].value = (pos[0]+math.cos(math.radians(roth)), pos[1]+math.sin(math.radians(rotv)), pos[2]+math.sin(math.radians(roth)))
            self.prog['eye'].value = pos
            #
            #  Draw
            #
            self.ctx.clear(0.1, 0.2, 1.0)
            for g in grids:
                #self.prog['Color'].value = g
                self.prog['img'].value = g  #0 if g==(0.1,1.0,0.1) else 1
                vaos[g].render(moderngl.TRIANGLES)
            pygame.display.flip()



def start(controller, debug=False):
    view = Pykeman3d()
    view.start(controller, debug)
