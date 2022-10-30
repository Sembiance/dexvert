import struct
import argparse
import os

header_format = '2shi'
header_size = struct.calcsize(header_format)

entry_format = '16si'
entry_size = struct.calcsize(entry_format)

def unpack(fileName):
	#BASE_NAME = os.path.splitext(os.path.basename(fileName))[0]

	#os.mkdir(BASE_NAME)

	with open(fileName, 'rb') as f:
		[magic_bytes, file_count, package_size] = struct.unpack(header_format, f.read(header_size))

		assert magic_bytes == b'PA'
		assert file_count > 0
		assert package_size > 0

		FILES = []

		for i in range(0, file_count, 1):
			[file_name, file_size] = struct.unpack(entry_format, f.read(entry_size))
			
			FILES.append([
				file_name.decode("ascii").rstrip('\x00'),
				file_size
			])
		
		for file_name, file_size in FILES:
			file_data = bytearray(f.read(file_size))

			with open(file_name, 'wb') as new_file:
				new_file.write(file_data)

if __name__ == '__main__':
	parser = argparse.ArgumentParser(
                    prog = 'dpk Unpacker',
                    description = 'Unpacks .dpk packages')
	parser.add_argument('INPUT_FILE')
	args = parser.parse_args()
	
	unpack(args.INPUT_FILE)
