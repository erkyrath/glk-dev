#!/usr/bin/env python

"""
encode-table.py: generate Glulx string objects and a Glulx string encoding
table, as I6 source code.

Start by creating a source text file. Each line will define a string object:

    hello_string: Hello.

The text of the string (the part after the colon) can be as long as you
want, but it should all be on one line. You can include newlines as \n.
Unicode characters can be given as \xFF (two hex digits) or \uABCD
(four hex digits). The \x marker will be compiled as a character leaf
node; \u as a Unicode character leaf node.

For a C-style string leaf node, use \'substring'. (Backslash markers are
not interpreted within the substring; this is a bug which I may fix
someday.) For a C-style Unicode string, use \"substring". (Again,
backslashes don't work, which means that you can't include any actual
Unicode characters in a Unicode string node. Annoying, but at least we
can exercise the feature.)

For an indirect reference, use \(object). The object must be a string
defined in the source file, or a function defined in your own code. For
a double-indirect reference, use \(N), where N is an integer. The
indirect reference will be to double_indirect-->N. You must fill this
in with a string or function address before printing the double-indirect
reference.

You can include arguments in a reference, separated by spaces:
\(object 1 2 func).

Run the script:

    encode-table.py < source-text

The output can be pasted directly into an I6 source file. You must first
call the patch_encoding_table() function. You can then set the string
table register to encoding_table, and print the string objects that
you defined:

    patch_encoding_table();
    @setstringtbl encoding_table;
    @streamstr hello_string;

Remember that you cannot print *normal* quoted strings once you have
done this; they will not decode correctly. To do that, you would have
restore the original string table register:

    origtbl = 0-->7;
    @setstringtbl origtbl;
    print "Back to normal.^";
"""

import sys
import bisect

string_table = {}
huff_ents = {}
ent_bits = {}
verbose = ('-v' in sys.argv)

def add_entity(res, ent):
    res.append(ent)
    count = huff_ents.get(ent, 0)
    huff_ents[ent] = count+1

def parse_text(ln, label):
    length = len(ln)
    res = []
    pos = 0
    while (pos < length):
        ch = ln[pos]
        pos += 1
        if (ch != '\\'):
            ent = (2, ch)
            add_entity(res, ent)
            continue
        if (pos >= length):
            sys.stderr.write('Line ends with newline: ' + label + '\n')
            break
        ch = ln[pos]
        pos += 1
        if (ch == 'n'):
            ent = (2, '\n')
            add_entity(res, ent)
            continue
        if (ch == 'x'):
            ch = ln[ pos : pos+2 ]
            ch = chr(int(ch, 16))
            pos += 2
            ent = (2, ch)
            add_entity(res, ent)
            continue
        if (ch == 'u'):
            ch = ln[ pos : pos+4 ]
            ch = unichr(int(ch, 16))
            pos += 4
            ent = (4, ch)
            add_entity(res, ent)
            continue
        if (ch == "'"):
            endpos = ln.find("'", pos)
            if (endpos < 0):
                sys.stderr.write('Unterminated substring in line: ' + label + '\n')
                continue
            ent = (3, ln[ pos : endpos ])
            pos = endpos+1
            add_entity(res, ent)
            continue
        if (ch == '"'):
            endpos = ln.find('"', pos)
            if (endpos < 0):
                sys.stderr.write('Unterminated substring in line: ' + label + '\n')
                continue
            ent = (5, ln[ pos : endpos ])
            pos = endpos+1
            add_entity(res, ent)
            continue
        sys.stderr.write('Unknown escape "\\' + ch + '" in line: ' + label + '\n')
        

    ent = (1,)
    add_entity(res, ent)
    return res

def build_tree():
    pool = [ (count, ent) for (ent, count) in huff_ents.items() ]
    pool.sort()
    while (len(pool) > 1):
        (lcount, left) = pool.pop(0)
        (rcount, right) = pool.pop(0)
        ent = (0, left, right)
        tup = (lcount+rcount, ent)
        bisect.insort_left(pool, tup)
    (count, ent) = pool[0]
    return ent

def dump_tree(tree, depth='! '):
    if (tree[0] == 0):
        print depth
        dump_tree(tree[1], depth+'-/')
        dump_tree(tree[2], depth+'-\\')
        return
    print depth, tree

def compute_tree(ls, tree, addr=12, bits=''):
    typ = tree[0]

    if (typ == 0):
        nodelen = 9
    elif (typ == 1):
        nodelen = 1
    elif (typ == 2):
        nodelen = 2
    elif (typ == 3):
        nodelen = 2 + len(tree[1])
    elif (typ == 4):
        nodelen = 5
    elif (typ == 5):
        nodelen = 5 + 4*len(tree[1])
    else:
        raise Exception("Unknown node type " + str(typ))

    box = [ tree, addr, nodelen ]
    addr += nodelen
    ls.append(box)

    if (typ == 0):
        box.append(addr)
        addr = compute_tree(ls, tree[1], addr, bits+'0')
        box.append(addr)
        addr = compute_tree(ls, tree[2], addr, bits+'1')
    else:
        ent_bits[tree] = bits

    return addr

def MemW4(mem, addr, val):
    mem[addr] = (val >> 24) & 0xff
    mem[addr+1] = (val >> 16) & 0xff
    mem[addr+2] = (val >> 8) & 0xff
    mem[addr+3] = (val) & 0xff

def write_tree(mem, ls):
    patches = [ 8 ] # root note address
    refs = []
    for box in ls:
        ent = box[0]
        addr = box[1]
        typ = ent[0]
        mem[addr] = typ
        if (typ == 0):
            MemW4(mem, addr+1, box[3])
            patches.append(addr+1)
            MemW4(mem, addr+5, box[4])
            patches.append(addr+5)
        elif (typ == 1):
            pass
        elif (typ == 2):
            mem[addr+1] = ord(ent[1])
        elif (typ == 3):
            addr += 1
            for ch in ent[1]:
                mem[addr] = ord(ch)
                addr += 1
            mem[addr] = 0
        elif (typ == 5):
            addr += 1
            for ch in ent[1]:
                MemW4(mem, addr, ord(ch))
                addr += 4
            MemW4(mem, addr, 0)
        elif (typ == 4):
            MemW4(mem, addr+1, ord(ent[1]))
    return (patches, refs)

while (True):
    ln = sys.stdin.readline()
    if (not ln):
        break
    ln = ln.lstrip()
    ln = ln.rstrip('\n\r')
    if (not ln):
        continue
    if (ln.startswith('#')):
        continue

    pos = ln.find(':')
    if (pos < 0):
        sys.stderr.write('Line has no label: ' + ln + '\n')
        continue

    label = ln[ : pos ]
    ln = ln[ pos+1 : ].lstrip(' ')
    ents = parse_text(ln, label)
    string_table[label] = ents

#for label in string_table:
#   print '###', label, ':', string_table[label]
#print huff_ents

if (not huff_ents):
    sys.stderr.write('No text to compress.\n')
    sys.exit(1)

sys.stderr.write(str(len(huff_ents)) + ' entities found.\n')

tree = build_tree()
if (verbose):
    dump_tree(tree)

addresses = []
totallen = compute_tree(addresses, tree)

mem = [ None for val in range(totallen) ]
MemW4(mem, 0, totallen)
MemW4(mem, 4, len(addresses))
MemW4(mem, 8, 12)
(patches, refs) = write_tree(mem, addresses)

if (None in mem):
    sys.stderr.write('Not all of memory was written.\n')
    sys.exit(1)

def print_table(arr, width=20, extrawidth=5):
    res = []
    pos = 0
    while (True):
        ls = [ str(val) for val in arr[ pos : pos+width ] ]
        if (not ls):
            break
        pos += width
        if (not res):
            width += extrawidth
        val = ' '.join(ls)
        if (res):
            val = '    ' + val
        res.append(val)
    res = '\n'.join(res) + ';'
    return res

print 'Array encoding_table ->', print_table(mem)

patches.append(0)
print 'Array encoding_patches -->', print_table(patches, 12)
print 'Global table_patched = false;'
print '[ patch_encoding_table   addr ix;'
print '  if (table_patched) return;'
print '  table_patched = true;'
print '  ix = 0;'
print '  while (1) {'
print '    addr = encoding_patches-->ix;'
print '    if (addr == 0) break;'
print '    addr = addr + encoding_table;'
print '    addr-->0 = addr-->0 + encoding_table;'
print '    ix++;'
print '  }'
for (addr, offset) in refs:
    print '  addr = encoding_table + ' + str(addr) + ';',
    print 'addr-->0 = ' + offset + ';'
print '];'

print '\n! String objects\n'

def bitstoint(val):
    res = 0
    bit = 1
    for ch in val:
        if (ch != '0'):
            res += bit
        bit *= 2
    return res

ls = string_table.keys()
ls.sort()
for label in ls:
    subls = [ ent_bits[ent] for ent in string_table[label] ]
    if (verbose):
        print '! ', label, subls
    bits = ''.join(subls)
    subls = [ bitstoint(bits[pos:pos+8]) for pos in range(0, len(bits), 8) ]
    if (not subls):
        # I6 won't compile a one-entry array correctly.
        subls.append('0')
    print 'Array', label, '->', '$E1', print_table(subls, 12)

sys.stderr.write(str(len(string_table)) + ' string objects created.\n')
    
