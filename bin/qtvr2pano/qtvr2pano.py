#!/usr/bin/env python3
# Vibe coded by Claude
"""
qtvr2pano.py - Convert QuickTime VR movie files to equirectangular panorama images.

Parses QTVR v1 panorama files (including MacBinary II wrapped), extracts
and decodes video frames (Cinepak, RPZA, RLE, SMC, YUV2), assembles them
into panoramic images, and outputs JPEGs with embedded GPano XMP metadata
suitable for use with Pannellum, Google Photos, and Facebook 360.

Supports multi-node QTVR files, outputting one JPEG per node plus a
JSON manifest with node metadata and inter-node links.

Usage: python3 qtvr2pano.py <inputFile> <outputDir>
"""

import argparse
import json
import math
import struct
import sys
from pathlib import Path

import av
from PIL import Image


# Codec FourCC to FFmpeg codec name mapping
CODEC_MAP = {
    "cvid": "cinepak",
    "rpza": "rpza",
    "rle ": "qtrle",
    "smc ": "smc",
    "jpeg": "mjpeg",
    "yuv2": "rawvideo",
}

# Codecs that need special pixel format setup
CODEC_PIX_FMT = {
    "yuv2": "yvyu422",
}


def read_uint32(data, offset):
    return struct.unpack(">I", data[offset : offset + 4])[0]


def read_int32(data, offset):
    return struct.unpack(">i", data[offset : offset + 4])[0]


def read_uint16(data, offset):
    return struct.unpack(">H", data[offset : offset + 2])[0]


def read_int16(data, offset):
    return struct.unpack(">h", data[offset : offset + 2])[0]


def read_fixed(data, offset):
    """Read a 16.16 fixed-point number as float."""
    raw = struct.unpack(">i", data[offset : offset + 4])[0]
    return raw / 65536.0


def find_atoms(data, target_type=None):
    """Iterate over atoms in data, yielding (type_bytes, content_bytes)."""
    offset = 0
    while offset + 8 <= len(data):
        atom_size = read_uint32(data, offset)
        atom_type = data[offset + 4 : offset + 8]
        if atom_size < 8 or offset + atom_size > len(data):
            break
        content = data[offset + 8 : offset + atom_size]
        if target_type is None or atom_type == target_type:
            yield atom_type, content
        offset += atom_size


def find_atom(data, target_type):
    """Find the first atom of a given type and return its content."""
    if data is None:
        return None
    for _, content in find_atoms(data, target_type):
        return content
    return None


def find_all_atoms(data, target_type):
    """Find all atoms of a given type and return their contents."""
    return [content for _, content in find_atoms(data, target_type)]


def is_macbinary(data):
    """Check if data starts with a MacBinary II header."""
    if len(data) < 128:
        return False
    if data[0] != 0:
        return False
    name_len = data[1]
    if name_len < 1 or name_len > 63:
        return False
    file_type = data[65:69]
    if file_type == b"MooV":
        return True
    data_fork_len = read_uint32(data, 83)
    if 128 + data_fork_len <= len(data):
        return True
    return False


def extract_macbinary(file_data):
    """Extract data fork and moov from resource fork of a MacBinary II file.
    Returns (data_fork, moov_content, macbinary_offset).
    """
    data_fork_len = read_uint32(file_data, 83)
    resource_fork_len = read_uint32(file_data, 87)
    data_fork = file_data[128 : 128 + data_fork_len]

    data_fork_padded = ((data_fork_len + 127) // 128) * 128
    res_start = 128 + data_fork_padded

    moov_content = None
    if res_start < len(file_data) and resource_fork_len > 0:
        rfork = file_data[res_start:]
        res_data_offset = read_uint32(rfork, 0)
        res_map_offset = read_uint32(rfork, 4)

        rmap = rfork[res_map_offset:]
        type_list_offset = read_uint16(rmap, 24)
        tlist = rmap[type_list_offset:]
        num_types = read_int16(tlist, 0) + 1

        offset = 2
        for _ in range(num_types):
            res_type = tlist[offset : offset + 4]
            ref_list_offset = read_uint16(tlist, offset + 6)

            if res_type == b"moov":
                ref = tlist[ref_list_offset:]
                attrs_and_off = read_uint32(ref, 4)
                res_data_off = attrs_and_off & 0xFFFFFF
                rdata = rfork[res_data_offset + res_data_off :]
                rdata_len = read_uint32(rdata, 0)
                moov_raw = rdata[4 : 4 + rdata_len]
                if moov_raw[4:8] == b"moov":
                    moov_content = moov_raw[8:]
                else:
                    moov_content = moov_raw
                break
            offset += 8

    return data_fork, moov_content, 128


def read_float32(data, offset):
    """Read a big-endian IEEE 754 float."""
    return struct.unpack(">f", data[offset : offset + 4])[0]


def parse_v2_atoms(data):
    """Parse QTAtomContainer atoms (20-byte headers used by QTVR v2)."""
    results = []
    o = 0
    while o + 20 <= len(data):
        sz = read_uint32(data, o)
        tp = data[o + 4 : o + 8]
        atom_id = read_uint32(data, o + 8)
        child_count = read_uint16(data, o + 14)
        if sz < 20 or o + sz > len(data):
            break
        leaf_data = data[o + 20 : o + sz]
        results.append((tp, atom_id, child_count, leaf_data))
        o += sz
    return results


def parse_v2_pano_sample(data):
    """Parse a v2 panorama track sample (QTAtomContainer with sean/pdat)."""
    # Skip 12-byte QTAtomContainer header
    atoms = parse_v2_atoms(data[12:])
    for tp, aid, cc, leaf in atoms:
        if tp == b"sean":
            for ctp, cid, ccc, cleaf in parse_v2_atoms(leaf):
                if ctp == b"pdat" and len(cleaf) >= 60:
                    return {
                        "minPan": read_float32(cleaf, 12),
                        "maxPan": read_float32(cleaf, 16),
                        "minTilt": read_float32(cleaf, 20),
                        "maxTilt": read_float32(cleaf, 24),
                        "defPan": read_float32(cleaf, 36),
                        "defTilt": read_float32(cleaf, 40),
                        "defFOV": read_float32(cleaf, 44),
                        "imageSizeX": read_uint32(cleaf, 48),
                        "imageSizeY": read_uint32(cleaf, 52),
                        "imageNumFramesX": read_uint16(cleaf, 56),
                        "imageNumFramesY": read_uint16(cleaf, 58),
                    }
    return None


def parse_node_sample(file_data, offset, size):
    """Parse a v1 panorama track sample (one per node) for metadata."""
    node_data = file_data[offset : offset + size]

    pHdr = find_atom(node_data, b"pHdr")
    pLnk = find_atom(node_data, b"pLnk")
    pHot = find_atom(node_data, b"pHot")
    strT = find_atom(node_data, b"strT")

    node = {"nodeID": 0, "defHPan": 0, "defVPan": 0, "defZoom": 0, "links": []}

    if pHdr and len(pHdr) >= 0x18:
        node["nodeID"] = read_uint32(pHdr, 0)
        node["defHPan"] = read_fixed(pHdr, 4)
        node["defVPan"] = read_fixed(pHdr, 8)
        node["defZoom"] = read_fixed(pHdr, 12)

    if pLnk and len(pLnk) >= 4:
        n_links = read_int16(pLnk, 2)
        for i in range(n_links):
            lo = 4 + i * 56
            if lo + 16 > len(pLnk):
                break
            link_id = read_uint16(pLnk, lo)
            to_node_id = read_uint32(pLnk, lo + 12)
            to_hpan = read_fixed(pLnk, lo + 28)
            to_vpan = read_fixed(pLnk, lo + 32)
            to_zoom = read_fixed(pLnk, lo + 36)
            node["links"].append({
                "linkID": link_id,
                "toNodeID": to_node_id,
                "toHPan": to_hpan,
                "toVPan": to_vpan,
                "toZoom": to_zoom,
            })

    if pHot and len(pHot) >= 4:
        n_hot = read_int16(pHot, 2)
        hotspots = []
        for i in range(n_hot):
            ho = 4 + i * 56
            if ho + 56 > len(pHot):
                break
            hs_id = read_uint16(pHot, ho)
            hs_type = pHot[ho + 4 : ho + 8]
            type_data = read_uint32(pHot, ho + 8)
            view_hpan = read_fixed(pHot, ho + 12)
            view_vpan = read_fixed(pHot, ho + 16)
            view_zoom = read_fixed(pHot, ho + 20)

            try:
                hs_type_str = hs_type.decode("ascii").strip("\x00")
            except Exception:
                hs_type_str = hs_type.hex()

            hotspots.append({
                "hotSpotID": hs_id,
                "type": hs_type_str,
                "typeData": type_data,
                "viewHPan": view_hpan,
                "viewVPan": view_vpan,
                "viewZoom": view_zoom,
            })
        node["hotspots"] = hotspots

    return node


def parse_qtvr(file_path):
    """Parse a QTVR file and return panorama metadata including per-node info."""
    with open(file_path, "rb") as f:
        file_data = f.read()

    macbinary_offset = 0

    if is_macbinary(file_data):
        data_fork, moov_content, macbinary_offset = extract_macbinary(file_data)
        if moov_content is None:
            moov_content = find_atom(data_fork, b"moov")
        if moov_content is None:
            raise ValueError("No moov atom found in MacBinary file")
    else:
        moov_content = find_atom(file_data, b"moov")
        if moov_content is None:
            raise ValueError("No moov atom found")
        macbinary_offset = 0

    # Parse moov atom to find tracks
    tracks = {}
    for _, trak_content in find_atoms(moov_content, b"trak"):
        tkhd = find_atom(trak_content, b"tkhd")
        if tkhd is None:
            continue
        track_id = read_uint32(tkhd, 12)
        tracks[track_id] = trak_content

    # Find panorama track — try v1 first (STpn/stpn handler), then v2 (qtvr handler)
    qtvr_version = 1
    pano_track = None
    pano_stsd_entry = None
    scene_track_id = None
    v2_pano_track = None

    # Build handler map
    track_handlers = {}
    for tid, trak in tracks.items():
        mdia = find_atom(trak, b"mdia")
        hdlr = find_atom(mdia, b"hdlr") if mdia else None
        if hdlr and len(hdlr) >= 12:
            track_handlers[tid] = hdlr[8:12]

    # v1: look for STpn/stpn handler
    for tid, trak in tracks.items():
        if track_handlers.get(tid) in (b"STpn", b"stpn"):
            pano_track = trak
            mdia = find_atom(trak, b"mdia")
            stbl = find_atom(find_atom(mdia, b"minf"), b"stbl")
            stsd = find_atom(stbl, b"stsd")
            pano_stsd_entry = stsd[16:]
            break

    # v2: look for qtvr handler with tref -> pano track
    if pano_track is None:
        for tid, trak in tracks.items():
            if track_handlers.get(tid) != b"qtvr":
                continue
            tref = find_atom(trak, b"tref")
            if tref is None:
                continue
            # Parse tref to find pano reference
            o = 0
            pano_ref_tid = None
            while o + 8 <= len(tref):
                sz = read_uint32(tref, o)
                tp = tref[o + 4 : o + 8]
                if sz < 8:
                    break
                if tp == b"pano" and sz >= 12:
                    pano_ref_tid = read_uint32(tref, o + 8)
                o += sz

            if pano_ref_tid is None:
                continue
            if pano_ref_tid not in tracks:
                continue

            # Found v2 panorama — follow pano track's tref to find image track
            qtvr_version = 2
            v2_pano_track = tracks[pano_ref_tid]
            pano_tref = find_atom(v2_pano_track, b"tref")
            if pano_tref:
                o = 0
                while o + 8 <= len(pano_tref):
                    sz = read_uint32(pano_tref, o)
                    tp = pano_tref[o + 4 : o + 8]
                    if sz < 8:
                        break
                    if tp == b"imgt" and sz >= 12:
                        scene_track_id = read_uint32(pano_tref, o + 8)
                    o += sz
            break

    if pano_track is None and v2_pano_track is None:
        # Check if it's an object movie
        for tid, trak in tracks.items():
            if track_handlers.get(tid) == b"qtvr":
                tref = find_atom(trak, b"tref")
                if tref and tref[4:8] == b"obje":
                    raise ValueError("QTVR object movies are not supported (not a panorama)")
        raise ValueError("No panorama track found in file")

    if qtvr_version == 1:
        # Parse v1 PanoSampleDescriptionTableEntry
        entry = pano_stsd_entry
        scene_track_id = read_int32(entry, 0x0C)
        h_pan_start = read_fixed(entry, 0x54)
        h_pan_end = read_fixed(entry, 0x58)
        v_pan_top = read_fixed(entry, 0x5C)
        v_pan_bottom = read_fixed(entry, 0x60)
        scene_size_x = read_uint32(entry, 0x6C)
        scene_size_y = read_uint32(entry, 0x70)
        num_frames = read_uint32(entry, 0x74)
        frames_x = read_int16(entry, 0x7A)
        frames_y = read_int16(entry, 0x7C)

        # Parse per-node metadata from panorama track samples
        pano_mdia = find_atom(pano_track, b"mdia")
        pano_stbl = find_atom(find_atom(pano_mdia, b"minf"), b"stbl")
        pano_stco = find_atom(pano_stbl, b"stco")
        pano_stsz = find_atom(pano_stbl, b"stsz")

        num_node_samples = read_uint32(pano_stsz, 8)
        uniform_node_size = read_uint32(pano_stsz, 4)

        nodes = []
        for i in range(num_node_samples):
            off = read_uint32(pano_stco, 8 + i * 4) + macbinary_offset
            sz = uniform_node_size if uniform_node_size else read_uint32(pano_stsz, 12 + i * 4)
            node = parse_node_sample(file_data, off, sz)
            node["index"] = i
            nodes.append(node)

    else:
        # Parse v2 panorama track samples (QTAtomContainer with sean/pdat)
        pano_mdia = find_atom(v2_pano_track, b"mdia")
        pano_stbl = find_atom(find_atom(pano_mdia, b"minf"), b"stbl")
        pano_stco = find_atom(pano_stbl, b"stco")
        pano_stsz = find_atom(pano_stbl, b"stsz")

        num_node_samples = read_uint32(pano_stsz, 8)
        uniform_node_size = read_uint32(pano_stsz, 4)

        # Parse first pano sample for common parameters
        first_off = read_uint32(pano_stco, 8) + macbinary_offset
        first_sz = uniform_node_size if uniform_node_size else read_uint32(pano_stsz, 12)
        first_sample = file_data[first_off : first_off + first_sz]
        pdat = parse_v2_pano_sample(first_sample)
        if pdat is None:
            raise ValueError("Could not parse v2 panorama sample data")

        h_pan_start = pdat["minPan"]
        h_pan_end = pdat["maxPan"]
        v_pan_top = pdat["maxTilt"]
        v_pan_bottom = pdat["minTilt"]
        scene_size_x = pdat["imageSizeX"]
        scene_size_y = pdat["imageSizeY"]
        frames_x = pdat["imageNumFramesX"]
        frames_y = pdat["imageNumFramesY"]
        num_frames = frames_x * frames_y

        nodes = []
        for i in range(num_node_samples):
            off = read_uint32(pano_stco, 8 + i * 4) + macbinary_offset
            sz = uniform_node_size if uniform_node_size else read_uint32(pano_stsz, 12 + i * 4)
            sample_data = file_data[off : off + sz]
            pd = parse_v2_pano_sample(sample_data)
            node = {
                "nodeID": i + 1,
                "defHPan": pd["defPan"] if pd else 0,
                "defVPan": pd["defTilt"] if pd else 0,
                "defZoom": pd["defFOV"] if pd else 0,
                "links": [],
                "index": i,
            }
            nodes.append(node)

    # Get the video (scene) track
    if scene_track_id not in tracks:
        raise ValueError(f"Scene track {scene_track_id} not found")
    scene_track = tracks[scene_track_id]

    tkhd = find_atom(scene_track, b"tkhd")
    frame_width = int(read_fixed(tkhd, 0x4C))
    frame_height = int(read_fixed(tkhd, 0x50))

    mdia = find_atom(scene_track, b"mdia")
    minf = find_atom(mdia, b"minf")
    stbl = find_atom(minf, b"stbl")

    stsd = find_atom(stbl, b"stsd")
    codec_fourcc = stsd[12:16].decode("ascii", errors="replace")
    video_entry = stsd[16:]
    video_depth = read_uint16(video_entry, 0x4A)

    stco = find_atom(stbl, b"stco")
    num_chunks = read_uint32(stco, 4)
    chunk_offsets = [read_uint32(stco, 8 + i * 4) for i in range(num_chunks)]

    stsz = find_atom(stbl, b"stsz")
    uniform_sample_size = read_uint32(stsz, 4)
    num_samples = read_uint32(stsz, 8)
    if uniform_sample_size:
        sample_sizes = [uniform_sample_size] * num_samples
    else:
        sample_sizes = [read_uint32(stsz, 12 + i * 4) for i in range(num_samples)]

    stsc = find_atom(stbl, b"stsc")
    num_stsc = read_uint32(stsc, 4)
    stsc_entries = []
    for i in range(num_stsc):
        first_chunk = read_uint32(stsc, 8 + i * 12)
        samples_per_chunk = read_uint32(stsc, 12 + i * 12)
        sdi = read_uint32(stsc, 16 + i * 12)
        stsc_entries.append((first_chunk, samples_per_chunk, sdi))

    sample_to_chunk = {}
    sample_id = 0
    for idx, (first_chunk, spc, _) in enumerate(stsc_entries):
        if idx + 1 < len(stsc_entries):
            next_chunk = stsc_entries[idx + 1][0]
        else:
            next_chunk = num_chunks + 1
        chunk_id = first_chunk
        while chunk_id < next_chunk:
            first_in_chunk = True
            for _ in range(spc):
                if sample_id < num_samples:
                    sample_to_chunk[sample_id] = (chunk_id, first_in_chunk)
                    first_in_chunk = False
                    sample_id += 1
            chunk_id += 1

    frames_per_node = frames_x * frames_y
    num_nodes = max(len(nodes), num_samples // frames_per_node if frames_per_node else 1)

    return {
        "file_data": file_data,
        "macbinary_offset": macbinary_offset,
        "codec_fourcc": codec_fourcc,
        "frame_width": frame_width,
        "frame_height": frame_height,
        "video_depth": video_depth,
        "num_frames": num_frames,
        "frames_x": frames_x,
        "frames_y": frames_y,
        "frames_per_node": frames_per_node,
        "scene_size_x": scene_size_x,
        "scene_size_y": scene_size_y,
        "h_pan_start": h_pan_start,
        "h_pan_end": h_pan_end,
        "v_pan_top": v_pan_top,
        "v_pan_bottom": v_pan_bottom,
        "chunk_offsets": chunk_offsets,
        "sample_sizes": sample_sizes,
        "sample_to_chunk": sample_to_chunk,
        "nodes": nodes,
        "num_nodes": num_nodes,
    }


def decode_frame(codec, data):
    """Decode a single video frame using PyAV."""
    packet = av.Packet(data)
    frames = codec.decode(packet)
    if frames:
        return frames[0].to_image()
    return None


def assemble_node(info, node_index):
    """Extract and assemble frames for a single node into a panoramic image."""
    fourcc = info["codec_fourcc"]
    ffmpeg_codec = CODEC_MAP.get(fourcc)
    if ffmpeg_codec is None:
        raise ValueError(
            f"Unsupported codec: {fourcc}. "
            f"Supported: {', '.join(CODEC_MAP.keys())}"
        )

    fw = info["frame_width"]
    fh = info["frame_height"]
    codec_width = fw
    needs_crop = False

    codec = av.Codec(ffmpeg_codec, "r").create()
    codec.height = fh
    codec.bits_per_coded_sample = info["video_depth"]
    pix_fmt = CODEC_PIX_FMT.get(fourcc)
    if pix_fmt:
        codec.pix_fmt = pix_fmt
        if fw % 2 != 0:
            codec_width = fw + 1
            needs_crop = True
    codec.width = codec_width

    file_data = info["file_data"]
    mac_offset = info["macbinary_offset"]
    chunk_offsets = info["chunk_offsets"]
    sample_sizes = info["sample_sizes"]
    sample_to_chunk = info["sample_to_chunk"]

    grid_cols = info["frames_x"]
    grid_rows = info["frames_y"]
    fpn = info["frames_per_node"]

    start_frame = node_index * fpn
    end_frame = start_frame + fpn

    dst = Image.new("RGB", (fw * grid_cols, fh * grid_rows))

    sample_offset = 0
    for sample_id in range(len(sample_sizes)):
        chunk_id, first_in_chunk = sample_to_chunk[sample_id]
        if first_in_chunk:
            sample_offset = 0

        if sample_id >= start_frame and sample_id < end_frame:
            chunk_file_offset = chunk_offsets[chunk_id - 1] + mac_offset
            abs_offset = chunk_file_offset + sample_offset
            sample_size = sample_sizes[sample_id]

            frame_data = file_data[abs_offset : abs_offset + sample_size]
            image = decode_frame(codec, frame_data)
            if image is None:
                print(f"  Warning: failed to decode frame {sample_id}", file=sys.stderr)
            else:
                if needs_crop:
                    image = image.crop((0, 0, fw, fh))
                local_id = sample_id - start_frame
                col = local_id % grid_cols
                row = local_id // grid_cols
                dst.paste(image, (col * fw, row * fh))

        sample_offset += sample_sizes[sample_id]

    dst = dst.rotate(-90, expand=True)
    return dst


def build_gpano_xmp(image_width, image_height, haov, vaov, v_pan_top, v_pan_bottom):
    """Build Google Photo Sphere XMP metadata for embedding in JPEG."""
    full_pano_width = round(image_width * 360.0 / haov) if haov < 360 else image_width
    full_pano_height = round(image_height * 180.0 / vaov)
    cropped_width = image_width
    cropped_height = image_height
    cropped_left = round((full_pano_width - cropped_width) / 2)
    cropped_top = round((90.0 - v_pan_top) / 180.0 * full_pano_height)
    initial_hfov = min(90.0, haov)

    xmp = f"""<?xpacket begin="\xef\xbb\xbf" id="W5M0MpCehiHzreSzNTczkc9d"?>
<x:xmpmeta xmlns:x="adobe:ns:meta/">
  <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
    <rdf:Description rdf:about=""
      xmlns:GPano="http://ns.google.com/photos/1.0/panorama/"
      GPano:ProjectionType="equirectangular"
      GPano:UsePanoramaViewer="True"
      GPano:FullPanoWidthPixels="{full_pano_width}"
      GPano:FullPanoHeightPixels="{full_pano_height}"
      GPano:CroppedAreaImageWidthPixels="{cropped_width}"
      GPano:CroppedAreaImageHeightPixels="{cropped_height}"
      GPano:CroppedAreaLeftPixels="{cropped_left}"
      GPano:CroppedAreaTopPixels="{cropped_top}"
      GPano:InitialViewHeadingDegrees="0"
      GPano:InitialViewPitchDegrees="0"
      GPano:InitialHorizontalFOVDegrees="{initial_hfov:.1f}"/>
  </rdf:RDF>
</x:xmpmeta>
<?xpacket end="w"?>"""

    return xmp.encode("utf-8")


def convert_qtvr(input_path, output_dir):
    """Convert a QTVR file to equirectangular panorama images.
    Outputs one JPEG per node plus a manifest.json.
    Returns list of result dicts.
    """
    input_path = Path(input_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Parsing {input_path.name}...")
    info = parse_qtvr(input_path)

    haov = abs(info["h_pan_end"] - info["h_pan_start"])
    vaov = abs(info["v_pan_top"] - info["v_pan_bottom"])
    num_nodes = info["num_nodes"]

    print(
        f"  Codec: {info['codec_fourcc']}, "
        f"Frame: {info['frame_width']}x{info['frame_height']}, "
        f"Grid: {info['frames_x']}x{info['frames_y']}"
    )
    print(f"  Nodes: {num_nodes}, Frames/node: {info['frames_per_node']}")
    print(f"  H-Pan: {info['h_pan_start']:.1f} to {info['h_pan_end']:.1f}, "
          f"V-Pan: {info['v_pan_top']:.1f} to {info['v_pan_bottom']:.1f}")

    base_name = input_path.stem
    results = []

    for ni in range(num_nodes):
        node_meta = info["nodes"][ni] if ni < len(info["nodes"]) else {}
        node_id = node_meta.get("nodeID", ni + 1)

        if num_nodes == 1:
            out_name = f"{base_name}.jpg"
        else:
            out_name = f"{base_name}_node{node_id}.jpg"

        out_path = output_dir / out_name

        print(f"  Assembling node {ni} (id={node_id})...")
        pano = assemble_node(info, ni)

        xmp_data = build_gpano_xmp(
            pano.width, pano.height, haov, vaov,
            info["v_pan_top"], info["v_pan_bottom"],
        )
        pano.save(str(out_path), "JPEG", quality=92, xmp=xmp_data)
        print(f"    {out_path} ({pano.width}x{pano.height})")

        result = {
            "file": out_name,
            "nodeID": node_id,
            "nodeIndex": ni,
            "width": pano.width,
            "height": pano.height,
            "haov": round(haov, 1),
            "vaov": round(vaov, 1),
            "defHPan": node_meta.get("defHPan", 0),
            "defVPan": node_meta.get("defVPan", 0),
            "defZoom": node_meta.get("defZoom", 0),
            "links": node_meta.get("links", []),
        }
        results.append(result)

    # Write manifest for multi-node files only
    if num_nodes > 1:
        manifest = {
            "source": input_path.name,
            "codec": info["codec_fourcc"],
            "nodes": results,
        }
        manifest_path = output_dir / f"{base_name}.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2)
        print(f"  Manifest: {manifest_path}")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Convert QuickTime VR movie files to panoramic images"
    )
    parser.add_argument("inputFile", type=Path, help="Input QTVR file")
    parser.add_argument("outputDir", type=Path, help="Output directory for JPEGs")
    args = parser.parse_args()

    if not args.inputFile.exists():
        print(f"Error: {args.inputFile} not found", file=sys.stderr)
        sys.exit(1)

    try:
        convert_qtvr(args.inputFile, args.outputDir)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
