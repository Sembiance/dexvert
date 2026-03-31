#!/usr/bin/env python3
# Vibe coded by Claude
"""unmacromind.py - Extract resources from MacroMind Director MacBinary files.

Handles MacBinary II wrapped MacroMind/Macromedia Director (VWMD) files
from the Mac OS 6-9 era (Director 3.x/4.x).

Usage: unmacromind.py [--verbose] <inputFile> <outputDir>
"""

import sys
import os
import struct
import json
import zlib
import argparse
import wave
import io
from collections import namedtuple

# ============================================================================
# Constants
# ============================================================================

# Mac epoch: Jan 1, 1904 00:00:00 UTC; Unix epoch: Jan 1, 1970
MAC_EPOCH_OFFSET = 2082844800

CAST_TYPE_NAMES = {
    1: 'bitmap', 2: 'filmloop', 3: 'text', 4: 'palette', 5: 'picture',
    6: 'sound', 7: 'button', 8: 'shape', 9: 'movie', 10: 'digitalvideo',
    11: 'script',
}

VWCI_STRING_NAMES = ['script', 'name', 'cProp03', 'cProp04', 'cProp05',
                     'cProp06', 'cProp07', 'cProp08', 'cProp09', 'cProp10',
                     'cProp11', 'cProp12', 'cProp13', 'cProp14', 'cProp15',
                     'cProp16', 'cProp17', 'cProp18', 'cProp19', 'cProp20',
                     'cProp21', 'cProp22']

VWFI_STRING_NAMES = ['script', 'name', 'directory', 'fileName', 'fileType',
                     'comment', 'copyright']

Resource = namedtuple('Resource', ['type', 'id', 'name', 'attributes', 'data'])


# ============================================================================
# Mac System Palette (256 colors)
# ============================================================================

def mac_system_palette():
    """Generate the Director/Macintosh 256-color system palette.

    Entries 0-214: 6x6x6 color cube (white to near-black, omitting pure black).
    Entries 215-224: red ramp. Entries 225-234: green ramp.
    Entries 235-244: blue ramp. Entries 245-254: grayscale ramp.
    Entry 255: black.
    Source: ScummVM Director engine (macPalette / kClutSystemMac).
    """
    pal = []
    ramp6 = [0xFF, 0xCC, 0x99, 0x66, 0x33, 0x00]
    # Entries 0-215 from cube, but pop the last one (pure black at index 215)
    for r in ramp6:
        for g in ramp6:
            for b in ramp6:
                pal.append((r, g, b))
    pal.pop()  # Remove (0,0,0); black goes to entry 255 instead
    ramp10 = [0xEE, 0xDD, 0xBB, 0xAA, 0x88, 0x77, 0x55, 0x44, 0x22, 0x11]
    # Entries 215-224: red ramp
    for v in ramp10:
        pal.append((v, 0, 0))
    # Entries 225-234: green ramp
    for v in ramp10:
        pal.append((0, v, 0))
    # Entries 235-244: blue ramp
    for v in ramp10:
        pal.append((0, 0, v))
    # Entries 245-254: grayscale ramp
    for v in ramp10:
        pal.append((v, v, v))
    # Entry 255: black
    pal.append((0, 0, 0))
    return pal

MAC_PALETTE = mac_system_palette()


def _bytes_to_palette(raw):
    """Convert raw bytes (R,G,B triplets) to list of (R,G,B) tuples."""
    return [(raw[i], raw[i+1], raw[i+2]) for i in range(0, len(raw), 3)]

# Built-in Director palettes from ScummVM (kClutSystemMac=-1, kClutRainbow=-2, etc.)
_BUILTIN_256 = {
    -1: MAC_PALETTE,
    -2: _bytes_to_palette(bytes.fromhex(
        'ffffff0069ff0063ff005dff0056ff0050ff004aff0043ff003dff0036ff0030ff002aff0023ff001dff0017ff0010ff000aff0003ff0600ff0c00ff'
        '1300ff1900ff1f00ff2600ff2c00ff3300ff3900ff3f00ff4600ff4c00ff5200ff5900ff5f00ff6600ff6c00ff7200ff7900ff7f00ff8500ff8c00ff'
        '9200ff9900ff9f00ffa500ffac00ffb200ffb800ffbf00ffc500ffcc00ffd200ffd800ffdf00ffe500ffeb00fff200fff800ffff00ffff00f8ff00f2'
        'ff00ebff00e5ff00dfff00d8ff00d2ff00ccff00c5ff00bfff00b8ff00b2ff00acff00a5ff009fff0099ff0092ff008cff0085ff007fff0079ff0072'
        'ff006cff0066ff005fff0059ff0052ff004cff0046ff003fff0039ff0033ff002cff0026ff001fff0019ff0013ff000cff0006ff0000ff0600ff0c00'
        'ff1300ff1900ff1f00ff2600ff2c00ff3300ff3900ff3f00ff4600ff4c00ff5200ff5900ff5f00ff6600ff6c00ff7200ff7900ff7f00ff8500ff8c00'
        'ff9200ff9900ff9f00ffa500ffac00ffb200ffb800ffbf00ffc500ffcc00ffd200ffd800ffdf00ffe500ffeb00fff200fff800ffff00f8ff00f2ff00'
        'ebff00e5ff00dfff00d8ff00d2ff00ccff00c5ff00bfff00b8ff00b2ff00acff00a5ff009fff0099ff0092ff008cff0085ff007fff0079ff0072ff00'
        '6cff0066ff005fff0059ff0052ff004cff0046ff003fff0039ff0033ff002cff0026ff001fff0019ff0013ff000cff0006ff0000ff0000ff0600ff0c'
        '00ff1300ff1900ff1f00ff2600ff2c00ff3300ff3900ff3f00ff4600ff4c00ff5200ff5900ff5f00ff6600ff6c00ff7200ff7900ff7f00ff8500ff8c'
        '00ff9200ff9900ff9f00ffa500ffac00ffb200ffb800ffbf00ffc500ffcc00ffd200ffd800ffdf00ffe500ffeb00fff200fff800ffff00f8ff00f2ff'
        '00ebff00e5ff00dfff00d8ff00d2ff00ccff00c5ff00bfff00b8ff00b2ff00acff00a5ff009fff0099ff0092ff008cff0085ff007fff0079ff0072ff'
        'f0f0f0e0e0e0d0d0d0c0c0c0b0b0b0a0a0a0909090808080707070606060505050404040303030202020101010000000')),
    -3: _bytes_to_palette(bytes.fromhex(
        'fffffffefefefdfdfdfcfcfcfbfbfbfafafaf9f9f9f8f8f8f7f7f7f6f6f6f5f5f5f4f4f4f3f3f3f2f2f2f1f1f1f0f0f0efefefeeeeeeedededececec'
        'ebebebeaeaeae9e9e9e8e8e8e7e7e7e6e6e6e5e5e5e4e4e4e3e3e3e2e2e2e1e1e1e0e0e0dfdfdfdedededddddddcdcdcdbdbdbdadadad9d9d9d8d8d8'
        'd7d7d7d6d6d6d5d5d5d4d4d4d3d3d3d2d2d2d1d1d1d0d0d0cfcfcfcecececdcdcdcccccccbcbcbcacacac9c9c9c8c8c8c7c7c7c6c6c6c5c5c5c4c4c4'
        'c3c3c3c2c2c2c1c1c1c0c0c0bfbfbfbebebebdbdbdbcbcbcbbbbbbbababab9b9b9b8b8b8b7b7b7b6b6b6b5b5b5b4b4b4b3b3b3b2b2b2b1b1b1b0b0b0'
        'afafafaeaeaeadadadacacacabababaaaaaaa9a9a9a8a8a8a7a7a7a6a6a6a5a5a5a4a4a4a3a3a3a2a2a2a1a1a1a0a0a09f9f9f9e9e9e9d9d9d9c9c9c'
        '9b9b9b9a9a9a9999999898989797979696969595959494949393939292929191919090908f8f8f8e8e8e8d8d8d8c8c8c8b8b8b8a8a8a898989888888'
        '8787878686868585858484848383838282828181818080807f7f7f7e7e7e7d7d7d7c7c7c7b7b7b7a7a7a797979787878777777767676757575747474'
        '7373737272727171717070706f6f6f6e6e6e6d6d6d6c6c6c6b6b6b6a6a6a696969686868676767666666656565646464636363626262616161606060'
        '5f5f5f5e5e5e5d5d5d5c5c5c5b5b5b5a5a5a5959595858585757575656565555555454545353535252525151515050504f4f4f4e4e4e4d4d4d4c4c4c'
        '4b4b4b4a4a4a4949494848484747474646464545454444444343434242424141414040403f3f3f3e3e3e3d3d3d3c3c3c3b3b3b3a3a3a393939383838'
        '3737373636363535353434343333333232323131313030302f2f2f2e2e2e2d2d2d2c2c2c2b2b2b2a2a2a292929282828272727262626252525242424'
        '2323232222222121212020201f1f1f1e1e1e1d1d1d1c1c1c1b1b1b1a1a1a191919181818171717161616151515141414131313121212111111101010'
        '0f0f0f0e0e0e0d0d0d0c0c0c0b0b0b0a0a0a090909080808070707060606050505040404030303020202010101000000')),
    -4: _bytes_to_palette(bytes.fromhex(
        'fffffffefef2fefde6fefddafefccefefbc2fefbb6fefaaafdfa9dfdf991fdf885fdf879fdf76dfdf761fdf655fcf548fcee47fce747fce047fcd947'
        'fdd247fdcb47fdc447fdbe47fdb747feb047fea947fea247fe9b47fe9447ff8d46fd8846fb8446f97f46f87b47f67747f47247f36e47f16a48ef6548'
        'ee6148ec5d48ea5849e95449e75049e54b4ae24949df4748dc4548d94347d64147d43f46d13d46ce3b45cb3945c83744c63544c33343c03143bd2f42'
        'ba2d41be2f47c2314ec63355ca355bce3762d23969d63b70da3d76de3f7de24184e6438bea4591ee4798f2499ff64ba6ed4aa7e54aa9dc49aad449ac'
        'cc48adc348afbb48b0b347b2aa47b3a246b59a46b69146b88945b98145bb7844bd7444bf7144c16d44c46a44c66644c86344cb6044cd5c44cf5944d2'
        '5544d45244d64f44d94b44db4844dd4445e0444de14455e2445ee34466e4456ee54577e6457fe74587e84590e94698ea46a0eb46a9ec46b1ed46b9ee'
        '47c2f048c2e549c3db4bc3d04cc4c64ec5bb4fc5b150c6a752c69c53c79255c88756c87d57c97359c9685aca5e5ccb535ac75258c35257bf5255bb52'
        '54b75252b35251af524fab524ea7524ca3524b9f52499b52489752469352448f51488c504c894f50864f55844e59814e5d7e4d617b4d66794c6a764c'
        '6e734b72704b776e4a7b6b4a7f68498465488c6e489478489c8248a48b48ac9548b49f48bca848c4b248ccbc48d4c548dccf48e4d948ece248f4ec48'
        'fdf649fbea49f9df49f8d349f6c849f5bd49f3b149f2a649f09b49ef8f49ed8449ec7949ea6d49e96249e75749e54b4ae64b50e74b56e84b5ce94b62'
        'ea4b68eb4b6eec4b74ee4b7bef4b81f04b87f14b8df24b93f34b99f44b9ff64ba6ea4aa9de4aadd249b1c649b5ba48b9af48bda348c19747c48b47c8'
        '7f46cc7446d06846d45c45d85045dc4444e04f4fe15a5ae26666e37171e47d7de58888e69494e79f9fe8ababe9b6b6eac2c2ebcdcdecd9d9ede4e4ee'
        'f0f0f0e0e0e0d0d0d0c0c0c0b0b0b0a0a0a0909090808080707070606060505050404040303030202020101010000000')),
    -5: _bytes_to_palette(bytes.fromhex(
        'fffffffefeeefefdddfefcccfefbbcfdfaabfdfa9afdf98afdf879fdf768fcf658fcf647fcf536fcf426fcf315fbf204fbe803fbdf03fbd503fccc03'
        'fcc203fcb903fcaf03fda602fd9c02fd9302fd8902fe8002fe7602fe6d02ff6301fc5c01fa5601f85002f54a02f34402f13e03ef3803ec3203ea2c04'
        'e82604e62004e31a05e11405df0e05dc0706d80607d50608d20509ce050acb040cc8040dc5030ec1030fbe0210bb0212b80113b40114b10015ae0016'
        'aa0018ae001fb30126b8012dbd0234c2023cc60343cb034ad00451d50458da0560de0567e3066ee80675ed077cf20884e60786db0688cf068ac4058c'
        'b8058fad0491a104939603958a03977f029a73029c68019e5c01a05100a24500a54000a83b00ab3700ae3200b12d00b42900b72400ba2000be1b00c1'
        '1600c41200c70d00ca0900cd0400d00000d4000bd50016d60022d8002dd90039db0044dc004fde015bdf0166e10172e2017de40188e50194e7019fe8'
        '02abea03abdb05accd07adbf09aeb00bafa20daf940fb08611b17713b26915b35b17b34d19b43e1bb5301db6221fb7131cb1121aab1218a61216a012'
        '149b121295121090120e8a110c85110a7f11087a11067411046f11026911006310055f0f0b5b0e11570d16540d1c500c224c0b28490a2d450a334109'
        '393e083f3a074436074a3306502f05562b046138046c45047753048260048d6d04987b04a38804ae9504b9a304c4b004cfbd04dacb04e5d804f0e504'
        'fcf305f9e305f7d305f5c305f3b405f1a405ef9405ed8505eb7505e96505e75605e54605e33605e12705df1705dc0706dd070ede0716e0071fe10727'
        'e30730e40738e60740e70749e90751ea075aec0762ed076aef0773f0077bf20884e10789d1068ec10694b10599a1059e9104a48104a97003ae6003b4'
        '5002b94002be3001c42001c91000ce0000d41010d52020d73030d94040db5050dd6060df7070e18080e29090e4a0a0e6b0b0e8c0c0ead0d0ece0e0ee'
        'f0f0f0e0e0e0d0d0d0c0c0c0b0b0b0a0a0a0909090808080707070606060505050404040303030202020101010000000')),
    -6: _bytes_to_palette(bytes.fromhex(
        'ffffff592b855d215f7b28529a3044a13d42a54341a9473eac4b3ab04f37b45333ba6635c17a36c88d37cfa139d5b53adcc93be3dd3cc6d438acce37'
        '93c83579c33360bd3146b72f2db12d279a3c2183491b6c55195b652158842952a3304bc21cc2d526c3d530c4d53bc5d545c6d54fc7d559c8d563c9d5'
        '6dcad577cbd581ccd58bcdd595ced59fcfd5a9d0d5b3d1d5b1f2b9a5f0ad9aefa18eed9482ec8876ea7c6be8705fe76353e55747e44b3be23f30e032'
        '24df2618dd1a0cdc0e01da0101c80100bb0100ae0100a001009301008501007800006b00005d00005000004200003500002800001a00000d00000000'
        '0a09001615012221022e2d023a39034644045250055e5c056a68067774078380088f8b089b9709a7a30ab3af0bbfbb0bc5c00cc8c415cbc71dcfca26'
        'd2cd2fd5d038d8d341dbd64adfd952e2dc5be5df64e8e26debe576efe87ff2eb87f5ee90d9afa1d9a998d9a28fd99c87d9957ed98f76d9886dd98265'
        'd97b5cd97553d96e4bd96842d9613ad95b31d95429d94e20d94a1bcb4519bc4017ae3b169f3614913112822c1074270e65220c571d0b4818093a1307'
        '2b0e051d09030e05010000000000000b000217000417030622040a2e060d390710450914510b175c0c1a680e1e730f217f11258b132896142ba2162f'
        'a2162fb10b2ab51735b9223fbd2e4ac13955c44560c8506bcc5c76d06781d4738cd77e97db8aa2df95ade3a1b8e7adc3c9aaf0c3a1efbe97edb98deb'
        'b384e9ae7ae8a870e6a367e49e5de39853e1934adf8d40dd8836dc832dda7d23d87819d7750fd76d0ec9660dbc5f0cae570ba1500a93490986410878'
        '3a076b32065d2b05502404421c03351502270e011a06000c000416000623000830000b3d000d4a00105700126400147100177e00198b001c98001ea5'
        '0020b20023bf0025cc0027d90029e30f36e41d42e52c4fe63b5be64a67e75974e86880e9778ce98699ea95a5eba4b2ecb3beecc2caedd1d7eee0e3ef'
        'f0f0f0e0e0e0d0d0d0c0c0c0b0b0b0a0a0a0909090808080707070606060505050404040303030202020101010000000')),
    -7: _bytes_to_palette(bytes.fromhex(
        'ffffff664c805f426c58375975475e9458639b66699f6c6aa36d68a66f66aa7365ae7967b4866bbb946fc2a273c9b077d0be7bddda83c7ce7bb6c877'
        'a6c37496bd7085b76d76b16966ab665894634a7d5f385a5f4361764e678e586da56373bc442a5c4e3566583f6f624a796c5582765f8c806a958a759f'
        '947fa89e8ab2a894bbb29fc4bcaacec6b4d7d0bfe1dacaeae4d4f4dac9eacfbee0c4b2d6b9a7cbaf9cc1a490b79985ad8f7aa3846e9979638f6f5885'
        '644c7b5941714e3667442a5c51201f5c2b2b6737377242427d4d4e8758599263659d6e71a8797cb38488be9094c99b9fd4a6abdfb1b7eabcc2f5c7ce'
        'ffd2daf4c6cde8bbc1ddafb4d1a3a8c5979bba8b8fae7f83a2737697676a8b5c5d7f50517444456838385d2c2c51201f4426194f3122593b2c644636'
        '6f5140795b498466538e715d997b66a48670ae917ab99b83c3a68dceb197d9bba1e3c6aaeed1b4e3c3a5d7b89bccac91c1a187b5967daa8b739f8069'
        '93745f8869557d5e4b7153416648375b3c2d4f3123442619765512805d1c8a6626936e2f9d7739a77f43b1884cbb9156c5995fcea269d8aa73e2b37c'
        'ecbb86f6c48fffcc99ffd5abffe1c2ffd8b1f6c48fecbb86e2b37cd8aa73cea269c5995fbb9156b1884ca77f439d7739936e2f8a6626805d1c765512'
        '0330030f3d0f1a4a1a2657263164313d713d497e49548b546098606ba56b77b27782bf838ecc8e9ad99aa5e6a5b1f2b1bcffbcb0f2b0a4e4a497d697'
        '8bc88b7fba7f72ad72669f665a915a4d834d417541346735285a281c4c1c0f3e10033003000f550d1d601b2a6a29377537458045528a535f95616da0'
        '6f7aaa7d87b58a95c098a2caa6afd5b4bde0c2caead0d7f5dee5ffcfd6f4c0c8e9b1badda3acd2949dc7858fbb7681b06773a55865994a568e3b4883'
        '2c3a771d2c6c0e1e61000f551111112020202f2f2f3e3e3e4d4d4d5c5c5c6a6a6a797979888888979797a6a6a6b5b5b5c4c4c4d3d3d3e2e2e2f1f1f1'
        'ffffffeeeeeeddddddccccccbbbbbbaaaaaa999999888888777777666666555555444444333333222222111111000000')),
}

# 16-color variants for 4-bit bitmaps
_BUILTIN_16 = {
    -1: _bytes_to_palette(bytes.fromhex('fffffffcf305ff6402dd0806f208844600a50000d402abea1fb714006411562c0590713ac0c0c0808080404040000000')),
    -2: _bytes_to_palette(bytes.fromhex('ffffff000aff5f00ffc500ffff00d2ff006cff0006ff5f00ffc500d2ff006cff0006ff0000ff5f00ffc500d2ff000000')),
    -3: _bytes_to_palette(bytes.fromhex('ffffffeeeeeeddddddccccccbababaa9a9a99898988787877676766565655454544343433131312020200f0f0f000000')),
    -4: _bytes_to_palette(bytes.fromhex('fffffffdbe47ef6548c83744e6438b9146b84b44db46b9ee5ccb53488c50947848f8d349e94b62ba48b98888e6000000')),
    -5: _bytes_to_palette(bytes.fromhex('fffffffccc03f34402c8040dcb034a9603951b00c10172e217b34d0674114a3306f0e504dc0706e107892020d7000000')),
    -6: _bytes_to_palette(bytes.fromhex('ffffffbebebeffe600808080562c057c601b009e00006411de00bf4600a5fa0039ff8c320000ea02abea646464000000')),
    -7: _bytes_to_palette(bytes.fromhex('ffffff00ffffff00ff0000ffffff0000ff00ff00007f7f7fbfbfbf007f7f7f007f00007f7f7f00007f007f0000000000')),
}

MAC_16_PALETTE = _BUILTIN_16[-1]


def _match_builtin_16(pal_256):
    """If pal_256 closely matches a built-in 256-color palette, return its 16-color variant."""
    best_id, best_count = None, 0
    for pid, bp in _BUILTIN_256.items():
        count = sum(1 for a, b in zip(pal_256, bp) if a == b)
        if count > best_count:
            best_count = count
            best_id = pid
    if best_count >= 200:
        return _BUILTIN_16.get(best_id)
    return None


def resolve_palette(clut_id, bpp, clut_palettes, cast_id_offset, movie_palette_256,
                    movie_palette_16):
    """Resolve the correct palette for a bitmap given its clut_id and bpp.

    movie_palette_256/16 = the file's movie default palette (from its CLUTs)
    or MAC_PALETTE/MAC_16_PALETTE if the file has no suitable movie palette.
    """
    use_16 = (bpp <= 4)

    if clut_id > 0:
        # Positive: cast member index referencing a CLUT
        pal = clut_palettes.get(clut_id)
        if pal is None:
            abs_id = clut_id + cast_id_offset
            pal = clut_palettes.get(abs_id)
        if pal is not None:
            if use_16 and len(pal) > 16:
                matched = _match_builtin_16(pal)
                return matched if matched else pal[:16]
            return pal
        # Referenced CLUT not found (external cast?) - fall back to movie palette
        return movie_palette_16 if use_16 else movie_palette_256

    if clut_id < 0:
        # Negative: built-in palette type. If the file has a movie palette CLUT,
        # use it (the bitmap was indexed against the file's palette, which was
        # loaded into this built-in slot). Only use the generic built-in when
        # the file has no movie palette.
        if movie_palette_256 is not MAC_PALETTE:
            return movie_palette_16 if use_16 else movie_palette_256
        # Director 3.x VWCR stores built-in palette IDs offset by +1 from
        # ScummVM's PaletteType enum: VWCR -1=Rainbow, -2=Grayscale, etc.
        # but our _BUILTIN dicts use ScummVM keys: -2=Rainbow, -3=Grayscale.
        # Subtract 1 to convert from VWCR numbering to dict keys.
        key = clut_id - 1
        if use_16:
            return _BUILTIN_16.get(key, MAC_16_PALETTE)
        return _BUILTIN_256.get(key, MAC_PALETTE)

    # clut_id == 0: movie default
    return movie_palette_16 if use_16 else movie_palette_256


def scan_sibling_cluts(input_file):
    """Scan sibling MacBinary files for CLUT resources.

    Returns a dict mapping resource_id -> palette (list of (R,G,B) tuples).
    Files named 'Shared Cast*' are scanned first for priority.
    """
    parent_dir = os.path.dirname(os.path.abspath(input_file))
    my_name = os.path.basename(os.path.abspath(input_file))
    sibling_cluts = {}

    # Collect siblings, prioritizing 'Shared Cast' files
    siblings = []
    for fn in os.listdir(parent_dir):
        if fn == my_name:
            continue
        fp = os.path.join(parent_dir, fn)
        if not os.path.isfile(fp):
            continue
        is_shared = fn.lower().startswith('shared cast')
        siblings.append((not is_shared, fn, fp))  # shared casts sort first
    siblings.sort()

    for _, fn, fp in siblings:
        try:
            with open(fp, 'rb') as f:
                raw = f.read()
            mb = parse_macbinary(raw)
            if mb is None:
                continue
            resources = parse_resource_fork(mb['resource_fork'])
            for r in resources:
                if r.type in ('CLUT', 'clut') and r.id not in sibling_cluts:
                    pal = decode_clut(r.data)
                    if pal:
                        sibling_cluts[r.id] = pal
        except Exception:
            continue
    return sibling_cluts


# ============================================================================
# PNG Writer (zero dependencies)
# ============================================================================

def _png_chunk(chunk_type, data):
    """Build a PNG chunk: length + type + data + CRC."""
    body = chunk_type + data
    return struct.pack('>I', len(data)) + body + struct.pack('>I', zlib.crc32(body) & 0xFFFFFFFF)


def write_png_indexed(path, width, height, pixels, palette):
    """Write an indexed-color (palette) PNG. pixels: width*height bytes."""
    sig = b'\x89PNG\r\n\x1a\n'
    ihdr = struct.pack('>IIBBBBB', width, height, 8, 3, 0, 0, 0)
    plte = b''.join(bytes(c) for c in palette)
    raw = b''
    for y in range(height):
        raw += b'\x00' + pixels[y * width:(y + 1) * width]
    with open(path, 'wb') as f:
        f.write(sig)
        f.write(_png_chunk(b'IHDR', ihdr))
        f.write(_png_chunk(b'PLTE', plte))
        f.write(_png_chunk(b'IDAT', zlib.compress(raw)))
        f.write(_png_chunk(b'IEND', b''))


def write_png_grayscale(path, width, height, pixels):
    """Write a grayscale PNG. pixels: width*height bytes."""
    sig = b'\x89PNG\r\n\x1a\n'
    ihdr = struct.pack('>IIBBBBB', width, height, 8, 0, 0, 0, 0)
    raw = b''
    for y in range(height):
        raw += b'\x00' + pixels[y * width:(y + 1) * width]
    with open(path, 'wb') as f:
        f.write(sig)
        f.write(_png_chunk(b'IHDR', ihdr))
        f.write(_png_chunk(b'IDAT', zlib.compress(raw)))
        f.write(_png_chunk(b'IEND', b''))


def write_png_rgb(path, width, height, pixels):
    """Write an RGB PNG. pixels: width*height*3 bytes (R,G,B repeating)."""
    sig = b'\x89PNG\r\n\x1a\n'
    ihdr = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
    stride = width * 3
    raw = b''
    for y in range(height):
        raw += b'\x00' + pixels[y * stride:(y + 1) * stride]
    with open(path, 'wb') as f:
        f.write(sig)
        f.write(_png_chunk(b'IHDR', ihdr))
        f.write(_png_chunk(b'IDAT', zlib.compress(raw)))
        f.write(_png_chunk(b'IEND', b''))


# ============================================================================
# MacBinary II Parser
# ============================================================================

def parse_macbinary(data):
    """Parse a MacBinary II file. Returns dict with header info + forks."""
    if len(data) < 128:
        raise ValueError('File too small for MacBinary header')
    if data[0] != 0:
        raise ValueError(f'Invalid MacBinary: byte 0 is {data[0]:#x}, expected 0x00')

    name_len = data[1]
    if name_len == 0 or name_len > 63:
        raise ValueError(f'Invalid MacBinary: filename length {name_len}')

    filename = data[2:2 + name_len].decode('mac_roman', errors='replace')
    file_type = data[65:69].decode('mac_roman', errors='replace')
    creator = data[69:73].decode('mac_roman', errors='replace')
    flags_high = data[73]
    flags_low = data[101]
    data_fork_len = struct.unpack_from('>I', data, 83)[0]
    res_fork_len = struct.unpack_from('>I', data, 87)[0]
    creation_date = struct.unpack_from('>I', data, 91)[0]
    modification_date = struct.unpack_from('>I', data, 95)[0]
    mb_version = data[122]
    mb_min_version = data[123]
    crc = struct.unpack_from('>H', data, 124)[0]

    # Data fork starts at offset 128
    df_start = 128
    df_end = df_start + data_fork_len
    # Resource fork starts after data fork, padded to 128-byte boundary
    rf_start = df_start + ((data_fork_len + 127) // 128) * 128
    rf_end = rf_start + res_fork_len

    if rf_end > len(data):
        raise ValueError(f'Resource fork extends past EOF: need {rf_end}, have {len(data)}')

    header_info = {
        'filename': filename,
        'file_type': file_type,
        'creator': creator,
        'flags_high': flags_high,
        'flags_low': flags_low,
        'data_fork_length': data_fork_len,
        'resource_fork_length': res_fork_len,
        'creation_date_mac': creation_date,
        'modification_date_mac': modification_date,
        'macbinary_version': mb_version,
        'macbinary_min_version': mb_min_version,
        'crc': crc,
    }

    return {
        'header': header_info,
        'data_fork': data[df_start:df_end],
        'resource_fork': data[rf_start:rf_end],
    }


# ============================================================================
# Apple Resource Fork Parser
# ============================================================================

def parse_resource_fork(data):
    """Parse a Mac resource fork. Returns list of Resource namedtuples."""
    if len(data) < 16:
        raise ValueError('Resource fork too small')

    res_data_offset = struct.unpack_from('>I', data, 0)[0]
    res_map_offset = struct.unpack_from('>I', data, 4)[0]
    res_data_length = struct.unpack_from('>I', data, 8)[0]
    res_map_length = struct.unpack_from('>I', data, 12)[0]

    if res_map_offset + res_map_length > len(data):
        raise ValueError('Resource map extends past end of fork')

    rmap = data[res_map_offset:]

    # Resource map header
    # 16 bytes: copy of fork header
    # 4 bytes: next resource map handle (reserved)
    # 2 bytes: file reference number (reserved)
    # 2 bytes: resource fork attributes
    type_list_offset = struct.unpack_from('>H', rmap, 24)[0]  # from start of map
    name_list_offset = struct.unpack_from('>H', rmap, 26)[0]  # from start of map

    # Type list
    tlist = rmap[type_list_offset:]
    num_types = struct.unpack_from('>H', tlist, 0)[0] + 1  # stored as count-1

    resources = []
    offset = 2
    for _ in range(num_types):
        rtype = tlist[offset:offset + 4].decode('mac_roman', errors='replace')
        num_res = struct.unpack_from('>H', tlist, offset + 4)[0] + 1  # stored as count-1
        ref_list_offset = struct.unpack_from('>H', tlist, offset + 6)[0]
        offset += 8

        # Reference list entries (12 bytes each)
        rlist = tlist[ref_list_offset:]
        for i in range(num_res):
            entry_off = i * 12
            res_id = struct.unpack_from('>h', rlist, entry_off)[0]  # signed int16
            name_offset_in_list = struct.unpack_from('>h', rlist, entry_off + 2)[0]  # -1 = no name
            attrs_and_data = struct.unpack_from('>I', rlist, entry_off + 4)[0]
            res_attrs = (attrs_and_data >> 24) & 0xFF
            res_data_off = attrs_and_data & 0x00FFFFFF

            # Resource name
            res_name = None
            if name_offset_in_list >= 0:
                nlist = rmap[name_list_offset:]
                if name_offset_in_list < len(nlist):
                    nlen = nlist[name_offset_in_list]
                    res_name = nlist[name_offset_in_list + 1:name_offset_in_list + 1 + nlen].decode(
                        'mac_roman', errors='replace')

            # Resource data
            abs_data_off = res_data_offset + res_data_off
            if abs_data_off + 4 <= len(data):
                rdata_len = struct.unpack_from('>I', data, abs_data_off)[0]
                rdata = data[abs_data_off + 4:abs_data_off + 4 + rdata_len]
            else:
                rdata = b''

            resources.append(Resource(
                type=rtype, id=res_id, name=res_name,
                attributes=res_attrs, data=rdata
            ))

    return resources


# ============================================================================
# Director Resource Parsers
# ============================================================================

def parse_vwcf(data):
    """Parse VideoWorks Config (VWCF) resource."""
    if len(data) < 30:
        return {'error': 'VWCF too short', 'raw_hex': data.hex()}

    result = {
        'data_size': struct.unpack_from('>H', data, 0)[0],
        'version': struct.unpack_from('>H', data, 2)[0],
        'stage_top': struct.unpack_from('>h', data, 4)[0],
        'stage_left': struct.unpack_from('>h', data, 6)[0],
        'stage_bottom': struct.unpack_from('>h', data, 8)[0],
        'stage_right': struct.unpack_from('>h', data, 10)[0],
        'cast_array_start': struct.unpack_from('>h', data, 12)[0],
        'cast_array_end': struct.unpack_from('>h', data, 14)[0],
        'frame_rate': data[16],
        'light_switch': data[17],
    }
    result['stage_width'] = result['stage_right'] - result['stage_left']
    result['stage_height'] = result['stage_bottom'] - result['stage_top']

    if len(data) >= 48:
        result['comment_font'] = struct.unpack_from('>H', data, 20)[0]
        result['comment_size'] = struct.unpack_from('>H', data, 22)[0]
        result['comment_style'] = struct.unpack_from('>H', data, 24)[0]
        result['stage_color'] = struct.unpack_from('>H', data, 26)[0]
        result['bit_depth'] = struct.unpack_from('>H', data, 28)[0]

    return result


def parse_vwcr(data, cast_start, cast_end):
    """Parse VideoWorks Cast Record (VWCR) resource.
    Returns dict mapping cast_index -> record."""
    records = {}
    pos = 0

    for cast_idx in range(cast_start, cast_end + 1):
        if pos >= len(data):
            break
        size = data[pos]
        pos += 1
        if size == 0:
            continue  # empty cast slot

        rec_data = data[pos:pos + size]
        pos += size

        if len(rec_data) < 1:
            continue

        cast_type = rec_data[0]
        record = {
            'cast_type': cast_type,
            'cast_type_name': CAST_TYPE_NAMES.get(cast_type, f'unknown_{cast_type}'),
            'record_size': size,
        }

        if cast_type == 1 and len(rec_data) >= 22:  # bitmap
            # Layout: [0]castType [1]flags1 [2-3]_bytes [4-11]initialRect [12-19]boundingRect
            #         [20-21]regY [22-23]regX [24-25]bpp [26-27]clutId
            flags1 = rec_data[1]
            _bytes = struct.unpack_from('>H', rec_data, 2)[0]
            top, left, bottom, right = struct.unpack_from('>hhhh', rec_data, 4)
            btop, bleft, bbottom, bright = struct.unpack_from('>hhhh', rec_data, 12)
            reg_y, reg_x = struct.unpack_from('>hh', rec_data, 20)

            bpp = 1
            clut_id = 0
            if _bytes & 0x8000 and len(rec_data) >= 28:
                bpp = struct.unpack_from('>H', rec_data, 24)[0]
                clut_id = struct.unpack_from('>h', rec_data, 26)[0]

            record.update({
                'bytes_flag': _bytes,
                'initial_rect': [top, left, bottom, right],
                'bounding_rect': [btop, bleft, bbottom, bright],
                'reg_point': [reg_x, reg_y],
                'width': right - left,
                'height': bottom - top,
                'bits_per_pixel': bpp,
                'clut_id': clut_id,
            })

        elif cast_type == 3 and len(rec_data) >= 2:  # text
            if len(rec_data) >= 2:
                record['text_flags'] = rec_data[1]
            if len(rec_data) >= 16:
                record['text_rect'] = list(struct.unpack_from('>hhhh', rec_data, 2))
            if len(rec_data) >= 22:
                record['text_shadow'] = list(struct.unpack_from('>hhhh', rec_data, 10))

        elif cast_type == 6 and len(rec_data) >= 1:  # sound
            pass  # sound metadata comes from the snd resource itself

        elif cast_type == 7 and len(rec_data) >= 2:  # button
            record['button_type'] = rec_data[1] if len(rec_data) > 1 else 0

        elif cast_type == 8 and len(rec_data) >= 2:  # shape
            if len(rec_data) >= 18:
                record['shape_type'] = struct.unpack_from('>H', rec_data, 1)[0]
                record['shape_rect'] = list(struct.unpack_from('>hhhh', rec_data, 3))

        records[cast_idx] = record

    return records


def _parse_string_table(data, header_size=16):
    """Parse a Director string-table structure (used by VWCI, VWFI, etc.).
    Returns (header_fields, strings_dict)."""
    if len(data) < header_size + 2:
        return {}, {}

    unk1 = struct.unpack_from('>I', data, 0)[0]
    unk2 = struct.unpack_from('>I', data, 4)[0]
    flags = struct.unpack_from('>I', data, 8)[0]
    script_id = struct.unpack_from('>I', data, 12)[0]

    string_count = struct.unpack_from('>H', data, 16)[0]

    offsets = []
    p = 18
    for _ in range(string_count + 1):
        if p + 4 > len(data):
            break
        offsets.append(struct.unpack_from('>I', data, p)[0])
        p += 4

    string_data_start = p
    strings = {}
    for i in range(min(string_count, len(offsets) - 1)):
        start = offsets[i]
        end = offsets[i + 1]
        if start < end and string_data_start + end <= len(data):
            raw = data[string_data_start + start:string_data_start + end]
            strings[i] = raw

    header_fields = {
        'unk1': unk1, 'unk2': unk2, 'flags': flags,
        'script_id': script_id, 'string_count': string_count,
    }
    return header_fields, strings


def _decode_pascal_or_raw(raw):
    """Decode a byte string that may be Pascal-encoded (length-prefixed)."""
    if len(raw) > 1 and raw[0] == len(raw) - 1 and raw[0] < 128:
        return raw[1:].decode('mac_roman', errors='replace')
    return raw.decode('mac_roman', errors='replace')


def parse_vwci(data):
    """Parse VideoWorks Cast Info (VWCI) resource."""
    header, raw_strings = _parse_string_table(data)

    result = dict(header)
    strings = {}
    for idx, raw in raw_strings.items():
        field = VWCI_STRING_NAMES[idx] if idx < len(VWCI_STRING_NAMES) else f'string_{idx}'
        try:
            strings[field] = _decode_pascal_or_raw(raw)
        except Exception:
            strings[field] = raw.hex()
    result['strings'] = strings
    return result


def parse_vwfi(data):
    """Parse VideoWorks File Info (VWFI) resource."""
    header, raw_strings = _parse_string_table(data)

    result = dict(header)
    strings = {}
    for idx, raw in raw_strings.items():
        field = VWFI_STRING_NAMES[idx] if idx < len(VWFI_STRING_NAMES) else f'string_{idx}'
        try:
            strings[field] = _decode_pascal_or_raw(raw)
        except Exception:
            strings[field] = raw.hex()
    result['strings'] = strings
    return result


def parse_vwsc(data):
    """Parse VideoWorks Score (VWSC) resource. Returns header + frame summaries."""
    if len(data) < 20:
        return {'error': 'VWSC too short'}

    total_size = struct.unpack_from('>I', data, 0)[0]
    header_marker = struct.unpack_from('>I', data, 4)[0]
    frame_count_raw = struct.unpack_from('>I', data, 8)[0]
    unk01 = struct.unpack_from('>H', data, 12)[0]
    frame_size = struct.unpack_from('>H', data, 14)[0]
    channel_count = struct.unpack_from('>H', data, 16)[0]
    unk02 = struct.unpack_from('>H', data, 18)[0]

    # Determine main channel size (2x sprite channel size for D4)
    main_ch_size = frame_size * 2  # convention: first 2 "slots" are main channel

    channel_buf_size = channel_count * frame_size
    channel_buf = bytearray(channel_buf_size)

    frames = []
    pos = 20

    while pos + 2 <= len(data):
        channel_size = struct.unpack_from('>H', data, pos)[0]
        pos += 2

        if channel_size > 2:
            end_pos = pos + channel_size - 2
            while pos < end_pos:
                if pos + 4 > len(data):
                    break
                delta_size = struct.unpack_from('>H', data, pos)[0]
                delta_offset = struct.unpack_from('>h', data, pos + 2)[0]
                pos += 4
                if delta_size > 0 and pos + delta_size <= len(data):
                    if 0 <= delta_offset < channel_buf_size:
                        copy_len = min(delta_size, channel_buf_size - delta_offset)
                        channel_buf[delta_offset:delta_offset + copy_len] = data[pos:pos + copy_len]
                    pos += delta_size
                elif delta_size == 0:
                    break
                else:
                    break

        # Extract sprite cast IDs from this frame
        active_sprites = []
        for ch in range(2, channel_count):
            ch_off = ch * frame_size
            if ch_off + 16 <= channel_buf_size:
                if frame_size >= 8:
                    cast_id = struct.unpack_from('>H', channel_buf, ch_off + 6)[0]
                    if cast_id > 0:
                        sprite_y = struct.unpack_from('>h', channel_buf, ch_off + 8)[0]
                        sprite_x = struct.unpack_from('>h', channel_buf, ch_off + 10)[0]
                        sprite_h = struct.unpack_from('>h', channel_buf, ch_off + 12)[0]
                        sprite_w = struct.unpack_from('>h', channel_buf, ch_off + 14)[0]
                        ink = channel_buf[ch_off + 5] & 0x3F if frame_size > 5 else 0
                        active_sprites.append({
                            'channel': ch,
                            'cast_id': cast_id,
                            'x': sprite_x, 'y': sprite_y,
                            'width': sprite_w, 'height': sprite_h,
                            'ink': ink,
                        })

        # Main channel: extract tempo and sound info
        main_info = {}
        if channel_buf_size >= main_ch_size:
            if frame_size == 20:  # D4
                main_info['tempo'] = channel_buf[4]
                main_info['transition_type'] = channel_buf[5]
                main_info['sound1'] = struct.unpack_from('>H', channel_buf, 6)[0]
                main_info['sound2'] = struct.unpack_from('>H', channel_buf, 8)[0]
                main_info['script_id'] = struct.unpack_from('>H', channel_buf, 16)[0]
            elif frame_size == 16:  # D2/D3
                main_info['tempo'] = channel_buf[4]
                main_info['transition_type'] = channel_buf[5]
                main_info['sound1'] = struct.unpack_from('>H', channel_buf, 6)[0]
                main_info['sound2'] = struct.unpack_from('>H', channel_buf, 8)[0]

        frames.append({
            'frame': len(frames) + 1,
            'main': main_info,
            'sprites': active_sprites,
        })

    return {
        'total_size': total_size,
        'header_marker': header_marker,
        'frame_count_declared': frame_count_raw,
        'frame_count_decoded': len(frames),
        'frame_size': frame_size,
        'channel_count': channel_count,
        'frames': frames,
    }


def parse_vwac(data):
    """Parse VideoWorks Actions (VWAC) - Lingo script actions."""
    if len(data) < 2:
        return {'error': 'VWAC too short'}

    count = struct.unpack_from('>H', data, 0)[0]
    entries = []
    pos = 2

    for _ in range(count):
        if pos + 4 > len(data):
            break
        frame_id = data[pos]
        action_type = data[pos + 1]
        text_offset = struct.unpack_from('>H', data, pos + 2)[0]
        entries.append({
            'frame': frame_id,
            'type': action_type,
            'text_offset': text_offset,
        })
        pos += 4

    # Remaining data is script text
    text_data = data[pos:]
    all_text = text_data.decode('mac_roman', errors='replace')

    # Associate text snippets with entries using offsets
    for entry in entries:
        off = entry['text_offset']
        if off < len(text_data):
            # Find the end: next entry's offset or end of data
            end = len(text_data)
            for other in entries:
                if other['text_offset'] > off:
                    end = min(end, other['text_offset'])
            snippet = text_data[off:end].decode('mac_roman', errors='replace').rstrip('\x00')
            entry['script'] = snippet

    return {
        'count': count,
        'entries': entries,
        'full_text': all_text.rstrip('\x00'),
    }


def parse_vwfm(data):
    """Parse VideoWorks Font Map (VWFM) resource."""
    if len(data) < 2:
        return {'error': 'VWFM too short'}

    count = struct.unpack_from('>H', data, 0)[0]
    fonts = []
    pos = 2

    for _ in range(count):
        if pos + 2 > len(data):
            break
        font_id = struct.unpack_from('>H', data, pos)[0]
        pos += 2
        if pos >= len(data):
            break
        name_len = data[pos]
        pos += 1
        name = data[pos:pos + name_len].decode('mac_roman', errors='replace')
        pos += name_len
        fonts.append({'id': font_id, 'name': name})

    return {'count': count, 'fonts': fonts}


def parse_vwlb(data):
    """Parse VideoWorks Labels (VWLB) resource."""
    if len(data) < 2:
        return {'error': 'VWLB too short'}

    count = struct.unpack_from('>H', data, 0)[0]
    entries = []
    pos = 2

    label_offsets = []
    for _ in range(count):
        if pos + 4 > len(data):
            break
        frame_num = struct.unpack_from('>H', data, pos)[0]
        str_offset = struct.unpack_from('>H', data, pos + 2)[0]
        label_offsets.append((frame_num, str_offset))
        pos += 4

    # Label strings follow the table
    text_start = pos
    text_data = data[text_start:]

    for i, (frame_num, str_off) in enumerate(label_offsets):
        # End offset is next label's start or end of data
        if i + 1 < len(label_offsets):
            end_off = label_offsets[i + 1][1]
        else:
            end_off = len(text_data)
        label_text = text_data[str_off:end_off].decode('mac_roman', errors='replace').rstrip('\x00')
        entries.append({'frame': frame_num, 'label': label_text})

    return {'count': count, 'labels': entries}


# ============================================================================
# PackBits Decompressor
# ============================================================================

def decode_packbits(data, expected_size):
    """Decode PackBits-compressed data. Returns decompressed bytes."""
    result = bytearray()
    pos = 0
    while pos < len(data) and len(result) < expected_size:
        n = data[pos]
        pos += 1
        if n < 128:  # 0-127: literal run of n+1 bytes
            count = n + 1
            result.extend(data[pos:pos + count])
            pos += count
        elif n > 128:  # 129-255: repeat next byte (257-n) times
            count = 257 - n
            if pos < len(data):
                result.extend(bytes([data[pos]]) * count)
                pos += 1
        # n == 128: no-op

    return bytes(result[:expected_size])


# ============================================================================
# BITD Decoder
# ============================================================================

def _calc_pitch(width, bpp):
    """Calculate row pitch (bytes per row, word-aligned) for a Mac bitmap."""
    return ((width * bpp + 15) // 16) * 2


def _packbits_decompress_all(data):
    """Decompress PackBits data without a target size. Returns all output bytes."""
    out = bytearray()
    i = 0
    while i < len(data):
        n = data[i]
        if n > 127:
            n = n - 256
        i += 1
        if n == -128:
            continue
        elif n >= 0:
            count = n + 1
            out.extend(data[i:i + count])
            i += count
        else:
            count = 1 - n
            if i < len(data):
                out.extend([data[i]] * count)
                i += 1
    return bytes(out)


def _infer_1bit_dimensions(decompressed_size):
    """Infer (width, height, pitch) for a 1-bit bitmap from decompressed byte count.
    Uses heuristics: prefers reasonable aspect ratios and common sizes."""
    if decompressed_size <= 0:
        return None
    best = None
    best_score = float('inf')
    for pitch in range(2, min(512, decompressed_size + 1), 2):
        if decompressed_size % pitch != 0:
            continue
        height = decompressed_size // pitch
        if height < 1 or height > 2048:
            continue
        width = pitch * 8
        if width > 2048:
            continue
        ratio = max(width, height) / max(1, min(width, height))
        if ratio > 20:
            continue
        # Score: prefer closer to square, penalize extreme ratios
        score = ratio
        if best is None or score < best_score:
            best = (width, height, pitch)
            best_score = score
    return best


def _detect_actual_width(pixels, pitch, height):
    """Detect actual bitmap width by finding rightmost non-zero bit across rows."""
    max_bit = 0
    for y in range(height):
        row_start = y * pitch
        for byte_idx in range(pitch - 1, -1, -1):
            off = row_start + byte_idx
            b = pixels[off] if off < len(pixels) else 0
            if b != 0:
                for bit in range(8):
                    if b & (1 << bit):
                        pixel_x = byte_idx * 8 + (7 - bit)
                        if pixel_x + 1 > max_bit:
                            max_bit = pixel_x + 1
                break
    return max_bit if max_bit > 0 else pitch * 8


def _decode_bitd_1bit_inferred(bitd_data, path, max_compressed=500000):
    """Decode a 1-bit BITD by inferring dimensions from PackBits decompressed size.
    Used as fallback when no cast record exists (old VideoWorks VWSC files)."""
    if len(bitd_data) > max_compressed:
        return False
    pixels = _packbits_decompress_all(bitd_data)
    if not pixels:
        return False
    dims = _infer_1bit_dimensions(len(pixels))
    if dims is None:
        return False
    width, height, pitch = dims
    actual_w = _detect_actual_width(pixels, pitch, height)
    gray = bytearray(actual_w * height)
    for y in range(height):
        for x in range(actual_w):
            byte_idx = y * pitch + x // 8
            bit = 7 - (x % 8)
            if byte_idx < len(pixels):
                px = (pixels[byte_idx] >> bit) & 1
                gray[y * actual_w + x] = 0 if px else 255
            else:
                gray[y * actual_w + x] = 255
    write_png_grayscale(path, actual_w, height, bytes(gray))
    return True


def decode_bitd_to_png(bitd_data, width, height, bpp, palette, path):
    """Decode BITD bitmap data and save as PNG."""
    if width <= 0 or height <= 0:
        return False

    pitch = _calc_pitch(width, bpp)
    expected_size = pitch * height

    if len(bitd_data) == expected_size:
        raw = bitd_data
    elif len(bitd_data) == 0:
        return False
    else:
        raw = decode_packbits(bitd_data, expected_size)

    if len(raw) < expected_size:
        # Pad with zeros if decompression fell short
        raw = raw + b'\x00' * (expected_size - len(raw))

    if bpp == 1:
        # 1-bit: convert to 8-bit grayscale (0=white on Mac, 1=black)
        pixels = bytearray(width * height)
        for y in range(height):
            row_start = y * pitch
            for x in range(width):
                byte_idx = row_start + x // 8
                bit_idx = 7 - (x % 8)
                bit = (raw[byte_idx] >> bit_idx) & 1
                pixels[y * width + x] = 0 if bit else 255
        write_png_grayscale(path, width, height, bytes(pixels))
        return True

    elif bpp == 2:
        # 2-bit indexed
        pixels = bytearray(width * height)
        for y in range(height):
            row_start = y * pitch
            for x in range(width):
                byte_idx = row_start + x // 4
                shift = 6 - 2 * (x % 4)
                idx = (raw[byte_idx] >> shift) & 0x03
                pixels[y * width + x] = idx
        write_png_indexed(path, width, height, bytes(pixels), palette)
        return True

    elif bpp == 4:
        # 4-bit indexed
        pixels = bytearray(width * height)
        for y in range(height):
            row_start = y * pitch
            for x in range(width):
                byte_idx = row_start + x // 2
                if x % 2 == 0:
                    idx = (raw[byte_idx] >> 4) & 0x0F
                else:
                    idx = raw[byte_idx] & 0x0F
                pixels[y * width + x] = idx
        write_png_indexed(path, width, height, bytes(pixels), palette)
        return True

    elif bpp == 8:
        # 8-bit indexed
        pixels = bytearray(width * height)
        for y in range(height):
            row_start = y * pitch
            for x in range(width):
                pixels[y * width + x] = raw[row_start + x]
        write_png_indexed(path, width, height, bytes(pixels), palette)
        return True

    elif bpp == 16:
        # 16-bit RGB555 (big-endian)
        pixels = bytearray(width * height * 3)
        for y in range(height):
            row_start = y * pitch
            for x in range(width):
                word = struct.unpack_from('>H', raw, row_start + x * 2)[0]
                r = ((word >> 10) & 0x1F) * 255 // 31
                g = ((word >> 5) & 0x1F) * 255 // 31
                b = (word & 0x1F) * 255 // 31
                off = (y * width + x) * 3
                pixels[off] = r
                pixels[off + 1] = g
                pixels[off + 2] = b
        write_png_rgb(path, width, height, bytes(pixels))
        return True

    elif bpp == 32:
        # 32-bit: interleaved XRGB (4 bytes per pixel: pad/alpha, R, G, B)
        pixels = bytearray(width * height * 3)
        for y in range(height):
            row_start = y * pitch
            for x in range(width):
                off = row_start + x * 4
                r = raw[off + 1] if off + 1 < len(raw) else 0
                g = raw[off + 2] if off + 2 < len(raw) else 0
                b = raw[off + 3] if off + 3 < len(raw) else 0
                poff = (y * width + x) * 3
                pixels[poff] = r
                pixels[poff + 1] = g
                pixels[poff + 2] = b
        write_png_rgb(path, width, height, bytes(pixels))
        return True

    return False


# ============================================================================
# Mac Sound (snd ) Decoder
# ============================================================================

def decode_snd_to_wav(data, path):
    """Decode a Mac snd resource and save as WAV."""
    if len(data) < 10:
        return False

    fmt = struct.unpack_from('>H', data, 0)[0]
    pos = 2

    if fmt == 1:
        # Format 1: skip data format list
        num_data_formats = struct.unpack_from('>H', data, pos)[0]
        pos += 2 + num_data_formats * 6
    elif fmt == 2:
        # Format 2: skip reference count
        pos += 2
    else:
        return False

    num_commands = struct.unpack_from('>H', data, pos)[0]
    pos += 2

    # Find bufferCmd (command 0x8051 or 0x51 with data flag)
    header_offset = None
    for _ in range(num_commands):
        if pos + 8 > len(data):
            break
        cmd = struct.unpack_from('>H', data, pos)[0]
        param1 = struct.unpack_from('>H', data, pos + 2)[0]
        param2 = struct.unpack_from('>I', data, pos + 4)[0]
        pos += 8

        if (cmd & 0x7FFF) == 0x51:  # bufferCmd
            if cmd & 0x8000:  # data offset flag
                header_offset = param2
            break

    if header_offset is None or header_offset >= len(data):
        return False

    # Parse sound header
    h = header_offset
    sample_ptr = struct.unpack_from('>I', data, h)[0]
    num_samples_or_channels = struct.unpack_from('>I', data, h + 4)[0]
    sample_rate_fixed = struct.unpack_from('>I', data, h + 8)[0]
    loop_start = struct.unpack_from('>I', data, h + 12)[0]
    loop_end = struct.unpack_from('>I', data, h + 16)[0]
    encode = data[h + 20]
    base_freq = data[h + 21]

    sample_rate = sample_rate_fixed >> 16  # integer part of Fixed 16.16

    if encode == 0x00:
        # Standard sound header: 8-bit mono unsigned PCM
        num_samples = num_samples_or_channels
        sample_data_start = h + 22
        sample_data = data[sample_data_start:sample_data_start + num_samples]
        channels = 1
        bits = 8
    elif encode == 0xFF:
        # Extended sound header
        num_channels = num_samples_or_channels
        num_frames = struct.unpack_from('>I', data, h + 22)[0]
        # aiff_sample_rate at h+26 (10 bytes, 80-bit extended float) - we already have sample_rate
        bits_per_sample = struct.unpack_from('>H', data, h + 48)[0] if h + 50 <= len(data) else 8
        sample_data_start = h + 64
        num_samples = num_frames * num_channels
        sample_data = data[sample_data_start:sample_data_start + num_samples * (bits_per_sample // 8)]
        channels = num_channels
        bits = bits_per_sample
    else:
        # Compressed (0xFE) - not found in samples, save raw
        return False

    if len(sample_data) == 0:
        return False

    # Write WAV
    with wave.open(path, 'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(bits // 8)
        wf.setframerate(sample_rate)
        wf.writeframes(sample_data)

    return True


# ============================================================================
# STXT (Styled Text) Decoder
# ============================================================================

def decode_stxt(data):
    """Decode styled text. Returns (plain_text, style_runs)."""
    if len(data) < 12:
        return '', []

    header_offset = struct.unpack_from('>I', data, 0)[0]  # should be 12
    text_length = struct.unpack_from('>I', data, 4)[0]
    data_length = struct.unpack_from('>I', data, 8)[0]

    text_start = 12
    text_end = text_start + text_length
    text = data[text_start:text_end].decode('mac_roman', errors='replace')
    # Convert Mac line endings
    text = text.replace('\r', '\n')

    # Style runs follow the text
    style_runs = []
    style_start = text_end
    if style_start + 2 <= len(data):
        num_runs = struct.unpack_from('>H', data, style_start)[0]
        pos = style_start + 2
        for _ in range(num_runs):
            if pos + 20 > len(data):
                break
            run_offset = struct.unpack_from('>I', data, pos)[0]
            height = struct.unpack_from('>H', data, pos + 4)[0]
            ascent = struct.unpack_from('>H', data, pos + 6)[0]
            font_id = struct.unpack_from('>H', data, pos + 8)[0]
            text_slant = data[pos + 10]
            font_size = struct.unpack_from('>H', data, pos + 12)[0]
            red = struct.unpack_from('>H', data, pos + 14)[0]
            green = struct.unpack_from('>H', data, pos + 16)[0]
            blue = struct.unpack_from('>H', data, pos + 18)[0]
            style_runs.append({
                'offset': run_offset,
                'height': height,
                'ascent': ascent,
                'font_id': font_id,
                'slant': text_slant,
                'font_size': font_size,
                'color': [red >> 8, green >> 8, blue >> 8],
            })
            pos += 20

    return text, style_runs


# ============================================================================
# CLUT (Color Lookup Table) Decoder
# ============================================================================

def decode_clut(data):
    """Decode a Director CLUT resource. Returns list of (r,g,b) tuples.

    Handles two formats:
    - Director raw format: 6 bytes per entry (R16 G16 B16), typically 1536 bytes for 256 colors.
    - Standard Mac 'clut' format: 8-byte header (seed, flags, count) + 8 bytes per entry
      (index, R16, G16, B16), typically 2056 bytes for 256 colors.

    The raw format is preferred when len(data) is an exact multiple of 6 and does NOT
    match the expected Mac clut size (8 + (count+1)*8), since 1536-byte CLUTs can be
    misdetected as Mac format when the first bytes happen to look like a valid header.
    """
    palette = []
    if len(data) >= 6:
        is_raw_format = False

        # Director raw format: exactly N*6 bytes, no header
        if len(data) % 6 == 0:
            # Check if data also matches Mac clut header expectations
            if len(data) >= 8:
                ct_size = struct.unpack_from('>H', data, 6)[0]
                mac_expected_size = 8 + (ct_size + 1) * 8
                if ct_size <= 256 and len(data) == mac_expected_size:
                    # Exact match for Mac clut format -- use Mac format
                    is_raw_format = False
                else:
                    # Does not match Mac clut expected size, use raw format
                    is_raw_format = True
            else:
                is_raw_format = True

        if is_raw_format:
            # Director raw format: 6 bytes per entry (R16 G16 B16, high byte used)
            num_entries = len(data) // 6
            for i in range(num_entries):
                off = i * 6
                r = data[off]
                g = data[off + 2]
                b = data[off + 4]
                palette.append((r, g, b))
        elif len(data) >= 8:
            # Standard Mac clut format: 8-byte header + 8 bytes per entry
            ct_size = struct.unpack_from('>H', data, 6)[0]
            if ct_size <= 256 and len(data) >= 8 + (ct_size + 1) * 8:
                for i in range(ct_size + 1):
                    off = 8 + i * 8
                    r = struct.unpack_from('>H', data, off + 2)[0] >> 8
                    g = struct.unpack_from('>H', data, off + 4)[0] >> 8
                    b = struct.unpack_from('>H', data, off + 6)[0] >> 8
                    palette.append((r, g, b))

    # Pad to 256 entries
    while len(palette) < 256:
        palette.append((0, 0, 0))

    return palette[:256]


# ============================================================================
# STR (Pascal String) Decoder
# ============================================================================

def decode_str(data):
    """Decode a Mac STR resource (Pascal string)."""
    if len(data) < 1:
        return ''
    length = data[0]
    return data[1:1 + length].decode('mac_roman', errors='replace')


# ============================================================================
# vers (Version) Decoder
# ============================================================================

def decode_vers(data):
    """Decode a Mac vers resource."""
    if len(data) < 8:
        return {'raw_hex': data.hex()}

    major = data[0]
    minor_bugfix = data[1]
    minor = (minor_bugfix >> 4) & 0x0F
    bugfix = minor_bugfix & 0x0F
    stage_byte = data[2]
    stage_names = {0x20: 'development', 0x40: 'alpha', 0x60: 'beta', 0x80: 'release'}
    stage = stage_names.get(stage_byte, f'0x{stage_byte:02x}')
    prerelease = data[3]
    country = struct.unpack_from('>H', data, 4)[0]

    # Short version string (Pascal string)
    pos = 6
    short_len = data[pos] if pos < len(data) else 0
    short_str = data[pos + 1:pos + 1 + short_len].decode('mac_roman', errors='replace')
    pos += 1 + short_len

    # Long version string (Pascal string)
    long_len = data[pos] if pos < len(data) else 0
    long_str = data[pos + 1:pos + 1 + long_len].decode('mac_roman', errors='replace')

    return {
        'version': f'{major}.{minor}.{bugfix}',
        'stage': stage,
        'prerelease': prerelease,
        'country_code': country,
        'short_version': short_str,
        'long_version': long_str,
    }


# ============================================================================
# Icon Decoders
# ============================================================================

def decode_icon_to_png(data, icon_type, path):
    """Decode a Mac icon resource to PNG."""
    if icon_type == 'ICON':
        # 32x32 1-bit icon, no mask (128 bytes)
        if len(data) < 128:
            return False
        pixels = bytearray(32 * 32)
        for y in range(32):
            for x in range(32):
                byte_idx = y * 4 + x // 8
                bit = (data[byte_idx] >> (7 - x % 8)) & 1
                pixels[y * 32 + x] = 0 if bit else 255
        write_png_grayscale(path, 32, 32, bytes(pixels))
        return True

    if icon_type in ('ICN#', 'ics#', 'icm#'):
        # 1-bit icon with mask
        size = 32 if icon_type == 'ICN#' else (12 if icon_type == 'icm#' else 16)
        expected = size * size // 8 * 2  # icon + mask
        if len(data) < expected // 2:
            return False
        # Just extract the icon part (first half), ignore mask
        icon_data = data[:size * size // 8]
        pixels = bytearray(size * size)
        for y in range(size):
            for x in range(size):
                byte_idx = y * (size // 8) + x // 8
                bit = (icon_data[byte_idx] >> (7 - x % 8)) & 1
                pixels[y * size + x] = 0 if bit else 255
        write_png_grayscale(path, size, size, bytes(pixels))
        return True

    elif icon_type in ('icl8', 'ics8', 'icm8'):
        # 8-bit indexed icon
        size = 32 if icon_type == 'icl8' else (12 if icon_type == 'icm8' else 16)
        if len(data) < size * size:
            return False
        pixels = data[:size * size]
        write_png_indexed(path, size, size, bytes(pixels), MAC_PALETTE)
        return True

    elif icon_type in ('icl4', 'ics4', 'icm4'):
        # 4-bit indexed icon
        size = 32 if icon_type == 'icl4' else (12 if icon_type == 'icm4' else 16)
        expected = size * size // 2
        if len(data) < expected:
            return False
        pixels = bytearray(size * size)
        for i in range(size * size):
            byte_idx = i // 2
            if i % 2 == 0:
                pixels[i] = (data[byte_idx] >> 4) & 0x0F
            else:
                pixels[i] = data[byte_idx] & 0x0F
        # 4-bit uses first 16 entries of system palette
        write_png_indexed(path, size, size, bytes(pixels), MAC_PALETTE)
        return True

    return False


# ============================================================================
# Mac Cursor (CURS) Decoder
# ============================================================================

def decode_curs_to_png(data, path):
    """Decode a Mac CURS resource (16x16 1-bit cursor) to PNG."""
    if len(data) < 68:
        return False
    # 32 bytes cursor data, 32 bytes mask, 2 bytes hotspot Y, 2 bytes hotspot X
    pixels = bytearray(16 * 16)
    for y in range(16):
        row = struct.unpack_from('>H', data, y * 2)[0]
        for x in range(16):
            bit = (row >> (15 - x)) & 1
            pixels[y * 16 + x] = 0 if bit else 255
    write_png_grayscale(path, 16, 16, bytes(pixels))
    return True


# ============================================================================
# STR# (String List) Decoder
# ============================================================================

def decode_str_list(data):
    """Decode a Mac STR# resource (list of Pascal strings)."""
    if len(data) < 2:
        return []
    count = struct.unpack_from('>H', data, 0)[0]
    strings = []
    pos = 2
    for _ in range(count):
        if pos >= len(data):
            break
        length = data[pos]
        pos += 1
        s = data[pos:pos + length].decode('mac_roman', errors='replace')
        strings.append(s)
        pos += length
    return strings


# ============================================================================
# Filesystem Helpers
# ============================================================================

def safe_type_name(type_code):
    """Make a resource type code safe for filesystem use."""
    return type_code.strip().replace('*', '_star_').replace('#', '_hash_').replace(' ', '_')


def safe_name(name):
    """Make a resource name safe for use in filenames."""
    if not name:
        return ''
    # Replace problematic characters
    safe = name.replace('/', '_').replace('\\', '_').replace(':', '_')
    safe = safe.replace('<', '_').replace('>', '_').replace('"', '_')
    safe = safe.replace('|', '_').replace('?', '_').replace('*', '_')
    safe = safe.replace('\x00', '')
    return safe.strip()


def make_resource_filename(res, ext='bin'):
    """Build a filename for a resource: ID_name.ext or just ID.ext."""
    name_part = safe_name(res.name) if res.name else ''
    if name_part:
        return f'{res.id}_{name_part}.{ext}'
    return f'{res.id}.{ext}'


def save_json(data, path):
    """Save data as pretty-printed JSON."""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False, default=str)


# ============================================================================
# Main Extraction Logic
# ============================================================================

def _try_raw_resource_fork(data):
    """Try parsing raw data as an Apple Resource Fork (no MacBinary wrapper).
    Returns list of Resource namedtuples or None if not a valid resource fork."""
    if len(data) < 16:
        return None
    try:
        data_off = struct.unpack_from('>I', data, 0)[0]
        map_off = struct.unpack_from('>I', data, 4)[0]
        data_len = struct.unpack_from('>I', data, 8)[0]
        map_len = struct.unpack_from('>I', data, 12)[0]
        # Sanity checks for raw resource fork
        if data_off < 16 or data_off > len(data):
            return None
        if map_off < 16 or map_off > len(data):
            return None
        if data_off + data_len > len(data):
            return None
        if map_off + map_len > len(data):
            return None
        if map_len < 28:
            return None
        resources = parse_resource_fork(data)
        if not resources:
            return None
        # Verify we got real resource types (4 printable chars)
        for r in resources[:5]:
            if len(r.type) != 4:
                return None
        return resources
    except Exception:
        return None


def extract(input_file, output_dir, verbose=False):
    """Extract all resources from a MacBinary Director file."""
    with open(input_file, 'rb') as f:
        data = f.read()

    # Try MacBinary first, then raw resource fork, then give up gracefully
    mb = None
    resources = None
    input_format = 'macbinary'

    try:
        mb = parse_macbinary(data)
        # Validate resource fork is actually parseable
        parse_resource_fork(mb['resource_fork'])
    except (ValueError, struct.error):
        mb = None

    if mb:
        print(f'Extracting "{mb["header"]["filename"]}" ...')
        if verbose:
            print(f'  type={mb["header"]["file_type"]} creator={mb["header"]["creator"]}')
            print(f'  Data fork: {mb["header"]["data_fork_length"]} bytes')
            print(f'  Resource fork: {mb["header"]["resource_fork_length"]} bytes')
    else:
        # Try parsing entire file as raw resource fork
        resources = _try_raw_resource_fork(data)
        if resources:
            input_format = 'raw_rsrc'
            fname = os.path.basename(input_file)
            print(f'Extracting "{fname}" (raw resource fork) ...')
        else:
            # Data fork only - no extractable resources
            fname = os.path.basename(input_file)
            print(f'Skipping "{fname}" - data fork only (no resource fork)')
            return

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    out = lambda name: os.path.join(output_dir, name)

    if mb:
        if verbose:
            save_json(mb['header'], out('macbinary_header.json'))
        # Parse Resource Fork
        resources = parse_resource_fork(mb['resource_fork'])

    # Organize resources by type
    by_type = {}
    for res in resources:
        by_type.setdefault(res.type, []).append(res)

    if verbose:
        print(f'  {len(resources)} resources:')
        for rtype in sorted(by_type.keys()):
            print(f'    {rtype:6s}: {len(by_type[rtype]):3d}')

    # Track handled resources; unhandled ones get dumped in verbose mode
    handled = set()

    # Counters for summary
    counts = {'png': 0, 'wav': 0, 'txt': 0, 'lingo': 0, 'icon': 0}

    # --- Parse VWCF (movie config) ---
    config = None
    if 'VWCF' in by_type:
        res = by_type['VWCF'][0]
        config = parse_vwcf(res.data)
        if verbose:
            save_json(config, out('VWCF.json'))
            print(f'  Stage: {config.get("stage_width")}x{config.get("stage_height")} '
                  f'depth={config.get("bit_depth", "?")}')
        handled.add((res.type, res.id))

    cast_start = config.get('cast_array_start', 1) if config else 1
    cast_end = config.get('cast_array_end', 1) if config else 1

    # --- Parse VWCR (cast records) ---
    cast_records = {}
    cast_id_offset = 1024
    if 'VWCR' in by_type:
        res = by_type['VWCR'][0]
        cast_id_offset = res.id
        cast_records = parse_vwcr(res.data, cast_start, cast_end)
        if verbose:
            save_json(cast_records, out('VWCR.json'))
        handled.add((res.type, res.id))

    # --- Parse VWCI (cast info) - get names and scripts ---
    cast_names = {}
    if 'VWCI' in by_type:
        for res in by_type['VWCI']:
            info = parse_vwci(res.data)
            name = info.get('strings', {}).get('name', '')
            if name:
                cast_names[res.id] = name
            if verbose:
                save_json(info, out(f'VWCI_{res.id}.json'))
            handled.add((res.type, res.id))

            # Extract Lingo script if present (always)
            script = info.get('strings', {}).get('script', '')
            if script and script.strip():
                sname = safe_name(name) if name else str(res.id)
                with open(out(f'cast_{res.id}_{sname}.lingo'), 'w') as f:
                    f.write(script.replace('\r', '\n'))
                counts['lingo'] += 1

    # --- Parse CLUTs (both uppercase Director 'CLUT' and lowercase Mac 'clut') ---
    clut_palettes = {}
    for clut_type in ('CLUT', 'clut'):
        if clut_type in by_type:
            for res in by_type[clut_type]:
                pal = decode_clut(res.data)
                clut_palettes[res.id] = pal
                if verbose:
                    save_json({'id': res.id, 'colors': pal}, out(f'palette_{res.id}.json'))
                    act_data = b''.join(bytes(c) for c in pal)
                    with open(out(f'palette_{res.id}.act'), 'wb') as f:
                        f.write(act_data)
                handled.add((res.type, res.id))

    # --- Scan sibling files for shared CLUTs if needed ---
    # Director projects often use shared casts or sibling movie files that
    # contain the project palette. If any bitmap references a positive
    # clut_id that doesn't exist locally, scan sibling files.
    bitmap_clut_ids = set(
        rec.get('clut_id', 0)
        for rec in cast_records.values()
        if rec.get('cast_type') == 1 and rec.get('clut_id', 0) > 0
    )
    unresolved = set()
    for cid in bitmap_clut_ids:
        if cid not in clut_palettes:
            abs_id = cid + cast_id_offset
            if abs_id not in clut_palettes:
                unresolved.add(cid)
    if unresolved:
        sibling_cluts = scan_sibling_cluts(input_file)
        # Merge sibling CLUTs for unresolved references (don't overwrite local)
        for rid, pal in sibling_cluts.items():
            if rid not in clut_palettes:
                clut_palettes[rid] = pal

    # --- Determine movie default palette ---
    # clut_id=0 means "movie default palette". If no bitmap explicitly
    # references a CLUT by positive cast index, ANY CLUT in the file is a
    # movie-level palette (not per-member). If bitmaps DO reference CLUTs
    # by cast index, only use the first CLUT as movie default if it's near
    # the start of the cast (low index = general movie palette vs. high
    # index = per-member palette like individual photo palettes).
    movie_palette_256 = MAC_PALETTE
    movie_palette_16 = MAC_16_PALETTE
    if clut_palettes:
        has_positive_clut_refs = any(
            rec.get('clut_id', 0) > 0
            for rec in cast_records.values()
            if rec.get('cast_type') == 1
        )
        first_clut_id = min(clut_palettes.keys())
        first_clut_idx = first_clut_id - cast_id_offset
        use_file_clut = False
        if not has_positive_clut_refs:
            # No explicit refs: file CLUT is the movie palette regardless of position
            use_file_clut = True
        elif first_clut_idx <= 16:
            # Has explicit refs but first CLUT is near the start = movie palette
            use_file_clut = True
        if use_file_clut:
            movie_palette_256 = clut_palettes[first_clut_id]
            # For 4-bit mode: if the CLUT matches a known built-in palette, use
            # its dedicated 16-color variant (which has a different color mapping
            # than just taking entries 0-15 of the 256-color version).
            movie_palette_16 = _match_builtin_16(movie_palette_256)
            if movie_palette_16 is None:
                movie_palette_16 = movie_palette_256[:16]

    # --- Extract BITDs ---
    # Use 1-bit fallback only for old VideoWorks files with no cast metadata
    has_cast_metadata = bool(cast_records)
    if 'BITD' in by_type:
        for res in by_type['BITD']:
            cast_idx = res.id - cast_id_offset
            rec = cast_records.get(cast_idx)
            if rec and rec.get('cast_type') == 1:
                width = rec['width']
                height = rec['height']
                bpp = rec.get('bits_per_pixel', 1)
                clut_id = rec.get('clut_id', 0)

                palette = resolve_palette(clut_id, bpp, clut_palettes,
                                          cast_id_offset, movie_palette_256,
                                          movie_palette_16)

                name = cast_names.get(res.id, '')
                sname = safe_name(name) if name else ''
                fname = f'{res.id}_{sname}.png' if sname else f'{res.id}.png'

                if decode_bitd_to_png(res.data, width, height, bpp, palette, out(fname)):
                    counts['png'] += 1
                elif verbose:
                    print(f'  WARNING: Failed to decode BITD {res.id} ({width}x{height}x{bpp})')
            elif not has_cast_metadata:
                # Fallback: infer 1-bit dimensions from PackBits decompressed size
                # (old VideoWorks VWSC files without any VWCI/CASt cast records)
                fname = f'{res.id}.png'
                if _decode_bitd_1bit_inferred(res.data, out(fname)):
                    counts['png'] += 1
                elif verbose:
                    print(f'  WARNING: No cast record for BITD {res.id}')
            elif verbose:
                print(f'  WARNING: No cast record for BITD {res.id}')
            handled.add((res.type, res.id))

    # --- Extract sounds ---
    if 'snd ' in by_type:
        for res in by_type['snd ']:
            name = cast_names.get(res.id, res.name or '')
            sname = safe_name(name) if name else ''
            fname = f'{res.id}_{sname}.wav' if sname else f'{res.id}.wav'
            if decode_snd_to_wav(res.data, out(fname)):
                counts['wav'] += 1
            elif verbose:
                print(f'  WARNING: Failed to decode snd {res.id} ({name})')
            handled.add((res.type, res.id))

    # --- Extract STXT ---
    if 'STXT' in by_type:
        for res in by_type['STXT']:
            name = cast_names.get(res.id, '')
            sname = safe_name(name) if name else ''
            base = f'{res.id}_{sname}' if sname else str(res.id)
            text, styles = decode_stxt(res.data)
            with open(out(f'{base}.txt'), 'w', encoding='utf-8') as f:
                f.write(text)
            counts['txt'] += 1
            if styles and verbose:
                save_json(styles, out(f'{base}_styles.json'))
            handled.add((res.type, res.id))

    # --- Parse VWSC (score) ---
    if 'VWSC' in by_type:
        res = by_type['VWSC'][0]
        score = parse_vwsc(res.data)
        if verbose:
            save_json(score, out('VWSC.json'))
            print(f'  Score: {score.get("frame_count_decoded", 0)} frames')
        handled.add((res.type, res.id))

    # --- Parse VWAC (actions/Lingo) ---
    if 'VWAC' in by_type:
        res = by_type['VWAC'][0]
        actions = parse_vwac(res.data)
        if verbose:
            save_json(actions, out('VWAC.json'))
        handled.add((res.type, res.id))
        if actions.get('full_text'):
            with open(out('actions.lingo'), 'w') as f:
                f.write(actions['full_text'].replace('\r', '\n'))
            counts['lingo'] += 1

    # --- Parse VWFI (file info) ---
    if 'VWFI' in by_type:
        res = by_type['VWFI'][0]
        file_info = parse_vwfi(res.data)
        if verbose:
            save_json(file_info, out('VWFI.json'))
        handled.add((res.type, res.id))
        script = file_info.get('strings', {}).get('script', '')
        if script and script.strip():
            with open(out('movie_script.lingo'), 'w') as f:
                f.write(script.replace('\r', '\n'))
            counts['lingo'] += 1

    # --- Parse VWFM (font map) ---
    if 'VWFM' in by_type:
        res = by_type['VWFM'][0]
        if verbose:
            save_json(parse_vwfm(res.data), out('VWFM.json'))
        handled.add((res.type, res.id))

    # --- Parse VWLB (labels) ---
    if 'VWLB' in by_type:
        res = by_type['VWLB'][0]
        if verbose:
            save_json(parse_vwlb(res.data), out('VWLB.json'))
        handled.add((res.type, res.id))

    # --- Extract STR resources ---
    if 'STR ' in by_type:
        for res in by_type['STR ']:
            if verbose:
                text = decode_str(res.data)
                with open(out(f'STR_{res.id}.txt'), 'w') as f:
                    f.write(text)
            handled.add((res.type, res.id))

    # --- Extract vers resources ---
    if 'vers' in by_type:
        for res in by_type['vers']:
            if verbose:
                save_json(decode_vers(res.data), out(f'vers_{res.id}.json'))
            handled.add((res.type, res.id))

    # --- Extract icon resources ---
    icon_types = ['ICN#', 'ICON', 'icl8', 'icl4', 'ics#', 'ics8', 'ics4',
                  'icm#', 'icm4', 'icm8']
    for itype in icon_types:
        if itype in by_type:
            for res in by_type[itype]:
                st = safe_type_name(itype)
                fname = f'icon_{res.id}_{st}.png'
                if decode_icon_to_png(res.data, itype, out(fname)):
                    counts['icon'] += 1
                handled.add((res.type, res.id))

    # --- Extract CURS (cursor) resources ---
    if 'CURS' in by_type:
        for res in by_type['CURS']:
            fname = f'cursor_{res.id}.png'
            if decode_curs_to_png(res.data, out(fname)):
                counts['icon'] += 1
            handled.add((res.type, res.id))

    # --- Extract PICT resources (raw Mac PICT data) ---
    if 'PICT' in by_type:
        for res in by_type['PICT']:
            name = cast_names.get(res.id, res.name or '')
            sname = safe_name(name) if name else ''
            fname = f'PICT_{res.id}_{sname}.pict' if sname else f'PICT_{res.id}.pict'
            with open(out(fname), 'wb') as f:
                f.write(res.data)
            handled.add((res.type, res.id))

    # --- Extract TEXT resources ---
    if 'TEXT' in by_type:
        for res in by_type['TEXT']:
            try:
                text = res.data.decode('mac_roman').replace('\r', '\n')
            except Exception:
                text = res.data.decode('latin-1').replace('\r', '\n')
            if text.strip():
                with open(out(f'TEXT_{res.id}.txt'), 'w') as f:
                    f.write(text)
                counts['txt'] += 1
            handled.add((res.type, res.id))

    # --- Extract STR# (string list) resources ---
    if 'STR#' in by_type:
        for res in by_type['STR#']:
            if verbose:
                strings = decode_str_list(res.data)
                save_json(strings, out(f'STRL_{res.id}.json'))
            handled.add((res.type, res.id))

    # --- Extract SCVW resources ---
    if 'SCVW' in by_type:
        for res in by_type['SCVW']:
            if verbose:
                with open(out(f'SCVW_{res.id}.bin'), 'wb') as f:
                    f.write(res.data)
            handled.add((res.type, res.id))

    # --- MooV (QuickTime movie reference) ---
    if 'MooV' in by_type:
        for res in by_type['MooV']:
            if verbose:
                with open(out(f'MooV_{res.id}.bin'), 'wb') as f:
                    f.write(res.data)
            handled.add((res.type, res.id))

    # --- Verbose-only metadata: MARK, VWTL, VWtc, FOND, FONT, NFNT, alis, fwst, SHAP ---
    verbose_only_types = [
        # Director metadata
        'MARK', 'VWTL', 'VWtc', 'SHAP',
        'OVWD', 'VWAD', 'm5cr', 'm5ax', 'VWst', 'VWCF', 'VWAC',
        'MMPB', 'MMPb', 'Tdta', 'MMCF', 'ROWN', 'MMdp',
        'ZERO', 'DREL', 'RMIN', 'CSND', 'vers',
        # Mac fonts
        'FOND', 'FONT', 'NFNT', 'sfnt',
        # Mac UI/system resources
        'ALRT', 'DLOG', 'DITL', 'DLGX', 'WIND',
        'DATA', 'DRVR', 'SIZE', 'BNDL', 'FREF',
        'PAT#', 'CMAP', 'cicn', 'acur',
        'dctb', 'wctb', 'cctb', 'mctb', 'actb',
        'alis', 'fwst', 'hfdr', 'FCMT', 'FRev',
        'snth', 'bdrp', 'lema',
        # App/tool-specific
        'KATA', 'ASHI', 'VYGR', 'SitC',
        'DKH\u2122', 'SAM\u02c7',
    ]
    for vtype in verbose_only_types:
        if vtype in by_type:
            for res in by_type[vtype]:
                if verbose:
                    st = safe_type_name(vtype)
                    fname = f'{st}_{make_resource_filename(res, "bin")}'
                    with open(out(fname), 'wb') as f:
                        f.write(res.data)
                handled.add((res.type, res.id))

    # --- Code resources ---
    code_type_prefixes = ['XCMD', 'XCOD', 'XFCN', 'SeLF', 'CCOD', 'WDEF']
    for rtype, rlist in by_type.items():
        is_code = rtype in code_type_prefixes
        if not is_code and len(rtype) == 4 and rtype[0] == 'C' and rtype[2:] == 'DE':
            is_code = True
        if is_code:
            for res in rlist:
                if verbose:
                    st = safe_type_name(rtype)
                    fname = f'{st}_{make_resource_filename(res, "bin")}'
                    with open(out(fname), 'wb') as f:
                        f.write(res.data)
                handled.add((res.type, res.id))

    # --- Dump unhandled resources ---
    unhandled_count = 0
    for res in resources:
        if (res.type, res.id) not in handled:
            if verbose:
                st = safe_type_name(res.type)
                fname = f'other_{st}_{make_resource_filename(res, "bin")}'
                with open(out(fname), 'wb') as f:
                    f.write(res.data)
            unhandled_count += 1

    # --- Save resource index (verbose only) ---
    if verbose:
        index = []
        for res in resources:
            entry = {
                'type': res.type,
                'id': res.id,
                'name': res.name,
                'attributes': res.attributes,
                'data_size': len(res.data),
            }
            if res.id in cast_names:
                entry['cast_name'] = cast_names[res.id]
            index.append(entry)
        save_json(index, out('resource_index.json'))

    # Summary
    parts = []
    if counts['png']:
        parts.append(f'{counts["png"]} PNGs')
    if counts['wav']:
        parts.append(f'{counts["wav"]} WAVs')
    if counts['txt']:
        parts.append(f'{counts["txt"]} text')
    if counts['lingo']:
        parts.append(f'{counts["lingo"]} scripts')
    if counts['icon']:
        parts.append(f'{counts["icon"]} icons')
    if unhandled_count and verbose:
        parts.append(f'{unhandled_count} other')
    print(f'  -> {", ".join(parts)}')
    return True


# ============================================================================
# Entry Point
# ============================================================================

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Extract resources from MacroMind Director MacBinary files.')
    parser.add_argument('inputFile', help='MacBinary input file')
    parser.add_argument('outputDir', help='Output directory for extracted resources')
    parser.add_argument('--verbose', action='store_true',
                        help='Also extract metadata JSON, palettes, code, and other internal resources')
    args = parser.parse_args()

    if not os.path.isfile(args.inputFile):
        print(f'Error: {args.inputFile} not found')
        sys.exit(1)

    try:
        extract(args.inputFile, args.outputDir, verbose=args.verbose)
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)
