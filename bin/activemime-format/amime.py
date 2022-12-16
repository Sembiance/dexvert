import base64
import zlib
from struct import unpack
import argparse
import email
import os
from os.path import isfile
import hashlib
import re
__has_ssdeep = False

try:
	import ssdeep
	__has_ssdeep = True
except:
	pass

__version__ = '1.0.0'
__author__ = 'Sean Wilson'

'''
----------------------------------------
Changelog
1.0.0  
 - Updated to scan input file for data blob 
 - Changed to emit sha256 hashes 
 - Minor updates
0.0.2
 - Minor updates to output
 - Updated script to include ssdeep hash
0.0.1
 - Initial Release
----------------------------------------
Copyright (c) 2016-2019 Sean Wilson
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

Copyright (c) 2016 Sean Wilson - PhishMe
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
----------------------------------------
'''

class ActiveMimeDocument(object):

	@staticmethod
	def is_activemime(doc):
		if doc.startswith('QWN0aXZlTWltZQ') or doc.startswith('ActiveMime'):
			return True
		else:
			return False

	@staticmethod
	def is_base64(doc):
		if doc.startswith('QWN0aXZlTWltZQ'):
			return True
		else:
			return False

	def __init__(self, mimedoc, b64encoded=False):

		self.rawdoc = mimedoc

		if b64encoded:
			self.rawdoc = base64.b64decode(mimedoc)

		self.header  = None
		self.unknown_a = None
		self.unknown_b = None
		self.unknown_c = None
		self.unknown_d = None
		self.vba_tail_type = None
		self.has_vba_tail = False
		self.compressed_size = 0
		self.size = 0
		self.compressed_data = None
		self.data = None
		self.is_ole_doc = False
		self._parsedoc()



	def _parsedoc(self):
		cursor = 0
		self.header = self.rawdoc[0:12]

		# Should be 01f0
		self.unknown_a =  self.rawdoc[12:14].encode('hex')

		field_size = unpack('<I', self.rawdoc[14:18])[0]
		cursor = 18

		# Should be ffffffff
		self.unknown_b = self.rawdoc[cursor:cursor+field_size].encode('hex')
		cursor += field_size

		# Should be {x}0000{y}f0
		self.unknown_c = self.rawdoc[cursor:cursor+4].encode('hex')
		cursor += 4

		self.compressed_size = unpack('<I', self.rawdoc[cursor:cursor + 4])[0]
		cursor += 4

		field_size_d = unpack('<I', self.rawdoc[cursor:cursor+4])[0]
		cursor += 4

		field_size_e = unpack('<I', self.rawdoc[cursor:cursor+4])[0]
		cursor += 4

		# Should be 00000000 or 00000000 00000001
		self.unknown_d = self.rawdoc[cursor:cursor + field_size_d].encode('hex')
		cursor += field_size_d

		self.vba_tail_type = unpack('<I', self.rawdoc[cursor:cursor + field_size_e])[0]
		cursor += field_size_e

		if self.vba_tail_type == 0:
			self.has_vba_tail = True

		self.size = unpack('<I', self.rawdoc[cursor:cursor + 4])[0]
		cursor += 4

		self.compressed_data = self.rawdoc[cursor:]
		self.data = zlib.decompress(self.compressed_data)

		if self.data[0:4].encode('hex') == 'd0cf11e0':
			self.is_ole_doc = True

	def __str__(self):
		str = "ActiveMime Document Size: %d\n" % len(self.rawdoc)
		str += "Compressed Size:         %d\n" % self.compressed_size
		str += "Uncompressed Size:       %d\n" % self.size
		return str

class ActimeMimeParser(object):
	"""

	"""

	def __init__(self):
		self.re_mimeblob = re.compile("(QWN0aXZlTWltZQ.*?)<", re.DOTALL)

	def check_header(self, doc_data):
		"""
		Some of the malicious documents have junk text inserted at the
		beginning of the document.
		Check to make sure the document starts with Mime-Version
		"""
		if doc_data.startswith("MIME-Version"):
			return doc_data
		else:
			# Attempt to find the actual header and update the data start.
			offset = doc_data.find("MIME-Version")
			if offset:
				return doc_data[offset:]

			# If all else fails return the input
			return doc_data

	def parse_mime(self, in_data, debug=False):
		"""
		Attempt to Parse the input data as MIME parts


		:param in_data: input data
		:param debug:
		:return:
		"""
		msg = email.message_from_string(self.check_header(in_data))

		for part in msg.walk():
			if part.get_content_type() == 'application/x-mso':
				payload = part.get_payload()

				if ActiveMimeDocument.is_activemime(payload):
					decoded = base64.b64decode(payload)
					return ActiveMimeDocument(decoded)

				else:
					# I've seen junk text within parts to throw off sandboxes/automated analysis
					# Attempt to seek to the header
					if 'QWN0aXZlTWltZQ' in payload:
						offset = payload.find("QWN0aXZlTWltZQ")
						doc = payload[offset:]
						decoded = base64.b64decode(doc)
						amd = ActiveMimeDocument(decoded)
						return amd

	def scan_document(self, in_data):
		"""
		Scan the document for the ActiveMime content.

		:param in_data:
		:return:
		"""
		search_result = self.re_mimeblob.search(in_data)
		if search_result:
			decoded = base64.b64decode(search_result.group(1))
			if ActiveMimeDocument.is_activemime(decoded):
				return ActiveMimeDocument(decoded)

	def process_file(self, mime_file):
		"""
		Process the passed file.

		:param mime_file:
		:return:
		"""

		with open(mime_file, 'rb') as inf:
			data = inf.read()

		return self.process(data)

	def process(self, data):
		"""
		Process the input data and return the ActiveMime content.

		:param data:
		:return:
		"""

		result = self.parse_mime(data)

		if result:
			return result

		result = self.scan_document(data)
		if result:
			return result

		return None



def formatmsg(string, color):
	# 31 - Error
	# 33 - Warning
	# 37 - Info
	# http://www.tldp.org/HOWTO/Bash-Prompt-HOWTO/x329.html

	if color == 'red':
		return "\033[31m%s \033[0m" % string
	elif color == 'green':
		return "\033[32m%s \033[0m" % string
	elif color == 'yellow':
		return "\033[33m%s \033[0m" % string
	elif color == 'white':
		return "\033[37m%s \033[0m" % string
	else:
		return string


def main():

	parser = argparse.ArgumentParser(description="Scan  document for embedded objects.")
	parser.add_argument("file", help="File to process.")
	parser.add_argument('--extract', dest='extract', help="Extract ActiveMime Objects.")

	args = parser.parse_args()

	print(' ActiveMime Helper')
	print(' -----------------')
	print(' [*] Loading file....%s ' % args.file)

	if isfile(args.file):
		f = open(args.file, 'rb')
		doc = f.read()
		if ActiveMimeDocument.is_activemime(doc):
			amd = ActiveMimeDocument(doc, ActiveMimeDocument.is_base64(doc))

		else:
			print(formatmsg(' [*] File is not an ActiveMime Document', 'yellow'))
			print(' [*] Parsing as MIME Document')
			amp = ActimeMimeParser()
			amd = amp.process_file(doc)

		if amd:
			print(' ------------------------------------------------------')
			print('  ActiveMime Document')
			print('   - {:18}{}'.format('Size:', len(amd.rawdoc)))
			print('   - {:18}{}'.format('SHA256:', hashlib.sha256(amd.rawdoc).hexdigest()))

			if __has_ssdeep:
				print('   - {:18}{}'.format('ssdeep:', ssdeep.hash(amd.rawdoc)))

			print('  Payload Data')
			print('   - {:18}{}'.format('Compressed Size:', amd.compressed_size))
			print('   - {:18}{}'.format('Size:', amd.size))
			print('   - {:18}{}'.format('SHA256:', hashlib.sha256(amd.data).hexdigest()))

			if __has_ssdeep:
				print('   - {:18}{}'.format('Data ssdeep:', ssdeep.hash(amd.data)))

			print('   - {:18}{}'.format('VBA Tail:', amd.has_vba_tail))
			print('   - {:18}{}'.format('OLE Doc:', amd.is_ole_doc))
			print(' ------------------------------------------------------')

			if args.extract is not None:
				print ' [*] Writing decoded Project file'
				with open(os.path.join(args.extract, hashlib.sha256(amd.data).hexdigest()), 'wb') as out:
					out.write(amd.data)

	else:
		print formatmsg(' [!] File does not exist...exiting', 'red')
		return

if __name__ == '__main__':
	main()
