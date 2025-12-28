#!/usr/bin/env python3

import argparse
import datetime
import gim
import io
import json
import os
import sys
import zlib
from bitconv import str_encode, int_encode, str_decode, int_decode
from PIL import Image

PTF_MAGIC = 0x0000010046545000 # \x00PTF\x00\x01\x00\x00
PTF_PSP_VERSION = '6.20'

def ptf_create(file, args):
    def png2gim(infilepath, outfilepath, args):
        #try:
            #print(infilepath, outfilepath, args)
            with open(infilepath, 'rb') as f:
                bin_data = gim.png2gim(f.read(), args)
                if not os.path.exists(outfilepath) or args.replace:
                    with open(outfilepath, 'wb') as f:
                        f.write(bin_data)
                return bin_data
        #except Exception as ex:
        #    print('{}: {}'.format(os.path.basename(outfilepath), ex), file=sys.stderr)
        #    return bytes()

    def png2pil(infilepath, outfilepath, args):
        try:
            #print(infilepath, outfilepath, args)
            with Image.open(infilepath) as im:
                temp = io.BytesIO()
                im.save(temp, format=outfilepath[-3:])
                if not os.path.exists(outfilepath) or args.replace:
                    im.save(outfilepath)
                return bytes(temp)
        except Exception as ex:
            print('{}: {}'.format(os.path.basename(outfilepath), ex), file=sys.stderr)
            return bytes()
    
    data = bytes()
    pos = 0
    
    json_fname = os.path.join(file, 'index.json')
    index_info = None
    if os.path.isfile(json_fname):
        with open(json_fname, 'r') as jsonf:
            index_info = json.loads(jsonf.read())
    else:
        raise Exception('To create theme from this directory, require an index.json file describing its contents.')
    
    data, pos = int_encode(data, pos, PTF_MAGIC, 8)
    if 'name' in index_info:
        data, pos = str_encode(data, pos, index_info['name'], 128, encoding='utf-8')
    else:
        raise Exception('PTF file requires "name" value.')
    if 'file_name' in index_info:
        data, pos = str_encode(data, pos, index_info['file_name'], 48, encoding='utf-8')
    else:
        raise Exception('PTF file requires "file_name" value.')
    if 'psp_version' in index_info:
        data, pos = str_encode(data, pos, index_info['psp_version'], 8, encoding='utf-8')
    else:
        data, pos = str_encode(data, pos, PTF_PSP_VERSION, 8, encoding='utf-8')
    if 'version' in index_info:
        data, pos = str_encode(data, pos, index_info['version'], 8, encoding='utf-8')
    else:
        data, pos = str_encode(data, pos, '', 8, encoding='utf-8')
    if 'value8' in index_info:
        data, pos = int_encode(data, pos, index_info['value8'], 4)
    else:
        data, pos = int_encode(data, pos, 8, 4)
    
    while pos < 0x100:
        data, pos = int_encode(data, pos, 0, 4)
    
    objs = {}
    start_offsets = {}
    if 'categories' in index_info:
        for obj_idx in range(8):
            if str(obj_idx) in index_info['categories']:
                obj = index_info['categories'][str(obj_idx)]
                start_offsets[obj_idx] = pos
                objs[obj_idx] = obj
            elif obj_idx < 5:
                raise Exception('PTF file requires category {}.'.format(obj_idx))
            data, pos = int_encode(data, pos, 0, 4)
    else:
        raise Exception('PTF file requires "categories" definitions.')
    
    size_offset = -1
    obj_start_offset = -1
    for obj_idx, obj in objs.items():
        # save previous object size
        if size_offset > 0:
            data, _   = int_encode(data, size_offset, pos - (obj_start_offset + 0x20), 4)
        # save offset to start of block
        obj_start_offset = pos
        # save pointer to here
        data, _   = int_encode(data, start_offsets[obj_idx], obj_start_offset, 4)
        # save object header
        data, pos = int_encode(data, pos, obj_idx, 2)
        data, pos = int_encode(data, pos, len(obj.items()), 2)
        size_offset = pos
        data, pos = int_encode(data, pos, 0, 4)
        data, pos = int_encode(data, pos, obj_start_offset + 0x20, 4)
        while pos < obj_start_offset + 0x20:
            data, pos = int_encode(data, pos, 0, 4)
        
        # save each element of this object
        for sub_idx_s, sub in obj.items():
            sub_idx = int(sub_idx_s)
            if 'file_type' in sub:
                file_type = int(sub['file_type'])
            else:
                raise Exception('File {}_{} requires a file type.'.format(obj_idx, sub_idx))
            
            # parse item
            bin_data = bytes()
            if obj_idx == 0 and sub_idx == 2: # special 4-byte value indicating background_mode
                file_data = None
                if 'file_data' in sub:
                    file_data = int(sub['file_data'])
                if 'background_mode' in index_info:
                    file_data = int(index_info['background_mode'])
                if args.set_background_mode >= 0:
                    file_data = args.set_background_mode
                if file_data is None:
                    raise Exception('File {}_{} must specify a background mode. Specify it in index.json or with --set-background-mode.'.format(obj_idx, sub_idx))
                bin_data, _ = int_encode(bin_data, 0, file_data, 4)
                file_type = 5
                file_comp = 2
                file_size = 4
                file_ucsize = 4
            else:
                if 'file_comp' in sub:
                    file_comp = int(sub['file_comp'])
                    if args.set_compression_mode >= 0 and args.set_compression_mode <= 2 and file_comp > 0:
                        file_comp = args.set_compression_mode
                    if file_comp == 1 or file_comp < 0 or file_comp > 2:
                        print('Warning: File {}_{} cannot be compressed with mode {comp}. Specify the mode in index.json or with --set-compression-mode. Using 2 (ZLIB).'.format(obj_idx, sub_idx, comp=file_comp))
                        file_comp = 2
                else:
                    file_comp = 2
                if 'file_name' in sub:
                    file_name = sub['file_name']
                else:
                    sub_ext = '.bin'
                    if file_type == 0: # PNG
                        sub_ext = '.png'
                    elif file_type == 1: # JPEG
                        sub_ext = '.jpg'
                    elif file_type == 2: # TIFF
                        sub_ext = '.tif'
                    elif file_type == 3: # GIF
                        sub_ext = '.gif'
                    elif file_type == 4: # BMP
                        sub_ext = '.bmp'
                    elif file_type == 5: # GIM
                        sub_ext = '.gim'
                    file_name = '{:d}_{:04d}.{}'.format(obj_idx, sub_idx, sub_ext)
                
                file_path = os.path.join(file, file_name)
                
                if args.convert_to_png:
                    # check for PNG replacement
                    if file_name[-4:] == '.png':
                        sub_conv = None
                    elif file_name[-4:] == '.gim':
                        sub_conv = png2gim
                    else:
                        sub_conv = png2pil
                    file_name_png = file_name[:-4] + '.png'
                    file_path_png = os.path.join(file, file_name_png)
                    
                    if sub_conv and os.path.isfile(file_path_png):
                        bin_data = sub_conv(file_path_png, file_path, args)
                
                if len(bin_data) == 0:
                    if os.path.isfile(file_path):
                        with open(file_path, 'rb') as f:
                            bin_data = f.read()
                    else:
                        raise Exception('{}: File specified in {}_{} not found.'.format(file_name, obj_idx, sub_idx))
                
                file_ucsize = len(bin_data)
                if file_comp == 2:
                    bin_data = zlib.compress(bin_data, level=args.zlib_compression_level)
                if len(bin_data) % 4 != 0:
                    bin_data, _ = int_encode(bin_data, len(bin_data), 0, 4 - (len(bin_data) % 4))
                file_size = len(bin_data)
            
            sub_start_offset = pos
            #save element header
            data, pos = int_encode(data, pos, sub_idx, 2)
            data, pos = int_encode(data, pos, 0, 2)
            data, pos = int_encode(data, pos, file_type, 2)
            data, pos = int_encode(data, pos, file_comp, 2)
            data, pos = int_encode(data, pos, file_size, 4)
            data, pos = int_encode(data, pos, file_ucsize, 4)
            while pos < sub_start_offset + 0x20:
                data, pos = int_encode(data, pos, 0, 4)
            
            data += bin_data
            pos += file_size
    if size_offset > 0:
        data, _   = int_encode(data, size_offset, pos - (obj_start_offset + 0x20), 4)
    
    file += '.ptf'
    if os.path.isfile(file) and not args.replace:
        raise Exception('Use "-r" to replace existing file.')
    if os.path.isdir(file):
        raise Exception('Cannot save theme. Existing directory in the way.')
    with open(file, 'wb') as f:
        f.write(data)

def ptf_extract(file, args):
    def gim2png(data, outfilepath, args):
        try:
            with gim.gim2png(data, args) as im:
                im.save(outfilepath)
        except Exception as ex:
            print('{}: {}'.format(os.path.basename(outfilepath), ex), file=sys.stderr)

    def pil2png(data, outfilepath, args):
        try:
            with Image.open(io.BytesIO(data)) as im:
                im.save(outfilepath)
        except Exception as ex:
            print('{}: {}'.format(os.path.basename(outfilepath), ex), file=sys.stderr)
    
    data = None
    with open(file, 'rb') as f:
        data = f.read()
    
    pos = 0
    magic, pos = int_decode(data, pos, 8)
    if magic != PTF_MAGIC:
        print('{}: Not a valid version 1.0 PTF theme.'.format(os.path.basename(file)), file=sys.stderr)
        return
    
    p = {}
    p['name'],          pos = str_decode(data, pos, 128, encoding='utf-8')
    p['file_name'],     pos = str_decode(data, pos, 48, encoding='utf-8')
    p['psp_version'],   pos = str_decode(data, pos, 8, encoding='utf-8')
    p['version'],       pos = str_decode(data, pos, 8, encoding='utf-8')
    p['value8'],        pos = int_decode(data, pos, 4)
    
    p['categories'] = {}
    
    if args.verbose:
        print('Theme: {}'.format(os.path.basename(file)))
        print('    Name:          {}'.format(p['name']))
        print('    File Name:     {}'.format(p['file_name']))
        print('    PSP Version:   {}'.format(p['psp_version']))
        print('    PTF Version:   {}'.format(p['version']))
        print('    Unknown 1:     {}'.format(p['value8']))
    
    pos = 0x100
    offsets = []
    while True:
        val, pos = int_decode(data, pos, 4)
        if val == 0:
            break
        offsets.append(val)
    
    #print('    Object Count:  {}'.format(len(offsets)))
    
    offsets.append(len(data))
    
    for index in range(len(offsets)-1):
        pos = offsets[index]
        obj_idx,     pos = int_decode(data, pos, 2) # index (0, 1, 2, 3, 4)
        obj_subcnt,  pos = int_decode(data, pos, 2) # number of sub-objects
        obj_size,    pos = int_decode(data, pos, 4) # size (excluding 32-byte header)
        obj_foff,    pos = int_decode(data, pos, 4) # offset to start of object (excluding 32-byte header)
        
        #os.makedirs(file[:-4], exist_ok=True)
        #obj_fname = os.path.join(file[:-4], '{}.bin'.format(obj_idx))
        #if args.verbose:
        #    print('    Object #{}:     '.format(obj_idx, os.path.basename(obj_fname)))
        #print('        Itm Count: {}'.format(obj_subcnt))
        
        objd = data[obj_foff:obj_foff+obj_size]
        #with open(obj_fname, 'wb') as objf:
        #    objf.write(objd)
        obj_pos = 0
        for sub_index in range(obj_subcnt):
            sub_idx,     obj_pos = int_decode(objd, obj_pos, 2) # index
            sub_val0,    obj_pos = int_decode(objd, obj_pos, 2) # 0
            sub_filetp,  obj_pos = int_decode(objd, obj_pos, 2) # file type (0=png, 1=jpeg, 2=tiff, 3=gif, 4=bmp, 5=gim)
            sub_comp,    obj_pos = int_decode(objd, obj_pos, 2) # decompress mode (1=???, 2=zlib)
            sub_size,    obj_pos = int_decode(objd, obj_pos, 4) # size (excluding 32-byte header)
            sub_ucsize,  obj_pos = int_decode(objd, obj_pos, 4) # uncompressed size
            obj_pos += 0x10
            
            subd = objd[obj_pos:obj_pos+sub_size]
            #if sub_comp == 1 and sub_size < sub_ucsize:
                #subd = gzip.decompress(subd)
            if sub_comp == 2 and sub_size < sub_ucsize:
                subd = zlib.decompress(subd)
            
            sub_ext = '.bin'
            sub_conv = pil2png
            if sub_filetp == 0: # PNG
                sub_ext = '.png'
                sub_conv = None
            elif sub_filetp == 1: # JPEG
                sub_ext = '.jpg'
            elif sub_filetp == 2: # TIFF
                sub_ext = '.tif'
            elif sub_filetp == 3: # GIF
                sub_ext = '.gif'
            elif sub_filetp == 4: # BMP
                sub_ext = '.bmp'
            elif sub_filetp == 5: # GIM
                sub_ext = '.gim'
                sub_conv = gim2png
            else:
                sub_conv = None
            
            if not obj_idx in p['categories']:
                p['categories'][obj_idx] = {}
            if len(subd) == 4 and obj_idx == 0 and sub_idx == 2:
                # special background mode handling
                sub_f4b, _ = int_decode(subd, 0, 4)
                p['background_mode'] = sub_f4b
                p['categories'][obj_idx][sub_idx] = {'file_type': -1, 'file_data': sub_f4b, 'file_length': 4, 'file_comp': 0}
                continue
            else:
                if len(subd) <= 4:
                    sub_ext = '.bin'
                    sub_conv = None
                
                os.makedirs(file[:-4], exist_ok=True)
                sub_fname = os.path.join(file[:-4], '{}_{:04d}{}'.format(obj_idx, sub_idx, sub_ext))
                
                p['categories'][obj_idx][sub_idx] = {'file_type': sub_filetp, 'file_name': os.path.basename(sub_fname), 'file_length': sub_ucsize, 'file_comp': sub_comp}
            
            if args.verbose:
                print('        Item #{:03d}: '.format(sub_idx, os.path.basename(sub_fname)))
                if sub_comp == 0 or sub_size == sub_ucsize:
                    sub_comp_s = 'NO COMP'
                elif sub_comp == 2:
                    sub_comp_s = 'ZLIB'
                else:
                    sub_comp_s = str(sub_comp)
                print('            Data:  {} ({})  {} ({}->{})'.format(sub_filetp, sub_ext, sub_comp_s, sub_size, sub_ucsize))
            
            with open(sub_fname, 'wb') as subf:
                subf.write(subd)
            
            if args.convert_to_png and sub_conv:
                sub_f, _ = os.path.splitext(sub_fname)
                sub_fname = sub_f + '.png'
                if args.verbose:
                    print('            Conv:  {}'.format(os.path.join(os.path.basename(file[:-4]), os.path.basename(sub_fname))))
                
                sub_conv(subd, sub_fname, args)
            
            obj_pos += sub_size
    
    os.makedirs(file[:-4], exist_ok=True)
    json_fname = os.path.join(file[:-4], 'index.json')
    if args.verbose:
        print('    JSON:          {}'.format(os.path.join(os.path.basename(file[:-4]), 'index.json')))
    with open(json_fname, 'w') as jsonf:
        jsonf.write(json.dumps(p, indent=4, ensure_ascii=False))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='PTF extraction and creation.')
    parser.add_argument('input', nargs='+',
                        help='File(s) to process. Pass a .ptf file to extract it (must be valid) and a folder to create a new one (must have all required parts including index.json; see an existing file to see what is required).')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Verbose output.')
    parser.add_argument('-c', '--convert-to-png', '--convert-from-png', action='store_true',
                        help='Whether to convert images to PNG. When creating a theme, looks for PNG first, then expected native formats (BMP, GIM) next.')
    parser.add_argument('-r', '--replace', action='store_true',
                        help='Create: Whether to replace existing theme.')
    parser.add_argument('--set-background-mode', type=int, default=-1,
                        help='Create: Replace the background mode value with this value (number from 0-12).')
    parser.add_argument('--set-compression-mode', type=int, default=-1,
                        help='Create: Replace the compression mode used with this value (0=none, 1=RLZ, 2=ZLIB).')
    parser.add_argument('-Z', '--zlib-compression-level', type=int, default=-1,
                        help='Create: Use the provided ZLIB compression level (number from 0-9).')
    parser.add_argument('--gim-byteorder', default='little',
                        help='Create: Use the provided GIM byte order when converting (little or big; default: little).')
    parser.add_argument('--gim-no-fileinfo', action='store_true',
                        help='Create: If set, don\'t provide a GIM fileinfo block at all when converting to GIM.')
    parser.add_argument('--gim-project-name', default='',
                        help='Create: Use the provided GIM project name value when converting to GIM.')
    parser.add_argument('--gim-user-name', default='',
                        help='Create: Use the provided GIM user name value when converting to GIM.')
    parser.add_argument('--gim-saved-date', type=lambda s: datetime.datetime.strptime(s, gim.GIM_SAVED_DATE_FORMAT), default=None,
                        help='Create: Use the provided GIM saved date value when converting to GIM (if not provided, use current date; if not valid, use blank).')
    parser.add_argument('--gim-originator', type=str, default=None,
                        help='Create: Use the provided GIM originator value when converting to GIM (if not provided, use this project\'s name).')
    parser.add_argument('--gim-pixel-order', default=0,
                        help='Create: Use the provided GIM pixel order when converting to GIM (0=normal, 1=tiled/faster).')
    args = parser.parse_args()
    
    found_any = None
    for file in args.input:
        if file.endswith('.ptf') and os.path.isfile(file):
            print(os.path.basename(file))
            try:
                ptf_extract(file, args)
            except Exception as ex:
                print('{}: {}'.format(os.path.basename(file), ex), file=sys.stderr)
            found_any = True
        elif os.path.isdir(file):
            print(os.path.basename(file))
            #try:
            ptf_create(file, args)
            #except Exception as ex:
            #    print('{}: {}'.format(os.path.basename(file), ex), file=sys.stderr)
            found_any = True
        else:
            if found_any is None:
                found_any = file
    
    if found_any is None:
        print('No files provided.', file=sys.stderr)
    elif found_any != True:
        print('{}: File not found.'.format(found_any), file=sys.stderr)
