#!/usr/bin/env python3
#
# Created by Jason Brooks: www.muckypaws.com and www.muckypawslabs.com
#            7th Febraury 2024
#
# There's much that can be done to optimise the code
#   Python Coders have to be clinically insane...
#       I mean seriously...
#       how difficult does it have to be to perform bitwise operations
#       On Bytes?
#       Apparently F**king difficult...
#       Any normal language... result = byte1 & Byte2
#       PYTHON Devs...
#           Hold Our Beer...
#               result = bytes([a & b for a, b in zip(abytes[::-1], bbytes[::-1])][::-1])
#       because... that's logical... init? ffs
#
#   Did I mention how I'm not enjoying Python right now?
#
# V0.02 - 9th February 2024      - A BIT crazy Edition.
#                                  Added code to view directory listing
#                                  on DSK Files.
# V0.02 - 10th February 2024     - Getting Head Edition.
#                                  Getting File Information
#                                  Load Address, Length and Execution +
#                                  Filetype
# V0.03 - 10th February 2024     - Bourne Legacy Edition.
#                                  Running tests against 11,000 disks from the community
#                                  highlighted inconsistencies with file formats
#                                  Circa 1997, in addition to a number of corrupt disks
#                                  Encoded in the domain.
#                                  Added more processing to detect these anomalies
#                                  Report and handle more gracefully.
# V0.04 - 11th February 2024     - Clive Mobile Edition
#                                  So how much extra effort was required to include
#                                  PLUS3DOS support for the ZX Spectrum Format Disks?
#                                  Not much it seems.
#                                  Produce a list of files, with Load Address, Param 1
#                                  Param2 info.
#                                  Still experimental...
# V0.04 - 11th February 2024     - Dulux Edition
#                                  Bit of code tidy up.
#                                  and add some terminal colour too.
# V0.04 - 13th February 2024     - Into the Format
#                                  Added new parameters to create New DSK Images.
#                                  Support for Amstrad CPC DATA, Vendor, IBM
#                                              ZX Spectrum +3 Standard Disk
# V0.05 - 15th February 2024     - Nearly Headless Nick Edition
#                                  Added Support for Headerless Files for Amstrad CPC
#                                  Can only report on the number of records * 128 bytes 
#                                  Recorded in the AMSDOS Directory Descriptor
#                                  Detection isn't 100%, i.e. if the FILENAME matches the
#                                  the first 12 bytes in a record, it's going to misreport.
#                                  Also... Changed the order of the Enhanced File Info Output
# V0.05 - 16th February 2024     - Nearly Headless Nick Edition V2
#                                  Discovered that |REN files will contain different filename
#                                  to the directory entry to that of the file entry...
#                                  My method of detection was pants.  After a protracted discussion
#                                  with my good friend  @DevilMarkus, (I'm like a neanderthal bashing
#                                  stones compared to his programming prowess...) He pointed out the 
#                                  error of my ways, that solved that problem!
#
#                                  Added functionality to extract Amstrad CPC Files from a DSK 
#                                  image to your local drive
#                                  --- STILL UNDER TESTING ---
# V0.05 - 10th March 2024        - Old School Classics Edition
#                                  Richard Deane identified CP/M programs are not extracted correctly
#                                  Temporary workaround to extract the full binary to cluster size
#                                  due to differing header information based on CP/M file type.
#                                  added the -cpm command line option, required to extract CPM Files.
'''
    Want to run this tool over multiple files?
    linux use: 
        #!/bin/bash
        find ./AllJason -name "*.dsk" -type f  -exec python3 DSKInfoV3.py -dir -d  {} \; > FileInfoList.txt
'''
# pylint: disable=line-too-long

import argparse
import os
import sys
import struct
from datetime import datetime

CEND      = '\33[0m'
CBOLD     = '\33[1m'
CITALIC   = '\33[3m'
CURL      = '\33[4m'
CBLINK    = '\33[5m'
CBLINK2   = '\33[6m'
CSELECTED = '\33[7m'

CBLACK  = '\33[30m'
CRED    = '\33[31m'
CGREEN  = '\33[32m'
CYELLOW = '\33[33m'
CBLUE   = '\33[34m'
CVIOLET = '\33[35m'
CBEIGE  = '\33[36m'
CWHITE  = '\33[37m'

CBLACKBG  = '\33[40m'
CREDBG    = '\33[41m'
CGREENBG  = '\33[42m'
CYELLOWBG = '\33[43m'
CBLUEBG   = '\33[44m'
CVIOLETBG = '\33[45m'
CBEIGEBG  = '\33[46m'
CWHITEBG  = '\33[47m'

CGREY    = '\33[90m'
CRED2    = '\33[91m'
CGREEN2  = '\33[92m'
CYELLOW2 = '\33[93m'
CBLUE2   = '\33[94m'
CVIOLET2 = '\33[95m'
CBEIGE2  = '\33[96m'
CWHITE2  = '\33[97m'

CGREYBG    = '\33[100m'
CREDBG2    = '\33[101m'
CGREENBG2  = '\33[102m'
CYELLOWBG2 = '\33[103m'
CBLUEBG2   = '\33[104m'
CVIOLETBG2 = '\33[105m'
CBEIGEBG2  = '\33[106m'
CWHITEBG2  = '\33[107m'

CONST_AMSTRAD       = 0
CONST_PLUS3DOS      = 1

CONST_DATA_FORMAT       = 0
CONST_VENDOR_FORMAT     = 1
CONST_IBM_FORMAT        = 2
CONST_IBM_ZXSPECTRUM    = 3

CONST_DATA_BIT      = 1
CONST_VENDOR_BIT    = 2
CONST_IBM_BIT       = 4
CONST_PLUS3DOS_BIT  = 8

DEFAULT_START_TRACK = 0
DEFAULT_END_TRACK   = 42
DEFAULT_HEAD        = 0
DEFAULT_DSK_FORMAT  = 0

DEFAULT_DSK_TYPE    = "DATA"

DEFAULT_SYSTEM      = CONST_AMSTRAD
GLOBAL_CORRUPTION_FLAG = 0

DEFAULT_ISCPM = False 

DSKDictionary = {}
DSKDataDictionary = {}
DSKSectorDictionary = {}
DSKSectorDataDictionary = {}


#
# Helper Class for creating easy structs.
# Nabbed from the O'Reilly Book
#       Python Cookbook 3rd Edition - Recipes for Mastering Python 3
#       ISBN 978-1-449-34037-7
#
class SizedRecord:
    def __init__(self, bytedata):
        self._buffer = memoryview(bytedata)

    @classmethod
    def from_file(cls, f, size_fmt, includes_size=True):
        sz_nbytes = struct.calcsize(size_fmt)
        sz_bytes = f.read(sz_nbytes)
        sz, = struct.unpack(size_fmt, sz_bytes)
        buf = f.read(sz - includes_size * sz_nbytes)
        return cls(buf)

    def iter_as(self, code):
        if isinstance(code, str):
            s = struct.Struct(code)
            for off in range(0, len(self._buffer), s.size):
                yield s.unpack_from(self._buffer, off)
        elif isinstance(code, StructureMeta):
            size = code.struct_size
            for off in range(0, len(self._buffer), size):
                data = self._buffer[off:off+size]
                yield code(data)

class StructField:
    '''
        Descriptor representing a simple structure field 
    '''
    def __init__(self, format, offset):
        self.format = format
        self.offset = offset

    def __get__(self, instance, cls):
        if instance is None:
            return self
        else:
            r = struct.unpack_from(self.format,
                                    instance._buffer, self.offset)
            return r[0] if len(r) == 1 else r

class NestedStruct:
    '''
        Descriptor representing a nested structure
    '''
    def __init__(self, name, struct_type, offset):
        self.name = name
        self.struct_type = struct_type
        self.offset = offset

    def __get__(self, instance, cls):
        if instance is None:
            return self
        else:
            data = instance._buffer[self.offset: self.offset+self.struct_type.struct_size]
            result = self.struct_type(data)
            # Save resulting structure back on instance to avoid 
            # further recomputation of this step 
            setattr(instance, self.name, result)
        return result

class StructureMeta(type):
    '''
        Metaclass that automatically creates StructField descriptors
    '''
    def __init__(self, clsname, bases, clsdict):
        fields = getattr(self, '_fields_', [])
        byte_order = ''
        offset = 0
        for format, fieldname in fields:
            if isinstance(format, StructureMeta):
                setattr(self,fieldname,
                        NestedStruct(fieldname, format, offset))
                offset += format.struct_size
            else:
                if format.startswith(('<','>','!','@')):
                    byte_order = format[0]
                    format = format[1:]
                format = byte_order + format
                setattr(self, fieldname, StructField(format, offset))
                offset += struct.calcsize(format)
        setattr(self, 'struct_size', offset)

class Structure(metaclass=StructureMeta):
    def __init__(self, bytedata):
        self._buffer = memoryview(bytedata)
        super().__init__()

    # Add a write method, should it be this hard?
    def write(self,  file):
        '''Helper Function to write the contents of the Structure to File'''
        for mydatatype, field in self._fields_:
            mydata = getattr(self,field)
            # Check instance type for write operation
            if isinstance(mydata,(bytes, bytearray)):
                file.write(mydata)
            elif isinstance(mydata,int):
                if mydatatype.startswith(('<','>','!','@')): 
                    byte_order = mydatatype[0]
                    len = struct.calcsize(mydatatype[1:])
                    if byte_order == '<':
                        byte_order = 'little'
                    elif byte_order == '>':
                        byte_order = 'big'
                    format = format[1:]
                    file.write(mydata.to_bytes(len,byte_order))
                else:
                    len = struct.calcsize(mydatatype)
                    file.write(mydata.to_bytes(len,'little'))
            else:
                file.write(mydata.encode())

'''
    Back to my code... 
        We're going to define from Python Structs based on the DSK
        File format specified here:
        https://www.cpcwiki.eu/index.php/Format:DSK_disk_image_file_format

        I will also look at the extensions from Simon Owen in a later release.

        https://simonowen.com/misc/extextdsk.txt

        For further extensions to the DSK File Format
'''

#
# Disk Header Structure
#
class DSKHeader(Structure):
    '''Structure for DSK File Disk-Info Header'''
    _fields_ = [
        ('<34s','header'), 		
        ('<14s','creator'),
        ('B',   'numberOfTracks'),
        ('B',   'numberOfSides'),
        ('h',   'oldTrackSize'),
        ('<204s','trackSizeTable')
    ]
    # Method to setup Defaults
    def defaults(self, numberOfTracks, numberOfSides, numberOfSectors):
        self.header = b'EXTENDED CPC DSK File\r\nDisk-Info\r\n'
        self.creator = b'muckypaws.com '
        self.numberOfTracks = numberOfTracks
        self.numberOfSides = numberOfSides
        self.oldTrackSize = b'\x00\x00'

        highbyte = andbytes(int.to_bytes(((numberOfSectors * 512) + 256) >> 8, 1,'little') , b'\xff')
        trackTable  = highbyte * (numberOfTracks * numberOfSides)
        trackTable2 = b'\x00' * (204 - (numberOfTracks * numberOfSides))
        finalTrackTable = trackTable + trackTable2
        self.trackSizeTable = finalTrackTable[:204]
#
# Define the Sector Information Block Structure
#
class SectorInformationBlock(Structure):
    '''Sector Information Structure'''
    _fields_ = [
        ('B','Track'),
        ('B','Side'),
        ('B','SectorID'),
        ('B','SectorSize'),
        ('B','FDC1'),
        ('B','FDC2'),
        ('h','notused')
    ]
#
#   Need to work out how to get this to work with memory view.
#
#   def __init__(self, *args):
#       if len(args) == 4:
#            self.defaults(*args)
#        else:
#            super().__init__
    def defaults(self, TrackNum, TrackSide, SectorID, SectorSize):
        ''' Set the defaults for a Sector ID'''
        self.Track = TrackNum
        self.Side = TrackSide
        self.SectorID = SectorID
        self.SectorSize = SectorSize
        self.FDC1 = b'\x00'
        self.FDC2 = b'\x00'
        self.notused = b'\x00\x00'

#
# Define the Track Information Block Structure
#
class TrackInformationBlock(Structure):
    '''Track Information Block Structure Definition'''
    _fields_ = [
        ('<12s','header'),
        ('<4s', 'unused'),
        ('B',   'TrackNumber'),
        ('B',   'TrackSide'),
        ('h',   'unused2'),
        ('B',   'sectorSize'),
        ('B',   'numberOfSectors'),
        ('B',   'gap3'),
        ('B',   'filler'),
        ('<232s','sectorTable')
    ]
        
    def defaults(self, TrackNum, TrackSide, numberOfSectors):
        ''' Set the defaults for the Structure'''
        self.header = b'Track-Info\r\n'
        self.unused = b'\x00\x00\x00\x00' 
        self.TrackNumber = TrackNum
        self.TrackSide = TrackSide
        self.unused2 = b'\x00\x00'
        self.sectorSize = b'\x02'
        self.numberOfSectors = numberOfSectors
        self.gap3 = b'\x4e'
        self.filler = b'\xe5'
        self.sectorTable = '\x00' * 232

#
# Define the PLUS3DOS Header
#
class Plus3DOSHeader(Structure):
    '''Data Structure for a PLUS 3 DOS Directory Entry'''
    _fields_ = [
        ('<8s', 'header'),
        ('B',   'SoftEOF'),
        ('B',   'Issue'),
        ('B',   'Version'),
        ('<L',  'TotalFileLen'),
        ('B',   'FileType'),
        ('<H',  'Filelen'),
        ('<H',  'Param1'),
        ('<H',  'Param2'),
        ('B',   'Unused'),
        ('<104s','Reserved'),
        ('B',   'Checksum'),
    ]

#
# Define the PLUS3DOS Header
#
class AmstradFileHeader(Structure):
    '''Data Structure for an Amstrad CPC Directory Entry'''
    _fields_ = [
        ('B',   'User'),
        ('<11s','Filename'),
        ('<4s', 'Filler'),
        ('B',   'BlockNumber'),
        ('B',   'LastBlock'),
        ('B',   'FileType'),            
        ('<H',  'FileSize'),
        ('<H',  'FileLoad'),
        ('B',   'FirstBlock'),
        ('<H',  'LogicalLength'),
        ('<H',  'EntryAddress'),
        ('<36s','Reserved'),
    ]

class CPM22DirectoryEntry(Structure):
    '''Data Structure for a CPM2.2 Directory Entry'''
    _fields_ = [
        ('B',   'User'),
        ('<11s','Filename'),
        ('<B',  'Extent'),
        ('<B',  'Reserved'),
        ('<B',  'ExtentHigh'),
        ('<B',  'RecordCount'),
        ('<16s','Allocation')
    ]

    # Read Only Flag
    def readOnly(self):
        '''Has the Read Only flag been set? Bit 7 of the 9th Filename Character'''
        return self.Filename[8] & 0x80

    # Read Only Flag
    def hidden(self):
        '''Has the Hidden/System flag been set? Bit 7 of the 10th Filename Character'''
        return self.Filename[9] & 0x80

#
#   FDC Status Bits are defined in the NEC µPD765A Specification
#   Only Implementing ones identified to date.
#
def GetFDCStatusText(FDC1, FDC2):
    '''Return FDC Status Bytes 1 and 2, as Hex and Expanded Description'''
    if not (FDC1 & FDC2):
        return f"{CGREEN2}#{FDC1:02X}, #{FDC2:02X} - OK{CWHITE}"
    else:
        FDCStatus = f"{CRED}#{FDC1:02X}, #{FDC2:02X} - "

    if FDC1&0x80:
        FDCStatus += "End of Cylinder "

    if FDC1&0x20 != 0:
        FDCStatus += "CRC Error "

    if FDC1&0x10:
        FDCStatus += "Overrun "

    if FDC1&0x4:
        FDCStatus += "No Data "

    if FDC1&0x2:
        FDCStatus += "Write Protect "

    if FDC1&0x1:
        FDCStatus += "Missing Address Mark "

    if FDC2&0x40 != 0:
        FDCStatus += "*Control Mark* "

    if FDC2&0x20 != 0:
        FDCStatus += "*Data Error* "

    if FDC2&0x10 != 0:
        FDCStatus += "*Wrong Cylinder* "

    if FDC2&0x8 != 0:
        FDCStatus += "*Scan Equal Hit* "

    if FDC2&0x4 != 0:
        FDCStatus += "*Scan Not Satisfied* "

    if FDC2&0x2 != 0:
        FDCStatus += "*Bad Cylinder* "

    if FDC2&0x1 != 0:
        FDCStatus += "*Missing Address Mark* "

    FDCStatus += f"{CWHITE}"
    return FDCStatus

#
# Get Sector information from Sector Table by position (0-numberOfSectors)
#
def GetSectorInfoFromTrackByPosition(TrackDict, SectorPosition):
    '''Calculate the correct Sector Info from the TRACK INFO Block'''

    table = TrackDict.sectorTable

    if SectorPosition > TrackDict.numberOfSectors:
        return -1, -1, -1, -1, -1, -1, -1

    SectorInfo = SectorInformationBlock(table[(SectorPosition*8):(SectorPosition*8)+8])

    return SectorInfo.Track, SectorInfo.Side, SectorInfo.SectorID, SectorInfo.SectorSize, GetFDCStatusText(SectorInfo.FDC1, SectorInfo.FDC2)

#
# Display Sector Info for All Sectors
#
def DisplaySectorInfo(StartTrack, EndTrack):
    '''
    Display Sector Info Stored in the Track, similarly to how Discology used to.
    '''
    global DSKDictionary

    print("Sector Information\n")

    trackDict = {k: v for k, v in DSKDictionary.items() if ":" in k}

    for tracks in trackDict:

        track = DSKDictionary[tracks]
        if track.TrackNumber >= StartTrack and \
            track.TrackNumber <= EndTrack:
            print()
            print("*"*80)
            print(f"\nTrack: {track.TrackNumber:02d}, GAP3: {CBLUE}#{track.gap3:02X}{CWHITE}, Filler Byte: {CBLUE}#{track.filler:02X}{CWHITE}\n")
            print(" C,  H,  ID,  N, FDC Status")

            for sectors in range(track.numberOfSectors):
                trackNum, side, sectorID, sectorSize, FDCStatus = GetSectorInfoFromTrackByPosition(track, sectors )
                print(f"{trackNum:02d}, {side:02d}, #{sectorID:02X}, {sectorSize:02d}, {FDCStatus}")

#
# Print the Disk Header Information
#
def DisplayDiskHeader(verbose):
    '''
    Break down the fields in a DSK Header and report the information.
    '''
    global DSKDictionary

    headerName = DSKDictionary['DiskHeader'].header.decode("utf-8").replace("\r","\\r").replace("\n","\\n")
    creatorName = DSKDictionary['DiskHeader'].creator.decode("utf-8").replace("\r","\\r").replace("\n","\\n")

    print(f"          Header: {headerName}")
    print(f"    Creator Name: {creatorName}")
    print(f"Number of Tracks: {DSKDictionary['DiskHeader'].numberOfTracks}")
    print(f" Number of Sides: {DSKDictionary['DiskHeader'].numberOfSides}")

    print()

    numberOfSides = DSKDictionary['DiskHeader'].numberOfSides
    # Parse Number of Tracks 
    for track in range (DSKDictionary['DiskHeader'].numberOfTracks):
        # Parse Number of Sides
        for trackside in range(numberOfSides):
            tracksize = DSKDictionary['DiskHeader'].trackSizeTable[track] * 256
            if tracksize > 0:
                trackSizeString = f"Size - {tracksize-256} bytes"
            else:
                trackSizeString = "Unformatted Track"

            trackString = f"{track:02d}:{trackside:01d}"

            if trackString in DSKDictionary:
                sectors = DSKDictionary[trackString].numberOfSectors
                trackSizeString += f", {sectors} Sectors"


            if numberOfSides > 1:
                print(f"Track: {track:02d} Side[{trackside}] - {trackSizeString}")
            else:
                print(f"Track: {track:02d} > {trackSizeString}")


def GetSectorOffset(Track, SectorToFind):
    '''
    Calculate the Sector Offset (Index) Into the Track Table to locate the Sector
    requested.  Real Disks would interlace sectors for performance reasons, so
    it's not a 1:1 relation ship.
    '''
    offset = -1

    maxSectors = Track.numberOfSectors
    if maxSectors > 29:
        maxSectors = 29
        print(f"Corrupt number of Sectors Detected in Track: {Track.TrackNumber}, Reporting - {Track.numberOfSectors}")

    for sectors in range(maxSectors):
        if Track.sectorTable[(sectors*8)+2] == SectorToFind:
            offset = sectors
    return offset

#
# Taken from StackOverflow:
# https://stackoverflow.com/questions/22593822/doing-a-bitwise-operation-on-bytes
#
def andbytes(abytes, bbytes):
    '''Logical AND a collection of BYTES or BYTE, madness... but there ya go'''
    return bytes([a & b for a, b in zip(abytes[::-1], bbytes[::-1])][::-1])

#
# Normalise the Filename
#
def normaliseFilename(filename):
    """Normalise a Filename to something printable."""
    # Iterate over Filename
    # Bit 7 Indicates Special Features.

    # Meh...  Remove control characters from Disks with filenames
    #         That would display a screen message instead of files.
    cleanName = bytearray()
    for count, x in enumerate(filename):
        if x >= ord(' '):
            cleanName.append(x)

    result=andbytes(cleanName,b'\x7f\x7f\x7f\x7f\x7f\x7f\x7f\x7f\x7f\x7f\x7f')

    normal=result[0:8].decode() + "." + result[8:11].decode()

    return normal

#
#
#
def getInitialDirectoryTrackAndSectorForDiskFormat(diskFormat):
    ''' 
    Set the inital track and sector for directory entry info
    based on disk file format for known CPM Valid Systems
    '''
    sectorCount = 9
    # Check which File Format
    if diskFormat & CONST_DATA_BIT:
        track = 0
        sector = 0xc1
    elif diskFormat & CONST_VENDOR_BIT:
        track = 2
        sector = 0x41
    elif diskFormat & CONST_IBM_BIT:
        track = 1
        sector = 1
        sectorCount = 8
    elif diskFormat & CONST_PLUS3DOS_BIT:
        track = 1
        sector = 1
    else:
        print(f"Failure to obtain Cluster info")
        print(f"Unknown Disk Format: {CRED}{diskFormat:02X}{CWHITE}")
        sys.exit(0)
        
    return track, sector, sectorCount
#
#   Get Track and Sector Offset for Cluster ID
#
def calcTrackAndSectorForCluster(cluster: int, diskFormatType: int):
    '''Calculate the Track and Sector Offset for any Cluster ID'''

    track, sectorID, maxSectors = getInitialDirectoryTrackAndSectorForDiskFormat(diskFormatType)

    # Clusters are two sectors
    cluster = cluster * 2
    
    # Divide by the number of Sectors Per track
    # Add the start Track for Directory Info, DATA = 0, VENDOR = 2, IBM = 1
    ClusterTrack = int((cluster / maxSectors ) + track)
    ClusterSector = (cluster % maxSectors) + sectorID
    
    # Next Sector
    cluster += 1
    ClusterTrack2 = int((cluster / maxSectors ) + track)
    ClusterSector2 = (cluster % maxSectors) + sectorID
    
    # Return Track and Sector
    return ClusterTrack, ClusterSector, ClusterTrack2, ClusterSector2
    
def getSectorDataFromTrack(track: int, sector: int, side:int):
    '''Get Sector Data from Track if available'''
    TrackEntry = f"{track:02d}:{side:01d}"
    
    if TrackEntry in DSKDictionary.keys():
            
        TrackDict = DSKDictionary[TrackEntry]

        offset = GetSectorOffset(TrackDict, sector)

        if offset >= 0 and offset < TrackDict.numberOfSectors:
            offset = offset * 512

        return DSKDataDictionary[TrackEntry][offset:offset+512]
    
    print(f"\nUnable to locate Data for Track:{CRED}{track}{CWHITE}, Sector:{CRED}#{sector:02X}{CWHITE}")
    return b'0'      
#
#   Get Complete Data from Cluster ID
#
def getDataFromClusterID(clusterID: int, diskFormatType: int, side: int):
    '''
    Return Cluster Data (1k) from Cluster ID from DSK Image
    Assuming conformance to CPM2.2 and 512Byte Sector Records.
    A cluster can span to the next track.
    '''
    
    # First Workout the initial Track and Sector Offset from Cluster ID
    Track1, Sector1, Track2, Sector2 = calcTrackAndSectorForCluster(clusterID, diskFormatType)

    data = getSectorDataFromTrack(Track1, Sector1, side) + \
            getSectorDataFromTrack(Track2, Sector2, side)
    
    if len(data) > 2:
        return data
    else:
        print(f"\nUnable to locate Data for Cluster: {clusterID} = Tracks:{Track1}, Sector:#{Sector1:02X}, Track:{Track2}, Sector:#{Sector2:02X}{CWHITE}")
        return b'0'

#
# Check the first 66 Bytes of the Header and Checksum 
#
def CheckCheckSum(filedata, type):
    ''' 
    Calculate the Header Checksum, if the checksum matches then we have a valid
    AMSDOS Header, otherwise the file is headerless.

    Testing seems to confirm records are over when terminated with a Soft EOF #1A #00
    Byte Combination
    '''

    if len(filedata) < 128:
        print(f"Invalid Disk Data Sent: expecting at least 128 Bytes, received: {len(filedata)}")
        return False
    
    checksum = 0
    filecheck = 0

    if type == CONST_AMSTRAD:
        for i in range(66):
            checksum += filedata[i]

        filecheck = int.from_bytes(filedata[67:69],'little')

    if type == CONST_PLUS3DOS:
        for i in range(127):
            checksum += filedata[i]

        # Only need the Lower Byte, could MOD 256 but AND is more efficient
        filecheck = filedata[127]
        checksum &= 255

    return checksum == filecheck

#
# Sectors have to be 512Bytes Each and conform to CPM2.2 Standards.
#
def getFileInfo(cluster: int, formatType: int, side: int, filename: str):
    """Try to get File information from Track and Sector."""
    global DEFAULT_SYSTEM
    global GLOBAL_CORRUPTION_FLAG


    fileType = b'\x00'
    fileStart = 0
    filelen = 0
    fileexec = 0

    # Only Need 128 Bytes just in case it's a PLUS3DOS Header... 
    FileHeader = getDataFromClusterID(cluster, formatType, side)[:128]

    # Suppress more messages.
    headerless = 0

    if len(FileHeader) == 128:

        if FileHeader[:8] != b'PLUS3DOS':
            FileInfoHeader = AmstradFileHeader(FileHeader[:64])

            # Check if Header or Headerless
            # Originally I was comparing the File Header with the Directory Header for Filename.
            # Turns out the |REN command, changes the directory entry but NOT, the file entry name
            # so need to rethink this....

            if CheckCheckSum(FileHeader, CONST_AMSTRAD):
                fileType = int(FileInfoHeader.FileType)
                fileStart = FileInfoHeader.FileLoad
                filelen = FileInfoHeader.LogicalLength
                fileexec = FileInfoHeader.EntryAddress
            else:
                fileType=-1

        else:
            # Experimental, Process +3DOS Info
            # Reference : https://area51.dev/sinclair/spectrum/3dos/fileheader/
            DEFAULT_SYSTEM = CONST_PLUS3DOS

            if CheckCheckSum(FileHeader,CONST_PLUS3DOS):
                FileInfoHeader = Plus3DOSHeader(FileHeader)
                fileType = FileInfoHeader.FileType
                filelen = FileInfoHeader.Filelen
                fileStart = FileInfoHeader.Param1
                fileexec = FileInfoHeader.Param2
            else:
                print("Fileheader Checksum Failure: ")
                print("Record file support not yet implemented")

    else:
        if GLOBAL_CORRUPTION_FLAG == 0:
            GLOBAL_CORRUPTION_FLAG = 1
            print("Warning, Possible Corrupt Disk Detected")
            print(f"FileHeader Bytes: {len(FileHeader)} insufficient sector data in Cluster:{cluster}, Side:{side}")

    return fileType,fileStart, filelen, fileexec

#
# Extract files from the DSK Level to your OS using the correct lengths.
#
def ExtractFiles(fileExtractDetails, side ):
    '''
    Extract each of the files in the list to an external file, fileExtractDetails is 
    Dictionary of FILENAMES and CPMDirectory Structures
    '''
    for filename in fileExtractDetails:
        # Process each file in the list
        if filename[0] > ' ':
            print(f" Processing: {CGREEN}{filename}{CWHITE}")

            # Directory Entries may contain more than one entry for each 16kb block of file
            # it also doesn't have to be in order.
            TotalRecords = 0

            AllocationEntries = {}
            for Entry in fileExtractDetails[filename]:
                AllocationEntries[Entry.Extent] = Entry.Allocation
                TotalRecords += Entry.RecordCount

            sortedAllocations = dict(sorted(AllocationEntries.items()))

            FileData = b''
            #for block in range(len(sortedAllocations)):
            for block in sortedAllocations:
                for x in range(16):
                    cluster = sortedAllocations[block][x]
                    if cluster > 0:
                        FileData += getDataFromClusterID(cluster, DEFAULT_DSK_FORMAT, side)
                    else:
                        break

            # Check if CP/M declared, if so process full filesize and quit.
            if DEFAULT_ISCPM:
                # CPM Header contains number of records per Entity entry
                # a Record is fixed at 128 bytes
                # Filelength can only be calculated by multiple of 128
                fileSize = TotalRecords * 128
                createDeviceFile(filename, FileData[:fileSize])
            else:
                if DEFAULT_SYSTEM == CONST_PLUS3DOS:
                    FileInfoHeader = Plus3DOSHeader(FileData[:128])
                    filelen = FileInfoHeader.Filelen
                    createDeviceFile(filename, FileData[128:128+filelen])
                else:
                    # Check if Valid File
                    valid = CheckCheckSum(FileData[:128], CONST_AMSTRAD)

                    if(valid):
                        fileinfo = AmstradFileHeader(FileData[:64])
                        filelen = fileinfo.LogicalLength

                        createDeviceFile(filename, FileData[128:128+filelen])
                    else:
                        # Records format so search for the first instance of
                        # Soft EOF = #1A byte for correct length

                        filelen = 0

                        for filelen, z in enumerate(FileData):
                            if z == 26:
                                filelen += 1
                                break
                        
                        createDeviceFile(filename, FileData[:filelen])

#
#
#
def remove_non_ascii(text):
    '''Remove None ASCII Charactets from Filename'''
    #return ''.join(filter(str.isalnum, text))
    clean=''
    for x, ch in enumerate(text):
        if ch == ' ' or ch == ':' or (ch > ',' and ch < ';') or (ch >'@' and ch < '['):
            clean = clean + text[x]

    return clean
#
# Create a File to your Device as Native OS File.
#
def createDeviceFile(filename, data):
    '''
    Save extracted file information to disk.  Filename and Data required.
    '''

    if not len(data):
        print(f"No data found for file: {filename}, nothing to write")
        return
    
    finalName = filename.replace(" ","").replace(":","-")
    finalName = remove_non_ascii(finalName)

    # Don't think this will trigger as there will be a USER and Colon at a minimum.
    if not len(filename):
        print(f"Santised filename unavailable for writing, original name: {filename}")
        return

    if len(filename) and len(data):
        print(f"Saving File: {CBLUE}{finalName}{CWHITE} \t    for length: {CBLUE}{len(data)}{CWHITE}")
        try:
            with open(finalName, mode="wb") as file:
                file.write(data)
                file.flush()
                file.close()
        except Exception as error:
            print(f"Failed to Write File: {finalName}")
            print(f"Error: {error}")
    else:
        print(f"Something went horrible wrong to get here.")

#
# Attempt to show files stored on DISK
# Thankfully Directories are on the Same Track and Incremental Sectors
#
def DisplayDirectory(head, detail, extract:int ):
    '''
    Show the contents of a CPM2.2 Directory
    head = Disk Side (0 or 1)
    detail = Flag to Show Extended File Information
    '''
    
    global DEFAULT_DSK_FORMAT
    
    if not DEFAULT_DSK_FORMAT:
        print("Error: Default Disk Directory Format Undetected")
        return

    track, sector = getInitialDirectoryTrackAndSectorForDiskFormat(DEFAULT_DSK_FORMAT)[0:2]

    FileList = []
    FileListExpanded = []
    
    FileExtractionList = {}

    track, sector = getInitialDirectoryTrackAndSectorForDiskFormat(DEFAULT_DSK_FORMAT)[0:2]

    # Four Sectors Make up Directory Entries
    TrackDataToProcess = getSectorDataFromTrack( track , sector ,head)
    TrackDataToProcess += getSectorDataFromTrack( track , sector+1 ,head)
    TrackDataToProcess += getSectorDataFromTrack( track , sector+2 ,head)
    TrackDataToProcess += getSectorDataFromTrack( track , sector+3 ,head)

    if len(TrackDataToProcess) < 2048:
        print(f"Failed to retrieve Directory Structures from Track:{CRED}{track}{CWHITE}, Sector:#{CRED}{sector}{CWHITE}, Head:{CRED}{head}{CWHITE} for 4 sectors.")
        return
    
    # 16 Entries per 512 Byte Sector (512/16) four sectors = 64 entries.
    for x in range(64):
        # Get File Record Info
        DirectoryRecord = CPM22DirectoryEntry(TrackDataToProcess[x*CPM22DirectoryEntry.struct_size:
                                                            (x*CPM22DirectoryEntry.struct_size)+
                                                            CPM22DirectoryEntry.struct_size])

        # Technically should validate 0-15 as those were valid, some protection
        # systems would modify this byte to prevent user intervention
        # Deleted Files would always contain #E5 (Filler Byte)
        if DirectoryRecord.User != 0xe5 and \
            DirectoryRecord.Filename[0] > 32:

            filename = normaliseFilename( DirectoryRecord.Filename)

            key = f"{DirectoryRecord.User:02d}:" + filename
        
            if key in FileExtractionList:
                FileExtractionList[key].append(DirectoryRecord)
            else:
                FileExtractionList[key] = [DirectoryRecord]
            #Read-Only Flag Set?
            if DirectoryRecord.readOnly():
                filename += "*"
            else:
                filename += " "
            #System/Hidden Flag Set?

            if DirectoryRecord.hidden():
                filename += "+"
            else:
                filename += " "

        for entry in FileExtractionList:
            # Check First Directory Entry
            # Extent Byte should be 00
            #     >0 Related entry to the primary file.
            if DirectoryRecord.Extent == 0:
                # Check Valid Name
                if filename[0] > " ":
                    entry = f"{DirectoryRecord.User:02d}:"+filename
                    if entry not in FileList:
                        # Add File to List
                        FileList += [entry]

                        # Get first Cluster ID where File Stored
                        # This contains the Actual File Header Info
                        # Stored at that Track and Sector
                        # Each Cluster is 1K or 2 Sectors.

                        cluster = int(DirectoryRecord.Allocation[0])

                        filetype, fileStart, fileLen, fileExec = getFileInfo(cluster, DEFAULT_DSK_FORMAT, head, filename[:12])

                        # Headerless Disk Record Check, Amstrad CPC doesn't write a Header when Records or ASCII Files written
                        # Need to work out some handling of this situation

                        # Reported by Richard Deane, CP/M File handling doesn't exist, more work needs to be done on this
                        # Temporarily adding in just full binary extract to cluster size since difference filetypes have
                        # Differing file headers.  .COM generated by GENCOM for example, others will vary depening on target
                        #

                        if filetype != -1:
                            fileDetails = [f"{DirectoryRecord.User:02d}:" +filename +f"    \t{filetype}\t#{fileStart:04X} \t#{fileExec:04X} \t#{fileLen:04X}"]
                        else:
                            recordCount = DirectoryRecord.RecordCount * 128
                            fileDetails = [f"{DirectoryRecord.User:02d}:" +filename +f"    \t{CGREEN}Headerless File Size:   #{recordCount:04X}{CWHITE}"]
                        # Add Enhanced File Details to List
                        FileListExpanded += fileDetails

    # You can do better than this frigging cludge Jason, stop being a lazy arsed git....
    # nah... fuck it....
    if DEFAULT_ISCPM:
        FileListExpanded = []
        for filename in FileExtractionList:
            # Process each file in the list
            if filename[0] > ' ':
                # Directory Entries may contain more than one entry for each 16kb block of file
                # it also doesn't have to be in order.
                TotalRecords = 0

                for Entry in FileExtractionList[filename]:
                    TotalRecords += Entry.RecordCount
                fileLen = TotalRecords * 128
                fileDetails = [filename +f"    \t \t  \t \t#{fileLen:04X}"]
                FileListExpanded += fileDetails


    # De Dupe and Sort
    FileList = sorted(set(FileList))
    FileListExpanded = sorted(set(FileListExpanded))

    if extract:
        ExtractFiles(FileExtractionList, head)

    print()
    print("*"*80)
    if len(FileList) == 0:
        print("No files Found, Possible Blank Disk Detected")
    else:
        print(f"Total Files Found: {len(FileList)}\n")

        if DEFAULT_SYSTEM == CONST_PLUS3DOS:
            print(f"{CYELLOW}*** PLUS3DOS File System Detected ***{CWHITE}\n")
        else:
            if DEFAULT_ISCPM:
                print(f"{CBLUE2}*** CPM File System Declared ***{CWHITE}\n")
            else:
                print(f"{CVIOLET}*** AMSDOS File System Detected ***{CWHITE}\n")

        if not detail:
            for filename in FileList:
                print(filename)
        else:
            if DEFAULT_SYSTEM == CONST_AMSTRAD:
                print(" U:Filename    RH  \tType\tStart\tExec\tLength")
                print("-"*53)
            else:
                print(" U:Filename    RH  \tType\tStart\tParam2\tLength")
                print("-"*53)

            for filename in FileListExpanded:
                print(filename)

#
# Load DSK File to Memory
#
def loadDSKToMemory(filename, verbose):
    global DSKDictionary
    global DSKDataDictionary
    global DSKSectorDictionary
    global DSKSectorDataDictionary
    global DEFAULT_DSK_TYPE
    global DEFAULT_DSK_FORMAT
    global GLOBAL_CORRUPTION_FLAG

    if os.path.isfile(filename):
        try:
            with open(filename, mode="rb") as file:

                totalFileSize = os.path.getsize(filename)
                # Process the first 256 Bytes - Disk Header Information
                dskHead = DSKHeader(file.read(256))
                DSKDictionary['DiskHeader']=dskHead

                # Check we're dealing with a Valid Disk Format
                # According to the Specification on 
                # https://www.cpcwiki.eu/index.php/Format:DSK_disk_image_file_format
                #
                # There are two VALID Eye Catchers for the Header.
                # "MV - CPCEMU Disk-File\r\nDisk-Info\r\n"
                # "EXTENDED CPC DSK File\r\nDisk-Info\r\n"
                #
                # Except... for Legacy Disks, before Standards Finalised.
                # If either of these don't match then quit.

                validHeader = dskHead.header.decode()

                if validHeader == "EXTENDED CPC DSK File\r\nDisk-Info\r\n" or \
                    validHeader == "MV - CPCEMU Disk-File\r\nDisk-Info\r\n":
                    if verbose:
                        print("\nValid DSK Header Found\n")
                elif validHeader[:11] == "MV - CPCEMU":
                    if verbose:
                        print(f"Legacy File Header Discovered: {validHeader}")
                else:
                    print(f"Invalid DSK Header Detected: {validHeader}\n")
                    sys.exit(0)


                # Check Old Version for Track Info Size
                legacy = 0
                if validHeader != "EXTENDED CPC DSK File\r\nDisk-Info\r\n":
                    legacy = 1

                #
                # Try processing the DSK information from file.
                DEFAULT_DSK_FORMAT = 0
                if dskHead.numberOfTracks > 0:
                    numberOfSides = DSKDictionary['DiskHeader'].numberOfSides
                    # Parse Number of Tracks 
                    for track in range (DSKDictionary['DiskHeader'].numberOfTracks):
                        # Parse Number of Sides
                        for trackside in range(numberOfSides):
                            if not legacy:
                                tracksize = DSKDictionary['DiskHeader'].trackSizeTable[track] * 256
                            else:
                                tracksize = DSKDictionary['DiskHeader'].oldTrackSize
                            # Check the track is formatted with data.

                            # Some Legacy Files Report 40 Tracks when only the relevant ones
                            # Were encoded... So we need to check...
                            bytesRemaining = file.tell()

                            if tracksize > 0 and (bytesRemaining+tracksize)<=totalFileSize:
                                trackString = f"{track:02d}:{trackside:01d}"
                                DSKDictionary[trackString] = TrackInformationBlock(file.read(256))
                                DSKDataDictionary[trackString] = file.read(tracksize-256)

                                # Check Track-Info is Correctly Set
                                # Some Legacy Disks appear to be corrupt
                                if DSKDictionary[trackString].header[:10] != b'Track-Info':
                                    print(f"Invalid Track Header Detected at Track: {track} - data = {DSKDictionary[trackString].header[:10]}\n")
                                    return


                                # Break out Sector Data
                                sectorCount = DSKDictionary[trackString].numberOfSectors

                                # Jacelock would fake/misreport the number of Sectors on a Track
                                if sectorCount > 28:
                                    sectorCount = 28

                                if sectorCount > 0:
                                    x = 0
                                    for sector in range(sectorCount):
                                        sectorData = SectorInformationBlock(DSKDictionary[trackString].sectorTable[sector*8:(sector*8)+8])
                                        #print(sectorData , len(sectorData))

                                        if sectorData.SectorID > 0xc0 and sectorData.SectorID < 0xca:
                                            DEFAULT_DSK_FORMAT |= CONST_DATA_BIT
                                        if sectorData.SectorID > 0x40 and sectorData.SectorID < 0x4a:
                                            DEFAULT_DSK_FORMAT |= CONST_VENDOR_BIT
                                        if sectorData.SectorID > 0x0 and sectorData.SectorID < 0x09:
                                            DEFAULT_DSK_FORMAT |= CONST_IBM_BIT
                                        if sectorData.SectorID > 0x0 and sectorData.SectorID < 0x0a:
                                            DEFAULT_DSK_FORMAT |= CONST_PLUS3DOS_BIT
                                        x += 8
                            else:
                                if tracksize > 0:
                                    if GLOBAL_CORRUPTION_FLAG == 0:
                                        GLOBAL_CORRUPTION_FLAG = 1
                                        print(f"{CRED}Possible Corruption, Insufficient data from Track: {track}{CWHITE}")
                                        print(f"Disk Header set to: {CRED}{DSKDictionary['DiskHeader'].numberOfTracks}{CWHITE}")
                # Set Disk Type Flags
                if DEFAULT_DSK_FORMAT == CONST_DATA_BIT:
                    DEFAULT_DSK_TYPE = "DATA"
                elif DEFAULT_DSK_FORMAT == CONST_VENDOR_BIT:
                    DEFAULT_DSK_TYPE = "SYSTEM"
                elif DEFAULT_DSK_FORMAT == CONST_PLUS3DOS_BIT + CONST_IBM_BIT:
                    DEFAULT_DSK_TYPE = "PLUS3DOS"
                    DEFAULT_DSK_FORMAT &= ~CONST_IBM_BIT
                elif DEFAULT_DSK_FORMAT == CONST_IBM_BIT:
                    DEFAULT_DSK_TYPE = "IBM"
                else:
                    # Protection Systems Mixed and Matched Sectors
                    DEFAULT_DSK_TYPE = "Proprietary"

                print(f"\nDisk Format Type: {DEFAULT_DSK_TYPE}, appears to be Valid.\n")

        except Exception as error:
            print(f"Failed to open DSK File: {filename}")
            print(f"Error: {error}")
            sys.exit(0)

def CreateBlankDSKFile(FilenameToWrite, tracks: int, sides :int, format: int):
    '''Create a Blank Disk File Image for use in an Emulator or GOTEK etc.'''
    global CONST_DATA_FORMAT
    global CONST_IBM_FORMAT
    global CONST_VENDOR_FORMAT


    # Check if File Exists
    if os.path.isfile(FilenameToWrite):
        print(f"\nFile Already Exists: {CGREEN}{FilenameToWrite}{CWHITE}")
        print(f"DSK Image {CRED}NOT{CWHITE} Created.\n")
    #    return

    # Used to create the initial Struct
    error = 0

    if sides < 1 or sides > 2:
        print(f"\n Invalid Number of Sides, Valid values are 1, or 2, you asked for{CRED} {sides} {CWHITE}\n")
        error = 1

    if tracks < 1 or tracks > 82:
        print(f"Minimum Tracks = 1, Maximum Tracks = 82, you asked for:{CRED} {tracks} {CWHITE}")
        error = 1

    if format == CONST_DATA_FORMAT:
        InitialSectorID = b'\xc1\xc6\xc2\xc7\xc3\xc8\xc4\xc9\xc5'
        TotalSectors = 9
        ftype = "DATA"
    elif format == CONST_VENDOR_FORMAT:
        InitialSectorID = b'\x41\x46\x42\x47\x43\x48\x44\x49\x45'
        TotalSectors = 9
        ftype = "VENDOR"
    elif format == CONST_IBM_FORMAT:
        InitialSectorID = b'\x01\x05\x02\x06\x03\x07\x04\x08'
        TotalSectors = 8
        ftype = "IBM"
    elif format == CONST_IBM_ZXSPECTRUM:
        InitialSectorID = b'\x01\x06\x02\x07\x03\x08\x04\x09\x05'
        TotalSectors = 9
        ftype = "IBM"
    else:
        print(f"Unknown Format Selected, received: {CRED}{format}{CWHITE}\n")
        print("Supported Formated are :\n")
        print("\t0 - DATA Format (Default)")
        print("\t1 - VENDOR Format")
        print("\t2 - IBM Format\n")
        print("\t3 - ZX Spectrum IBM Format\n")
        error = 1

    if error:
        print(f"{CRED}Operation Aborted...{CWHITE}")
        sys.exit(0)
            
    print(f"Disk Format: {CGREEN}{ftype}{CWHITE}")
    print(f" Disk Sides: {CGREEN}{sides}{CWHITE}")
    print(f"     Tracks: {CGREEN}{tracks}{CWHITE}\n")
    # Create a structure.  Technically, we could just write all this to disk...
    # But... I may want to create a DSK in memory to inject files at a later
    # date.

    DiskHeader = DSKHeader(b'\x00' * DSKHeader.struct_size)
    DiskHeader.defaults(tracks,sides,TotalSectors)

    TrackInfo = TrackInformationBlock(b'\0'*TrackInformationBlock.struct_size)
    TrackInfo.defaults(0,0,TotalSectors)

    # Interleved Sectors List
    try:
        with open(FilenameToWrite, mode="wb") as file:

            DiskHeader.write(file)

            # Now write out Blank Track Information
            for track in range(tracks):
                for side in range(sides):
                    SectorDetail = b''
                    side = int.to_bytes(side,1,'little')
                    TrackInfo.TrackNumber = int.to_bytes(track,1,'little')
                    TrackInfo.TrackSide = side

                    for count in range(TotalSectors):
                        SectorToAdd = SectorInformationBlock(b'\x00' * SectorInformationBlock.struct_size)
                        SectorToAdd.defaults(TrackInfo.TrackNumber, TrackInfo.TrackSide,InitialSectorID[count:count+1],b'\x02')
                        SectorDetail += TrackInfo.TrackNumber + \
                                        TrackInfo.TrackSide + \
                                        InitialSectorID[count:count+1] + \
                                        b'\x02\x00\x00\x00\x00'

                        sectorBlank = b'\x00' * (232 - (TotalSectors * sides))
                        finalSectorTable = SectorDetail + sectorBlank

                    TrackInfo.sectorTable = finalSectorTable[:232]

                    TrackInfo.write(file)

                    # Write the Blank Sectors filled with filler byte.

                    file.write(TrackInfo.filler * TotalSectors * 512)



            # Combine All this Sector Information in to the track block.
    except Exception as error:
        print(f"Failed to Create Blank DSK File: {FilenameToWrite}")
        print(f"Error: {error}")
        sys.exit(0)

#
#   The Main Program, Parse Arguments and run features.
#       You know the drill.
#
if __name__ == "__main__":
    # Add user options to the code
    parser = argparse.ArgumentParser(description="Amstrad CPC DSK File Info",
                                     epilog='https://github.com/muckypaws/AmstradDSKExplorer')

    # Mandatory Parameter - Need a Filename
    parser.add_argument("filename",help="Name of the DSK File to Process")

    # Optional Parameters
    parser.add_argument("-ts","--trackStart", help="Start Track to View", type=int, default=0)
    parser.add_argument("-te","--trackEnd", help="End Track to View", type=int, default=42)

    parser.add_argument("-dh","--displayHeader",
                        help="Display Disk Header Information",
                        action="store_true",default=False)

    parser.add_argument("-ds","--displaySector",
                        help="Display Sector Information",
                        action="store_true",default=False)

    parser.add_argument("-dir","--directory",
                        help="Display Directory Information",
                        action="store_true",default=False)

    parser.add_argument("-s","--side",
                        help="Select Drive Head (0:1)",
                        type=int, default=0)

    parser.add_argument("-v","--verbose",
                        help="Show Startup Parameters",
                        action="store_true",default=False)

    parser.add_argument("-d","--detail",
                        help="Show File Information",
                        action="store_true",default=False)

    # First Mutually Excluded Group of Flags
    #group=parser.add_mutually_exclusive_group()
    parser.add_argument("-f","--format",
                    help="Create an Amstrad CPC Compatible Formatted Disk, Needs Format Type Param",
                    action="store_true",default=False)

    parser.add_argument("-ft","--formatType",
                    help="Disk Format Type to Create, 0 = DATA, 1 = SYSTEM, 2 = IBM, 3 = ZX Spectrum +3, Default = DATA",
                    type=int, default=0)

    parser.add_argument("-ftracks","--formatTracks",
                help="Number of Tracks for the Disk Image, default = 42",
                type=int, default=42)
    parser.add_argument("-fsides","--formatSides",
                help="Number of Sides for the Disk Image (1 or 2), default = 1",
                type=int, default=1)
    parser.add_argument("-ex","--extract",
                help="Number of Sides for the Disk Image (1 or 2), default = 1, can only be used with the -dir option",
                action="store_true",default=False)

    parser.add_argument("-cpm","--cpm",
                help="Treat All files for extraction as CPM binaries",
                action="store_true",default=False)

    args = parser.parse_args()

    DEFAULT_START_TRACK = args.trackStart
    DEFAULT_END_TRACK = args.trackEnd

    DEFAULT_ISCPM = args.cpm

    # Start up Message
    print(f"\n{CWHITE}{CBLACKBG}")
    print("-"*80)
    print(f"{CGREEN}DSK File Info Utility... www.muckypaws.com\n")

    now = datetime.now()
    print(now.strftime(f"Program Run: %Y-%m-%d %H:%M:%S{CWHITE}"))
    print("-"*80)

    if args.format:
        print(f"\nCreating New DSK: {CGREENBG}{CBLACK} {args.filename} {CWHITE}{CBLACKBG}\n")
        CreateBlankDSKFile(args.filename, args.formatTracks, args.formatSides, args.formatType)
    else:
        print(f"\nProcessing: {CGREENBG}{CBLACK} {args.filename} {CWHITE}{CBLACKBG}\n")

    # Check file actually exists before we start...
    if not os.path.isfile(args.filename):
        print(f"\nInvalid Filename, Can't find it: {args.filename}\n")
        sys.exit(0)

    # Check File Size is multiples of 256 bytes
    size = os.path.getsize(args.filename)
    if size % 256:
        print(f"\n\n*** Warning might not be valid DSK File: Must be multiples of 256 Bytes: Size = {size}, Ignore if disk Created with SAMDisk. ***")

    # Situations for Corrupt DSK files that just contain a header, nothing more
    # I.e. totally unformatted disks
    if size == 256:
        print(f"\n\n{CRED}*** Sorry, this disk is not formatted ***{CWHITE}\n\n")
        sys.exit(0)

    if size <= 1024:
        print(f"\n\n{CRED}*** Unknown formatted disk, quitting... ***{CWHITE}\n\n")
        sys.exit(0)

    if args.verbose:
        print(f"Start Track: {CGREEN}{DEFAULT_START_TRACK}{CWHITE}")
        print(f"  End Track: {CGREEN}{DEFAULT_END_TRACK}{CWHITE}")
        print(f"       Head: {CGREEN}{args.side}{CWHITE}")

    # Load the File to Memory and Pre-Process it
    # Also Validated a new DSK Image if it's just been created.
    loadDSKToMemory(args.filename, args.verbose)

    if args.displayHeader:
        DisplayDiskHeader(args.verbose)

    if args.displaySector:
        DisplaySectorInfo(args.trackStart, args.trackEnd)

    if args.directory:
        DisplayDirectory(args.side, args.detail, args.extract)
