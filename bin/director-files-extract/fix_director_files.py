#!/usr/bin/python3
import os
from io import BytesIO
from struct import unpack
from sys import argv

def read_ident(f):
	end = None
	sig = f.read(4)
	if sig == b'XFIR':
		end = '<'
	elif sig == b'RIFX':
		end = '>'
	return end

def read_tag(f, endian='<'):
	s = f.read(4)
	if endian == '<':
		s = s[::-1]
	return(s.decode('ascii'))

def fix_filename(filename, file_type):
	if filename.lower()[-4:] == '.dir':
		if file_type == 'MV93':
			filename = filename[:-4] + '.dxr'
		elif file_type == 'FGDM':
			filename = filename[:-4] + '.dcr'
	elif filename.lower()[-4:] == '.cst':
		if file_type == 'MV93':
			filename = filename[:-4] + '.cxt'
		elif file_type == 'FGDC':
			filename = filename[:-4] + '.cct'
	return filename


if len(argv) > 1:
	for i in range(1, len(argv)):
		filename = argv[i]
		file_obj = open(filename, 'rb').read()
		file_bytes = BytesIO(file_obj)
		endian = read_ident(file_bytes)
		if endian == None:
			print('Not a Director file: ' + filename)
			continue
		file_bytes.seek(0, 2) # Jump to the end of the file
		file_size = file_bytes.tell() # Get the current position
		file_bytes.seek(0x4)
		correct_file_size, = unpack(endian+'I', file_bytes.read(0x4))
		# Length indicated by the header does not include the header itself
		correct_file_size += 8 
		if file_size < correct_file_size:
			print('Unable to fix file: ' + filename + ' - the file is missing ' + str(correct_file_size - file_size) + ' bytes!')
			continue
		elif file_size > correct_file_size:
			print('Trimming ' + str(file_size - correct_file_size) + ' bytes from file: ' + filename)
		file_bytes.seek(0x8)
		file_type = read_tag(file_bytes, endian)
		correct_filename = fix_filename(filename, file_type)
		file_bytes.seek(0)
		correct_file_bytes = file_bytes.read(correct_file_size)
		if filename != correct_filename or file_size != correct_file_size:
			os.remove(filename)
			print('Writing file: ' + correct_filename)
			open(correct_filename, 'wb').write(correct_file_bytes)
		else:
			print('File length and extension are correct: ' + filename)
else:
	print('Usage: python fix_director_files.py file1.dxr file2.dcr ...')

