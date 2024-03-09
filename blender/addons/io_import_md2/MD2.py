from dataclasses import dataclass
import struct
from typing import List
"""
This part is used to load an md2 file into a MD2 dataclass object
"""
""" 
Dataclasses resembling structs in C. Used for storing MD2 information, being nested and forming one big dataclass
"""

@dataclass
class vec3_t:
    x: float
    y: float
    z: float


@dataclass
class vertex_t:  # 4 bytes in total
    v: list  # unsigned char (in python 1 byte int), list of len 3, compressed vertex
    lightnormalindex: int  # unsigned char, index to a normal vector for the lighting


@dataclass
class frame_t:  # 40 + num_xyz*4 bytes
    scale: vec3_t  # scale values, 3 elements
    translate: vec3_t  # translation vector, 3 elements
    name: str  # frame name, 16 characters aka bytes at most
    verts: List[vertex_t]  # list of num_xyz vertex_t's


@dataclass
class md2_t:
    ident: int              # magic number. must be equal to "IDP2" or 844121161 as int
    version: int            # md2 version. must be equal to 8

    skinwidth: int          # width of the texture
    skinheight: int         # height of the texture
    framesize: int          # size of one frame in bytes

    num_skins: int          # number of textures
    num_xyz: int            # number of vertices
    num_st: int             # number of texture coordinates
    num_tris: int           # number of triangles
    num_glcmds: int         # number of opengl commands
    num_frames: int         # total number of frames

    ofs_skins: int          # offset to skin names (64 bytes each)
    ofs_st: int             # offset to s-t texture coordinates
    ofs_tris: int           # offset to triangles
    ofs_frames: int         # offset to frame data
    ofs_glcmds: int         # offset to opengl commands
    ofs_end: int            # offset to end of file


@dataclass
class triangle_t:  # 12 bytes each
    vertexIndices: List[int]  # short, 3 values
    textureIndices: List[int]  # short, 3 values


@dataclass
class textureCoordinate_t: # 4 bytes each
    s: int  # short
    t: int  # short


@dataclass
class glCommandVertex_t:
    s: float
    t: float
    vertexIndex: int


@dataclass
class glCommand_t:
    mode: str  # string saying GL_TRIANGLE_STRIP or GL_TRIANGLE_FAN
    vertices: List[glCommandVertex_t]  # all vertices rendered with said mode


@dataclass
class md2_object:
    header: md2_t
    skin_names: List[str]
    triangles: List[triangle_t]
    frames: List[frame_t]
    texture_coordinates: List[textureCoordinate_t]
    gl_commands: List[glCommand_t]

"""
Functions used to create an MD2 Object
"""
def load_gl_commands(gl_command_bytes):
    """
    Loads gl_commands which are a list of GL_TRIANGLE_STRIP and GL_TRIANGLE_FAN calls that reduce fps
    Code differs much from original loading code in C
    :param gl_command_bytes: bytes belonging to gl_commands lump from md2 file
    :return: list of dataclasses storing gl commands
    """
    offset = 0
    gl_commands = list()
    while True:  # ends when mode is 0
        (mode,) = struct.unpack("<i", gl_command_bytes[offset:offset+4])
        num_verts = abs(mode)
        if mode > 0:
            mode = "GL_TRIANGLE_STRIP"
        elif mode == 0:
            offset += 4
            break
        else:
            mode = "GL_TRIANGLE_FAN"
        offset += 4
        gl_vertices = list()
        for i in range(num_verts):
            s_and_t = struct.unpack("<ff", gl_command_bytes[offset+12*i:offset+12*i+8])
            vertex_index = struct.unpack("<i", gl_command_bytes[offset+12*i+8:offset+12*i+12])
            gl_vertices.append(glCommandVertex_t(*s_and_t, *vertex_index))
        # print(gl_vertices)
        offset += 12*num_verts
        gl_commands.append(glCommand_t(mode, gl_vertices))
    return gl_commands


def load_triangles(triangle_bytes, header):
    """
    Creates basic list of triangle dataclasses which contain indices to vertices
    :param triangle_bytes: bytes from md2 file belonging to triangles lump
    :param header: dataclass containing header information
    :return: list of triangles
    """
    triangles = list()
    for i in range(header.num_tris):
        triangle = triangle_t(list(struct.unpack("<hhh", triangle_bytes[12*i:12*i+6])), list(struct.unpack("<hhh", triangle_bytes[12*i+6:12*i+12])))
        # print(triangle)
        triangles.append(triangle)
    return triangles


def load_frames(frames_bytes, header):
    """
    Loads frames
    :param frames_bytes: bytes from md2 file belonging to frames lump
    :param header: header dataclass
    :return: list of frame dataclass objects
    """
    # # check if header.ofs_glcmds - header.ofs_frames == header.num_frames*(40+4*header.num_xyz) # #
    # print("len", len(frames_bytes))
    # print("frames", header.num_frames)
    # print("check", header.num_frames*(40+4*header.num_xyz))

    frames = list()
    for current_frame in range(header.num_frames):
        scale = vec3_t(*struct.unpack("<fff", frames_bytes[(40+4*header.num_xyz)*current_frame:(40+4*header.num_xyz)*current_frame+12]))
        translate = vec3_t(*struct.unpack("<fff", frames_bytes[(40+4*header.num_xyz)*current_frame+12:(40+4*header.num_xyz)*current_frame+24]))
        name = frames_bytes[(40+4*header.num_xyz)*current_frame+24:(40+4*header.num_xyz)*current_frame+40].decode("ascii", "ignore")
        verts = list()
        for v in range(header.num_xyz):
            # print(v)
            verts.append(vertex_t(list(struct.unpack("<BBB", frames_bytes[(40+4*header.num_xyz)*current_frame+40+v*4:(40+4*header.num_xyz)*current_frame+40+v*4+3])), *struct.unpack("<B", frames_bytes[(40+4*header.num_xyz)*current_frame+43+v*4:(40+4*header.num_xyz)*current_frame+44+v*4])))  # list() only for matching expected type
        # print(scale, translate, name, verts)
        frame = frame_t(scale, translate, name, verts)
        # print(frame)
        frames.append(frame)
    return frames


def load_header(file_bytes):
    """
    Creates header dataclass object
    :param file_bytes: bytes from md2 file belonging to header
    :return: header dataclass object
    """
    # print(file_bytes[:4].decode("ascii", "ignore"))
    arguments = struct.unpack("<iiiiiiiiiiiiiiiii", file_bytes[:68])
    header = md2_t(*arguments)
    # Verify MD2
    if not header.ident == 844121161 or not header.version == 8:
        raise ValueError(
            f"Error: File type is not MD2. Ident or version not matching. "
            f'Ident: {file_bytes[:4].decode("ascii", "ignore")} should be "IDP2". '
            f"Version: {header.version} should be 8"
        )
    return header


def load_texture_coordinates(texture_coordinate_bytes, header):
    """
    Loads UV (in Q2 term ST) coordinates
    :param texture_coordinate_bytes:
    :param header:
    :return: list of texture coordinate dataclass objects
    """
    texture_coordinates = list()
    for i in range(header.num_st):
        texture_coordinates.append(textureCoordinate_t(*struct.unpack("<hh", texture_coordinate_bytes[4*i:4*i+4])))
    return texture_coordinates


def load_file(path):
    """
    Master function returning one dataclass object containing all the MD2 information
    :param path:
    :return:
    """
    with open(path, "rb") as f:  # bsps are binary files
        byte_list = f.read()  # stores all bytes in bytes1 variable (named like that to not interfere with builtin names
    header = load_header(byte_list)
    skin_names = [byte_list[header.ofs_skins + 64 * x:header.ofs_skins + 64 * x + 64].decode("ascii", "ignore") for x in range(header.num_skins)]
    triangles = load_triangles(byte_list[header.ofs_tris:header.ofs_frames], header)
    frames = load_frames(byte_list[header.ofs_frames:header.ofs_glcmds], header)
    texture_coordinates = load_texture_coordinates(byte_list[header.ofs_st:header.ofs_tris], header)
    gl_commands = load_gl_commands(byte_list[header.ofs_glcmds:header.ofs_end])
    # print(header)
    # print(skin_names)
    # print(triangles)
    # print(frames)
    # print(texture_coordinates)
    for i in range(len(texture_coordinates)):
        texture_coordinates[i].s = texture_coordinates[i].s/header.skinwidth
        texture_coordinates[i].t = texture_coordinates[i].t / header.skinheight
    # print(texture_coordinates)
    # print(header.num_xyz)
    for i_frame in range(len(frames)):
        for i_vert in range((header.num_xyz)):
            frames[i_frame].verts[i_vert].v[0] = frames[i_frame].verts[i_vert].v[0]*frames[i_frame].scale.x+frames[i_frame].translate.x
            frames[i_frame].verts[i_vert].v[1] = frames[i_frame].verts[i_vert].v[1] * frames[i_frame].scale.y + frames[i_frame].translate.y
            frames[i_frame].verts[i_vert].v[2] = frames[i_frame].verts[i_vert].v[2] * frames[i_frame].scale.z + frames[i_frame].translate.z
    model = md2_object(header, skin_names, triangles, frames, texture_coordinates, gl_commands)
    return model
