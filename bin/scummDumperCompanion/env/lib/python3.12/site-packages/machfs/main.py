import struct
from macresources import Resource, make_file, parse_file
from . import btree, bitmanip
from .directory import AbstractFolder, Folder, File


def _catalog_rec_sort(b):
    order = [
        0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07,
        0x08, 0x09, 0x0a, 0x0b, 0x0c, 0x0d, 0x0e, 0x0f,
        0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17,
        0x18, 0x19, 0x1a, 0x1b, 0x1c, 0x1d, 0x1e, 0x1f,

        0x20, 0x22, 0x23, 0x28, 0x29, 0x2a, 0x2b, 0x2c,
        0x2f, 0x30, 0x31, 0x32, 0x33, 0x34, 0x35, 0x36,
        0x37, 0x38, 0x39, 0x3a, 0x3b, 0x3c, 0x3d, 0x3e,
        0x3f, 0x40, 0x41, 0x42, 0x43, 0x44, 0x45, 0x46,

        0x47, 0x48, 0x58, 0x5a, 0x5e, 0x60, 0x67, 0x69,
        0x6b, 0x6d, 0x73, 0x75, 0x77, 0x79, 0x7b, 0x7f,
        0x8d, 0x8f, 0x91, 0x93, 0x96, 0x98, 0x9f, 0xa1,
        0xa3, 0xa5, 0xa8, 0xaa, 0xab, 0xac, 0xad, 0xae,

        0x54, 0x48, 0x58, 0x5a, 0x5e, 0x60, 0x67, 0x69,
        0x6b, 0x6d, 0x73, 0x75, 0x77, 0x79, 0x7b, 0x7f,
        0x8d, 0x8f, 0x91, 0x93, 0x96, 0x98, 0x9f, 0xa1,
        0xa3, 0xa5, 0xa8, 0xaf, 0xb0, 0xb1, 0xb2, 0xb3,

        0x4c, 0x50, 0x5c, 0x62, 0x7d, 0x81, 0x9a, 0x55,
        0x4a, 0x56, 0x4c, 0x4e, 0x50, 0x5c, 0x62, 0x64,
        0x65, 0x66, 0x6f, 0x70, 0x71, 0x72, 0x7d, 0x89,
        0x8a, 0x8b, 0x81, 0x83, 0x9c, 0x9d, 0x9e, 0x9a,

        0xb4, 0xb5, 0xb6, 0xb7, 0xb8, 0xb9, 0xba, 0x95,
        0xbb, 0xbc, 0xbd, 0xbe, 0xbf, 0xc0, 0x52, 0x85,
        0xc1, 0xc2, 0xc3, 0xc4, 0xc5, 0xc6, 0xc7, 0xc8,
        0xc9, 0xca, 0xcb, 0x57, 0x8c, 0xcc, 0x52, 0x85,

        0xcd, 0xce, 0xcf, 0xd0, 0xd1, 0xd2, 0xd3, 0x26,
        0x27, 0xd4, 0x20, 0x4a, 0x4e, 0x83, 0x87, 0x87,
        0xd5, 0xd6, 0x24, 0x25, 0x2d, 0x2e, 0xd7, 0xd8,
        0xa7, 0xd9, 0xda, 0xdb, 0xdc, 0xdd, 0xde, 0xdf,

        0xe0, 0xe1, 0xe2, 0xe3, 0xe4, 0xe5, 0xe6, 0xe7,
        0xe8, 0xe9, 0xea, 0xeb, 0xec, 0xed, 0xee, 0xef,
        0xf0, 0xf1, 0xf2, 0xf3, 0xf4, 0xf5, 0xf6, 0xf7,
        0xf8, 0xf9, 0xfa, 0xfb, 0xfc, 0xfd, 0xfe, 0xff,
    ]

    b = b[0] # we are only sorting keys!

    return b[:4] + bytes(order[ch] for ch in b[5:])


def _suggest_allocblk_size(volsize, minalign):
    min_nonalloc_blks = 6 # just for this estimation
    retval = minalign
    while volsize - min_nonalloc_blks*512 > retval*65536:
        retval += minalign
    return retval


def _get_every_extent(nblocks, firstrecord, cnid, xoflow, fork):
    accum = 0
    extlist = []

    for a, b in btree.unpack_extent_record(firstrecord):
        if not b: continue
        accum += b
        extlist.append((a, b))

    while accum < nblocks:
        nextrecord = xoflow[cnid, fork, accum]
        for a, b in btree.unpack_extent_record(nextrecord):
            if not b: continue
            accum += b
            extlist.append((a, b))

    return extlist


def _encode_name(name, kind='file'):
    longest = {'file': 31, 'vol': 27, 'bb': 15}[kind]

    try:
        encoded = name.encode('mac_roman')
    except UnicodeEncodeError:
        raise BadNameError(name)
    except AttributeError:
        pass

    if not 1 <= len(encoded) <= longest or b':' in encoded:
        raise BadNameError(name)

    return encoded


def _bb_name(name):
    return bitmanip.pstring(_encode_name(name)).ljust(16)


def _common_prefix(*tuples):
    for i in range(min(len(t) for t in tuples)):
        for t in tuples[1:]:
            if t[i] != tuples[0][i]:
                return i

    return 0


def _link_aliases(vol_cr_date, cnid_dict): # vol creation date confirms within-volume alias
    for cnid, obj in cnid_dict.items():
        try:
            if obj.flags & 0x8000:
                alis_rsrc = next(r.data for r in parse_file(obj.rsrc) if r.type == b'alis')

                # print(hex(obj.flags))
                # print(obj)
                # open('/tmp/interpreting' + hex(cnid),'wb').write(alis_rsrc)

                userType, aliasSize, aliasVersion, \
                thisAliasKind, volumeName, volumeCrDate, \
                volumeSig, volumeType, parDirID, fileName, \
                fileNum, fileCrDate, fileType, fdCreator, \
                nlvlFrom, nlvlTo, volumeAttributes, volumeFSID \
                = struct.unpack_from('>4s H hh 28p L 2s hL 64p LL 4s4s HHLh', alis_rsrc)

                # print(userType, aliasSize, aliasVersion,
                #     thisAliasKind, volumeName, volumeCrDate,
                #     volumeSig, volumeType, parDirID, fileName,
                #     fileNum, fileCrDate, fileType, fdCreator,
                #     nlvlFrom, nlvlTo, volumeAttributes, volumeFSID)

                if volumeCrDate != vol_cr_date: raise ValueError

                obj.aliastarget = cnid_dict[fileNum]

        except (AttributeError, KeyError, StopIteration, ValueError):
            pass


def _defer_special_files(iter_paths):
    """Defer special files (aliases) to late CNIDs, and resolve aliases"""
    approved_dict = dict()
    unapproved = []

    for path, obj in iter_paths:
        if isinstance(obj, File) and obj.aliastarget is not None:
            unapproved.append((path, obj))
        else:
            yield path, obj, None
            approved_dict[id(obj)] = path

    while unapproved:
        made_progress = False

        for i in reversed(range(len(unapproved))):
            path, obj = unapproved[i]

            try:
                targetpath = approved_dict[id(obj.aliastarget)]
            except KeyError:
                continue

            yield path, obj, targetpath
            approved_dict[id(obj)] = path

            unapproved.pop(i)
            made_progress = True

        if not made_progress: break


def _alis_append(alis, kind, data):
    if len(alis) % 2: alis.append(0)
    alis.extend(struct.pack('>hH', kind, len(data)))
    alis.extend(data)
    if len(alis) % 2: alis.append(0)


class _TempWrapper:
    """Volume uses this to store metadata while serialising"""
    def __init__(self, of):
        self.of = of


class OutOfSpaceError(Exception):
    pass


class BadNameError(Exception):
    pass


class Volume(AbstractFolder):
    def __init__(self):
        super().__init__()

        self.crdate = self.mddate = self.bkdate = 0
        self.name = 'Untitled'

    def read(self, from_volume):
        for i in range(0, len(from_volume), 512):
            if from_volume[i+1024:i+1024+2] == b'BD':
                if i: from_volume = from_volume[i:]
                break
        else:
            raise ValueError('Magic number not found in image')

        drSigWord, drCrDate, drLsMod, drAtrb, drNmFls, \
        drVBMSt, drAllocPtr, drNmAlBlks, drAlBlkSiz, drClpSiz, drAlBlSt, \
        drNxtCNID, drFreeBks, drVN, drVolBkUp, drVSeqNum, \
        drWrCnt, drXTClpSiz, drCTClpSiz, drNmRtDirs, drFilCnt, drDirCnt, \
        drFndrInfo, drVCSize, drVBMCSize, drCtlCSize, \
        drXTFlSize, drXTExtRec, \
        drCTFlSize, drCTExtRec, \
        = struct.unpack_from('>2sLLHHHHHLLHLH28pLHLLLHLL32sHHHL12sL12s', from_volume, 1024)

        self.crdate, self.mddate, self.bkdate = drCrDate, drLsMod, drVolBkUp

        block2offset = lambda block: 512*drAlBlSt + drAlBlkSiz*block
        getextents = lambda extents: b''.join(from_volume[block2offset(firstblk):block2offset(firstblk+blkcnt)] for (firstblk, blkcnt) in extents)
        getfork = lambda size, extrec1, cnid, fork: getextents(_get_every_extent((size+drAlBlkSiz-1)//drAlBlkSiz, extrec1, cnid, extoflow, fork))[:size]

        extoflow = {}
        for rec in btree.dump_btree(getfork(drXTFlSize, drXTExtRec, 3, 'data')):
            if rec[0] != 7: continue
            xkrFkType, xkrFNum, xkrFABN, extrec = struct.unpack_from('>xBLH12s', rec)
            if xkrFkType == 0xFF:
                fork = 'rsrc'
            elif xkrFkType == 0:
                fork = 'data'
            extoflow[xkrFNum, fork, xkrFABN] = extrec

        cnids = {}
        childlist = [] # list of (parent_cnid, child_name, child_object) tuples

        prev_key = None
        for rec in btree.dump_btree(getfork(drCTFlSize, drCTExtRec, 4, 'data')):
            # create a directory tree from the catalog file
            rec_len = rec[0]
            if rec_len == 0: continue

            key = rec[2:1+rec_len]
            val = rec[bitmanip.pad_up(1+rec_len, 2):]

            # if prev_key: # Uncomment this to test the sort order with 20% performance cost!
            #     if _catalog_rec_sort((prev_key,)) >= _catalog_rec_sort((key,)):
            #         raise ValueError('Sort error: %r, %r' % (prev_key, key))
            # prev_key = key

            ckrParID, namelen = struct.unpack_from('>LB', key)
            ckrCName = key[5:5+namelen]

            datatype = (None, 'dir', 'file', 'dthread', 'fthread')[val[0]]
            datarec = val[2:]

            # print(datatype + '\t' + repr(key))
            # print('\t', datarec)
            # print()

            if datatype == 'dir':
                dirFlags, dirVal, dirDirID, dirCrDat, dirMdDat, dirBkDat, dirUsrInfo, dirFndrInfo \
                = struct.unpack_from('>HHLLLL16s16s', datarec)

                f = Folder()
                cnids[dirDirID] = f
                childlist.append((ckrParID, ckrCName, f))

                f.crdate, f.mddate, f.bkdate = dirCrDat, dirMdDat, dirBkDat

            elif datatype == 'file':
                filFlags, filTyp, filUsrWds, filFlNum, \
                filStBlk, filLgLen, filPyLen, \
                filRStBlk, filRLgLen, filRPyLen, \
                filCrDat, filMdDat, filBkDat, \
                filFndrInfo, filClpSize, \
                filExtRec, filRExtRec, \
                = struct.unpack_from('>BB16sLHLLHLLLLL16sH12s12sxxxx', datarec)

                f = File()
                cnids[filFlNum] = f
                childlist.append((ckrParID, ckrCName, f))

                f.crdate, f.mddate, f.bkdate = filCrDat, filMdDat, filBkDat
                f.type, f.creator, f.flags, f.x, f.y = struct.unpack_from('>4s4sHHH', filUsrWds)

                f.data = getfork(filLgLen, filExtRec, filFlNum, 'data')
                f.rsrc = getfork(filRLgLen, filRExtRec, filFlNum, 'rsrc')

            # elif datatype == 3:
            #     print('dir thread:', rec)
            # elif datatype == 4:
            #     print('fil thread:', rec)

        for parent_cnid, child_name, child_obj in childlist:
            if parent_cnid != 1:
                parent_obj = cnids[parent_cnid]
                parent_obj[child_name] = child_obj

        self.update(cnids[2])

        self.pop('Desktop', None)
        self.pop('Desktop DB', None)
        self.pop('Desktop DF', None)

        _link_aliases(drCrDate, cnids)

    def write(self, size=800*1024, align=512, desktopdb=True, bootable=True, startapp=None, sparse=False):
        if align < 512 or align % 512:
            raise ValueError('align must be multiple of 512')

        if size < 400 * 1024 or size % 512:
            raise ValueError('size must be a multiple of 512b and >= 400K')

        # These are declared up here because they are needed for aliases
        drVN = _encode_name(self.name, 'vol')
        drSigWord = b'BD'
        drAtrb = 1<<8                  # volume attributes (hwlock, swlock, CLEANUNMOUNT, badblocks)
        drCrDate, drLsMod, drVolBkUp = self.crdate, self.mddate, self.bkdate

        # overall layout:
        #   1. two boot blocks (offset=0)
        #   2. one volume control block (offset=2)
        #   3. some bitmap blocks (offset=3)
        #   4. many allocation blocks
        #   5. duplicate VCB (offset=-2)
        #   6. unused block (offset=-1)

        # so we will our best guess at these variables as we go:
        # drNmAlBlks, drAlBlkSiz, drAlBlSt

        # the smallest possible alloc block size
        drAlBlkSiz = _suggest_allocblk_size(size, align)

        # how many blocks will we use for the bitmap?
        # (cheat by adding blocks to align the alloc area)
        bitmap_blk_cnt = 0
        while (size - (5+bitmap_blk_cnt)*512) // drAlBlkSiz > bitmap_blk_cnt*512*8:
            bitmap_blk_cnt += 1
        while (3+bitmap_blk_cnt)*512 % align:
            bitmap_blk_cnt += 1

        # decide how many alloc blocks there will be
        drNmAlBlks = (size - (5+bitmap_blk_cnt)*512) // drAlBlkSiz
        blkaccum = []

        def accumulate(x):
            blkaccum.extend(x)
            if len(blkaccum) > drNmAlBlks:
                raise OutOfSpaceError

        # <<< put the empty extents overflow file in here >>>
        extoflowfile = btree.make_btree([], bthKeyLen=7, blksize=drAlBlkSiz)
        # also need to do some cleverness to ensure that this gets picked up...
        drXTFlSize = len(extoflowfile)
        drXTExtRec_Start = len(blkaccum)
        accumulate(bitmanip.chunkify(extoflowfile, drAlBlkSiz))
        drXTExtRec_Cnt = len(blkaccum) - drXTExtRec_Start

        # write all the files in the volume
        topwrap = _TempWrapper(self)
        topwrap.path = (self.name,)
        topwrap.cnid = 2

        godwrap = _TempWrapper(None)
        godwrap.cnid = 1

        root_dict_backup = self._prefdict
        if desktopdb:
            self._prefdict = dict(self._prefdict)
            f = File()
            f.type, f.creator = b'FNDR', b'ERIK'
            f.flags = 0x4000 # invisible
            f.rsrc = make_file([Resource(b'STR ', 0, data=b'\x0AFinder 1.0')])
            self['Desktop'] = f
            if size >= 2*1024*1024:
                f = File()
                f.type, f.creator = b'BTFL', b'DMGR'
                f.flags = 0x4000
                f.data = btree.make_btree([], bthKeyLen=37, blksize=drAlBlkSiz)
                self['Desktop DB'] = f
                f = File()
                f.type, f.creator = b'DTFL', b'DMGR'
                f.flags = 0x4000
                self['Desktop DF'] = f

        system_folder_cnid = 0
        startapp_folder_cnid = 0
        bootblocks = bytearray(1024)

        path2wrap = {(): godwrap, (self.name,): topwrap}
        drNxtCNID = 16
        for path, obj, aliastarget in _defer_special_files(self.iter_paths()):
            path = (self.name,) + path
            wrap = _TempWrapper(obj)
            path2wrap[path] = wrap
            wrap.path = path
            wrap.cnid = drNxtCNID; drNxtCNID += 1

            if isinstance(obj, File) and obj.type.upper() == b'ZSYS':
                try:
                    sysname = path[-1]

                    fellows = path2wrap[path[:-1]].of.items()
                    fndrname = next(n for (n, o) in fellows if isinstance(o, File) and o.type == b'FNDR')

                    sysresources = parse_file(obj.rsrc)
                    boot1 = next(r for r in sysresources if (r.type, r.id) == (b'boot', 1))
                    bb = bytearray(boot1.data)
                    if len(bb) != 1024: raise ValueError

                    bb[0x0A:0x1A] = _bb_name(sysname)
                    bb[0x1A:0x2A] = _bb_name(fndrname)

                except:
                    pass

                else:
                    bootblocks[:] = bb
                    system_folder_cnid = path2wrap[path[:-1]].cnid

            if isinstance(obj, File) and startapp and path[1:] == tuple(startapp):
                startapp_folder_cnid = path2wrap[path[:-1]].cnid

            if isinstance(obj, File):
                wrap.data, wrap.rsrc = obj.data, obj.rsrc
                wrap.type, wrap.creator = obj.type, obj.creator

            # This is the place to manage your special files (aliases for now)
            if aliastarget is not None:
                aliastarget = (self.name,) + aliastarget # match the convention for this function
                targetobj = path2wrap[aliastarget].of # probe the target to set some metadata

                if isinstance(targetobj, Folder):
                    wrap.creator = b'MACS'
                    wrap.type = b'fdrp'

                elif isinstance(targetobj, Volume):
                    wrap.creator = b'MACS'
                    wrap.type = b'hdsk' if size > 1440*1024 else b'flpy'

                elif isinstance(targetobj, File):
                    wrap.creator = targetobj.creator

                    if targetobj.type == b'APPL':
                        wrap.type = b'adrp'
                    else:
                        wrap.type = targetobj.type

                wrap.data = b''

                userType = b''
                aliasSize = 9999 # fill this short at offset 4
                aliasVersion = 2
                thisAliasKind = 1 if isinstance(targetobj, Folder) else 0
                volumeName = drVN
                volumeCrDate = drCrDate
                volumeSig = drSigWord
                volumeType = 5 #2 if size == 400*1024 else 3 if size == 800*1024 else 4 if size == 1440*1024 else 1
                parDirID = path2wrap[aliastarget[:-1]].cnid
                fileName = _encode_name(aliastarget[-1])
                fileNum = path2wrap[aliastarget].cnid
                fileCrDate = path2wrap[aliastarget].of.crdate
                fileType = targetobj.type if isinstance(targetobj, File) else b''
                fdCreator = targetobj.creator if isinstance(targetobj, File) else b''
                nlvlFrom = len(path) - _common_prefix(path, aliastarget)
                nlvlTo = len(aliastarget) - _common_prefix(path, aliastarget)
                volumeAttributes = 0 # this is aliasmgr-specific
                volumeFSID = 0

                # Stress test: find file by name, not CNID
                # fileNum = 0

                alis = Resource(b'alis', 0, name=path[-1])
                alis.data[:] = struct.pack('>4s H hh 28p L 2s hL 64p LL 4s4s HHLh',
                    userType, aliasSize, aliasVersion, \
                    thisAliasKind, volumeName, volumeCrDate, \
                    volumeSig, volumeType, parDirID, fileName, \
                    fileNum, fileCrDate, fileType, fdCreator, \
                    nlvlFrom, nlvlTo, volumeAttributes, volumeFSID \
                ) + bytes(10) # reserved stuff

                _alis_append(alis.data, 0, aliastarget[-2].encode('mac_roman'))
                _alis_append(alis.data, 2, ':'.join(aliastarget).encode('mac_roman'))
                _alis_append(alis.data, -1, b'')

                struct.pack_into('>H', alis.data, 4, len(alis.data))

                # open('/tmp/creating','wb').write(alis.data)

                wrap.rsrc = make_file([alis])

            if isinstance(obj, File):
                wrap.dfrk = wrap.rfrk = (0, 0)
                if wrap.data:
                    pre = len(blkaccum)
                    accumulate(bitmanip.chunkify(wrap.data, drAlBlkSiz))
                    wrap.dfrk = (pre, len(blkaccum)-pre)
                if wrap.rsrc:
                    pre = len(blkaccum)
                    accumulate(bitmanip.chunkify(wrap.rsrc, drAlBlkSiz))
                    wrap.rfrk = (pre, len(blkaccum)-pre)

        self._prefdict = root_dict_backup

        catalog = [] # (key, value) tuples

        drFilCnt = 0
        drDirCnt = -1 # to exclude the root directory

        for path, wrap in path2wrap.items():
            if wrap.cnid == 1: continue

            obj = wrap.of
            pstrname = bitmanip.pstring(_encode_name(path[-1], 'file'))

            mainrec_key = struct.pack('>L', path2wrap[path[:-1]].cnid) + pstrname

            if isinstance(wrap.of, File):
                drFilCnt += 1

                cdrType = 2
                filFlags = 1 << 1 # file thread record exists, but is not locked, nor "file record is used"
                filTyp = 0
                filUsrWds = struct.pack('>4s4sHHHxxxxxx', wrap.type, wrap.creator, obj.flags, obj.x, obj.y)
                filFlNum = wrap.cnid
                filStBlk, filLgLen, filPyLen = wrap.dfrk[0], len(wrap.data), bitmanip.pad_up(len(wrap.data), drAlBlkSiz)
                filRStBlk, filRLgLen, filRPyLen = wrap.rfrk[0], len(wrap.rsrc), bitmanip.pad_up(len(wrap.rsrc), drAlBlkSiz)
                filCrDat, filMdDat, filBkDat = obj.crdate, obj.mddate, obj.bkdate
                filFndrInfo = bytes(16) # todo must fix
                filClpSize = 0 # todo must fix
                filExtRec = struct.pack('>HHHHHH', *wrap.dfrk, 0, 0, 0, 0)
                filRExtRec = struct.pack('>HHHHHH', *wrap.rfrk, 0, 0, 0, 0)

                mainrec_val = struct.pack('>BxBB16sLHLLHLLLLL16sH12s12sxxxx',
                    cdrType, \
                    filFlags, filTyp, filUsrWds, filFlNum, \
                    filStBlk, filLgLen, filPyLen, \
                    filRStBlk, filRLgLen, filRPyLen, \
                    filCrDat, filMdDat, filBkDat, \
                    filFndrInfo, filClpSize, \
                    filExtRec, filRExtRec, \
                )

            else: # assume directory
                drDirCnt += 1

                cdrType = 1
                dirFlags = 0 # must fix
                dirVal = len(wrap.of)
                dirDirID = wrap.cnid
                dirCrDat, dirMdDat, dirBkDat = obj.crdate, obj.mddate, obj.bkdate
                dirUsrInfo = bytes(16)
                dirFndrInfo = bytes(16)
                mainrec_val = struct.pack('>BxHHLLLL16s16sxxxxxxxxxxxxxxxx',
                    cdrType, dirFlags, dirVal, dirDirID,
                    dirCrDat, dirMdDat, dirBkDat,
                    dirUsrInfo, dirFndrInfo,
                )

            catalog.append((mainrec_key, mainrec_val))

            thdrec_key = struct.pack('>Lx', wrap.cnid)
            thdrec_val_type = 4 if isinstance(wrap.of, File) else 3
            thdrec_val = struct.pack('>BxxxxxxxxxL', thdrec_val_type, path2wrap[path[:-1]].cnid) + pstrname

            catalog.append((thdrec_key, thdrec_val))


        # now it is time to sort these records! fuck that shit...
        catalog.sort(key=_catalog_rec_sort)
        catalogfile = btree.make_btree(catalog, bthKeyLen=37, blksize=drAlBlkSiz)
        # also need to do some cleverness to ensure that this gets picked up...
        drCTFlSize = len(catalogfile)
        drCTExtRec_Start = len(blkaccum)
        accumulate(bitmanip.chunkify(catalogfile, drAlBlkSiz))
        drCTExtRec_Cnt = len(blkaccum) - drCTExtRec_Start

        if len(blkaccum) > drNmAlBlks:
            raise ValueError('Does not fit!')

        # Create the bitmap of free volume allocation blocks
        bitmap = bitmanip.bits(bitmap_blk_cnt * 512 * 8, len(blkaccum))

        # Set the startup app
        if system_folder_cnid and startapp_folder_cnid:
            try:
                bootblocks[0x5A:0x6A] = _bb_name(startapp[-1])
            except:
                startapp_folder_cnid = 0

        # Create the Volume Information Block
        drNmFls = sum(isinstance(x, File) for x in self.values())
        drNmRtDirs = sum(not isinstance(x, File) for x in self.values())
        drVBMSt = 3 # first block of volume bitmap
        drAllocPtr = 0
        drClpSiz = drXTClpSiz = drCTClpSiz = drAlBlkSiz
        drAlBlSt = 3 + bitmap_blk_cnt
        drFreeBks = drNmAlBlks - len(blkaccum)
        drWrCnt = 0 # ????volume write count
        drVCSize = drVBMCSize = drCtlCSize = 0
        drVolBkUp = 0                  # date and time of last backup
        drVSeqNum = 0                  # volume backup sequence number
        drFndrInfo = struct.pack('>LLL28x', system_folder_cnid, startapp_folder_cnid, startapp_folder_cnid)

        vib = struct.pack('>2sLLHHHHHLLHLH28pLHLLLHLL32sHHHLHHxxxxxxxxLHHxxxxxxxx',
            drSigWord, drCrDate, drLsMod, drAtrb, drNmFls,
            drVBMSt, drAllocPtr, drNmAlBlks, drAlBlkSiz, drClpSiz, drAlBlSt,
            drNxtCNID, drFreeBks, drVN, drVolBkUp, drVSeqNum,
            drWrCnt, drXTClpSiz, drCTClpSiz, drNmRtDirs, drFilCnt, drDirCnt,
            drFndrInfo, drVCSize, drVBMCSize, drCtlCSize,
            drXTFlSize, drXTExtRec_Start, drXTExtRec_Cnt,
            drCTFlSize, drCTExtRec_Start, drCTExtRec_Cnt,
        )
        vib += bytes(512-len(vib))

        assert all(len(x) == drAlBlkSiz for x in blkaccum)
        left_elements = [bootblocks, vib, bitmap, *blkaccum]

        unused_offset = sum(len(x) for x in left_elements)
        unused_length = size - unused_offset - 2*512

        right_elements = [vib, bytes(512)]

        if sparse:
            return b''.join(left_elements), unused_length, b''.join(right_elements)
        else:
            all_elements = left_elements
            all_elements.append(bytes(unused_length))
            all_elements.extend(right_elements)
            return b''.join(all_elements)
