from nifgen.formats.manis.imports import name_type_map
import contextlib
import logging
import math
import struct
import os
import numpy as np

import root_path
from nifgen.formats.manis.bitfields.ManisDtype import ManisDtype
from ovl_util.logs import logging_setup
from nifgen.formats.manis.bitfields.StoreKeys import StoreKeys
from nifgen.formats.manis.compounds.InfoHeader import InfoHeader
from nifgen.io import IoFile

try:
    import bitarray
    import bitarray.util
except:
    logging.warning(f"bitarray module is not installed")

np.set_printoptions(suppress=True, precision=4)


def swap16(i):
    return struct.unpack("<h", struct.pack(">h", i))[0]


def hex_test():
    for i in range(20):
        x = 2 ** i
        print(i, bin(i), x, bin(x))


class BinStream:
    def __init__(self, val):
        self.data = bitarray.bitarray(endian='little')
        self.data.frombytes(val)
        self.pos = 0

    def seek(self, pos):
        self.pos = pos

    def read(self, size):
        d = self.data[self.pos: self.pos + size]
        assert len(d) == size, f"Reached end of chunk reading {size} bits at {self.pos}"
        self.pos += size
        return d

    def read_int(self, size):
        bits = self.read(size)
        return bitarray.util.ba2int(bits, signed=True)

    def read_uint(self, size):
        bits = self.read(size)
        return bitarray.util.ba2int(bits, signed=False)

    # return bitarray.util.int2ba(0x99c51a50c66, length=45, endian="little", signed=False)

    def read_int_reversed(self, size):
        out = 0
        for _ in range(size):
            new_bit = self.read_uint(1)
            out = new_bit | (out * 2)
        return out

    def interpret_as_shift(self, size, flag):
        out = 0
        for _ in range(size):
            out += flag
            flag *= 2
        return out

    def read_bit_size_flag(self, max_size):
        for rel_key_size in range(max_size):
            new_bit = self.read_uint(1)
            if not new_bit:
                return rel_key_size
        return -1

    def find_all(self, bits):
        for match_offset in self.data.itersearch(bits):
            # logging.info(match)
            yield match_offset


class KeysContext:
    def __init__(self, f2, wavelet_byte_offset):
        # logging.info(f"wavelet_byte_offset {wavelet_byte_offset}")
        f2.seek(wavelet_byte_offset * 8)
        self.do_increment = f2.read_uint(1)
        self.runs_remaining = f2.read_uint(16)
        # size = k_channel_bitsize + 1
        # verified
        size = 4
        self.init_k_a = f2.read_int_reversed(size)
        self.init_k_b = f2.read_int_reversed(size)
        if not self.do_increment:
            self.init_k_a, self.init_k_b = self.init_k_b, self.init_k_a
        logging.info(self)
        self.do_increment = not self.do_increment
        self.begun = True
        self.i_in_run = 0

    def __repr__(self):
        return f"do_increment {self.do_increment}, runs_remaining {self.runs_remaining}, init_k_a {self.init_k_a}, init_k_b {self.init_k_b}"


def f_as_i(f):
    return np.int32(struct.unpack('<i', struct.pack('<f', f))[0])


def i_as_f(f):
    return np.float32(struct.unpack('<f', struct.pack('<i', f))[0])


@contextlib.contextmanager
def as_int(f):
    i = f_as_i(f)
    yield i
    return i_as_f(i)


def get_quat_scale_fac(norm_half_abs):
    # pointless, as norm is already squared
    # norm_half_abs = abs(norm_half_abs)
    # logging.info(f"half_norm {norm_half_abs}")
    # fVar3 = norm_half_abs * 0.6366197 + 8388608.0
    # masked_8388609 = f_as_i(8388609.0) & f_as_i(fVar3)
    # matches_8388609 = -int(i_as_f(masked_8388609) == 8388609.0)
    # logging.info(f"matches_8388609 {matches_8388609}")
    # fVar4 = fVar3 - 8388608.0
    # logging.info(f"fVar4 {fVar4}")
    # uVar7 = 0 & -(i_as_f(f_as_i(fVar3) & f_as_i(8388610.0)) == 8388610.0)
    # fVar4 = ((norm_half_abs - fVar4 * 1.570313) - fVar4 * 0.0004837513 - fVar4 * 7.54979e-08)# ^ (0 & uVar8)
    # fVar4_squared = fVar4 * fVar4
    # fVar5 = (((0.000024433157 * fVar4_squared + -0.001388732) * fVar4_squared + 0.04166665) * fVar4_squared - 0.5) * fVar4_squared + 1.0
    # fVar4 = ((fVar4_squared * -0.000195153 + 0.008332161) * fVar4_squared + -0.1666666) * fVar4_squared * fVar4 + fVar4
    # scale = (f_as_i(fVar5) & matches_8388609 | f_as_i(fVar4) & ~matches_8388609) ^ uVar7
    # res = np.array(1.0, dtype=np.float32) & np.array(-1, dtype=np.int32)
    # print(res)
    # fVar6 = abs(norm_half_abs)
    # fVar3 = fVar6 * 0.6366197 + 8388608.0
    # uVar4 = f_as_i(8388609.0) & f_as_i(fVar3)
    # uVar8 = -int(i_as_f(uVar4) == 8388609.0)
    # fVar4 = fVar3 - 8388608.0
    # uVar6 = 0.0
    # uVar7 = (uint)uVar6 & -(uint)((float)((uint)fVar3 & f_as_i(8388610.0)) == 8388610.0)
    # uVar9 = 0.000024433157
    # xmm0 = np.float32(1.0)
    # # xmm0 = 2.0
    # print(xmm0, type(xmm0))
    # raise AttributeError

    xmm2 = np.float32(8388608.0)  # 00 00 00 4B
    xmm0 = np.float32(8388609.0)  # 01 00 00 4B
    xmm1 = np.float32(8388610.0)  # 02 00 00 4B
    # store new norm at ptr (used to have old norm)
    xmm3 = xmm1  # copy 8388610f to xmm3
    # store 1.0 vec4f at ptr (not sure what it does)
    xmm7 = xmm0  # copy 8388609f
    # store 0 0 0 0 0 16383 6.10389e-005 16383 at ptr (not sure why)
    xmm8 = np.float32(norm_half_abs)  # move halfnorm to xmm8 from ptr
    xmm6 = xmm8  # copy halfnorm from xmm8 to xmm6
    xmm6 = np.abs(xmm6)  # take abs of xmm6 (copy of halfnorm)
    xmm4 = xmm6  # copy abs halfnorm to xmm4
    xmm4 *= np.float32(0.63662)  # halfnorm
    xmm4 += xmm2  # halfnorm + 8388608f
    xmm3 = i_as_f(f_as_i(xmm3) & f_as_i(xmm4))  # mask xmm3 (...10f) with xmm4 (halfnorm+...8f)
    xmm7 = i_as_f(f_as_i(xmm7) & f_as_i(xmm4))  # mask xmm7 (...9f) with xmm4 (halfnorm+...8f)
    xmm3 = xmm3 == xmm1  # compare equality of masked and ..10f -> xmm3 = 0
    xmm7 = xmm7 == xmm0  # compare equality of masked and ..9f -> xmm7 = -1 or 0
    # xmm3 = i_as_f(-1 if xmm3 else 0)
    # xmm7 = i_as_f(-1 if xmm7 else 0)
    # xmm3 = 2147483647 if xmm3 else 0
    # xmm7 = 2147483647 if xmm7 else 0
    # print(bin(xmm3))
    # print(bin(xmm7))
    xmm4 -= xmm2  # halfnorm - (..8f)  = 1 or 0
    xmm2 = xmm7
    xmm0 = xmm4
    xmm1 = xmm4
    xmm0 *= np.float32(1.57031)
    xmm4 *= np.float32(7.54979e-08)
    xmm1 *= np.float32(0.0004837513)
    xmm6 -= xmm0  # halfnorm -xmm0
    xmm6 -= xmm1  # halfnorm -= xmm1
    xmm1 = np.float32(-0.0)  # copy -0.0 to xmm1
    xmm0 = xmm1
    xmm5 = xmm1
    xmm5 = xmm5 if xmm3 else 0.0
    xmm0 = xmm0 if xmm7 else 0.0
    # xmm5 = i_as_f(f_as_i(xmm5) & xmm3)
    # xmm0 = i_as_f(f_as_i(xmm0) & xmm7)
    xmm3 = np.float32(-0.000195153)  # copy to xmm3
    xmm8 = i_as_f(f_as_i(xmm8) & f_as_i(xmm1))
    xmm1 = xmm7
    xmm6 = i_as_f(f_as_i(xmm6) ^ f_as_i(xmm5))
    xmm6 -= xmm4
    xmm4 = np.float32(2.44332e-005)  # copy from ptr
    xmm6 = i_as_f(f_as_i(xmm6) ^ f_as_i(xmm0))
    xmm0 = xmm6
    xmm0 *= xmm6
    xmm4 *= xmm0
    xmm3 *= xmm0
    xmm4 += np.float32(-0.00138873)
    xmm3 += np.float32(0.00833216)
    xmm4 *= xmm0
    xmm3 *= xmm0
    xmm4 += np.float32(0.0416666)
    xmm3 += np.float32(-0.166667)
    xmm4 *= xmm0
    xmm4 -= np.float32(0.5)
    xmm4 *= xmm0
    xmm0 *= xmm6
    xmm4 += np.float32(1.0)
    xmm3 *= xmm0

    # changed # xmm1 = i_as_f(~f_as_i(xmm1) & f_as_i(xmm4))  # slight change here
    xmm1 = 0.0 if xmm1 else xmm4
    xmm0 = xmm4
    xmm3 += xmm6
    # changed  # i_as_f(f_as_i(xmm0) & f_as_i(xmm7))
    xmm0 = xmm0 if xmm7 else 0.0
    # get new norm again
    # xmm2 = i_as_f(~f_as_i(xmm2) & f_as_i(xmm3))
    xmm2 = 0.0 if xmm2 else xmm3
    # changed  #  i_as_f(f_as_i(xmm3) & f_as_i(xmm7))
    xmm3 = xmm3 if xmm7 else 0.0
    # get 1.0 float again
    xmm1 = i_as_f(f_as_i(xmm1) | f_as_i(xmm3))
    xmm0 = i_as_f(f_as_i(xmm0) | f_as_i(xmm2))
    xmm1 = i_as_f(f_as_i(xmm1) ^ f_as_i(xmm5))  # xmm1[0] is q
    xmm0 = i_as_f(f_as_i(xmm0) ^ f_as_i(xmm8))  # xmm0 is scale_fac
    return xmm1, xmm0


class ManisFile(InfoHeader, IoFile):

    def __init__(self):
        super().__init__(self)

    def load(self, filepath):
        # store file name for later
        self.file = filepath
        self.dir, self.basename = os.path.split(filepath)
        self.path_no_ext = os.path.splitext(self.file)[0]

        with open(filepath, "rb") as stream:
            self.read_fields(stream, self)
            self.eoh = stream.tell()
            # print(self)
            for mi, name in zip(self.mani_infos, self.names):
                mi.name = name
                if hasattr(mi, "keys"):
                    mi.keys.name = name
                    mi.keys.compressed.name = name
                # print(mi.keys.name)
                # if mi.root_pos_bone != 255:
                # 	print(mi.root_pos_bone, mi.keys.pos_bones_names[mi.root_pos_bone])
                # if mi.root_ori_bone != 255:
                # 	print(mi.root_ori_bone, mi.keys.ori_bones_names[mi.root_ori_bone])

    def iter_compressed_manis(self):
        for mani_info in self.mani_infos:
            if hasattr(mani_info, "keys"):
                if mani_info.dtype.compression and hasattr(mani_info.keys.compressed, "segments"):
                    yield mani_info

    def iter_uncompressed_manis(self):
        for mani_info in self.mani_infos:
            if hasattr(mani_info, "keys"):
                if not mani_info.dtype.compression:
                    yield mani_info

    def iter_compressed_keys(self):
        for mani_info in self.iter_compressed_manis():
            # logging.info(mani_info.keys.compressed)
            for i, mb in enumerate(mani_info.keys.compressed.segments):
                yield mani_info, i, mb

    def dump_keys(self):
        for mani_info, i, mb in self.iter_compressed_keys():
            with open(os.path.join(self.dir, f"{mani_info.name}_{i}.maniskeys"), "wb") as f:
                f.write(mb.data)

    def get_bitsize(self):
        # for i in reversed(range(31, -1, -1)):
        # 	# print(i, 15 >> i)
        # 	if 15 >> i == 0:
        # 		return i
        # return -1
        new_bit = 0xf  # MOV new_bit,0xf
        # return new_bit.bit_length()  # - 1
        return new_bit.bit_length() - 1

    def segment_frame_count(self, i, frame_count):
        # get from chunk index
        return min(32, frame_count - (i * 32))

    def log_loc_keys(self):
        for mani_info in self.iter_uncompressed_manis():
            # logging.info(mani_info)
            for pos_index, pos_name in enumerate(mani_info.keys.pos_bones_names):
                v = mani_info.keys.pos_bones[0][pos_index]
                x, y, z = v.x, v.y, v.z
                logging.info(f"unc {pos_index} {pos_name} {(x, y, z)}")
            break

    def log_rot_keys(self):
        for mani_info in self.iter_uncompressed_manis():
            # logging.info(mani_info)
            for ori_index, ori_name in enumerate(mani_info.keys.ori_bones_names):
                v = mani_info.keys.ori_bones[0][ori_index]
                x, y, z, w = v.x, v.y, v.z, v.w
                # if "def_c_hips_joint" == ori_name:
                #     logging.info(f"{ori_index} {ori_name} {(x, y, z, w)}")

    def parse_keys(self):
        for mani_info in self.iter_compressed_manis():
            keys_iter = None
            # if mani_info.name != "acrocanthosaurus@standidle01":
            if mani_info.name != "acrocanthosaurus@drinksocialinteractiona":
                continue
            # acro debug keys
            dump_path = os.path.join(root_path.root_dir, "dumps", f"{mani_info.name}_keys.txt")
            if os.path.isfile(dump_path):
                logging.info(f"Found reference keys for {mani_info.name}")
                keys = [int(line.strip(), 0) for line in open(dump_path, "r")]
                keys_iter = iter(keys)
            # logging.info(mani_info)
            # logging.info(mani_info.keys.compressed)
            try:
                self.decompress(keys_iter, mani_info)
            except:
                logging.exception(f"Decompressing {mani_info.name} failed")
            # break

    def decompress(self, keys_iter, mani_info):
        scale = 6.103888e-05
        k_channel_bitsize = self.get_bitsize()
        logging.info(
            f"Anim {mani_info.name} with {len(mani_info.keys.compressed.segments)} segments, {mani_info.frame_count} frames")
        mani_info.keys.compressed.pos_bones = np.empty((mani_info.frame_count, mani_info.pos_bone_count, 3), np.float32)
        mani_info.keys.compressed.ori_bones = np.empty((mani_info.frame_count, mani_info.ori_bone_count, 4), np.float32)
        assert mani_info.keys.compressed.pos_bone_count == mani_info.pos_bone_count
        assert mani_info.keys.compressed.ori_bone_count == mani_info.ori_bone_count
        frame_offset = 0
        for segment_i, mb in enumerate(mani_info.keys.compressed.segments):
            f = BinStream(mb.data)
            f2 = BinStream(mb.data)
            segment_frames_count = self.segment_frame_count(segment_i, mani_info.frame_count)
            logging.info(f"Segment[{segment_i}] frames {segment_frames_count}")
            try:
                segment_pos_bones = mani_info.keys.compressed.pos_bones[
                                    frame_offset:frame_offset + segment_frames_count]
                segment_ori_bones = mani_info.keys.compressed.ori_bones[
                                    frame_offset:frame_offset + segment_frames_count]

                # this is a jump to the end of the compressed keys
                wavelet_byte_offset = f.read_int_reversed(16)
                context = KeysContext(f2, wavelet_byte_offset)
                self.read_vec3_keys(context, f, f2, segment_i, k_channel_bitsize, mani_info,
                                    scale, segment_frames_count, segment_pos_bones, keys_iter=keys_iter)
                self.read_rot_keys(context, f, f2, segment_i, k_channel_bitsize, mani_info, scale, segment_frames_count,
                                   segment_ori_bones, keys_iter=keys_iter)
            except:
                logging.exception(f"Reading Segment[{segment_i}] failed at bit {f.pos}, byte {f.pos / 8}")
                raise
            frame_offset += segment_frames_count
        ck = mani_info.keys.compressed
        loc_min = ck.loc_bounds.mins[ck.loc_bound_indices]
        loc_ext = ck.loc_bounds.scales[ck.loc_bound_indices]
        loc = ck.pos_bones
        loc *= loc_ext
        loc += loc_min
        # logging.info(ck)
        # for pos_index, pos_name in enumerate(mani_info.keys.pos_bones_names):
        #     logging.info(f"dec {pos_index} {pos_name} {loc[0, pos_index]}")

    def read_vec3_keys(self, context, f, f2, i, k_channel_bitsize, mani_info,
                       scale, segment_frames_count, segment_pos_bones, keys_iter=None):
        identity = np.zeros(3, np.float32)
        for pos_index, pos_name in enumerate(mani_info.keys.pos_bones_names):
            frame_map = np.zeros(32, dtype=np.uint32)
            ushort_storage = np.zeros(156, dtype=np.uint32)
            # definitely not byte aligned as the key bytes can not be found in the manis data
            # defines basic loc values and which channels are keyframed
            # logging.info(f"pos[{pos_index}] {pos_name} at bit {f.pos}")
            f_pos = f.pos
            pos_base, vec = self.read_vec3(f)
            vec *= scale
            # logging.info(f"{pos_index} {pos_name} {vec}")
            # logging.info(f"{(x, y, z)} {struct.pack('f', x), struct.pack('f', y), struct.pack('f', z)}")
            self.compare_key_with_reference(f, keys_iter, pos_base)
            keys_flag = f.read_int_reversed(3)
            keys_flag = StoreKeys.from_value(keys_flag)
            # logging.info(f"{keys_flag}")
            if keys_flag.x or keys_flag.y or keys_flag.z:
                wavelet_i = self.read_wavelet_table(context, f2, frame_map, segment_frames_count)
                self.read_rel_keys(f, frame_map, k_channel_bitsize, keys_flag, ushort_storage, wavelet_i)
                # logging.info(f"key {i} = {rel_key_masked}")
                if segment_frames_count > 1:
                    frame_inc = 0
                    # set base keyframe
                    segment_pos_bones[0, pos_index] = vec[:3]
                    # set other keyframes
                    last_key_a = identity.copy()
                    last_key_b = identity.copy()
                    key_picked = vec[:3].copy()
                    for out_frame_i in range(1, segment_frames_count):
                        trg_frame_i = frame_map[frame_inc]
                        if trg_frame_i == out_frame_i:
                            frame_inc += 1
                        rel = ushort_storage[out_frame_i*3: out_frame_i*3+3]
                        out = rel.astype(np.float32)
                        out[0] = self.make_signed(rel[0])
                        out[1] = self.make_signed(rel[1])
                        out[2] = self.make_signed(rel[2])
                        last_key_delta = (last_key_b - last_key_a) + last_key_b
                        base_plus_delta = last_key_delta + key_picked
                        # todo do something here for base_key_float
                        base_key_float = base_plus_delta
                        final = base_key_float + out * scale
                        # todo get flag
                        next_key_offset = 0 if out_frame_i == trg_frame_i else 4
                        which_key_flag = True if next_key_offset else False
                        key_picked = vec[:3] if which_key_flag else final
                        key_a = identity.copy() if which_key_flag else last_key_b.copy()
                        key_b = identity.copy() if which_key_flag else last_key_delta.copy() + out * scale
                        last_key_a = identity.copy()
                        last_key_b = identity.copy()
                        if out_frame_i == trg_frame_i:
                            pass
                        output = final if which_key_flag else vec[:3]
                        segment_pos_bones[out_frame_i, pos_index] = output
                        # segment_pos_bones[out_frame_i, pos_index] = out * scale
                        # segment_pos_bones[out_frame_i, pos_index] = final
                # return
                # print(segment_pos_bones[:, pos_index])
                # return
            else:
                # set all keyframes
                segment_pos_bones[:, pos_index] = vec[:3]
        logging.info(f"Segment[{i}] loc finished at bit {f.pos}, byte {f.pos / 8}")

    def read_rot_keys(self, context, f, f2, i, k_channel_bitsize, mani_info, scale, segment_frames_count,
                      segment_ori_bones, keys_iter=None):
        q_scale = 6.283185
        epsilon = 1.1920929E-7
        identity = np.zeros(4, dtype=np.float32)
        identity[3] = 1.0
        for ori_index, ori_name in enumerate(mani_info.keys.ori_bones_names):
            # logging.info(context)
            frame_map = np.zeros(32, dtype=np.uint32)
            ushort_storage = np.zeros(156, dtype=np.uint32)
            # defines basic rot values
            # logging.info(f"pos[{ori_index}] {ori_name} at bit {f.pos}")
            f_pos = f.pos
            pos_base, vec = self.read_vec3(f)
            vec *= scale * q_scale
            norm = np.linalg.norm(vec)
            # logging.info(f"{ori_index} {pos_base} at {f_pos} {vec} {norm}")
            if norm < epsilon:
                quat = identity.copy()
            else:
                y_rel = identity.copy()
                y_rel[1] = vec[1] * vec[1]
                y_rel[0] = norm * 0.5
                b = identity.copy()
                b[1] = vec[2] * vec[2]
                b[0] = 0.0
                q, scale_fac = get_quat_scale_fac(norm * 0.5)
                # print(vec, norm)
                quat = vec / norm
                quat *= scale_fac
                quat[3] = q
                # logging.info(f"normed {quat}, scale_fac {scale_fac}, q {q}")
                # print(scale_fac, quat)
            # logging.info(f"{(x, y, z)} {struct.pack('f', x), struct.pack('f', y), struct.pack('f', z)}")
            self.compare_key_with_reference(f, keys_iter, pos_base)
            # return
            # which channels are keyframed
            keys_flag = f.read_int_reversed(3)
            keys_flag = StoreKeys.from_value(keys_flag)
            # logging.info(f"{keys_flag}")
            if keys_flag.x or keys_flag.y or keys_flag.z:
                wavelet_i = self.read_wavelet_table(context, f2, frame_map, segment_frames_count)
                self.read_rel_keys(f, frame_map, k_channel_bitsize, keys_flag, ushort_storage, wavelet_i)
                # logging.info(f"key {i} = {rel_key_masked}")
                if segment_frames_count > 1:
                    frame_inc = 0
                    # print(ushort_storage)
                    # set base keyframe
                    segment_ori_bones[0, ori_index] = quat
                    # set other keyframes
                    for out_frame_i in range(1, segment_frames_count):
                        trg_frame_i = frame_map[frame_inc]
                        if trg_frame_i == out_frame_i:
                            frame_inc += 1
                        rel = ushort_storage[out_frame_i*3: out_frame_i*3+4]
                        out = rel.astype(np.float32)
                        out[0] = self.make_signed(rel[0])
                        out[1] = self.make_signed(rel[1])
                        out[2] = self.make_signed(rel[2])
                        out[3] = 0.0
                        # todo check if this is the right scale
                        out *= scale
                        norm = math.sqrt(max(0.0, 1.0 - np.linalg.norm(out)))
                        rel_scaled = out.copy()
                        rel_scaled[3] = norm

                        rel_inter = out.copy()
                        rel_inter[0] = (quat[0] * norm + quat[1] * rel_scaled[2]) - (quat[2] * rel_scaled[1] - quat[3] * rel_scaled[0])
                        rel_inter[1] = quat[2] * norm + quat[3] * rel_scaled[2] + (quat[0] * rel_scaled[1] - quat[1] * rel_scaled[0])
                        rel_inter[2] = (norm * quat[3] - rel_scaled[2] * quat[2]) - (rel_scaled[1] * quat[1] + rel_scaled[0] * quat[0])
                        rel_inter[3] = (norm * quat[1] - rel_scaled[2] * quat[0]) + rel_scaled[1] * quat[3] + rel_scaled[0] * quat[2]
                        norm = math.sqrt(np.linalg.norm(rel_inter))
                        if norm == 0.0:
                            scaled_inter = identity.copy()
                        else:
                            scaled_inter = rel_inter * norm
                        segment_ori_bones[out_frame_i, ori_index, ] = scaled_inter
                        # segment_ori_bones[out_frame_i, ori_index, ] = out + quat
            else:
                # set all keyframes
                segment_ori_bones[:, ori_index] = quat
        logging.info(f"Segment[{i}] rot finished at bit {f.pos}, byte {f.pos / 8}")

    def read_rel_keys(self, f, frame_map, k_channel_bitsize, keys_flag, ushort_storage, wavelet_i):
        for channel_i, is_active in enumerate((keys_flag.x, keys_flag.y, keys_flag.z)):
            if is_active:
                # logging.info(f"rel_keys[{channel_i}] at bit {f.pos}")
                # define the minimal key size for this channel
                ch_key_size = f.read_int_reversed(k_channel_bitsize + 1)
                ch_key_size_masked = ch_key_size & 0x1f
                assert ch_key_size <= 32
                # logging.info(f"channel[{channel_i}] base_size {ch_key_size} at bit {f.pos}")
                for trg_frame_i in frame_map[:wavelet_i]:
                    rel_key_flag = 1 << ch_key_size_masked | 1 >> 0x20 - ch_key_size_masked
                    # rel_key_size = f.read_bit_size_flag(15 - ch_key_size_masked)
                    rel_key_size = f.read_bit_size_flag(32)
                    # todo this may have to be shifted only with the corresponding clamp applied
                    rel_key_base = f.interpret_as_shift(rel_key_size, rel_key_flag)
                    ch_rel_key_size = ch_key_size + rel_key_size
                    # clamp key size to 0-15 bits
                    ch_rel_key_size = min(ch_rel_key_size, 15)
                    # ensure the final key size is valid
                    assert ch_rel_key_size <= 32
                    # logging.info(f"ch_rel_key_size {ch_rel_key_size}")
                    # read the key, if it has a size
                    if ch_rel_key_size:
                        ch_rel_key = f.read_int_reversed(ch_rel_key_size)
                    else:
                        ch_rel_key = 0
                    # logging.info(f"key = {ch_rel_key}")
                    rel_key_masked = (rel_key_base + ch_rel_key) & 0xffff
                    ushort_storage[channel_i + trg_frame_i * 3] = rel_key_masked

    def read_wavelet_table(self, context, f2, frame_map, segment_frames_count):
        # logging.info(f"wavelets at bit {f2.pos}")
        wavelet_i = 0
        for wave_frame_i in range(1, segment_frames_count):
            if context.i_in_run == 0:
                assert context.runs_remaining != 0
                context.runs_remaining -= 1
                context.do_increment = not context.do_increment
                init_k = context.init_k_a if context.do_increment else context.init_k_b
                assert init_k < 32
                # run 0: init_k_a = 2
                # run 1: init_k_b = 4
                # logging.info(f"do_increment {do_increment} init_k {init_k} at {f2.pos}")
                k_size = f2.read_bit_size_flag(32 - init_k)
                k_flag = 1 << (init_k & 0x1f)
                k_flag_out = f2.interpret_as_shift(k_size, k_flag)
                # logging.info(
                # 	f"pos before key {f2.pos}, k_flag_out {k_flag_out}, initk bare {k_size}")
                k_key = f2.read_int_reversed(k_size + init_k)
                assert k_size + init_k < 32
                context.i_in_run = k_key + k_flag_out
            # logging.info(
            # 	f"wavelet_frame[{wave_frame_i}] total init_k {init_k + k_size} key {k_key} k_flag_out {k_flag_out} i {i_in_run}")
            # logging.info(f"pos after read {f2.pos}")
            context.i_in_run -= 1
            if context.do_increment:
                frame_map[wavelet_i] = wave_frame_i
                wavelet_i += 1
        # logging.info(frame_map)
        # logging.info(f"wavelets finished at bit {f2.pos}, byte {f2.pos / 8}, out_count {wavelet_i}")
        return wavelet_i

    def read_vec3(self, f):
        pos_base = f.read_uint(45)
        # logging.info(pos_base)
        # logging.info(f"{hex(pos_base)}, {pos_base}")
        x = pos_base & 0x7fff
        y = (pos_base >> 0xf) & 0x7fff
        z = (pos_base >> 0x1e) & 0x7fff
        # x = self.make_signed(x)
        # y = self.make_signed(y)
        # z = self.make_signed(z)
        vec = np.zeros(4, dtype=np.float32)
        vec[0] = self.make_signed(x)
        vec[1] = self.make_signed(y)
        vec[2] = self.make_signed(z)
        # f.pos = f_pos
        # x = f.read_int(15)
        # y = f.read_int(15)
        # z = f.read_int(15)
        # logging.info(f"{(x, y, z)} {(hex(x), hex(y), hex(z))}")
        return pos_base, vec

    def compare_key_with_reference(self, f, keys_iter, pos_base):
        if keys_iter is not None:
            expected_key = next(keys_iter)
            expected_key_bin = bitarray.util.int2ba(expected_key, length=45, endian="little", signed=False)
            f.find_all(expected_key_bin)
            # logging.info(f"Expected {expected_key} found at bits {tuple(f.find_all(expected_key_bin))}")
            if expected_key != pos_base:
                raise AttributeError(f"Expected and found keys do not match")

    def make_signed(self, x):
        return -(x + 1 >> 1) if x & 1 else x >> 1


if __name__ == "__main__":
    logging_setup("mani")
    for k in (0, 1, 4, 5, 6, 32, 34, 36, 37, 38, 64, 66, 68, 69, 70, 82):
        print(ManisDtype.from_value(k))
    # print(bin(-4395513102365351936))
    # print(bin(554058852231815168))
    # key = Key94C.from_value(2305843010808512512)
    # key.type = 0
    # key.loc_x = 0
    # key.loc_y = 0
    # # key.loc_z = 0b11111111111111111111
    # key.loc_z = 0b11111111111111111111
    # # key.unk = 0
    # # key.more_loc = 0
    # key.rot_rel = 4
    # print(key)
    mani = ManisFile()
    # acro stand_ide
    target = "acrocanthosaurus@standidle01"
    mani.load("C:/Users/arnfi/Desktop/Coding/Frontier/Warhammer/Annihilator/animation.maniset52a766ac.manis")
    print(mani)
    # mani.load("C:/Users/arnfi/Desktop/acro/notmotionextracted.maniset53978456.manis")
    # mani.load("C:/Users/arnfi/Desktop/animationmotionextractedlocomotion.maniset648a1a01.manis")
    # mani.load("C:/Users/arnfi/Desktop/crane/animationnotmotionextractedfighting.maniset3d816f2c.manis")
    # mani.load("C:/Users/arnfi/Desktop/kangaroo/animation.maniset32dc487b.manis")
    # mani.load("C:/Users/arnfi/Desktop/Wheel/animation.maniset9637aeb4.manis")
    # mani.load("C:/Users/arnfi/Desktop/DLA scale anim.manis")
    # mani.load("C:/Users/arnfi/Desktop/dinomascot/animation.maniset293c241f.manis")
    # mani.dump_keys()
    # mani.parse_keys()
    # mani.log_rot_keys()
    # mani.log_loc_keys()
# mani.load("C:/Users/arnfi/Desktop/donationbox/animation.maniseteaf333c5.manis")
# mani.dump_keys()
# mani.parse_keys()
# # mani.load("C:/Users/arnfi/Desktop/gate/animation.manisetd2b36ae0.manis")
# print(mani)
# # mani.load("C:/Users/arnfi/Desktop/JWE2/pyro/hatcheryexitcamera.maniset8c6441b9.manis")
# mani.parse_keys()
# mani.load("C:/Users/arnfi/Desktop/dilo/locomotion.maniset1c05e0f4.manis")
# mani.load("C:/Users/arnfi/Desktop/ostrich/ugcres.maniset8982114c.manis")
# mani.load("C:/Users/arnfi/Desktop/Coding/ovl/OVLs/anim test/rot_x_0_22_42.manis")
# mani.load("C:/Users/arnfi/Desktop/Coding/ovl/OVLs/anim test/ugcres.maniset8982114c0.manis")
# mani.load("C:/Users/arnfi/Desktop/Coding/ovl/OVLs/anim test/ugcres.maniset8982114c1.manis")
# mani.load("C:/Users/arnfi/Desktop/Coding/ovl/OVLs/anim test/ugcres.maniset8982114c2.manis")
# mani.load("C:/Users/arnfi/Desktop/Coding/ovl/PZ 1.6/anim/animation.maniset9637aeb4.manis")
# mani.load("C:/Users/arnfi/Desktop/Coding/ovl/PZ 1.6/anim/animationmotionextractedbehaviour.maniset5f721adf.manis")
# mani.load("C:/Users/arnfi/Desktop/Coding/ovl/PZ 1.6/anim/animationmotionextractedlocomotion.maniset58076276.manis")
# mani.load("C:/Users/arnfi/Desktop/lemur/animationnotmotionextractedpartials.maniset919dac12.manis")
# mani.load("C:/Users/arnfi/Desktop/lemur/animationmotionextractedfighting.maniset9c749130.manis")
# mani.load("C:/Users/arnfi/Desktop/lemur/animationnotmotionextractedlocomotion.maniset87d072d8.manis")

# mani.load("C:/Users/arnfi/Desktop/Coding/Frontier/anim/wheel/animation.maniset9637aeb4.manis")

# mani.load("C:/Users/arnfi/Desktop/Coding/Frontier/anim/Iron_piston/ugcres.maniset8982114c.manis")
# mani.load("C:/Users/arnfi/Desktop/Coding/Frontier/anim/pc dino/animation.maniset293c241f.manis")

# mani.load("C:/Users/arnfi/Desktop/Coding/Frontier/anim/dilo/notmotionextracted.manisetf2b1fd43.manis")  # ok 0000 24 bytes f
# mani.load("C:/Users/arnfi/Desktop/Coding/Frontier/anim/dilo/motionextracted.maniset1823adb0.manis")  # 0111 48 bytes f
# mani.load("C:/Users/arnfi/Desktop/Coding/Frontier/anim/dilo/motionextracted.maniset1bfb6052.manis")  # 0, 2, 3, 1

# mani.load("C:/Users/arnfi/Desktop/Coding/Frontier/anim/ceara/hatcheryexitcamera.maniset9762d823.manis")
# mani.load("C:/Users/arnfi/Desktop/Coding/Frontier/anim/ceara/motionextracted.maniset7e6b0db3.manis") # keys are external
# mani.load("C:/Users/arnfi/Desktop/Coding/Frontier/anim/ceara/motionextracted.manisetf2b6c52d.manis")
# print(mani)

# mani.load("C:/Users/arnfi/Desktop/manis/fee_feeder_ground.maniset2759dfaf.manis")
# mani.load("C:/Users/arnfi/Desktop/manis/motionextracted.maniset167ed454.manis")
# hex_test()
