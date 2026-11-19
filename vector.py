"""Vetor 3D com as operações básicas usadas em raycasting."""

from math import sqrt


class Vector3:
    """Um ponto ou direção no espaço 3D."""

    __slots__ = ("x", "y", "z")

    def __init__(self, x=0.0, y=0.0, z=0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    # ---------- representação ----------

    def __repr__(self):
        return f"Vector3({self.x:g}, {self.y:g}, {self.z:g})"

    def __eq__(self, other):
        if not isinstance(other, Vector3):
            return NotImplemented
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __iter__(self):
        yield self.x
        yield self.y
        yield self.z

    # ---------- soma, subtração e negação ----------

    def __add__(self, other):
        return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __neg__(self):
        return Vector3(-self.x, -self.y, -self.z)

    # ---------- multiplicação e divisão por escalar ----------

    def __mul__(self, escalar):
        return Vector3(self.x * escalar, self.y * escalar, self.z * escalar)

    __rmul__ = __mul__

    def __truediv__(self, escalar):
        return Vector3(self.x / escalar, self.y / escalar, self.z / escalar)

    # ---------- produtos ----------

    def dot(self, other):
        """Produto escalar: mede o quanto dois vetores apontam no mesmo sentido."""
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other):
        """Produto vetorial: devolve um vetor perpendicular aos dois."""
        return Vector3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )

    # ---------- comprimento ----------

    def length_squared(self):
        """Comprimento ao quadrado (evita a raiz quando só se compara distâncias)."""
        return self.dot(self)

    def length(self):
        return sqrt(self.length_squared())

    def normalized(self):
        """Vetor unitário: mesma direção, comprimento 1."""
        comprimento = self.length()
        if comprimento == 0.0:
            return Vector3(0.0, 0.0, 0.0)
        return self / comprimento

    # ---------- utilidades de raycasting ----------

    def reflect(self, normal):
        """Reflete o vetor em torno de uma normal unitária."""
        return self - normal * (2.0 * self.dot(normal))

    def lerp(self, other, t):
        """Interpola linearmente entre dois vetores (t entre 0 e 1)."""
        return self + (other - self) * t

    @staticmethod
    def zero():
        return Vector3(0.0, 0.0, 0.0)