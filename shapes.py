import os

class Shape:
    class Polygon:
        def __init__(self, texture, vertices):
            self._t = texture
            self._v = vertices
        def texture(self):
            return self._t
        def vertices(self):
            return self._v
    def __init__(self, shape_name, texture_idxs):
        p = []
        self._t = []
        self._q = []
        fpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'shapes', shape_name)+'.txt'
        if os.path.exists(fpath):
            with open(fpath) as f:
                lines = [x.strip() for x in f.readlines()]
            for line in lines:
                if line[0] == '(':
                    v = tuple([float(x) for x in line[1:-1].split()])
                    p.append(v)
                else:
                    e = [int(x) for x in line.split()]
                    t = texture_idxs[e[1]%len(texture_idxs)]
                    v = [p[x] for x in e[2:]]
                    poly = Shape.Polygon(t, v)
                    self._t.append(poly) if e[0]==3 else self._q.append(poly)
    def tris(self):
        return self._t
    def quads(self):
        return self._q
    def polygon_count(self):
        return len(self._t)+len(self._q)
