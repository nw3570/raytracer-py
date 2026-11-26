from vector import Vector3

def loader(path):
    vertices = []
    normals = []
    vertex_indices = []
    normal_indices = []

    with open(path, 'r') as f:
        for line in f:
            parts = line.split()
            if not parts:
                continue
            tag = parts[0]

            if tag == 'v':
                vertices.append(Vector3(
                    float(parts[1]),
                    float(parts[2]),
                    float(parts[3])
                ))

            elif tag == 'vn':
                normals.append(Vector3(
                    float(parts[1]),
                    float(parts[2]),
                    float(parts[3])
                ))

            elif tag == 'f':
                v_idx = []
                n_idx = []
                for part in parts[1:]:
                    fields = part.split('/')
                    v_idx.append(int(fields[0]) - 1)
                    if len(fields) == 3 and fields[2]:
                        n_idx.append(int(fields[2]) - 1)

                vertex_indices.append(v_idx)
                if n_idx:
                    normal_indices.append(n_idx)

    if not normals:
        for i, face in enumerate(vertex_indices):
            a = vertices[face[0]]
            b = vertices[face[1]]
            c = vertices[face[2]]
            normals.append((b - a).cross(c - a).normalized())
            normal_indices.append([i, i, i])

    return vertices, normals, vertex_indices, normal_indices
