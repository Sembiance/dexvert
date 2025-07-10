import struct
from . import bitmanip


class _Node:
    """Wrapper to use while serialising a B*-tree"""
    def __init__(self, **kwargs):
        self.records = []
        self.ndFLink = self.ndBLink = self.ndType = self.ndNHeight = 0
        self.__dict__.update(kwargs)

    def __bytes__(self):
        buf = bytearray(512)

        next_left = 14
        next_right = 510

        for r in self.records:
            if next_left + len(r) > next_right - 2:
                raise ValueError('cannot fit these records in a B*-tree node')

            buf[next_left:next_left+len(r)] = r
            struct.pack_into('>H', buf, next_right, next_left)

            next_left += len(r)
            next_right -= 2

        struct.pack_into('>H', buf, next_right, next_left) # offset of free space

        struct.pack_into('>LLBBH', buf, 0,
            self.ndFLink, self.ndBLink, self.ndType, self.ndNHeight&0xFF, len(self.records))

        return bytes(buf)

    def records_fit(self):
        """Tell whether the records will fit in 512 bytes"""
        try:
            self.__bytes__()
        except ValueError:
            return False
        else:
            return True


def unpack_extent_record(record):
    """Extract up to three (first_block, block_count) tuples from a 12-byte extent record"""
    a, b, c, d, e, f = struct.unpack('>6H', record)
    l = []
    if b: l.append((a, b))
    if d: l.append((c, d))
    if f: l.append((e, f))
    return l


def _unpack_btree_node(buf, start):
    """Slice a btree node into records, including the 14-byte node descriptor"""
    ndFLink, ndBLink, ndType, ndNHeight, ndNRecs = struct.unpack_from('>LLBBH', buf, start)
    offsets = list(reversed(struct.unpack_from('>%dH'%(ndNRecs+1), buf, start+512-2*(ndNRecs+1))))
    starts = offsets[:-1]
    stops = offsets[1:]
    records = [bytes(buf[start+i_start:start+i_stop]) for (i_start, i_stop) in zip(starts, stops)]
    return ndFLink, ndBLink, ndType, ndNHeight, records


def _pack_leaf_record(key, value):
    """Pack a key-value pair to go into a leaf node as a record"""
    if len(value) & 1: value += b'\x00'
    b = bytes([len(key)+1, 0, *key])
    if len(b) & 1: b += bytes(1)
    b += value
    return b


def _make_index_record(rec, pointer):
    """Convert a key-value to a special key-pointer record"""
    rec = rec[:1+rec[0]]
    rec = b'\x25' + rec[1:]
    rec += bytes(rec[0]+1-len(rec))
    rec += struct.pack('>L', pointer)
    return rec


def dump_btree(buf):
    """Walk an HFS B*-tree, returning an iterator of (key, value) tuples."""

    # Get the header node
    ndFLink, ndBLink, ndType, ndNHeight, (header_rec, unused_rec, map_rec) = _unpack_btree_node(buf, 0)

    # Ask about the header record in the header node
    bthDepth, bthRoot, bthNRecs, bthFNode, bthLNode, bthNodeSize, bthKeyLen, bthNNodes, bthFree = \
    struct.unpack_from('>HLLLLHHLL', header_rec)
    # print('btree', bthDepth, bthRoot, bthNRecs, bthFNode, bthLNode, bthNodeSize, bthKeyLen, bthNNodes, bthFree)

    # And iterate through the linked list of leaf nodes
    this_leaf = bthFNode
    while True:
        ndFLink, ndBLink, ndType, ndNHeight, records = _unpack_btree_node(buf, 512*this_leaf)

        yield from records

        if this_leaf == bthLNode:
            break
        this_leaf = ndFLink


def make_btree(records, bthKeyLen, blksize):
    nodemult = blksize // 512

    nodelist = [] # append to this as we go

    # pointers per index node, range 2-11
    index_step = 8 # not really worth tuning

    # First node is always a header node, with three records:
    # header records, reserved record, bitmap record
    headnode = _Node(ndType=1, ndNHeight=0, records=['header placeholder', bytes(128), 'bitmap placeholder'])
    nodelist.append(headnode)

    # Followed (in our implementation) by leaf nodes
    bthNRecs = 0
    bthRoot = 0
    bthDepth = 0
    for key, val in records:
        bthNRecs += 1
        bthRoot = 1
        bthDepth = 1

        packed = _pack_leaf_record(key, val)

        if bthNRecs == 1:
            nodelist.append(_Node(ndType=0xFF, ndNHeight=1))

        nodelist[-1].records.append(packed)

        if not nodelist[-1].records_fit():
            nodelist[-1].records.pop()
            nodelist.append(_Node(ndType=0xFF, ndNHeight=1, records=[packed]))

    # Create index nodes (some sort of Btree, they tell me)
    while len(nodelist) - bthRoot > 1:
        nums = list(range(bthRoot, len(nodelist)))
        groups = [nums[i:i+index_step] for i in range(0, len(nums), index_step)]

        bthRoot = len(nodelist)
        bthDepth = nodelist[-1].ndNHeight + 1

        # each element of groups will become a record:
        # it is currently a list of node indices to point to
        for g in groups:
            newnode = _Node(ndType=0, ndNHeight=bthDepth)
            for pointer in g:
                rec = nodelist[pointer].records[0]
                rec = _make_index_record(rec, pointer)
                newnode.records.append(rec)
            nodelist.append(newnode)

    # Header node already has a 256-bit bitmap record (2048-bit)
    # Add map nodes with 3952-bit bitmap recs to cover every node
    bits_covered = 2048
    mapnodes = []
    while bits_covered < bitmanip.pad_up(len(nodelist), nodemult):
        mapnode = _Node(ndType=2, ndNHeight=1)
        nodelist.append(mapnode)
        mapnodes.append(mapnode)
        mapnode.records = [bytes(3952//8)]
        bits_covered += len(mapnode.records[0]) * 8

    # Populate the bitmap (1 = used)
    headnode.records[2] = bitmanip.bits(2048, len(nodelist))
    for i, mnode in enumerate(mapnodes):
        nset = len(nodelist) - 2048 - i*3952
        mnode.records = [bitmanip.bits(3952, nset)]

    # Run back and forth to join up one linked list for each type
    most_recent = {}
    for i, node in enumerate(nodelist):
        node.ndBLink = most_recent.get(node.ndType, 0)
        most_recent[node.ndType] = i
    bthLNode = most_recent.get(0xFF, 0)
    most_recent = {}
    for i, node in reversed(list(enumerate(nodelist))):
        node.ndFLink = most_recent.get(node.ndType, 0)
        most_recent[node.ndType] = i
    bthFNode = most_recent.get(0xFF, 0)

    bthFree = bitmanip.pad_up(len(nodelist), nodemult) - len(nodelist)
    bthNNodes = len(nodelist) + bthFree

    # Populate the first (header) record of the header node
    bthNodeSize = 512
    headnode.records[0] = struct.pack('>HLLLLHHLL76x',
        bthDepth, bthRoot, bthNRecs, bthFNode, bthLNode,
        bthNodeSize, bthKeyLen, bthNNodes, bthFree)

    nodelist.append(512 * bthFree)

    return b''.join(bytes(node) for node in nodelist)
