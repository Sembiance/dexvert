import logging

import numpy as np

UBYTE_SCALE = 127
UBYTE_MAX = 255
USHORT_SCALE = 2048
USHORT_OFFSET = 32766.5
USHORT_MIN = 0
USHORT_MAX = 65535
PACKEDVEC_MAX = 2 ** 20 - 1
FUR_OVERHEAD = 2
zero_uint64 = np.uint64(0)
# describe the amount of bits taken up by each logical field in the uint64
PACKED_WEIGHT_FIELDS = ((10, 8), (10, 8), (10, 8), (10,))
# the indices into the unpacked weights per field
PACKED_WEIGHT_TITLES = ("bone ids", "bone weights")


def get_bitmask(num_bits):
    """Returns num_bits toggled on"""
    return (1 << num_bits) - 1

# high level access - while more readable, these are noticeably slower for dino meshes than working on the whole array
def decode_oct(decoded, encoded):
    decoded[:, :2] = encoded
    oct_to_vec3(decoded)
    unpack_swizzle_vectorized(decoded)


def encode_oct(decoded, encoded):
    pack_swizzle_vectorized(decoded)
    vec3_to_oct(decoded)
    encoded[:] = decoded[:, :2]


def unpack_ubyte_vector(arr, normalize=True):
    # convert to +-1 range; 255 is unused
    arr[:] = arr / UBYTE_SCALE - 1.0
    # some cases (oct) do not use normalization after unpacking
    if normalize:
        arr /= np.linalg.norm(arr, axis=1, keepdims=True)


def unpack_ubyte_color(arr):
    arr[:] = arr / UBYTE_MAX


def pack_ubyte_color(arr):
    arr[:] = np.round(arr * UBYTE_MAX)


def pack_ubyte_vector(arr):
    arr[:] = np.round(arr * UBYTE_SCALE + UBYTE_SCALE)


def unpack_ushort_vector(arr):
    arr[:] = (arr - USHORT_OFFSET) / USHORT_SCALE


def unpack_ushort_vector_impostor(arr):
    # improved precision in 0, 1 range
    arr[:] = arr / USHORT_MAX


def pack_ushort_vector(arr):
    arr[:] = np.round(arr * USHORT_SCALE + USHORT_OFFSET)


def pack_ushort_vector_impostor(arr):
    arr[:] = np.round(arr * USHORT_MAX)


def unpack_swizzle(vec):
    # swizzle to avoid a matrix multiplication for global axis correction
    return -vec[0], -vec[2], vec[1]


def unpack_swizzle_vectorized(arr):
    arr[:] = arr[:, (0, 2, 1)]
    arr[:, (0, 1)] *= -1.0


def unpack_swizzle_vectorized_b(arr):
    arr[:] = arr[:, (2, 0, 1)]
    arr[:, (0, 1)] *= -1.0


def pack_swizzle(vec):
    # swizzle to avoid a matrix multiplication for global axis correction
    return -vec[0], vec[2], -vec[1]


def pack_swizzle_vectorized(arr):
    arr[:] = arr[:, (0, 2, 1)]
    arr[:, (0, 2)] *= -1.0


def ushort_clamp(coord):
    return max(min(coord, USHORT_MAX), USHORT_MIN)


def scale_unpack_vectorized(f, pack_base):
    """Converts a packed int component into a float in the range specified by pack_base"""
    f[:] = (f + pack_base) * pack_base / PACKEDVEC_MAX - pack_base


def scale_pack_vectorized(f, pack_base):
    """Packs a float into the range specified by pack_base"""
    f[:] = np.round((f + pack_base) / pack_base * PACKEDVEC_MAX - pack_base)


def unpack_int64_vector(packed_vert, vertices, extra):
    for i in range(3):
        # grab the last 21 bits with bitand
        vertices[:, i] = (packed_vert >> (i * 21)) & get_bitmask(21)
    extra[:] = packed_vert >> 63


def unpack_int64_weights(packed_weights, weights):
    offset = 0
    for i, field in enumerate(PACKED_WEIGHT_FIELDS):
        for size, title in zip(field, PACKED_WEIGHT_TITLES):
            weights[title][:, i] = (packed_weights >> offset) & get_bitmask(size)
            offset += size
    # reconstruct the last weight
    weights["bone weights"][:, 3] = 255 - np.sum(weights["bone weights"][:, :3], axis=1)


def pack_int64_vector(packed_vert, vertices, extra):
    packed_vert[:] = 0
    for i in range(3):
        packed_vert |= vertices[:, i] << (21 * i)
    packed_vert |= extra.astype(np.int64) << 63


def pack_int64_weights(packed_weights, weights):
    offset = 0
    # cast the weights to allow for bitshifting far enough
    dt_weights = [
        ("bone ids", np.uint64, (4,)),
        ("bone weights", np.uint64, (4,)),
    ]
    weights = weights.astype(dt_weights)
    packed_weights[:] = 0
    for i, field in enumerate(PACKED_WEIGHT_FIELDS):
        for size, title in zip(field, PACKED_WEIGHT_TITLES):
            packed_weights |= weights[title][:, i] << offset
            offset += size


def remap(v, old_min, old_max, new_min, new_max):
    return ((v - old_min) / (old_max - old_min)) * (new_max - new_min) + new_min


def sign_not_zero(a):
    # 	vec2 signNotZero(vec2 v) {
    # return vec2((v.x >= 0.0) ? +1.0 : -1.0, (v.y >= 0.0) ? +1.0 : -1.0);
    # }
    # np.sign returns -1 if x < 0, 0 if x==0, 1 if x > 0
    c = a.copy()
    c[:] = -1.0
    c[a >= 0.0] = 1.0
    return c


def vec3_to_oct(arr):
    # ported from Cigolle et al. "Survey of Efficient Representations for Independent Unit Vectors" 2014.
    # // Assume normalized input. Output is on [-1, 1] for each component.
    # vec2 float32x3_to_oct(in vec3 v) {
    # // Project the sphere onto the octahedron, and then onto the xy plane
    # vec2 p = v.xy * (1.0 / (abs(v.x) + abs(v.y) + abs(v.z)));
    # // Reflect the folds of the lower hemisphere over the diagonals
    # return (v.z <= 0.0) ? ((1.0 - abs(p.yx)) * signNotZero(p)) : p;
    # }
    # Project the sphere onto the octahedron, and then onto the xy plane
    arr[:, (0, 1)] /= np.sum(np.abs(arr), axis=1, keepdims=True)
    # Reflect the folds of the lower hemisphere over the diagonals
    # update xy when z <= 0
    arr[arr[:, 2] <= 0.0, :2] = ((1.0 - np.abs(arr[:, (1, 0)])) * sign_not_zero(arr[:, (0, 1)]))[arr[:, 2] <= 0.0, :2]
    # could also use np.where
    # arr[:, :2] = np.where(arr[:, 2] <= 0.0, (1.0 - np.abs(arr[:, (1, 0)])) * sign_not_zero(arr[:, (0, 1)]), arr[:, :2])
    pack_ubyte_vector(arr)
    # clear z coord
    arr[:, 2] = 0.0


def oct_to_vec3(arr, unpack=True):
    # ported from Cigolle et al. "Survey of Efficient Representations for Independent Unit Vectors" 2014.
    # vec3 oct_to_float32x3(vec2 e) {
    # vec3 v = vec3(e.xy, 1.0 - abs(e.x) - abs(e.y));
    # if (v.z < 0) v.xy = (1.0 - abs(v.yx)) * signNotZero(v.xy);
    # return normalize(v);
    # }
    if unpack:
        unpack_ubyte_vector(arr, normalize=False)
    arr[:, 2] = 1.0 - np.abs(arr[:, 0]) - np.abs(arr[:, 1])
    # note that advanced indexing like this creates a copy instead of a view, which makes this messy
    arr[arr[:, 2] < 0, 0:2] = ((1.0 - np.abs(arr[:, (1, 0)])) * sign_not_zero(arr[:, :2]))[arr[:, 2] < 0]
    # normalize after conversion
    arr /= np.linalg.norm(arr, axis=1, keepdims=True)
