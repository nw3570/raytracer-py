MAX_DEPTH = 5
MAX_TRI = 2

class Node:
    def __init__(self, axis=None, cut=None, left=None, right=None, scene=None):
        self.axis = axis    # eixo do corte
        self.cut = cut      # coordenada do corte no eixo
        self.left = left    # filho esquerdo
        self.right = right  # filho direito
        self.scene = scene  # para os nos folha

    def is_leaf(self):
        return not self.left and not self.right

class KDTree:
    def __init__(self, scene):
        self.root = self.build_tree(scene)

    def build_tree(self, scene, axis=0, depth=0, k=3):
        # Caso base 1:
        if len(scene) <= MAX_TRI or depth >= MAX_DEPTH:
            return Node(scene=scene) # cria um no folha

        axis = depth % k # a divisao resulta em 0, 1 ou 2 (x, y, z)
        centroids = []
        for tri in scene:
            centroids.append(tri.centroid())       
        ordered = sorted(centroids, key=lambda c: tuple(c)[axis])
        mid = len(ordered) // 2
        cut = (tuple(ordered[mid - 1])[axis] + tuple(ordered[mid])[axis]) / 2
        
        left = []
        right = []

        for a, b, c in scene:
            coord = [] # guarda as coordenadas dos tres vertices no eixo especifico
            coord.append(tuple(a)[axis])
            coord.append(tuple(b)[axis])
            coord.append(tuple(c)[axis])

            if min(coord) <= cut:
                left.append([a, b, c])
            if max(coord) >= cut:
                right.append([a, b, c])

        # Caso base 2
        if len(left) == len(scene) or len(right) == len(scene):
            return Node(scene=scene)

        return Node(
            axis=axis,
            cut=cut,
            left=self.build_tree(left, depth=depth+1),
            right=self.build_tree(right, depth=depth+1)
        )

    def find_leaf(self, node):
        if node.is_leaf():
            if node.scene is not None:
                return node.scene

    def search_tree(self, node, ray, leafs=[]):
        leafs.append(self.find_leaf(node))
        if ray.direction[node.axis] < node.cut:
            return self.search_tree(node.left, ray)
        else:
            return self.search_tree(node.right, ray)
        return leafs
