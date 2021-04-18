#!/usr/bin/env python3

### -a Inform.app -w Standard game.ulx
### -a ~/Library/Inform game.ulx
### -a Inform.app -w Standard -i Vorple game.ulx
### -w ~/lib/OneCol.zip -i ~/lib/Quixe.zip game.ulx
### -a Inform.app -i ~/lib/Quixe game.ulx

import sys
import os
import os.path
import optparse
import io
import re
import zipfile
import struct
import base64
import json
from chunk import Chunk

MANIFEST_FILE = '(manifest).txt'
ZCODE = 'Z-code'
GLULX = 'Glulx'

popt = optparse.OptionParser(usage='ifsitegen.py [ options ] GAME')

popt.add_option('-a', '--app', '--application',
                action='store', dest='app', metavar='DIR',
                help='Inform application')

popt.add_option('-l', '--lib', '--library',
                action='store', dest='lib', metavar='DIR',
                help='Inform document library')

popt.add_option('-w', '--website',
                action='store', dest='website', metavar='TEMPLATE',
                help='website template package or directory')

popt.add_option('-i', '--terp', '--interpreter',
                action='store', dest='terp', metavar='TEMPLATE',
                help='interpreter template package or directory')

popt.add_option('-r', '--release',
                action='store', dest='release', metavar='DIR',
                default='Release',
                help='destination directory')

(opts, args) = popt.parse_args()

def locate_dirs():
    # Identify the Templates directories
    
    appdir = opts.app
    libdir = opts.lib

    if not libdir:
        if sys.platform == 'darwin':
            path = os.path.join(os.environ['HOME'], 'Library/Inform')
            if os.path.isdir(path):
                libdir = path
        elif sys.platform == 'win32':
            path = os.path.join(os.environ['USERPROFILE'], 'My Documents', 'Inform')
            if os.path.isdir(path):
                libdir = path
        else:
            path = os.path.join(os.environ['HOME'], 'Inform')
            if os.path.isdir(path):
                libdir = path

    if libdir:
        # Can specify "~/Library/Inform" or "~/Library/Inform/Templates"
        path = os.path.join(libdir, 'Templates')
        if os.path.isdir(path):
            libdir = path

    if not appdir:
        if sys.platform == 'darwin':
            path = '/Applications/Inform.app'
            if os.path.isdir(path):
                appdir = path
        elif sys.platform == 'win32':
            pass ###?
        else:
            path = '/usr/local/share/inform7/Internal'
            if os.path.isdir(path):
                appdir = path
            
    if appdir:
        if sys.platform == 'darwin':
            path = os.path.join(appdir, 'Inform.app')
            if os.path.isdir(path):
                appdir = path
            path = os.path.join(appdir, 'Contents/Resources/Internal')
            if os.path.isdir(path):
                appdir = path
        elif sys.platform == 'win32':
            pass ###?
        else:
            pass ###?
    
    if appdir:
        path = os.path.join(appdir, 'Templates')
        if os.path.isdir(path):
            appdir = path

    return appdir, libdir

def find_terp_template(path, appdir=None, libdir=None, gametype=None):
    defaultterp = None
    if gametype == ZCODE:
        defaultterp = 'Parchment'
    elif gametype == GLULX:
        defaultterp = 'Quixe'

    if path and not os.path.split(path)[0]:
        # The path has no slashes; try reading it as a dir in appdir/libdir
        if libdir:
            tpath = os.path.join(libdir, path)
            manpath = os.path.join(tpath, MANIFEST_FILE)
            if os.path.isfile(manpath):
                return Template(dir=tpath, manpath=manpath)
        if appdir:
            tpath = os.path.join(appdir, path)
            manpath = os.path.join(tpath, MANIFEST_FILE)
            if os.path.isfile(manpath):
                return Template(dir=tpath, manpath=manpath)

    if path is None and defaultterp:
        # Look for "Parchment/Quixe" in appdir/libdir
        if libdir:
            tpath = os.path.join(libdir, defaultterp)
            manpath = os.path.join(tpath, MANIFEST_FILE)
            if os.path.isfile(manpath):
                return Template(dir=tpath, manpath=manpath)
        if appdir:
            tpath = os.path.join(appdir, defaultterp)
            manpath = os.path.join(tpath, MANIFEST_FILE)
            if os.path.isfile(manpath):
                return Template(dir=tpath, manpath=manpath)
        
    if path and os.path.isfile(path):
        if not path.endswith('.zip'):
            print('Warning: template does not appear to be a zip package: %s' % (path,))
        zip = zipfile.ZipFile(path)
        ls = zip.namelist()
        for val in ls:
            head, sep, tail = val.rpartition('/')
            if tail == MANIFEST_FILE:
                return Template(zip=zip, prefix=head, manpath=val)
        else:
            raise Exception('Unable to find manifest in zip template: %s' % (path,))
    elif path and os.path.isdir(path):
        manpath = os.path.join(path, MANIFEST_FILE)
        if os.path.isfile(manpath):
            return Template(dir=path, manpath=manpath)
        elif defaultterp:
            tpath = os.path.join(path, defaultterp)
            manpath = os.path.join(tpath, MANIFEST_FILE)
            if os.path.isfile(manpath):
                return Template(dir=tpath, manpath=manpath)
        raise Exception('Unable to locate template: %s' % (path,))

    if path is None:
        raise Exception('Unable to locate template')
    raise Exception('Unable to read template: %s' % (path,))

def find_web_template(path, appdir=None, libdir=None):
    if path and not os.path.split(path)[0]:
        # The path has no slashes; try reading it as a dir in appdir/libdir
        if libdir:
            tpath = os.path.join(libdir, path)
            if os.path.isdir(tpath):
                return Template(dir=tpath)
        if appdir:
            tpath = os.path.join(appdir, path)
            if os.path.isdir(tpath):
                return Template(dir=tpath)

    if path is None:
        # Look for "Standard" in appdir/libdir
        if libdir:
            tpath = os.path.join(libdir, 'Standard')
            if os.path.isdir(tpath):
                return Template(dir=tpath)
        if appdir:
            tpath = os.path.join(appdir, 'Standard')
            if os.path.isdir(tpath):
                return Template(dir=tpath)
        
    if path and os.path.isfile(path):
        if not path.endswith('.zip'):
            print('Warning: template does not appear to be a zip package: %s' % (path,))
        zip = zipfile.ZipFile(path)
        prefix = None
        ls = zip.namelist()
        if ls and ls[0] and ls[0].endswith('/'):
            prefix = ls[0][:-1]
        return Template(zip=zip, prefix=prefix)
    elif path and os.path.isdir(path):
        return Template(dir=path)
        raise Exception('Unable to locate template: %s' % (path,))

    if path is None:
        raise Exception('Unable to locate template')
    raise Exception('Unable to read template: %s' % (path,))


class Template:
    def __init__(self, dir=None, zip=None, prefix=None, manpath=None):
        # list of (origpath, destfile)
        self.files = []
        
        if dir is not None:
            self.iszip = False
            self.dir = dir
            for ent in os.scandir(dir):
                if not ent.is_file():
                    continue
                if ent.name == MANIFEST_FILE:
                    continue
                self.files.append( (ent.path, ent.name) )
        elif zip is not None:
            self.iszip = True
            self.zip = zip
            for path in zip.namelist():
                val = path
                if prefix:
                    if not val.startswith(prefix):
                        continue
                    val = val[ len(prefix) : ]
                    if val.startswith('/'):
                        val = val[ 1 : ]
                if not val:
                    continue
                if val == MANIFEST_FILE:
                    continue
                self.files.append( (path, val) )
        else:
            raise Exception('Template must have zip or dir')

        self.manifest = None
        if manpath:
            if not self.iszip:
                manfile = open(manpath, 'r')
            else:
                manfile = zip.open(manpath)
                manfile = io.TextIOWrapper(manfile)
            self.manifest = Manifest(manfile)

    def __repr__(self):
        if not self.iszip:
            return '<Template (dir): %s>' % (self.dir,)
        else:
            return '<Template (zip): %s>' % (self.zip.filename,)

    def shortname(self):
        if not self.iszip:
            val = self.dir
        else:
            val = self.zip.filename
        return os.path.split(val)[1]

    def getfile(self, path, text=False):
        if not self.iszip:
            if not text:
                fl = open(path, 'rb')
                dat = fl.read()
                fl.close()
            else:
                fl = open(path, 'r')
                dat = fl.read()
                fl.close()
            return dat
        else:
            fl = self.zip.open(path)
            dat = fl.read()
            fl.close()
            if text:
                dat = dat.encode()
            return dat

class Manifest:
    def __init__(self, file=None):
        self.body = []
        self.metadata = {}

        if file:
            self.load(file)

    def get_meta(self, key):
        return self.metadata.get(key, [])

    def get_meta_line(self, key, defval=None):
        ls = self.metadata.get(key)
        if not ls:
            return defval
        return ls[0]

    def load(self, file):
        section = None
        
        for ln in file.readlines():
            ln = ln.rstrip()
            
            if ln.startswith('[') and ln.endswith(']'):
                key = ln[1:-1]
                if not key:
                    section = None
                    continue
                section = []
                self.metadata[key] = section
                continue

            if section is None:
                if not ln or ln.startswith('!'):
                    continue
                self.body.append(ln)
            else:
                section.append(ln)

def identify_gamefile(filename):
    fl = open(filename, 'rb')
    dat = fl.read(4)
    fl.seek(0)
    
    if dat == b'Glul':
        return (fl, GLULX)
    if dat[0] in (3, 4, 5, 6, 7, 8):
        return (fl, ZCODE)

    if dat == b'FORM':
        fl.close()
        fl = BlorbFile(filename)
        chunk = fl.usagemap.get( (b'Exec', 0) )
        if not chunk:
            raise Exception('No executable chunk: %s' % (filename,))
        if chunk.type == b'GLUL':
            return (fl, GLULX)
        if chunk.type == b'ZCOD':
            return (fl, ZCODE)
        raise Exception('Unrecognized executable chunk (%s): %s' % (typestring(chunk.type), filename,))

    raise Exception('File not recognized: %s' % (filename,))

def do_release(filename, gamefile, gametype, terp_template, web_template, release):
    print('###', filename, gametype, release)
    print('###', terp_template, web_template)
    manifest = terp_template.manifest
    basefilename = os.path.split(filename)[1]

    map = {}
    for key, ls in manifest.metadata.items():
        map[key] = '\n'.join(ls)
    map['ENCODEDSTORYFILE'] = htmlencode(basefilename+'.js')
    
    map['OTHERCREDITS'] = ''
    
    if not os.path.exists(release):
        os.mkdir(release)

    pat_tag = re.compile('\\[([A-Z_]+)\\]')
    def subst(match):
        key = match.group(1)
        val = map.get(key)
        if val is not None:
            return val
        return '[?'+key+'?]'
        
    for (path, name) in web_template.files:
        if name.endswith('.html'):
            dat = web_template.getfile(path, text=True)
            while pat_tag.search(dat):
                dat = pat_tag.sub(subst, dat)
            fl = open(os.path.join(release, name), 'w')
            fl.write(dat)
            fl.close()
        else:
            dat = web_template.getfile(path)
            fl = open(os.path.join(release, name), 'wb')
            fl.write(dat)
            fl.close()

    tpath = os.path.join(release, 'interpreter')
    if not os.path.exists(tpath):
        os.mkdir(tpath)

    for (path, name) in terp_template.files:
        # We're ignoring the list in the manifest, but it should be the same.
        dat = terp_template.getfile(path)
        fl = open(os.path.join(tpath, name), 'wb')
        fl.write(dat)
        fl.close()

    dat = gamefile.read()
    fl = open(os.path.join(release, basefilename), 'wb')
    fl.write(dat)
    fl.close()

    dat = base64.encodebytes(dat)
    fl = open(os.path.join(tpath, basefilename+'.js'), 'w')
    lines = manifest.get_meta('BASESIXTYFOURTOP')
    fl.write('\n'.join(lines)+'\n')
    fl.write(dat.decode())
    lines = manifest.get_meta('BASESIXTYFOURTAIL')
    fl.write('\n'.join(lines)+'\n')
    fl.close()

class BlorbChunk:
    def __init__(self, blorbfile, typ, start, len, formtype=None):
        self.blorbfile = blorbfile
        self.type = typ
        self.start = start
        self.len = len
        self.formtype = formtype
        self.literaldata = None
        self.filedata = None
        self.filestart = None
        
    def __repr__(self):
        return '<BlorbChunk %s at %d, len %d>' % (typestring(self.type), self.start, self.len)
    
    def data(self, max=None):
        if (self.literaldata):
            if (max is not None):
                return self.literaldata[0:max]
            else:
                return self.literaldata
        if (self.filedata):
            fl = open(self.filedata, 'rb')
            if (self.filestart is not None):
                fl.seek(self.filestart)
            if (max is not None):
                dat = fl.read(max)
            else:
                dat = fl.read()
            fl.close()
            return dat
        self.blorbfile.formchunk.seek(self.start)
        toread = self.len
        if (max is not None):
            toread = min(self.len, max)
        return self.blorbfile.formchunk.read(toread)

class BlorbFile:
    def __init__(self, filename):
        self.chunks = []
        self.chunkmap = {}
        self.chunkatpos = {}
        self.usages = []
        self.usagemap = {}
        
        self.filename = filename

        self.file = open(filename, 'rb')
        formchunk = Chunk(self.file)
        self.formchunk = formchunk
        
        if (formchunk.getname() != b'FORM'):
            raise Exception('This does not appear to be a Blorb file.')
        formtype = formchunk.read(4)
        if (formtype != b'IFRS'):
            raise Exception('This does not appear to be a Blorb file.')
        formlen = formchunk.getsize()
        while formchunk.tell() < formlen:
            chunk = Chunk(formchunk)
            start = formchunk.tell()
            size = chunk.getsize()
            formtype = None
            if chunk.getname() == b'FORM':
                formtype = chunk.read(4)
            subchunk = BlorbChunk(self, chunk.getname(), start, size, formtype)
            self.chunks.append(subchunk)
            chunk.skip()
            chunk.close()

        for chunk in self.chunks:
            self.chunkatpos[chunk.start] = chunk
            dict_append(self.chunkmap, chunk.type, chunk)

        # Sanity checks. Also get the usage list.
        
        ls = self.chunkmap.get(b'RIdx')
        if (not ls):
            raise Exception('No resource index chunk!')
        elif (len(ls) != 1):
            print('Warning: too many resource index chunks!')
        else:
            chunk = ls[0]
            if (self.chunks[0] is not chunk):
                print('Warning: resource index chunk is not first!')
            dat = chunk.data()
            numres = struct.unpack('>I', dat[0:4])[0]
            if (numres*12+4 != chunk.len):
                print('Warning: resource index chunk has wrong size!')
            for ix in range(numres):
                subdat = dat[4+ix*12 : 16+ix*12]
                typ = struct.unpack('>4c', subdat[0:4])
                typ = b''.join(typ)
                num = struct.unpack('>I', subdat[4:8])[0]
                start = struct.unpack('>I', subdat[8:12])[0]
                subchunk = self.chunkatpos.get(start)
                if (not subchunk):
                    print('Warning: resource (%s, %d) refers to a nonexistent chunk!' % (typestring(typ), num))
                self.usages.append( (typ, num, subchunk) )
                self.usagemap[(typ, num)] = subchunk

    def close(self):
        if (self.formchunk):
            self.formchunk.close()
            self.formchunk = None
        if (self.file):
            self.file.close()
            self.file = None

    def chunk_position(self, chunk):
        try:
            return self.chunks.index(chunk)
        except:
            return None

def dict_append(map, key, val):
    ls = map.get(key)
    if (not ls):
        ls = []
        map[key] = ls
    ls.append(val)

def typestring(dat):
    return "'" + dat.decode() + "'"

def htmlencode(val):
    val = val.replace('&', '&amp;')
    val = val.replace('<', '&lt;')
    val = val.replace('>', '&gt;')
    val = val.replace('"', '&quot;')
    return val

# Do the work

if len(args) != 1:
    popt.print_help()
    sys.exit(-1)

filename = args[0]
try:
    (gamefile, gametype) = identify_gamefile(filename)
except Exception as ex:
    print(ex)
    sys.exit(1)

isblorb = isinstance(gamefile, BlorbFile)
print('%s file (%s): %s' % (gametype, ('Blorb' if isblorb else 'plain'), filename,))

(appdir, libdir) = locate_dirs()

try:
    terp_template = find_terp_template(opts.terp, appdir=appdir, libdir=libdir, gametype=gametype)
except Exception as ex:
    print(ex)
    sys.exit(-1)

try:
    web_template = find_web_template(opts.website, appdir=appdir, libdir=libdir)
except Exception as ex:
    print(ex)
    sys.exit(-1)

val = terp_template.manifest.get_meta_line('INTERPRETERVERSION')
print('Interpreter: %s' % (val,))
print('Website: %s' % (web_template.shortname(),))

val = terp_template.manifest.get_meta_line('INTERPRETERVM', '')
if gametype == GLULX and 'g' not in val:
    print('Warning: Template does not appear to support Glulx')
if gametype == ZCODE and 'z' not in val:
    print('Warning: Template does not appear to support Z-code')

do_release(filename, gamefile, gametype, terp_template, web_template, release=opts.release)