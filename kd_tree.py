MAX_DEPTH = 5
MAX_OBJECTS = 2

class Node:
    def __init__(self, axis=None, cut=None, left=None, right=None, scene=None):
        self.axis = axis
        self.cut = cut
        self.left = left
        self.right = right
        self.scene = scene

    def is_leaf(self):
        return self.scene is not None

class KDTree:
    def __init__(self, scene, axis, depth):
        self.root = self.build_tree(self, scene, axis, depth)

    def build_tree(self, scene, axis=0, depth=0):
        '''
        Se o numeros maximo de objetos for atingido
        ou a profundidade maxima alcancada
        cria um no folha com os objetos contidos no espaco
        '''
        if len(scene) <= MAX_OBJECTS or depth >= MAX_DEPTH:
            return Node(scene=scene)

        axis = depth % 3
        ordered = sorted(scene, key=lambda obj: tuple(obj.pos())[axis])
        median = len(ordered) // 2
        cut = (
            (tuple(ordered[median - 1].pos())[axis] +
             tuple(ordered[median].pos())[axis]) / 2
        )
