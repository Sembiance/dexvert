from __future__ import annotations


class Face:
    """
    Helper structure representing a XFile mesh face
    """
    indices: list[int]

    def __init__(self):
        self.indices = []


class TexEntry:
    """
    Helper structure representing a texture filename inside a material and its potential source
    """
    name: str
    isNormalMap: bool

    def __init__(self, name: str = '', isNormalMap: bool = False):
        self.name = name
        self.isNormalMap = isNormalMap


class Material:
    """
    Helper structure representing a XFile material
    """
    name: str
    isReference: bool
    diffuse: tuple[float, float, float, float]
    specularExponent: float
    specular: tuple[float, float, float]
    emissive: tuple[float, float, float]
    textures: list[TexEntry]
    sceneIndex: int

    def __init__(self):
        self.name = ''
        self.isReference = False
        self.diffuse = (0.0, 0.0, 0.0, 1.0)
        self.specularExponent = 0.0
        self.specular = (0.0, 0.0, 0.0)
        self.emissive = (0.0, 0.0, 0.0)
        self.textures = []
        self.sceneIndex = -1


class BoneWeight:
    """
    Helper structure to represent a bone weight
    """
    vertex: int
    weight: float

    def __init__(self):
        self.vertex = 0
        self.weight = 0.0


class Bone:
    """
    Helper structure to represent a bone in a mesh
    """
    name: str
    weights: list[BoneWeight]
    offsetMatrix: tuple[float]

    def __init__(self):
        self.name = ''
        self.weights = []
        self.offsetMatrix = ()


class Mesh:
    """
    Helper structure to represent an XFile mesh
    """
    positions: list[tuple[float, float, float]]
    posFaces: list[Face]
    normals: list[tuple[float, float, float]]
    normFaces: list[Face]
    numTextures: int
    texCoords: list[list[tuple[float, float]]]
    numColorSets: int
    colors: list[list[tuple[float, float, float, float]]]
    faceMaterials: list[int]
    materials: list[Material]
    bones: list[Bone]

    def __init__(self):
        self.positions = []
        self.posFaces = []
        self.normals = []
        self.normalFaces = []
        self.numTextures = 0
        self.texCoords = [[], []]
        self.numColorSets = 0
        self.colors = [[]]
        self.faceMaterials = []
        self.materials = []
        self.bones = []


class Node:
    """
    Helper structure to represent a XFile frame
    """
    name: str
    trafoMatrix: tuple[float]
    parent: Node | None
    children: list[Node]
    meshes: list[Mesh]

    def __init__(self, parent: Node | None = None):
        self.name = ''
        self.trafoMatrix = ()
        self.parent = parent
        self.children = []
        self.meshes = []


class MatrixKey(object):
    time: float
    matrix: list[float]

    def __init__(self):
        self.time = 0.0
        self.matrix = ()


class AnimBone(object):
    """
    Helper structure representing a single animated bone in a XFile
    """
    boneName: str
    posKeys: list[tuple[float, tuple[float, float, float]]]
    rotKeys: list[tuple[float, tuple[float, float, float, float]]]
    scaleKeys: list[tuple[float, tuple[float, float, float]]]
    trafoKeys: list[tuple[float, tuple[float, ...]]]

    def __init__(self):
        self.boneName = ''
        self.posKeys = []
        self.rotKeys = []
        self.scaleKeys = []
        self.trafoKeys = []


class Animation(object):
    """
    Helper structure to represent an animation set in a XFile
    """
    name: str
    anims: list[AnimBone]

    def __init__(self):
        self.name = ''
        self.anims = []


class Scene(object):
    """
    Helper structure analogue to aiScene
    """
    rootNode: Node | None
    globalMeshes: list[Mesh]
    globalMaterials: list[Material]
    anims: list[Animation]
    animTicksPerSecond: int

    def __init__(self):
        self.rootNode = None
        self.globalMeshes = []
        self.globalMaterials = []
        self.anims = []
        self.animTicksPerSecond = 0


AI_MAX_NUMBER_OF_TEXTURECOORDS = 2
AI_MAX_NUMBER_OF_COLOR_SETS = 1
