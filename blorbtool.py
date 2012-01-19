#!/usr/bin/env python

# blorbtool.py: A (semi-)multifunctional Blorb utility
# Created by Andrew Plotkin (erkyrath@eblong.com)
# This script is in the public domain.

import sys
import optparse
import struct
from chunk import Chunk
try:
    import readline
except:
    pass

popt = optparse.OptionParser(usage='blorbtool.py BLORBFILE [ command ]')

popt.add_option('-o', '--output',
                action='store', dest='output', metavar='BLORBFILE',
                help='blorb file to write to (if requested)')
popt.add_option('-f', '--force',
                action='store_true', dest='force',
                help='overwrite files without confirming')
popt.add_option('-l', '--commands',
                action='store_true', dest='listcommands',
                help='list all commands (and exit)')

(opts, args) = popt.parse_args()

def dict_append(map, key, val):
    ls = map.get(key)
    if (not ls):
        ls = []
        map[key] = ls
    ls.append(val)

class BlorbChunk:
    def __init__(self, blorbfile, typ, start, len):
        self.blorbfile = blorbfile
        self.type = typ
        self.start = start
        self.len = len
    def __repr__(self):
        return '<BlorbChunk %s at %d, len %d>' % (repr(self.type), self.start, self.len)
    def data(self, max=None):
        self.blorbfile.formchunk.seek(self.start)
        toread = self.len
        if (max is not None):
            toread = min(self.len, max)
        return self.blorbfile.formchunk.read(toread)
    def display(self):
        print '* %s (%d bytes, start %d)' % (repr(self.type), self.len, self.start)
        if (self.type == 'RIdx'):
            # Index chunk
            dat = self.data()
            (subdat, dat) = (dat[:4], dat[4:])
            num = struct.unpack('>I', subdat)[0]
            print '%d resources:' % (num,)
            while (dat):
                (subdat, dat) = (dat[:12], dat[12:])
                subls = struct.unpack('>4c2I', subdat)
                print '  \'%c%c%c%c\' %d: starts at %d' % subls
        elif (self.type == 'IFmd'):
            # Metadata chunk
            dat = self.data()
            print dat
        elif (self.type == 'Fspc'):
            # Frontispiece chunk
            dat = self.data()
            if (len(dat) != 4):
                print 'Warning: invalid contents!'
            else:
                num = struct.unpack('>I', dat[0:4])[0]
                print 'Frontispiece is pict number', num
        elif (self.type == 'APal'):
            # Adaptive palette
            dat = self.data()
            if (len(dat) % 4 != 0):
                print 'Warning: invalid contents!'
            else:
                ls = []
                while (dat):
                    (subdat, dat) = (dat[:4], dat[4:])
                    num = struct.unpack('>I', subdat)[0]
                    ls.append(str(num))
                print 'Picts using adaptive palette:', ' '.join(ls)
        elif (self.type == 'Loop'):
            # Looping
            dat = self.data()
            if (len(dat) % 8 != 0):
                print 'Warning: invalid contents!'
            else:
                while (dat):
                    (subdat, dat) = (dat[:8], dat[8:])
                    (num, count) = struct.unpack('>II', subdat)
                    print 'Sound %d repeats %d times' % (num, count)
        elif (self.type == 'RelN'):
            # Release number
            dat = self.data()
            if (len(dat) != 2):
                print 'Warning: invalid contents!'
            else:
                num = struct.unpack('>H', dat)[0]
                print 'Release number', num
        elif (self.type == 'SNam'):
            # Story name (obsolete)
            dat = self.data()
            if (len(dat) % 2 != 0):
                print 'Warning: invalid contents!'
            else:
                ls = []
                while (dat):
                    (subdat, dat) = (dat[:2], dat[2:])
                    num = struct.unpack('>H', subdat)[0]
                    ls.append(chr(num))
                print 'Story name:', ''.join(ls)
        elif (self.type in ('ANNO', 'AUTH', '(c) ')):
            dat = self.data()
            print dat
        elif (self.type == 'Reso'):
            # Resolution chunk
            dat = self.data()
            if (len(dat)-24) % 28 != 0:
                print 'Warning: invalid contents!'
            else:
                (subdat, dat) = (dat[:24], dat[24:])
                subls = struct.unpack('>6I', subdat)
                print 'Standard window size %dx%d, min %dx%d, max %dx%d' % subls
                while (dat):
                    (subdat, dat) = (dat[:28], dat[28:])
                    subls = struct.unpack('>7I', subdat)
                    print 'Pict %d: standard ratio: %d/%d, min %d/%d, max %d/%d' % subls
        else:
            dat = self.data(16)
            if (len(dat) == self.len):
                print 'contents: %s' % (repr(dat,))
            else:
                print 'beginning: %s' % (repr(dat,))

class BlorbFile:
    def __init__(self, filename):
        self.chunks = []
        self.filename = filename

        self.file = open(filename)
        formchunk = Chunk(self.file)
        self.formchunk = formchunk
        
        if (formchunk.getname() != 'FORM'):
            raise Exception('This does not appear to be a Blorb file.')
        formtype = formchunk.read(4)
        if (formtype != 'IFRS'):
            raise Exception('This does not appear to be a Blorb file.')
        formlen = formchunk.getsize()
        while formchunk.tell() < formlen:
            chunk = Chunk(formchunk)
            self.chunks.append(BlorbChunk(self, chunk.getname(), formchunk.tell(), chunk.getsize()))
            chunk.skip()
            chunk.close()

        self.chunkmap = {}
        self.chunkatpos = {}
        for chunk in self.chunks:
            self.chunkatpos[chunk.start] = chunk
            dict_append(self.chunkmap, chunk.type, chunk)

        # Sanity checks. Also get the usage list.
        self.usages = []
        self.usagemap = {}
        
        ls = self.chunkmap.get('RIdx')
        if (not ls):
            raise Exception('No resource index chunk!')
        elif (len(ls) != 1):
            print 'Warning: too many resource index chunks!'
        else:
            chunk = ls[0]
            if (self.chunks[0] is not chunk):
                print 'Warning: resource index chunk is not first!'
            dat = chunk.data()
            numres = struct.unpack('>I', dat[0:4])[0]
            if (numres*12+4 != chunk.len):
                print 'Warning: resource index chunk has wrong size!'
            for ix in range(numres):
                subdat = dat[4+ix*12 : 16+ix*12]
                typ = struct.unpack('>4c', subdat[0:4])
                typ = ''.join(typ)
                num = struct.unpack('>I', subdat[4:8])[0]
                start = struct.unpack('>I', subdat[8:12])[0]
                subchunk = self.chunkatpos.get(start)
                if (not subchunk):
                    print 'Warning: resource (%s, %d) refers to a nonexistent chunk!' % (typ, num)
                self.usages.append( (typ, num, subchunk) )
                self.usagemap[(typ, num)] = subchunk

    def close(self):
        if (self.formchunk):
            self.formchunk.close()
            self.formchunk = None
        if (self.file):
            self.file.close()
            self.file = None
                               
class CommandError(Exception):
    pass

class BlorbTool:
    def show_commands():
        print 'list'
        print 'index'
        #  display (verbose output)
        #  display TYPE (display all chunks with this type)
        #  display USAGE N (display the chunk with the given usage/num)
        #  export TYPE (write out chunk contents -- at most one)
        #  export USAGE N (write out chunk contents -- at most one)
        #  import FILE2 TYPE (add new chunk with given type; check format if known)
        #  import FILE2 TYPE USAGE N

    show_commands = staticmethod(show_commands)
        
    def __init__(self):
        self.is_interactive = False
        self.has_quit = False
        
    def set_interactive(self, val):
        self.is_interactive = val

    def quit_yet(self):
        return self.has_quit

    def handle(self, args=None):
        try:
            if (self.is_interactive):
                args = raw_input('>').split()
            if (not args):
                return
            argname = args.pop(0)
            if (argname in self.aliasmap):
                argname = self.aliasmap[argname]
            cmd = getattr(self, 'cmd_'+argname, None)
            if (not cmd):
                raise CommandError('Unknown command: ' + argname)
                return
            cmd(args)
        except KeyboardInterrupt:
            # EOF or interrupt. Pass it on.
            raise
        except EOFError:
            # EOF or interrupt. Pass it on.
            raise
        except CommandError, ex:
            print str(ex)
        except Exception, ex:
            # Unexpected exception: print it.
            print ex.__class__.__name__+':', str(ex)

    def parse_int(self, val, label=''):
        if (label):
            label = label+': '
        try:
            return int(val)
        except:
            raise CommandError(label+'integer required')

    def parse_chunk_type(self, val, label=''):
        if (label):
            label = label+': '
        if len(val) > 4:
            raise CommandError(label+'chunk type must be 1-4 characters')
        return val.ljust(4)

    aliasmap = { '?':'help', 'q':'quit' }

    def cmd_quit(self, args):
        if (args):
            raise CommandError('usage: quit')
        self.has_quit = True

    def cmd_help(self, args):
        if (args):
            raise CommandError('usage: help')
        self.show_commands()

    def cmd_list(self, args):
        if (args):
            raise CommandError('usage: list')
        print len(blorbfile.chunks), 'chunks:'
        for chunk in blorbfile.chunks:
            print '  %s (%d bytes)' % (repr(chunk.type), chunk.len)

    def cmd_index(self, args):
        if (args):
            raise CommandError('usage: index')
        print len(blorbfile.usages), 'resources:'
        for (use, num, chunk) in blorbfile.usages:
            print '  %s %d: %s (%d bytes)' % (repr(use), num, repr(chunk.type), chunk.len)

    def cmd_display(self, args):
        if (not args):
            ls = blorbfile.chunks
        elif (len(args) == 1):
            typ = self.parse_chunk_type(args[0], 'display')
            ls = [ chunk for chunk in blorbfile.chunks if chunk.type == typ ]
            if (not ls):
                raise CommandError('No chunks of type %s' % (repr(typ),))
        elif (len(args) == 2):
            use = self.parse_chunk_type(args[0], 'display')
            num = self.parse_int(args[1], 'display (second argument)')
            chunk = blorbfile.usagemap.get( (use, num) )
            if (not chunk):
                raise CommandError('No resource with usage %s, number %d' % (repr(use), num))
            ls = [ chunk ]
        else:
            raise CommandError('usage: display | display TYPE | display USE NUM')
        for chunk in ls:
            chunk.display()

# Actual work begins here.

if (not args):
    popt.print_help()
    sys.exit(-1)

if (opts.listcommands):
    BlorbTool.show_commands()
    sys.exit(-1)
    
filename = args.pop(0)
try:
    blorbfile = BlorbFile(filename)
except Exception, ex:
    print ex.__class__.__name__+':', str(ex)
    sys.exit(-1)
    
# If args exist, execute them as a command. If not, loop grabbing and
# executing commands until we discover that the user has executed Quit.
# (The handler catches all exceptions except KeyboardInterrupt.)
try:
    tool = BlorbTool()
    if (args):
        tool.set_interactive(False)
        tool.handle(args)
    else:
        tool.set_interactive(True)
        while (not tool.quit_yet()):
            tool.handle()
        print '<exiting>'
except KeyboardInterrupt:
    print '<interrupted>'
except EOFError:
    print '<eof>'

blorbfile.close()
