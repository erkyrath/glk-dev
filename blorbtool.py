#!/usr/bin/env python

# blorbtool.py: A (semi-)multifunctional Blorb utility
# Created by Andrew Plotkin (erkyrath@eblong.com)
# This script is in the public domain.

import sys
import os
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

def confirm_input(prompt):
    ln = raw_input(prompt+' >')
    if (ln.lower().startswith('y')):
        return True

class BlorbChunk:
    def __init__(self, blorbfile, typ, start, len, formtype=None):
        self.blorbfile = blorbfile
        self.type = typ
        self.start = start
        self.len = len
        self.formtype = formtype
        self.literaldata = None
        self.filedata = None
        
    def __repr__(self):
        return '<BlorbChunk %s at %d, len %d>' % (repr(self.type), self.start, self.len)
    
    def data(self, max=None):
        if (self.literaldata):
            if (max is not None):
                return self.literaldata[0:max]
            else:
                return self.literaldata
        if (self.filedata):
            fl = open(self.filedata)
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

    def describe(self):
        if (not self.formtype):
            return '%s (%d bytes, start %d)' % (repr(self.type), self.len, self.start)
        else:
            return '%s/%s (%d bytes, start %d)' % (repr(self.type), repr(self.formtype), self.len, self.start)
    
    def display(self):
        print '* %s' % (self.describe(),)
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
    def __init__(self, filename, outfilename=None):
        self.filename = filename
        self.outfilename = outfilename
        if (not self.outfilename):
            self.outfilename = self.filename
            
        self.changed = False

        self.file = open(filename)
        formchunk = Chunk(self.file)
        self.formchunk = formchunk
        self.chunks = []
        
        if (formchunk.getname() != 'FORM'):
            raise Exception('This does not appear to be a Blorb file.')
        formtype = formchunk.read(4)
        if (formtype != 'IFRS'):
            raise Exception('This does not appear to be a Blorb file.')
        formlen = formchunk.getsize()
        while formchunk.tell() < formlen:
            chunk = Chunk(formchunk)
            start = formchunk.tell()
            size = chunk.getsize()
            formtype = None
            if chunk.getname() == 'FORM':
                formtype = chunk.read(4)
            subchunk = BlorbChunk(self, chunk.getname(), start, size, formtype)
            self.chunks.append(subchunk)
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
                    print 'Warning: resource (%s, %d) refers to a nonexistent chunk!' % (repr(typ), num)
                self.usages.append( (typ, num, subchunk) )
                self.usagemap[(typ, num)] = subchunk

    def close(self):
        if (self.formchunk):
            self.formchunk.close()
            self.formchunk = None
        if (self.file):
            self.file.close()
            self.file = None

    def sanity_check(self):
        if (len(self.usages) != len(self.usagemap)):
            print 'Warning: internal mismatch (usages)!'
        if (len(self.chunks) != len(self.chunkatpos)):
            print 'Warning: internal mismatch (chunks)!'

    def save_if_needed(self):
        if self.changed:
            try:
                self.save()
            except CommandError, ex:
                print str(ex)

    def canonicalize(self):
        self.sanity_check()
        try:
            indexchunk = self.chunkmap['RIdx'][0]
        except:
            raise CommandError('There is no index chunk, so this cannot be a legal blorb file.')
        indexchunk.len = 4 + 12*len(self.usages)
        pos = 12
        for chunk in self.chunks:
            chunk.start = pos
            pos = pos + 8 + chunk.len
            if (pos % 2):
                pos = pos+1
        self.usages.sort(key=lambda tup:tup[2].start)
        ls = []
        ls.append(struct.pack('>I', len(self.usages)))
        for (typ, num, chunk) in self.usages:
            ls.append(struct.pack('>4cII', typ[0], typ[1], typ[2], typ[3], num, chunk.start))
        dat = ''.join(ls)
        if (len(dat) != indexchunk.len):
            print 'Warning: index chunk length does not match!'
        indexchunk.literaldata = dat

    def save(self, outfilename=None):
        if (outfilename):
            self.outfilename = outfilename
        if (not self.changed and (self.outfilename == self.filename)):
            raise CommandError('No changes need saving.')
        if (os.path.exists(self.outfilename) and not opts.force):
            if (not confirm_input('File %s exists. Rewrite?' % (self.outfilename,))):
                print 'Cancelled.'
                return
        self.canonicalize()
        tmpfilename = self.outfilename + '~TEMP'
        fl = open(tmpfilename, 'w')
        fl.write('FORM----IFRS')
        pos = 12
        for chunk in self.chunks:
            typ = chunk.type
            fl.write(struct.pack('>4cI', typ[0], typ[1], typ[2], typ[3], chunk.len))
            pos = pos+8
            dat = chunk.data()
            fl.write(dat)
            pos = pos+len(dat)
            if (pos % 2):
                fl.write('\0')
                pos = pos+1
        fl.seek(4)
        fl.write(struct.pack('>I', pos-8))
        fl.close()
        os.rename(tmpfilename, self.outfilename)
        print 'Wrote file:', self.outfilename
        return self.outfilename

    def delete_chunk(self, delchunk):
        self.chunks = [ chunk for chunk in self.chunks if (chunk is not delchunk) ]
        ls = self.chunkmap[delchunk.type]
        ls = [ chunk for chunk in ls if (chunk is not delchunk) ]
        if (ls):
            self.chunkmap[delchunk.type] = ls
        else:
            self.chunkmap.pop(delchunk.type)
        self.chunkatpos.pop(delchunk.start)
        self.usages = [ tup for tup in self.usages if (tup[2] is not delchunk) ]
        ls = [ key for (key,val) in self.usagemap.items() if (val is delchunk) ]
        for key in ls:
            self.usagemap.pop(key)
        self.changed = True
                               
class CommandError(Exception):
    pass

class BlorbTool:
    def show_commands():
        print 'blorbtool commands:'
        print
        print 'list -- list all chunks'
        print 'index -- list all resources in the index chunk'
        print 'display -- display contents of all chunks'
        print 'display TYPE -- contents of chunk(s) of that type'
        print 'display USE NUM -- contents of chunk by use and number (e.g., "display Exec 0")'
        print 'export TYPE FILENAME -- export the chunk of that type to a file'
        print 'export USE NUM FILENAME -- export a chunk by use and number'
        print 'delete TYPE -- delete chunk(s) of that type'
        print 'delete USE NUM -- delete chunk by use and number'
        print 'save -- write out changes'
        print 'reload -- discard changes and reload existing blorb file'
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

    aliasmap = { '?':'help', 'q':'quit', 'write':'save', 'restart':'reload', 'restore':'reload' }

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
            print '  %s' % (chunk.describe(),)

    def cmd_index(self, args):
        if (args):
            raise CommandError('usage: index')
        print len(blorbfile.usages), 'resources:'
        for (use, num, chunk) in blorbfile.usages:
            print '  %s %d: %s' % (repr(use), num, chunk.describe())

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

    def cmd_export(self, args):
        if (len(args) == 2):
            typ = self.parse_chunk_type(args[0], 'export')
            ls = [ chunk for chunk in blorbfile.chunks if chunk.type == typ ]
            if (not ls):
                raise CommandError('No chunks of type %s' % (repr(typ),))
            if (len(ls) != 1):
                raise CommandError('%d chunks of type %s' % (len(ls), repr(typ),))
            chunk = ls[0]
        elif (len(args) == 3):
            use = self.parse_chunk_type(args[0], 'export')
            num = self.parse_int(args[1], 'export (second argument)')
            chunk = blorbfile.usagemap.get( (use, num) )
            if (not chunk):
                raise CommandError('No resource with usage %s, number %d' % (repr(use), num))
        else:
            raise CommandError('usage: export TYPE FILENAME | export USE NUM FILENAME')
        outfilename = args[-1]
        if (outfilename == blorbfile.filename):
            raise CommandError('You can\'t export a chunk over the original blorb file!')
        if (os.path.exists(outfilename) and not opts.force):
            if (not confirm_input('File %s exists. Overwrite?' % (outfilename,))):
                print 'Cancelled.'
                return
        outfl = open(outfilename, 'w')
        if (chunk.formtype and chunk.formtype != 'FORM'):
            # For an AIFF file, we must include the FORM/length header.
            # (Unless it's an overly nested AIFF.)
            outfl.write('FORM')
            outfl.write(struct.pack('>I', chunk.len))
        outfl.write(chunk.data())
        finallen = outfl.tell()
        outfl.close()
        print 'Wrote %d bytes to %s.' % (finallen, outfilename)

    def cmd_delete(self, args):
        if (len(args) == 1):
            typ = self.parse_chunk_type(args[0], 'delete')
            ls = [ chunk for chunk in blorbfile.chunks if chunk.type == typ ]
            if (not ls):
                raise CommandError('No chunks of type %s' % (repr(typ),))
        elif (len(args) == 2):
            use = self.parse_chunk_type(args[0], 'delete')
            num = self.parse_int(args[1], 'delete (second argument)')
            chunk = blorbfile.usagemap.get( (use, num) )
            if (not chunk):
                raise CommandError('No resource with usage %s, number %d' % (repr(use), num))
            ls = [ chunk ]
        else:
            raise CommandError('usage: delete TYPE | delete USE NUM')
        for chunk in ls:
            blorbfile.delete_chunk(chunk)
        print 'Deleted %d chunk%s' % (len(ls), ('' if len(ls)==1 else 's'))

    def cmd_reload(self, args):
        global blorbfile
        if (args):
            raise CommandError('usage: reload')
        filename = blorbfile.filename
        blorbfile.close()
        blorbfile = BlorbFile(filename)
        print 'Reloaded %s.' % (filename,)
        
    def cmd_save(self, args):
        global blorbfile
        if (len(args) == 0):
            outfilename = None
        elif (len(args) == 1):
            outfilename = args[0]
        else:
            raise CommandError('usage: save | save FILENAME')
        filename = blorbfile.save(outfilename)
        if (filename):
            # Reload, so that the blorbfile's Chunk (and its chunks)
            # refer to the new file. (The reloaded blorbfile will have
            # changed == False, too.)
            blorbfile.close()
            blorbfile = BlorbFile(filename)

    def cmd_dump(self, args):
        print '### chunks:', blorbfile.chunks
        print '### chunkmap:', blorbfile.chunkmap
        print '### chunkatpos:', blorbfile.chunkatpos
        print '### usages:', blorbfile.usages
        print '### usagemap:', blorbfile.usagemap

# Actual work begins here.

if (opts.listcommands):
    BlorbTool.show_commands()
    sys.exit(-1)
    
if (not args):
    popt.print_help()
    sys.exit(-1)

filename = args.pop(0)
try:
    blorbfile = BlorbFile(filename, opts.output)
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
        blorbfile.sanity_check()
        blorbfile.save_if_needed()
    else:
        tool.set_interactive(True)
        while (not tool.quit_yet()):
            tool.handle()
            blorbfile.sanity_check()
        blorbfile.save_if_needed()
        print '<exiting>'
except KeyboardInterrupt:
    print '<interrupted>'
except EOFError:
    print '<eof>'

blorbfile.close()
