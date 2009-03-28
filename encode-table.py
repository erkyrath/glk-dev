#!/usr/bin/env python

import sys
import bisect

string_table = {}
huff_ents = {}
ent_bits = {}

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

def dump_tree(tree, depth=''):
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
    patches = []
    for box in ls:
        ent = box[0]
        addr = box[1]
        typ = ent[0]
        mem[addr] = typ
        if (typ == 0):
            MemW4(mem, addr+1, box[3])
            patches.append( (addr+1, 'encoding_table') )
            MemW4(mem, addr+5, box[4])
            patches.append( (addr+5, 'encoding_table') )
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
        elif (typ == 4):
            MemW4(mem, addr+1, ord(ent[1]))
    return patches

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
#dump_tree(tree)

addresses = []
totallen = compute_tree(addresses, tree)

mem = [ None for val in range(totallen) ]
MemW4(mem, 0, totallen)
MemW4(mem, 4, len(addresses))
MemW4(mem, 8, 12)
patches = write_tree(mem, addresses)

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
print '[ patch_encoding_table   addr;'
for (addr, offset) in patches:
    print '  addr = encoding_table + ' + str(addr) + ';',
    print 'addr-->0 += ' + offset + ';'
print '];'

print '\n! String objects\n'

ls = string_table.keys()
ls.sort()
for label in ls:
    subls = [ ent_bits[ent] for ent in string_table[label] ]
    bits = ''.join(subls)
    subls = [ int(bits[pos:pos+8], 2) for pos in range(0, len(bits), 8) ]
    if (not subls):
        # I6 won't compile a one-entry array correctly.
        subls.append('0')
    print 'Array', label, '->', '$E1', print_table(subls, 12)

    
