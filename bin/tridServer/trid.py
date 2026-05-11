#!/usr/bin/env python3

# Vibe coded by Codex

#--------------------------------------------------------------------------
# TrID
# Copyright (C) 2003-2025 Marco Pontello - https://mark0.net
#
# This program is dual-licensed.
#
# For personal or non-commercial use, TrID is free software, 
# licensed under the GNU AGPLv3. See: <http://www.gnu.org/licenses/>
#
# For commercial use, a separate license is needed.
# Commercial use includes any use for profit, business-related
# activities, or by for-profit entities.
# Contact the author at: marcopon@gmail.com
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#--------------------------------------------------------------------------


import os
import sys
sys.dont_write_bytecode = True
import glob
import argparse
from struct import unpack_from, unpack
from time import perf_counter
import pickle
from pathlib import Path
import platform

import hashlib
import zipfile
import tempfile
from urllib.request import urlopen
import csv
import itertools
from dataclasses import dataclass

# If stringzilla is available will use to get big speedup!
try:
    import stringzilla
    STRINGZILLA_AVAILABLE = True
except ImportError:
    STRINGZILLA_AVAILABLE = False

PROGRAM_VER = "2.46"
HEADER_FRONT_SIZE = 2048
MAX_FILE_SIZE = 1024 * 1024 * 10
MAX_STRING_SIZE = 256


class TrIDDef(object):
    # TrID definition.
    def __init__(self):
        self.filetype = ""
        self.ext = []
        self.mime = ""
        self.filename = ""
        self.tag = 0
        self.rem = ""
        self.refurl = ""
        self.user = ""
        self.email = ""
        self.home = ""
        self.filenum = 0
        self.checkstrings = True
        self.refine = ""
        self.patterns = []
        self.strings = []
    def __str__(self):
        return "FileType: '%s', Ext: '%s', Patterns: %d, Strings: %d" % \
               (self.filetype, self.ext,
               len(self.patterns), len(self.strings))

class TrIDResult(object):
    # TrID analysis results structure
    def __init__(self):
        self.perc = 0
        self.pts = 0
        self.patt = 0
        self.str = 0
        self.triddef = ""
    def __str__(self):
        return "Result: FileType='%s')" % self.triddef.filetype

@dataclass
class TrIDDefsBlock:
    # Contains the actual block of defs that will be passed to the analysis function
    version: int        # to check the versions of cached definitions
    defs_num: int       # total defs num
    defs_group: list    # contain the lists of definitions grouped by each first-byte value
    defs_index: object = None  # definitions indexed by first fixed pattern prefix
    index_slots: object = None # (position, prefix length) pairs used by defs_index


if __name__ == "__main__":
    sys.modules.setdefault("trid", sys.modules[__name__])
TrIDDef.__module__ = "trid"
TrIDResult.__module__ = "trid"
TrIDDefsBlock.__module__ = "trid"


def LoadDataFromFile(filename):
    # Load the relevant parts of a (big) file for analysis
    filesize = os.path.getsize(filename)
    with open(filename, "rb") as f:
        if filesize <= MAX_FILE_SIZE:
            data = f.read()
        else:
            part_size = MAX_FILE_SIZE // 2
            data = f.read(part_size)
            f.seek(filesize - part_size)
            data += b"|" + f.read()
    return data.upper()


def get_cmdline():
    # Evaluate command line parameters, usage & help.
    parser = argparse.ArgumentParser(
             description="Identifies the type of a file based on a library of filetypes definitions")
    parser.add_argument("files", action="store", nargs="*", 
                        help = "files to scan (can include path & wildcards; quote patterns like '*' to prevent shell expansion)")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-ae", "--add-ext", action="store_true", dest="addext", default=False,
                        help = "add guessed extension to filenames")
    group.add_argument("-ce", "--change-ext", action="store_true", dest="changeext", default=False,
                        help = "change filenames extensions")
    parser.add_argument("-r", "--recursive", action="store_true",
                        help="recursively include files in subdirectories")
    parser.add_argument("-d", action="store", dest="trdfile",
                        help = "use specified defs package")
    parser.add_argument("-ns", "--no-strings", action="store_true", dest="nostr", default=False,
                        help = "disable strings check")
    parser.add_argument("-n", action="store", dest="resnum", type=int, default=5,
                        help = "show the first RESNUM matches")
    parser.add_argument("-e", "--extended-info", action="store_true", dest="ex_info", default=False,
                        help = "show more info from the matching definition")
    parser.add_argument("-w", "--wait", action="store_true", dest="wait", default=False,
                        help = "wait a key at the end")
    parser.add_argument("-u", "--update", action="store_true", dest="update", default=False,
                        help = "update defs package and exit")
    parser.add_argument("-f", "--file-list", action="store", dest="filelist",
                        help="specify a text file containing a list of files to scan " 
                        "(use - to read from stdin)")
    parser.add_argument("-o", "--out", action="store", dest="outfile",
                        help="create a CSV file with the results")
    parser.add_argument("-v", "--version", action='store_true', dest="version", default=False,
                        help = "show program version, platform, licenses and exit") 
    res = parser.parse_args()
    
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    return res

def get_files(filenames, recursive=False):
    # Expand filenames and directories into a list of file paths.
    result = []
    for arg in filenames:
        if os.path.isfile(arg):
            result.append(arg)
            continue
        
        if os.path.isdir(arg):
            if recursive:
                for root, _, files_ in os.walk(arg):
                    for f in files_:
                        result.append(os.path.join(root, f))
            else:
                try:
                    items = os.listdir(arg)
                    for item in items:
                        full_path = os.path.join(arg, item)
                        if os.path.isfile(full_path):
                            result.append(full_path)
                except (OSError, PermissionError):
                    # Skip inaccessible directories
                    pass
            continue
        
        # Treat as pattern
        has_wildcard = '*' in arg or '?' in arg or '[' in arg
        if not has_wildcard:
            # No wildcards: simple glob (likely empty if not existing file/dir)
            matches = glob.glob(arg, recursive=False)
            result.extend([m for m in matches if os.path.isfile(m)])
            continue
        
        # Has wildcards: apply glob, with recursion logic
        if recursive:
            if '**' in arg:
                # Already recursive pattern
                pattern = arg
            else:
                # Construct recursive pattern
                dir_part = os.path.dirname(arg) or '.'
                base_part = os.path.basename(arg)
                if base_part:
                    pattern = os.path.join(dir_part, '**', base_part)
                else:
                    # Ends with separator (unlikely here, but fallback)
                    pattern = arg + '**/*'
            matches = glob.glob(pattern, recursive=True)
        else:
            matches = glob.glob(arg, recursive=False)
        
        # Filter to files only
        result.extend([m for m in matches if os.path.isfile(m)])
    
    return result


def get_files_from_filelist(source):
    # Process a list of file, or read from stdin
    lines = []
    if source == "-":
        # read the list from stdin
        for line in sys.stdin:
            # Strip leading/trailing whitespace, including the newline character
            line = line.strip()
            if line:  # Ensure the line isn't empty
                lines.append(line)
    else:
        try:
            with open(source, "r") as f:
                lines = f.read().splitlines()
        except IOError:
            errprint(f"I/O Error: unable to open file {source}.")
            sys.exit(1)
    return lines


def errprint(msg, filename=os.path.basename(sys.argv[0])):
    txt = f"{filename}: {msg}\n"
    print(txt, file=sys.stderr)


def trdpkg2defs(filename, usecache=False):
    # Get a list of TrID's definition from a TRD package file
    path = Path(filename)
    cachefilename = '.' + path.name + ".cache"
    cachefilename = path.parent / cachefilename
    cached = False
    updatecache = False

    ts = perf_counter()
    if usecache and os.path.exists(cachefilename):
        if os.path.getmtime(cachefilename) > os.path.getmtime(filename):
            print("  (Reading from cache...)")
            try:
                with open(cachefilename, "rb") as f:
                    TDB = pickle.load(f)
                # check cached TDB version - if older, invalidate
                if isinstance(TDB, TrIDDefsBlock) and TDB.version == 2:
                    cached = True
                else:
                    print("  (Wrong cached data version)")
            except Exception:
                print("  (Unable to read cached data)")

    if not cached:
        triddefs = []
        # read the entire .trd file
        try:
            with open(filename, "rb") as f:
                package = f.read()
        except IOError:
            errprint(f"I/O Error: unable to read TrID definitions from file {filename}.")
            sys.exit(1)

        # couple of basic sanity checks
        
        if package[:4]+package[8:12] != b"RIFFTRID":
            errprint(f"Error: file {filename} is not a TrID definitions package!")
            sys.exit(1)

        pkglen = unpack_from("<i", package, offset=4)[0] 
        if (pkglen + 8) != len(package):
            errprint(f"Error: TrID definitions package {filename} lenght mismatch!")
            sys.exit(1)

        # decoding...

        infoBlock = package[12:12+12]
        defsnum = unpack_from("<i", infoBlock, offset = len(infoBlock)-4)[0]
        blen= unpack_from("<i", package, offset = 28)[0]
        package = package[32:32+blen]

        loopdefpos = 0
        for i in range(defsnum):
            if  loopdefpos < len(package) - 8:
                chunkid = package[loopdefpos:loopdefpos+4]
                if chunkid == b"DEF ":
                    blen = unpack_from("<i", package, offset = loopdefpos+4)[0]
                    defblock = package[loopdefpos+8:loopdefpos+8+blen]
                    loopdefpos += 8 + blen
                    triddef = trdblock2def(defblock)
                    triddefs.append(triddef)
                    
        # reorganize definitions in various lists, per starting byte
        TDB = TrIDDefsBlock(
            version = 2,
            defs_num = len(triddefs),
            defs_group = {},
            defs_index = {},
            index_slots = (),
        )
        for b in range(-1, 256):
            TDB.defs_group[b] = []
        index_slots = set()
        for triddef in triddefs:
            ppos = triddef.patterns[0][0]
            patt = triddef.patterns[0][1]
            pbyte = patt[0]
            # if the first pattern include byte 0, add to the corresponding def-list, else in the catch-all
            if ppos == 0:
                TDB.defs_group[pbyte].append(triddef)
            else:
                TDB.defs_group[-1].append(triddef)
            plen = min(4, len(patt))
            prefix = patt[:plen]
            slot = (ppos, plen)
            index_slots.add(slot)
            TDB.defs_index.setdefault(slot, {}).setdefault(prefix, []).append(triddef)
        TDB.index_slots = tuple(sorted(index_slots))
        updatecache = True

    te= perf_counter()
    #print(f"  (Time: {(te-ts):.2f})") #info

    if usecache and updatecache:
        print("  (Updating cache...)")
        with open(cachefilename, "wb") as f:
            pickle.dump(TDB, f, -1)

    return TDB


def trdblock2def(block):
    # Decode a single definition block in TRD format
    triddef = TrIDDef()
    defpos = 0
    while defpos < len(block)-8:
        chunkid = block[defpos:defpos+4]
        chunklen = unpack_from("<i", block, offset=defpos+4)[0]
        chunk = block[defpos+8:defpos+8+chunklen]
        if chunkid == b"DATA":
            subpos = 0
            while subpos < len(chunk)-8:
                subchunkid = chunk[subpos:subpos+4]
                subchunklen = unpack_from("<i", chunk, offset=subpos+4)[0]
                subchunk = chunk[subpos+8:subpos+8+subchunklen]
                subpos += 8+subchunklen
                if subchunkid == b"PATT":
                    triddef.patterns = trdblock2patts(subchunk)
                elif subchunkid == b"STRN":
                    triddef.strings = trdblock2strs(subchunk)
        elif chunkid == b"INFO":
            infopos = 0
            while infopos < len(chunk)-6:
                infotype = chunk[infopos:infopos+4]
                infolen = unpack_from("<h", chunk, offset=infopos+4)[0]
                infotext = chunk[infopos+6:infopos+6+infolen]
                infopos += 6+infolen
                if infotype == b"TYPE":
                    triddef.filetype = infotext.decode()
                elif infotype == b"EXT ":
                    triddef.ext = infotext.decode()
                elif infotype == b"TAG ":
                    triddef.tag = unpack("<i", infotext)[0]
                elif infotype == b"MIME":
                    triddef.mime = infotext.decode()
                elif infotype == b"NAME":
                    triddef.filename = infotext.decode()
                elif infotype == b"FNUM":
                    triddef.filenum = unpack("<i", infotext)[0]
                elif infotype == b"RURL":
                    triddef.refurl = infotext.decode()
                elif infotype == b"USER":
                    triddef.user = infotext.decode()
                elif infotype == b"MAIL":
                    triddef.email = infotext.decode()
                elif infotype == b"HOME":
                    triddef.home = infotext.decode()
                elif infotype == b"REM ":
                    triddef.rem = infotext.decode()
        defpos += 8 + chunklen
    return triddef

def trdblock2patts(chunk):
    # Decode the patterns block from a TRD def
    patts = []
    pattn = unpack_from("<h", chunk)[0]
    cpos = 2
    for i in range(pattn):
        patpos = unpack_from("<h", chunk, offset=cpos)[0]
        patlen = unpack_from("<h", chunk, offset=cpos+2)[0]
        patt = chunk[cpos+4:cpos+4+patlen]
        patts.append((patpos,patt))
        cpos+=4+patlen
    return patts

def trdblock2strs(chunk):
    # Decode the strings block from a TRD def
    strings = []
    strn = unpack_from("<h", chunk)[0]
    cpos = 2
    for i in range(strn):
        slen = unpack_from("<i", chunk, offset=cpos)[0]
        strings.append(chunk[cpos+4:cpos+4+slen])
        cpos+=4+slen
    return strings


def tridAnalyze(filename, TDB, stringcheck=True):
    # Analyze a file with the given definitions
    results = []
    totalpts = 0
    foundcache = {}
    stopcache = {}
    cachehits = 0
    cachemiss = 0

    # read the first part of the file
    try:
        filesize = os.path.getsize(filename)
        with open(filename, "rb") as f:
            frontsize = min(filesize, HEADER_FRONT_SIZE)
            frontblock = f.read(frontsize)
    except:
        errprint(f"I/O Error: unable to process file {filename}.")
        return results

    if filesize == 0:
        return results
    elif frontsize < filesize:
        filebuffer = ""
    else:
        filebuffer = frontblock.upper()
        if STRINGZILLA_AVAILABLE:
            filebufferZ = stringzilla.Str(filebuffer)

    # build a triddefs list from TDB, depending on the first fixed pattern prefix
    defs_index = getattr(TDB, "defs_index", None)
    index_slots = getattr(TDB, "index_slots", None)
    if defs_index and index_slots:
        triddefs = []
        for ppos, plen in index_slots:
            if frontsize >= ppos + plen:
                prefix = frontblock[ppos:ppos+plen]
                triddefs.extend(defs_index.get((ppos, plen), {}).get(prefix, ()))
    else:
        triddefs = itertools.chain(TDB.defs_group[-1], TDB.defs_group[frontblock[0]])

    # search for matches against each definitions
    for triddef in triddefs:
        # check for fixed patterns at fixed positions
        pts = 0
        for pattern in triddef.patterns:
            ppos = pattern[0]
            plen = len(pattern[1])
            if frontsize >= ppos + plen:
                if pattern[1] == frontblock[ppos:ppos+plen]:
                    if ppos == 0:
                        pts += plen * 1000
                    else:
                        pts += plen
                else:
                    pts = 0
                    break
            else:
                pts = 0
                break
        # check for strings anywhere
        if pts > 0 and stringcheck:
            if not filebuffer:
                filebuffer = LoadDataFromFile(filename)
                if STRINGZILLA_AVAILABLE:
                    filebufferZ = stringzilla.Str(filebuffer)
            skipsearch = False
            #check if one of the strings is known a show-stopper!
            for string in triddef.strings:
                if string in stopcache:
                    #print("Skipped %i" % (len(triddef.strings))) #info
                    skipsearch = True
                    pts = 0
                    break
            #if not, start searching as usual (but with cache!)
            if not skipsearch:
                for string in triddef.strings:
                    if string in foundcache:
                        #print "Hit: [%s]" % (string)
                        cachehits += 1
                        pts += len(string) * 500
                    else:
                        cachemiss += 1
                        # different code paths to make use of stringzilla
                        if STRINGZILLA_AVAILABLE:
                            subfound = filebufferZ.find(string) != -1
                        else:        
                            subfound = string in filebuffer
                        
                        if subfound:
                            pts += len(string) * 500
                            foundcache[string] = True
                        else:
                            pts = 0
                            stopcache[string] = True
                            break
 
                            
        # store the results / just a raw list at the moment
        if pts > 0:
            totalpts += pts
            tr = TrIDResult()
            tr.perc = 0
            tr.pts = pts
            tr.patt = len(triddef.patterns)
            tr.str = len(triddef.strings)
            tr.triddef = triddef
            results.append(tr)

    for res in results:
        res.perc = res.pts * 100 / totalpts

    results = sorted(results, reverse=True, key=lambda res: res.pts)

    #print(f"  (Hits: {cachehits} - Miss: {cachemiss} - stopcache: {len(stopcache)})") #info
    
    return results


def get_unique_filename(path):
    if not path.exists():
        return str(path)
    
    base = path.stem 
    ext = path.suffix # extension with dot
    parent = path.parent 
    counter = 1
    
    while True:
        new_name = f"{base} ({counter}){ext}"
        new_path = parent / new_name
        if not new_path.exists():
            return str(new_path)
        counter += 1


def trid_update(trdfilename):
    # Check and get the latest TrID's definition package

    def chunked(file, chunk_size):
        # Helper function to read files in chunks.
        return iter(lambda: file.read(chunk_size), b'')


    def MD5digest(filename=None, data=None):
        # Return an MD5 digest for a file or a string.
        h = hashlib.md5()
        if filename:
            with open(filename, "rb") as f:
                for data in chunked(f, 1024*1024):
                    h.update(data)
        elif data:
            h.update(data)
        return h.hexdigest()

    def trdget(url_defs):
        # Download & unzip a new TrID defs package
        try:
            with tempfile.TemporaryFile() as f:
                u = urlopen(url_defs)
                size = u.getheader('Content-Length')
                if size:
                    print(f"File size: {(int(size) // 1024)}KB")
                for data in chunked(u, 1024*8):
                    f.write(data)
                    print(f"\r{(f.tell() // 1024)}KB", end='')
                    sys.stdout.flush()
                print("\r", end='')
                with zipfile.ZipFile(f) as z:
                    trd = z.read("triddefs.trd")
        except Exception as err:
            errprint("Unable to download updated file.", err)
            sys.exit(1)

        return trd

    url_MD5 = "http://mark0.net/download/triddefs.trd.md5"
    url_defs = "http://mark0.net/download/triddefs.zip"

    print(f"TrID defs package {trdfilename} - Checking for updates...")

    if os.path.exists(trdfilename):
        curdigest = MD5digest(filename=trdfilename)
        print("MD5:", curdigest)
    else:
        curdigest = 0
        print(f"File {trdfilename} not found")

    print("Checking last version online...")
    try:
        with urlopen(url_MD5) as f:
            newdigest = f.read().decode()
        print("MD5:", newdigest)
    except Exception as err:
        errprint("Unable to get updated MD5.", err)
        sys.exit(1)

    if curdigest == newdigest:
        print("Current defs are up-to-date.")
        sys.exit(0)

    print("Downloading new defs...")
    trdpack = trdget(url_defs)

    print("Checking defs integrity...")
    if MD5digest(data=trdpack) == newdigest:
        with open(trdfilename, "wb") as f:
            f.write(trdpack)
        print("OK.")
        sys.exit(0)
    else:
        errprint("Error: digest don't match. Retry!.")
        sys.exit(1)

    return


def get_base_path():
    # Get the correct base dir, including PyInstaller bundles.
    if getattr(sys, 'frozen', False):
        base_path = Path(sys.executable).resolve().parent
    else:
        base_path = Path(__file__).resolve().parent
    return base_path


def output_res(results, filename):
    # Create a parse-friendly CSV file with the results
    
    try:
        with open(filename, "w", newline='', encoding='utf-8') as f:
            csv_writer = csv.writer(f)
            data_row = ["File", "TrID-Score", "%", "Extension(s)", "Filetype", "MIME type"]
            csv_writer.writerow(data_row)
            for result in results:
                data_row = [ result[0] ] # filename
                res = result[1]
                if res:
                    data_row.extend([res.pts, f"{res.perc:.1f}%", res.triddef.ext, res.triddef.filetype, 
                                     res.triddef.mime])
                else:
                    data_row.extend(["0", "", "", "", ""])
                csv_writer.writerow(data_row)
        print(f"\nCSV file '{filename}' written ({len(results)} rows).")
    except IOError:
        errprint(f"I/O Error writing file '{filename}'")


def version_info():
    # various info and licenses notices
    print("Platform Informations")
    print(f"  Operating System: {platform.system()}")
    print(f"  OS release: {platform.release()}")
    print(f"  OS details: {platform.platform()}")
    print(f"  Machine architecture (CPU): {platform.machine()}")
    print(f"  Python Interpreter: {platform.architecture()[0]}")

    notes = []
    if STRINGZILLA_AVAILABLE:
        notes.append("  StringZilla library (C) Ash Vardanian - Three-clause BSD license")
    if notes:
        print("Components copyrights/licenses")
        print("\n".join(notes))
    sys.exit(0)

# --------------------------------------------------------------

def main():

    print(f"TrID - File Identifier v{PROGRAM_VER} - (C) 2003-2025 By Marco Pontello\n")

    # eval parameters
    params = get_cmdline()

    # display various info
    if params.version:
        version_info()

    # set definitions from specified file, or try current path, or script path
    trdfilename = params.trdfile
    if not trdfilename:
        trdfilename = "triddefs.trd"
        if not os.path.exists(trdfilename):
            trdfilename = get_base_path() / trdfilename

    # check if a definition supdate is requested
    if params.update:
        trid_update(trdfilename)

    # build files list to examine
    filenames = get_files(params.files, recursive=params.recursive)
    if params.filelist:
        filenames.extend(get_files_from_filelist(params.filelist))
    filenames = sorted(set(filenames))

    if len(filenames) == 0:
        errprint("Error: no file(s) to analyze!")
        sys.exit(1)

    # try load definitions
    print("Loading definitions from file:", trdfilename)
    if not os.path.exists(trdfilename):
        errprint(f"I/O Error: file {trdfilename} not found.")
        print("(you may download the definitions package with --update)")
        sys.exit(1)
    TDB = trdpkg2defs(trdfilename, usecache=True)
    print("Definitions found:", TDB.defs_num)

    #id process
    sttime_trid_analyze = perf_counter()
    stringcheck = True if not params.nostr else False
    rencount = 0
    renerr = 0
    results_list = []
    print("Analyzing...")
    for filename in filenames:
        print("\nFile:", filename)
        
        if os.path.exists(filename):
            results = tridAnalyze(filename, TDB, stringcheck)
            
            if results:
                for res in results[:min(len(results), params.resnum)]:
                    print("%5.1f%% (.%s) %s (%i/%i/%i)" % (res.perc, res.triddef.ext,
                                                           res.triddef.filetype,
                                                           res.pts, res.patt, res.str))

                    if params.ex_info:
                        if res.triddef.mime:
                            print("         Mime type  : ", res.triddef.mime)
                        if res.triddef.refurl:
                            print("         Related URL: ", res.triddef.refurl)
                        if res.triddef.rem:
                            print("         Remarks    : ", res.triddef.rem)
                        print("       Definition   : ", res.triddef.filename)
                        print("         Files      : ", res.triddef.filenum)
                        if res.triddef.user:
                            print("       Author       : ", res.triddef.user)
                        if res.triddef.email:
                            print("         E-Mail     : ", res.triddef.email)
                        if res.triddef.home:
                            print("         Home Page  : ", res.triddef.home)

                    results_list.append( (filename, res))

            else:
                print(" " * 6, "Unknown!")
                
                results_list.append( (filename, None))


            if results and (params.addext or params.changeext):
                res = results[0]
                newext = res.triddef.ext.split("/")[0].lower()
                # check if the matching filetype have an associate extension
                if newext: 
                    path = Path(filename)
                    rename = False
                    renerr = 0

                    # Check if it's needed to add the guessed extension
                    if params.addext:
                        if res.triddef.ext:
                            newfilename = path.with_suffix(path.suffix + "." + newext)
                            rename = True

                    # Check if it's needed to change to the guessed extension
                    if params.changeext:
                        if path.suffix.upper().strip(".") not in res.triddef.ext.split("/"):
                            newfilename = path.with_suffix("." + newext)
                            rename = True

                    if rename:
                        newfilename = get_unique_filename(newfilename)
                        try:
                            path.rename(newfilename)
                            rencount += 1
                        except:
                            renerr += 1
        else:
            print("  File not found! Skipping.")

    ettime_trid_analyze = perf_counter()
    
    if params.addext or params.changeext:
        print(f"\n{rencount} file(s) renamed. ", end="")
        if renerr:
            print(f"\n{renerr} error(s).", end="")
        print()

    #print(f"Elapsed time: {ettime_trid_analyze-sttime_trid_analyze:.2f}sec")

    if params.wait:
        input("Press Enter to continue...")

    # prepare the CSV file with the results for easy parsing
    if params.outfile:
        output_res(results_list, params.outfile)

    sys.exit(0)


if __name__ == "__main__":
    main()
