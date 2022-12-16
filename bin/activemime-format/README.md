# ActiveMime File Format
Research and documentation into the ActiveMime binary file format.

The file format contains 2 parts. A header which contains information such as the data size, compressed size and other metadata and a zlib compressed data block.

## Background
ActiveMime is an undocumented Microsoft file format often seen used to encode Office Macros.

Current IR scripts often seek to the zlib header within the data block or use a hard coded index of 0x32 (50). This library and script hopes to help analysts better process ActiveMime files and detect malformed samples and other anomolies.

If you have additional details, want to collaborate or corrections about the format feel free to reach out!

## ActiveMime Header
```
    Offset   Sample Bytes                Size      Desc
    -------------------------------------------------------------------------------
    00:12    4163746976654d696d650000  | 12   |  Header 'ActiveMime'
    12:14    01f0                      |  2   |  Unknown -- always 01f0 -- Version?
    14:18    04000000                  |  4   |  FieldSize?
    18:22    ffffffff                  |  4   |  Always ffffffff
    22:26    {x}0000{y}f0              |  2   |  x observed as {0,1,2,3,4,5,6,B,A}
                                       |      |  y observed as {6,7,8} -- Note: Usually 7 other values could indicate a malformed document
    26:30    xxxxxxxx                  |  4   |  Length of zlib compressed data
    30:34    04000000                  |  4   |  FieldSize  -- Observed as 4 or 8..almost always 4
    34:38    04000000                  |  4   |  FieldSize  -- Always observed as 04000000
    38:xx    00000000                  |  4|8 |  00000000          With size (4)
                                       |      |  00000000 10000000 With Size (8)
    xx:xx    0{x}000000                |  4   |  Seems to indicate if the block includes unencoded vb strings at the end.
                                       |      |  00000000 - Block contains some unencoded VB Project Strings
                                       |      |  02000000 - Block does not contains unencoded VB Project Strings
                                       |      |  tail includes unencoded VB Project Data
    xx:xx    xxxxxxxx                  |  4   |  Uncompressed Size
    xx:xx    789ced7d                  | Var  |  Compressed data
```

##Usage
The script can be either used as a commandline tool or library. When being used as a script it simply requires the name of the file to scan. This can either be a mime document (MHTML file etc) or an ActiveMime blob.

Example: 
```
python amime.py myfile
```

Passing the parameter --extract will extract the vbaProject.bin file to the current directory.
```
usage: amime.py [-h] [--extract] file

Scan document for embedded objects.

positional arguments:
  file        File to process.

optional arguments:
  -h, --help  show this help message and exit
  --extract   Extract ActiveMime Object.
  
```
## Future Research
 - Prove out VBA Tail var
 - Identify what generates values in [22:26]

## References
 - https://isc.sans.edu/forums/diary/XML+A+New+Vector+For+An+Old+Trick/19423/
 - https://www.fireeye.com/blog/threat-research/2015/06/evolution_of_dridex.html
 - https://en.wikipedia.org/wiki/Zlib
