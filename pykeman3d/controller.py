
# inherit from this to build a custom controller which is passed into pyke3d start() for callbacks
#  it can reference the model directly to 
class Pykeman3dController:
    def __init__(self):
        pass
    def tint_color(self):
        return (1.0, 1.0, 1.0, 1.0)
    def bg_color(self):
        return (0.0, 0.0, 0.0, 1.0)
    def update(self, dt):
        pass   #  intended to use as a model updater based on elapsed time since last call (once per frame)
    def load_textures(self):
        #  return list of list of textures, the size of the textures, and their count
        import pygame
        return [pygame.image.fromstring(bytes([255,0,255,255]*4), (2,2), 'RGBA')], 2, 1
    def input_button(self, button_name, button_value):
        pass
    def input_axis(self, axis_name, axis_value):
        pass
    def camera_pos(self):
        return (0,0,0)
    def draw_distances(self):
        return (5,5,5)
    def stale_at_coord(self, x, y, z):
        return False
    def shapes_at_coord(self, x, y, z):
        return []
    def camera_angle_horizontal(self):
        return 0.0
    def camera_angle_vertical(self):
        return 0.0
    def camera_setup(self):
        return (90, 1.0, 0.01, 1000)
    def shape_definitions(self):
        return {}
