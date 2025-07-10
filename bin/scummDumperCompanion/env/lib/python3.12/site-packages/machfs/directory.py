from collections.abc import MutableMapping
import os
from os import path
from macresources import make_rez_code, parse_rez_code, make_file, parse_file
from warnings import warn


TEXT_TYPES = [b'TEXT', b'ttro'] # Teach Text read-only


def _unsyncability(name): # files named '_' reserved for directory Finder info
    if path.splitext(name)[1].lower() in ('.rdump', '.idump'): return True
    if name.startswith('.'): return True
    if name == '_': return True
    if len(name) > 31: return True

    try:
        name.encode('mac_roman')
    except UnicodeEncodeError:
        return True

    return False

def _fuss_if_unsyncable(name):
    if _unsyncability(name):
        raise ValueError('Unsyncable name: %r' % name)

def _try_delete(name):
    try:
        os.remove(name)
    except FileNotFoundError:
        pass

def _symlink_rel(src, dst):
    rel_path_src = path.relpath(src, path.dirname(dst))
    os.symlink(rel_path_src, dst)

def _get_datafork_paths(base):
    """Symlinks are NOT GOOD"""
    base = path.abspath(path.realpath(base))
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = [x for x in dirnames if not _unsyncability(x)]
        filenames[:] = [x for x in filenames if not _unsyncability(x)]

        for kindcode, the_list in ((0, filenames), (1, dirnames)):
            for fname in the_list:
                nativepath = path.join(dirpath, fname)
                hfspath = tuple(_swapsep(c) for c in path.relpath(nativepath, base).split(path.sep))

                hfslink = kindcode # if not a link then default to this

                if path.islink(nativepath):
                    nativelink = path.realpath(nativepath)
                    if len(path.commonpath((nativelink, base))) < len(base): continue

                    hfslink = tuple(_swapsep(c) for c in path.relpath(nativelink, base).split(path.sep))
                    if hfslink == (path.relpath('x', 'x'),): hfslink = () # nasty special case

                yield nativepath, hfspath, hfslink

def _swapsep(n):
    return n.replace(':', path.sep)



class AbstractFolder(MutableMapping):
    def __init__(self, from_dict=()):
        self._prefdict = {} # lowercase to preferred
        self._maindict = {} # lowercase to contents
        self.update(from_dict)

    def __setitem__(self, key, value):
        if isinstance(key, tuple):
            if len(key) == 1:
                self[key[0]] = value
                return
            elif len(key) == 0:
                raise KeyError
            else:
                self[key[0]][key[1:]] = value
                return

        try:
            key = key.decode('mac_roman')
        except AttributeError:
            pass

        key.encode('mac_roman')

        lower = key.lower()
        self._prefdict[lower] = key
        self._maindict[lower] = value

    def __getitem__(self, key):
        if isinstance(key, tuple):
            if len(key) == 1:
                return self[key[0]]
            elif len(key) == 0:
                return self
            else:
                return self[key[0]][key[1:]]

        try:
            key = key.decode('mac_roman')
        except AttributeError:
            pass

        lower = key.lower()
        return self._maindict[lower]

    def __delitem__(self, key):
        if isinstance(key, tuple):
            if len(key) == 1:
                del self[key[0]]
                return
            elif len(key) == 0:
                raise KeyError
            else:
                del self[key[0]][key[1:]]
                return

        try:
            key = key.decode('mac_roman')
        except AttributeError:
            pass

        lower = key.lower()
        del self._maindict[lower]
        del self._prefdict[lower]

    def __iter__(self):
        return iter(self._prefdict.values())

    def __len__(self):
        return len(self._maindict)

    def __repr__(self):
        the_dict = {self._prefdict[k]: v for (k, v) in self._maindict.items()}
        return repr(the_dict)

    def __str__(self):
        lines = []
        for k, v in self.items():
            v = str(v)
            if '\n' in v:
                lines.append(k + ':')
                for l in v.split('\n'):
                    lines.append('  ' + l)
            else:
                lines.append(k + ': ' + v)
        return '\n'.join(lines)

    def iter_paths(self):
        for name, child in self.items():
            yield ((name,), child)
            try:
                childs_children = child.iter_paths()
            except AttributeError:
                pass
            else:
                for each_path, each_child in childs_children:
                    yield (name,) + each_path, each_child

    def walk(self, topdown=True):
        result = self._recursive_walk(my_path=(), topdown=topdown)

        if not topdown:
            result = list(result)
            result.reverse()

        return result

    def _recursive_walk(self, my_path, topdown): # like os.walk, except dirpath is a tuple
        dirnames = [n for (n, obj) in self.items() if isinstance(obj, AbstractFolder)]
        filenames = [n for (n, obj) in self.items() if not isinstance(obj, AbstractFolder)]

        yield (my_path, dirnames, filenames)

        if not topdown: dirnames.reverse() # hack to account for reverse() in walk()

        for dn in dirnames: # the caller can change dirnames in a loop
            yield from self[dn]._recursive_walk(my_path=my_path+(dn,), topdown=topdown)

    def read_folder(self, folder_path, date=0, mpw_dates=False):
        self.crdate = self.mddate = self.bkdate = date

        deferred_aliases = []
        for nativepath, hfspath, hfslink in _get_datafork_paths(folder_path):
            if hfslink == 0: # file
                thefile = File(); self[hfspath] = thefile
                thefile.crdate = thefile.mddate = thefile.bkdate = date

                if mpw_dates: thefile.real_t = 0

                try:
                    with open(nativepath + '.idump', 'rb') as f:
                        if mpw_dates: thefile.real_t = max(thefile.real_t, path.getmtime(f.name))
                        thefile.type = f.read(4)
                        thefile.creator = f.read(4)
                except FileNotFoundError:
                    pass

                try:
                    with open(nativepath + '.rdump', 'rb') as f:
                        if mpw_dates: thefile.real_t = max(thefile.real_t, path.getmtime(f.name))
                        thefile.rsrc = make_file(parse_rez_code(f.read()), align=4)
                except FileNotFoundError:
                    pass

                with open(nativepath, 'rb') as f:
                    if mpw_dates: thefile.real_t = max(thefile.real_t, path.getmtime(f.name))
                    thefile.data = f.read()

                if thefile.type in TEXT_TYPES:
                    thefile.data = thefile.data.replace(b'\r\n', b'\r').replace(b'\n', b'\r')
                    try:
                        thefile.data = thefile.data.decode('utf8').encode('mac_roman')
                    except UnicodeEncodeError:
                        pass # not happy, but whatever...

            elif hfslink == 1: # folder
                thedir = Folder(); self[hfspath] = thedir
                thedir.crdate = thedir.mddate = thedir.bkdate = date

            else: # symlink, i.e. alias
                deferred_aliases.append((hfspath, hfslink)) # alias, targetpath

        for aliaspath, targetpath in deferred_aliases:
            try:
                alias = File()
                alias.flags |= 0x8000
                alias.aliastarget = self[targetpath]
                self[aliaspath] = alias
            except (KeyError, ValueError):
                raise

        if mpw_dates:
            all_real_times = set()
            for pathtpl, obj in self.iter_paths():
                try:
                    all_real_times.add(obj.real_t)
                except AttributeError:
                    pass
            ts2idx = {ts: idx for (idx, ts) in enumerate(sorted(set(all_real_times)))}

            for pathtpl, obj in self.iter_paths():
                try:
                    real_t = obj.real_t
                except AttributeError:
                    pass
                else:
                    fake_t = obj.crdate + 60 * ts2idx[real_t]
                    obj.crdate = obj.mddate = obj.bkdate = fake_t

    def write_folder(self, folder_path):
        def any_exists(at_path):
            if path.exists(at_path): return True
            if path.exists(at_path + '.rdump'): return True
            if path.exists(at_path + '.idump'): return True
            return False

        written = []
        blacklist = list()
        alias_fixups = list()
        valid_alias_targets = dict()
        for p, obj in self.iter_paths():
            blacklist_test = ':'.join(p) + ':'
            if blacklist_test.startswith(tuple(blacklist)): continue
            if _unsyncability(p[-1]):
                warn('Ignoring unsyncable name: %r' % (':' + ':'.join(p)))
                blacklist.append(blacklist_test)
                continue

            nativepath = path.join(folder_path, *(comp.replace(path.sep, ':') for comp in p))
            info_path = nativepath + '.idump'
            rsrc_path = nativepath + '.rdump'

            valid_alias_targets[id(obj)] = nativepath

            if isinstance(obj, Folder):
                os.makedirs(nativepath, exist_ok=True)

            elif obj.mddate != obj.bkdate or not any_exists(nativepath):
                if obj.aliastarget is not None:
                    alias_fixups.append((nativepath, id(obj.aliastarget)))

                # always write the data fork
                data = obj.data
                if obj.type in TEXT_TYPES:
                    data = data.decode('mac_roman').replace('\r', os.linesep).encode('utf8')
                with open(nativepath, 'wb') as f:
                    f.write(data)

                # write a resource dump iff that fork has any bytes (dump may still be empty)
                if obj.rsrc:
                    with open(rsrc_path, 'wb') as f:
                        rdump = make_rez_code(parse_file(obj.rsrc), ascii_clean=True)
                        f.write(rdump)
                else:
                     _try_delete(rsrc_path)   

                # write an info dump iff either field is non-null
                idump = obj.type + obj.creator
                if any(idump):
                    with open(info_path, 'wb') as f:
                        f.write(idump)
                else:
                    _try_delete(info_path)

        if written:
            t = path.getmtime(written[-1])
            for w in written:
                os.utime(w, (t, t))

        for alias_path, target_id in alias_fixups:
            try:
                target_path = valid_alias_targets[target_id]
            except KeyError:
                pass
            else:
                _try_delete(alias_path)
                _try_delete(alias_path + '.idump')
                _try_delete(alias_path + '.rdump')

                _symlink_rel(target_path, alias_path)
                for ext in ('.idump', '.rdump'):
                    if path.exists(target_path + ext):
                        _symlink_rel(target_path + ext, alias_path + ext)


class Folder(AbstractFolder):
    def __init__(self):
        super().__init__()

        self.flags = 0 # help me!
        self.x = 0 # where to put this spatially?
        self.y = 0

        self.crdate = self.mddate = self.bkdate = 0


class File:
    def __init__(self):
        self.type = b'????'
        self.creator = b'????'
        self.flags = 0 # help me!
        self.x = 0 # where to put this spatially?
        self.y = 0

        self.locked = False
        self.crdate = self.mddate = self.bkdate = 0

        self.aliastarget = None

        self.rsrc = bytearray()
        self.data = bytearray()

    def __str__(self):
        if isinstance(self.aliastarget, File):
            return '[alias] ' + str(self.aliastarget)
        elif self.aliastarget is not None:
            return '[alias to folder]'

        typestr, creatorstr = (x.decode('mac_roman') for x in (self.type, self.creator))
        dstr, rstr = (repr(bytes(x)) if 1 <= len(x) <= 32 else '%db' % len(x) for x in (self.data, self.rsrc))
        return '[%s/%s] data=%s rsrc=%s' % (typestr, creatorstr, dstr, rstr)
