# Vibe coded by Claude
"""
UNCRYPT - CRYPTON file decoder
Decrypts .cpt and .lcr files encrypted by CRYPTON (Olivier ACBM, ISICOM 1995)

Algorithm: Mode 1 (XOR + ROL + NOT with 14-byte evolving key)
  Data processed in 4096-byte blocks. For each block:
    Key resets to initial values, byte_index resets to 1.
    For each byte in the block:
      key_offset = byte_index % 14
      temp = encrypted_byte XOR key[key_offset]
      temp = ROL(temp, 1)
      plaintext = NOT(temp)
      key[key_offset] = (key[key_offset] + 1) & 0xFF
      byte_index += 1

  Key format: [0x0E, pw_char1, pw_char2, ..., pw_char13] (14 bytes)
  Key resets to initial state for each block AND each BMP.
  Password derived via known-plaintext attack on BMP headers.

Usage: python3 uncrypt.py <input_dir_or_file> [output_dir]
"""

import struct
import os
import sys

def ror8(val, count):
    count %= 8
    return ((val >> count) | (val << (8 - count))) & 0xFF

def rol8(val, count):
    count %= 8
    return ((val << count) | (val >> (8 - count))) & 0xFF

# Known bytes in a standard 8-bit BMP header (BITMAPINFOHEADER, biClrUsed=0)
# These positions have fixed/predictable values we can use for key derivation
KNOWN_BYTES_8BIT = {
    0: 0x42,   # 'B' signature
    1: 0x4D,   # 'M' signature
    6: 0x00,   # reserved
    7: 0x00,   # reserved
    8: 0x00,   # reserved
    9: 0x00,   # reserved
    10: 0x36,  # bfOffBits low byte (1078 = 14 + 40 + 256*4)
    11: 0x04,  # bfOffBits byte 2
    12: 0x00,  # bfOffBits byte 3
    13: 0x00,  # bfOffBits byte 4
    14: 0x28,  # biSize = 40 (BITMAPINFOHEADER)
    15: 0x00,  # biSize byte 2
    16: 0x00,  # biSize byte 3
    17: 0x00,  # biSize byte 4
    26: 0x01,  # biPlanes = 1
    27: 0x00,  # biPlanes high
    28: 0x08,  # biBitCount = 8
    29: 0x00,  # biBitCount high
    30: 0x00,  # biCompression = 0 (BI_RGB)
    31: 0x00,  # biCompression byte 2
    32: 0x00,  # biCompression byte 3
    33: 0x00,  # biCompression byte 4
}

def derive_key(enc_data, known_bytes=KNOWN_BYTES_8BIT):
    """Derive the 14-byte key from known BMP header plaintext bytes."""
    key = [None] * 14
    for pos in sorted(known_bytes.keys()):
        if pos >= len(enc_data):
            continue
        byte_index = pos + 1
        key_offset = byte_index % 14
        # Count how many times this key position was used before this byte
        uses_before = sum(1 for ep in range(pos) if (ep + 1) % 14 == key_offset)
        plain = known_bytes[pos]
        not_plain = (~plain) & 0xFF
        rotated = ror8(not_plain, 1)
        used_key = enc_data[pos] ^ rotated
        original = (used_key - uses_before) & 0xFF
        if key[key_offset] is None:
            key[key_offset] = original
        elif key[key_offset] != original:
            return None  # Inconsistent - wrong assumptions
    return key

BLOCK_SIZE = 4096

def decrypt_block(data, key_buf):
    """Decrypt a single block (up to 4096 bytes) with the given key.

    The key evolves during decryption but the caller's copy is unaffected
    (matches decode.exe behavior where func_0758 copies key to local buffer).
    """
    key = list(key_buf)
    result = bytearray(len(data))
    for i in range(len(data)):
        byte_index = i + 1
        key_offset = byte_index % 14
        key_byte = key[key_offset]
        xored = data[i] ^ key_byte
        rotated = rol8(xored, 1)
        result[i] = (~rotated) & 0xFF
        key[key_offset] = (key_byte + 1) & 0xFF
    return bytes(result)

def decrypt_data(data, key_buf):
    """Decrypt CRYPTON Mode 1 encrypted data in 4096-byte blocks.

    Matches decode.exe wrapper function (0xB8F) which:
    1. Reads 4096-byte blocks from the encrypted file
    2. Calls func_0758 for each block with the SAME initial key
       (func_0758 copies key to local buffer, so caller's key is unchanged)
    3. byte_index resets to 1 for each block

    Since 4096 % 14 = 8, key position cycling is NOT aligned across blocks,
    so the key MUST reset per block to produce correct results.
    """
    result = bytearray()
    offset = 0
    while offset < len(data):
        block = data[offset:offset + BLOCK_SIZE]
        result.extend(decrypt_block(block, key_buf))
        offset += BLOCK_SIZE
    return bytes(result)

def is_crypton_file(path):
    """Check if a file is a CRYPTON encrypted file."""
    try:
        with open(path, 'rb') as f:
            header = f.read(72)
        return b'CRYPTON' in header and b'ISICOM' in header
    except:
        return False

def parse_metadata(data):
    """Parse CRYPTON file metadata from the 606-byte header."""
    info = {}
    # Mode byte at offset 0x100
    info['mode'] = data[0x100]
    # PCL identifier at offset 0x104 (Pascal string)
    pcl_len = data[0x104]
    if pcl_len > 0 and pcl_len <= 20:
        info['pcl'] = data[0x105:0x105 + pcl_len].decode('ascii', errors='replace')
    return info

def process_file(filepath, output_dir, verbose=True):
    """Process a single .cpt or .lcr file: derive key, decrypt all BMPs."""
    basename = os.path.splitext(os.path.basename(filepath))[0]

    with open(filepath, 'rb') as f:
        filedata = f.read()

    if len(filedata) < 660:
        return None, "File too small"

    # Verify it's a CRYPTON file
    if b'CRYPTON' not in filedata[:72]:
        return None, "Not a CRYPTON file"

    metadata = parse_metadata(filedata)
    enc_start = filedata[606:]

    # Derive key from known plaintext
    key = derive_key(enc_start)
    if key is None or any(k is None for k in key):
        return None, "Could not derive key from known plaintext"

    # Verify by decrypting first 2 bytes
    dec_test = decrypt_data(enc_start[:2], key)
    if dec_test[0:2] != b'BM':
        return None, "Key verification failed - first bytes don't decode to BM"

    # Extract password
    pw_bytes = bytes(key[1:14])
    try:
        password = pw_bytes.decode('ascii')
    except:
        password = pw_bytes.hex()

    # Extract all BMPs
    pos = 606
    bmps = []
    bmp_idx = 0

    while pos < len(filedata):
        remaining = len(filedata) - pos
        if remaining < 54:
            break

        # Decrypt header to get BMP file size
        dec_hdr = decrypt_data(filedata[pos:pos + 6], key)
        if dec_hdr[0:2] != b'BM':
            break

        file_size = struct.unpack('<I', dec_hdr[2:6])[0]
        if file_size < 54 or file_size > remaining:
            break

        # Decrypt full BMP
        enc_bmp = filedata[pos:pos + file_size]
        decrypted = decrypt_data(enc_bmp, key)

        # Parse BMP dimensions
        width = struct.unpack('<I', decrypted[18:22])[0]
        height = struct.unpack('<I', decrypted[22:26])[0]
        bpp = struct.unpack('<H', decrypted[28:30])[0]

        # Use original filename from metadata if available, else generate one
        out_name = f'bmp{bmp_idx + 1}.bmp'
        out_path = os.path.join(output_dir, out_name)

        with open(out_path, 'wb') as f:
            f.write(decrypted)

        bmps.append({
            'index': bmp_idx + 1,
            'offset': pos,
            'size': file_size,
            'width': width,
            'height': height,
            'bpp': bpp,
            'path': out_path,
        })

        pos += file_size
        bmp_idx += 1

    return {
        'password': password,
        'key': key,
        'metadata': metadata,
        'bmps': bmps,
    }, None

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 uncrypt.py <input_dir_or_file> [output_dir]")
        print()
        print("Decrypts CRYPTON .cpt and .lcr files (ISICOM 1995)")
        print("Passwords are derived automatically via known-plaintext attack.")
        sys.exit(1)

    input_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(input_path), 'decrypted')

    os.makedirs(output_dir, exist_ok=True)

    # Collect files to process
    if os.path.isfile(input_path):
        files = [input_path]
    elif os.path.isdir(input_path):
        files = sorted([
            os.path.join(input_path, f)
            for f in os.listdir(input_path)
            if f.lower().endswith(('.cpt', '.lcr'))
        ])
    else:
        print(f"Error: {input_path} is not a file or directory")
        sys.exit(1)

    if not files:
        print(f"No .cpt or .lcr files found in {input_path}")
        sys.exit(1)

    print(f"CRYPTON Decoder - Processing {len(files)} file(s)")
    print(f"Output: {output_dir}")
    print("=" * 70)

    total_bmps = 0
    total_bytes = 0
    failed = 0

    for filepath in files:
        fname = os.path.basename(filepath)
        result, error = process_file(filepath, output_dir)

        if error:
            print(f"FAIL  {fname}: {error}")
            failed += 1
            continue

        print(f"OK    {fname}  password=\"{result['password']}\"")
        for bmp in result['bmps']:
            print(f"      BMP{bmp['index']}: {bmp['width']}x{bmp['height']} "
                  f"{bmp['bpp']}bpp ({bmp['size']:,} bytes)")
            total_bmps += 1
            total_bytes += bmp['size']

    print("=" * 70)
    print(f"Done: {total_bmps} BMPs ({total_bytes:,} bytes) from "
          f"{len(files) - failed}/{len(files)} files")
    if failed:
        print(f"Failed: {failed} file(s)")

if __name__ == '__main__':
    main()
