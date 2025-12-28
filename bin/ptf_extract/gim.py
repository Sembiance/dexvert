#!/usr/bin/env python3

import argparse
import datetime
import io
import sys
from bitconv import str_encode, int_encode, str_decode, int_decode
from collections import namedtuple
from contextlib import contextmanager
from PIL import Image

GIM_MAGIC1_BIG = 0x4D49472E # GIM.
GIM_MAGIC1_LIT = 0x2E47494D # .MIG
GIM_MAGIC2_BIG = 0x30302E31 # 00.1
GIM_MAGIC2_LIT = 0x312E3030 # 1.00
GIM_MAGIC3_BIG = 0x50535000 # PSP
GIM_MAGIC3_LIT = 0x00505350 #  PSP

GIMImageBlock = namedtuple('GIMImageBlock', \
    'structure_size format pixel_order width height ' + \
    'rsx_bpp rsx_pitch_align rsx_height_align ' + \
    'unknown_12 next_index_block frame_data_start frame_data_end ' + \
    'plane_mask level_type level_count frame_type frame_count frame_data')
GIMFileInfoBlock = namedtuple('GIMFileInfoBlock', \
    'project_name user_name saved_date originator')
GIMBlockHeader = namedtuple('GIMBlockHeader', \
    'type block_size next_block data_offset')

GIM_SAVED_DATE_FORMAT = '%a %b %d %H:%M:%S %Y'
GIM_DEFAULT_ORIGINATOR = 'GeofrontTeam LibPSPThemes 1.0'

def overscan_for_tile_size(value, tile_value):
    if value % tile_value == 0:
        return value
    else:
        return value + (tile_value - (value % tile_value))

def png2gim(data, args):
    def encode_image_data_rgba(im, gim_pixel_order):
        im_pixels = list(im.getdata())
        
        w = im.width
        h = im.height
        pixels = [None] * h
        for y in range(h):
            pixels[y] = [0] * w
        pos = 0
        for y in range(h):
            for x in range(w):
                if isinstance(im_pixels[pos], int):
                    pixels[y][x] = im_pixels[pos]
                else:
                    pixels[y][x] = int.from_bytes(bytes(im_pixels[pos]), byteorder='little')
                pos += 1
        
        return pixels
    
    def encode_image_data_rgba_palette(im, gim_pixel_order):
        im_pixels = encode_image_data_rgba(im, gim_pixel_order)
        im_pixels_palette = list(im.getpalette())
        
        pixels_palette = [[0] * 256]
        pos = 0
        y = 0
        for x in range(256):
            if pos < len(im_pixels_palette):
                if isinstance(im_pixels[pos], int):
                    pixels_palette[y][x] = im_pixels_palette[pos]
                else:
                    pixels_palette[y][x] = int.from_bytes(bytes(im_pixels_palette[pos]), byteorder='little')
            else:
                pixels_palette[y][x] = 0
            pos += 1
        
        return im_pixels, pixels_palette
    
    def px2by_arr(px, w, h, bpp):
        by = bytes()
        for y in range(h):
            for x in range(w):
                by += px[y][x].to_bytes((bpp + 7) // 8, byteorder='little')
        return by
    
    def swap_tiles(pixels, w, h, tile_w, tile_h):
        over_w = overscan_for_tile_size(w, tile_w)
        over_h = overscan_for_tile_size(h, tile_h)
        tile_origin_x = 0
        tile_origin_y = 0
        tile_pos = 0
        new_pixels = [None] * over_h
        for y in range(over_h):
            new_pixels[y] = [0] * over_w
        for y in range(over_h):
            for x in range(over_w):
                d_x = tile_origin_x + (tile_pos % tile_w)
                d_y = tile_origin_y + (tile_pos // tile_w)
                
                if d_x < w and d_y < h:
                    new_pixels[y][x] = pixels[d_y][d_x]
                else:
                    pass
                    #print('out of range', hex(pixels[y][x]), x, ',', y, ' -> ', d_x, ',', d_y)
                
                tile_pos += 1
                if tile_pos == tile_w * tile_h:
                    tile_pos = 0
                    tile_origin_x += tile_w
                    if tile_origin_x >= over_w:
                        tile_origin_x = 0
                        tile_origin_y += tile_h
        
        return new_pixels, over_w, over_h
    
    def recursive_encode_block(data, pos, gim_block, prev_block_link, byteorder):
        if isinstance(gim_block, dict):
            for name, val in gim_block.items():
                # emit block header
                gim_type = 0
                if name == 'root':
                    gim_type = 2
                elif name == 'picture':
                    gim_type = 3
                elif name == 'image':
                    gim_type = 4
                elif name == 'image_palette':
                    gim_type = 5
                elif name == 'fileinfo':
                    gim_type = 0xff
                rel_offset_start = pos
                # save offset to this block into previous block
                if prev_block_link > 0:
                    data, _   = int_encode(data, prev_block_link + 8, pos - prev_block_link, 4, byteorder=byteorder)
                prev_block_link = rel_offset_start
                data, pos = int_encode(data, pos, gim_type, 2, byteorder=byteorder)
                data, pos = int_encode(data, pos, 0,        2, byteorder=byteorder)
                rel_offset_children_len = pos
                data, pos = int_encode(data, pos, 0,        4, byteorder=byteorder)
                data, pos = int_encode(data, pos, 0,        4, byteorder=byteorder)
                data, pos = int_encode(data, pos, 0x10,     4, byteorder=byteorder)
                
                # emit sub-blocks
                data, pos, prev_block_link = recursive_encode_block(data, pos, val, prev_block_link, byteorder=byteorder)
                
                # save size of children
                data, _   = int_encode(data, rel_offset_children_len, pos - rel_offset_start, 4, byteorder=byteorder)
        elif type(gim_block).__name__ == 'GIMImageBlock':
            # emit image block
            rel_offset_start = pos
            data, pos = int_encode(data, pos, gim_block.structure_size,     2, byteorder=byteorder)
            data, pos = int_encode(data, pos, 0,                            2, byteorder=byteorder)
            data, pos = int_encode(data, pos, gim_block.format,             2, byteorder=byteorder)
            data, pos = int_encode(data, pos, gim_block.pixel_order,        2, byteorder=byteorder)
            data, pos = int_encode(data, pos, gim_block.width,              2, byteorder=byteorder)
            data, pos = int_encode(data, pos, gim_block.height,             2, byteorder=byteorder)
            data, pos = int_encode(data, pos, gim_block.rsx_bpp,            2, byteorder=byteorder)
            data, pos = int_encode(data, pos, gim_block.rsx_pitch_align,    2, byteorder=byteorder)
            data, pos = int_encode(data, pos, gim_block.rsx_height_align,   2, byteorder=byteorder)
            data, pos = int_encode(data, pos, gim_block.unknown_12,         2, byteorder=byteorder)
            data, pos = int_encode(data, pos, 0,                            4, byteorder=byteorder)
            data, pos = int_encode(data, pos, gim_block.next_index_block,   4, byteorder=byteorder)
            data, pos = int_encode(data, pos, gim_block.frame_data_start,   4, byteorder=byteorder)
            data, pos = int_encode(data, pos, gim_block.frame_data_end,     4, byteorder=byteorder)
            data, pos = int_encode(data, pos, gim_block.plane_mask,         4, byteorder=byteorder)
            data, pos = int_encode(data, pos, gim_block.level_type,         2, byteorder=byteorder)
            data, pos = int_encode(data, pos, gim_block.level_count,        2, byteorder=byteorder)
            data, pos = int_encode(data, pos, gim_block.frame_type,         2, byteorder=byteorder)
            data, pos = int_encode(data, pos, gim_block.frame_count,        2, byteorder=byteorder)
            # emit index
            if pos < rel_offset_start + gim_block.next_index_block:
                data, pos = int_encode(data, pos, 0, (rel_offset_start + gim_block.next_index_block) - pos)
            data, pos = int_encode(data, pos, gim_block.frame_data_start,   4, byteorder=byteorder)
            # emit frame
            if pos < rel_offset_start + gim_block.frame_data_start:
                data, pos = int_encode(data, pos, 0, (rel_offset_start + gim_block.frame_data_start) - pos)
            width = gim_block.width
            height = gim_block.height
            tile_width = 0x80 // gim_block.rsx_bpp
            tile_height = 0x08
            if gim_block.pixel_order == 1:
                width = overscan_for_tile_size(width, tile_width)
                height = overscan_for_tile_size(height, tile_height)
            pixels = px2by_arr(gim_block.frame_data, width, height, gim_block.rsx_bpp)
            #print(hex(len(pixels)), hex(gim_block.frame_data_end-gim_block.frame_data_start))
            data += pixels
            pos += len(pixels)
        elif type(gim_block).__name__ == 'GIMFileInfoBlock':
            data, pos = str_encode(data, pos, gim_block.project_name, len(gim_block.project_name) + 1)
            data, pos = str_encode(data, pos, gim_block.user_name, len(gim_block.user_name) + 1)
            data, pos = str_encode(data, pos, gim_block.saved_date, len(gim_block.saved_date) + 1)
            data, pos = str_encode(data, pos, gim_block.originator, len(gim_block.originator) + 1)
            if pos % 4 != 0:
                data, pos = int_encode(data, pos, 0, 4 - (pos % 4))
        return data, pos, prev_block_link
    
    with Image.open(io.BytesIO(data)) as im:
        if im.size == 0:
            raise Exception('Not able to read input data as image.')
        
        data = bytes()
        pos = 0
        byteorder = args.gim_byteorder
        data, pos = int_encode(data, pos, GIM_MAGIC1_LIT, 4, byteorder=byteorder) # GIM.
        data, pos = int_encode(data, pos, GIM_MAGIC2_LIT, 4, byteorder=byteorder) # 1.00
        data, pos = int_encode(data, pos, GIM_MAGIC3_LIT, 4, byteorder=byteorder) # PSP
        data, pos = int_encode(data, pos, 0, 4, byteorder=byteorder) # 0
        
        gim_saved_date = args.gim_saved_date
        if gim_saved_date is None:
            gim_saved_date = datetime.datetime.now()
        dt_string = gim_saved_date.strftime(GIM_SAVED_DATE_FORMAT)
        dt_string += '\n'
        gim_originator = args.gim_originator
        if gim_originator is None:
            gim_originator = GIM_DEFAULT_ORIGINATOR
        fileinfo_block = GIMFileInfoBlock(
                args.gim_project_name,  # project_name
                args.gim_user_name,     # user_name
                dt_string,              # saved_date
                gim_originator          # originator
            )
        gim_blocks = {'root': {'picture': {}}}
        gim_width = im.width
        gim_height = im.height
        if im.mode == 'RGBA' or im.mode == 'RGB':
            if im.mode == 'RGB':
                im = im.convert('RGBA')
            gim_has_palette = False
            gim_format = 3
            gim_pixel_order = 0
            if args.gim_pixel_order:
                gim_pixel_order = 1
            gim_rsx_bpp = 32
            gim_rsx_pitch_align = 0x10
            gim_rsx_height_align = 0x08
            
            gim_pixels = encode_image_data_rgba(im, gim_pixel_order)
            gim_pixels_len = gim_width * gim_height * ((gim_rsx_bpp + 7) // 8)
        elif im.mode == 'P' or im.mode == 'PA':
            if im.mode == 'PA':
                im = im.convert('P')
            gim_has_palette = True
            gim_format = 5
            gim_pixel_order = 0
            if args.gim_pixel_order:
                gim_pixel_order = 1
            gim_rsx_bpp = 8
            gim_rsx_pitch_align = 0x10
            gim_rsx_height_align = 0x08
            
            gim_pixels, gim_pixels_palette = encode_image_data_rgba_palette(im, gim_pixel_order)
            gim_pixels_len = gim_width * gim_height * ((gim_rsx_bpp + 7) // 8)
        
        tile_width = 0x80 // gim_rsx_bpp
        tile_height = 0x08
        if gim_pixel_order == 1:
            gim_pixels, gim_over_width, gim_over_height = swap_tiles(gim_pixels, gim_width, gim_height, tile_width, tile_height)
            gim_pixels_len = gim_over_width * gim_over_height * ((gim_rsx_bpp + 7) // 8)
        
        # the image part
        gim_blocks['root']['picture']['image'] = GIMImageBlock( \
            0x30, # structure_size
            gim_format,
            gim_pixel_order,
            gim_width,
            gim_height,
            gim_rsx_bpp,
            gim_rsx_pitch_align,
            gim_rsx_height_align,
            2, # unknown_12
            0x30, # next_index_block
            0x40, #frame_data_start
            0x40 + gim_pixels_len, # frame_data_end
            0, # plane_mask
            1, # level_type
            1, # level_count
            3, # frame_type
            1, # frame_count
            gim_pixels)
        
        if gim_has_palette:
            # the palette part
            gim_blocks['root']['picture']['image_palette'] = GIMImageBlock( \
                0x30, # structure_size
                3, # format
                0, # pixel_order
                256, # width
                1, # height
                32, # rsx_bpp
                0x10, # rsx_pitch_align
                0x08, # rsx_height_align
                2, # unknown_12
                0x30, # next_index_block
                0x40, #frame_data_start
                0x40 + 256 * 4, # frame_data_end
                0, # plane_mask
                2, # level_type
                1, # level_count
                3, # frame_type
                1, # frame_count
                gim_pixels_palette)
        
        if not args.gim_no_fileinfo:
            gim_blocks['root']['fileinfo'] = fileinfo_block
        
        data, pos, prev_block_link = recursive_encode_block(data, pos, gim_blocks, 0, byteorder=byteorder)
        
        # save offset to last block into previous block
        if prev_block_link > 0:
            data, _   = int_encode(data, prev_block_link + 8, pos - prev_block_link, 4, byteorder=byteorder)
        
        return data

@contextmanager
def gim2png(data, args):
    def read_header(data, pos, byteorder):
        p = {}
        p['type'],              pos = int_decode(data, pos, 2, byteorder=byteorder) # type of block
        _,                      pos = int_decode(data, pos, 2, byteorder=byteorder) # 0
        p['block_size'],        pos = int_decode(data, pos, 4, byteorder=byteorder) # block size (include header)
        p['next_block'],        pos = int_decode(data, pos, 4, byteorder=byteorder) # next block offset
        p['data_offset'],       pos = int_decode(data, pos, 4, byteorder=byteorder) # data offset
        return GIMBlockHeader(*p.values()), pos
    
    def read_image_block(data, pos, byteorder):
        p = {}
        p['structure_size'],    pos = int_decode(data, pos, 2, byteorder=byteorder) # size of block data
        _,        pos = int_decode(data, pos, 2, byteorder=byteorder) # 0
        if p['structure_size'] != 0x30:
            raise Exception('GIM image block size invalid: 0x{:02X}'.format(structsz))
        p['format'],            pos = int_decode(data, pos, 2, byteorder=byteorder) # image format (0=rgba5650, 1=rgba5551, 2=rgba4444, 3=rgba8888, 4=p4, 5=p8, 6=pa88, 7=paxx8888, 8=dxt1, 9=dxt3, 10=dxt5)
        p['pixel_order'],       pos = int_decode(data, pos, 2, byteorder=byteorder) # pixel order (0=normal, 1=faster)
        p['width'],             pos = int_decode(data, pos, 2, byteorder=byteorder) # width
        p['height'],            pos = int_decode(data, pos, 2, byteorder=byteorder) # height
        p['rsx_bpp'],           pos = int_decode(data, pos, 2, byteorder=byteorder) # RSX bits per pixel
        p['rsx_pitch_align'],   pos = int_decode(data, pos, 2, byteorder=byteorder) # RSX x alignment
        p['rsx_height_align'],  pos = int_decode(data, pos, 2, byteorder=byteorder) # RSX y alignment
        p['unknown_12'],        pos = int_decode(data, pos, 2, byteorder=byteorder) # 2
        _,                      pos = int_decode(data, pos, 4, byteorder=byteorder) # 0
        p['next_index_block'],  pos = int_decode(data, pos, 4, byteorder=byteorder) # offset to index block
        p['frame_data_start'],  pos = int_decode(data, pos, 4, byteorder=byteorder) # offset to first frame block
        p['frame_data_end'],    pos = int_decode(data, pos, 4, byteorder=byteorder) # offset to last frame block end
        p['plane_mask'],        pos = int_decode(data, pos, 4, byteorder=byteorder) # plane mask
        p['level_type'],        pos = int_decode(data, pos, 2, byteorder=byteorder) # level type (1=MIPMAP, 2=MIPMAP2)
        p['level_count'],       pos = int_decode(data, pos, 2, byteorder=byteorder) # level count
        p['frame_type'],        pos = int_decode(data, pos, 2, byteorder=byteorder) # frame type (3=SEQUENCE)
        p['frame_count'],       pos = int_decode(data, pos, 2, byteorder=byteorder) # frame count
        p['frame_data']             = None
        return GIMImageBlock(*p.values()), pos
    
    def read_fileinfo_block(data, pos, byteorder):
        p = {}
        p['project_name'],      pos = str_decode(data, pos, -1, 'utf-8')
        p['user_name'],         pos = str_decode(data, pos, -1, 'utf-8')
        p['saved_date'],        pos = str_decode(data, pos, -1, 'utf-8')
        p['originator'],        pos = str_decode(data, pos, -1, 'utf-8')
        return GIMFileInfoBlock(*p.values()), pos
    
    def take_pixel(data, pos, partial_byte, bpp):
        bytes = (bpp + 7) // 8
        last_byte_bits = bpp % 8
        pixel_value, pos = int_decode(data, pos, bytes, byteorder='little')
        if last_byte_bits > 0:
            bits_in_partial, partial_value = partial_byte
            if bits_in_partial == 0:
                bits_in_partial = 8
            partial_byte = (bits_in_partial - last_byte_bits, pixel_value & (0xFF >> (bits_in_partial - last_byte_bits)))
            pixel_value >>= bits_in_partial - last_byte_bits
            pixel_value &= (0xFF >> last_byte_bits)
            # AABBCCDD
            if bits_in_partial - last_byte_bits > 0:
                pos -= 1
        return pixel_value, pos, partial_byte
    
    def swap_tiles(pixels, w, h, tile_w, tile_h):
        over_w = overscan_for_tile_size(w, tile_w)
        over_h = overscan_for_tile_size(h, tile_h)
        tile_origin_x = 0
        tile_origin_y = 0
        tile_pos = 0
        new_pixels = [None] * h
        for y in range(h):
            new_pixels[y] = [0] * w
        for y in range(over_h):
            for x in range(over_w):
                d_x = tile_origin_x + (tile_pos % tile_w)
                d_y = tile_origin_y + (tile_pos // tile_w)
                
                if d_x < w and d_y < h:
                    new_pixels[d_y][d_x] = pixels[y][x]
                else:
                    pass
                    #print('out of range', hex(pixels[y][x]), x, ',', y, ' -> ', d_x, ',', d_y)
                
                tile_pos += 1
                if tile_pos == tile_w * tile_h:
                    tile_pos = 0
                    tile_origin_x += tile_w
                    if tile_origin_x >= over_w:
                        tile_origin_x = 0
                        tile_origin_y += tile_h
        
        return new_pixels
    
    pos = 0
    magic1, pos = int_decode(data, pos, 4) # GIM.
    magic2, pos = int_decode(data, pos, 4) # 1.00
    magic3, pos = int_decode(data, pos, 4) # PSP
    magic4, pos = int_decode(data, pos, 4) # 0
    
    byteorder = None
    is_psp = False
    
    if magic1 == GIM_MAGIC1_BIG and magic2 == GIM_MAGIC2_BIG and magic4 == 0:
        byteorder = 'big'
        if magic3 == GIM_MAGIC3_BIG:
            is_psp = True
    elif magic1 == GIM_MAGIC1_LIT and magic2 == GIM_MAGIC2_LIT and magic4 == 0:
        byteorder = 'little'
        if magic3 == GIM_MAGIC3_LIT:
            is_psp = True
    else:
        raise Exception('Invalid GIM file.')
    
    im_image = None
    im_mode = None
    im_palette = None
    im_palette_mode = None
    im_width = 0
    im_height = 0
    #im_bufsz = 0
    while pos < len(data):
        block_start = pos
        block_header, pos = read_header(data, pos, byteorder)
        block_content_start = pos
        if block_header.type == 2: # root
            pass
        elif block_header.type == 3: # picture
            pass
        elif block_header.type == 4 or block_header.type == 5: # image or palette
            image_block, pos = read_image_block(data, pos, byteorder)
            #print(image_block)
            if image_block.frame_count != 1:
                raise Exception('GIM file with more than one frame not supported.')
            for frame_index in range(image_block.frame_count):
                pos = block_content_start + image_block.next_index_block
                frame_offset, pos = int_decode(data, pos, 4, byteorder=byteorder)
                im_data = data[block_content_start + frame_offset:block_content_start + image_block.frame_data_end]
                im_partial_byte = (0, 0)
                im_data_pos = 0
                im_pixels = []
                tile_width = 0x80 // image_block.rsx_bpp
                tile_height = 0x08
                width = image_block.width
                height = image_block.height
                if image_block.pixel_order == 1:
                    width = overscan_for_tile_size(width, tile_width)
                    height = overscan_for_tile_size(height, tile_height)
                for y in range(height):
                    im_row = []
                    for x in range(width):
                        pixel_data, im_data_pos, im_partial_byte = take_pixel(im_data, im_data_pos, im_partial_byte, image_block.rsx_bpp)
                        im_row.append(pixel_data)
                    im_pixels.append(im_row)
                    if im_data_pos % image_block.rsx_pitch_align != 0:
                        im_data_pos += image_block.rsx_pitch_align - (im_data_pos % image_block.rsx_pitch_align)
                if image_block.pixel_order == 1:
                    #print("do_swap", image_block.width, image_block.height, tile_width, tile_height)
                    im_pixels = swap_tiles(im_pixels, image_block.width, image_block.height, tile_width, tile_height)
                if block_header.type == 4: # image
                    im_image = im_pixels
                    im_mode = image_block.format
                    im_width = image_block.width
                    im_height = image_block.height
                    #im_bufsz = len(im_data)
                if block_header.type == 5: # palette
                    im_palette = im_pixels
                    im_palette_mode = image_block.format
        elif block_header.type == 0xff: # fileinfo
            fileinfo_block, pos = read_fileinfo_block(data, pos, byteorder)
            if args.verbose:
                print('ProjectName:       {}'.format(fileinfo_block.project_name))
                print('UserName:          {}'.format(fileinfo_block.user_name))
                print('SavedDate:         {}'.format(fileinfo_block.saved_date))
                print('Originator:        {}'.format(fileinfo_block.originator))
        
        pos = block_start + block_header.next_block
    
    #print("image", im_pixels)
    #print("palette", im_palette)
    if im_palette is not None:
        for y in range(im_height):
            for x in range(im_width):
                im_image[y][x] = im_palette[0][im_image[y][x]]
        im_mode = im_palette_mode
    
    im = Image.new('RGBA', (im_width, im_height), 0)
    im_image = [item for sublist in im_image for item in sublist]
    im.putdata(im_image)
    #print("mode\t", im_mode, "wh\t", im_width, "x\t", im_height, "expected_buffersz\t", im_width * im_height, "buffersz\t", im_bufsz)
    
    try:
        yield im
    finally:
        im.close()
