#!/usr/bin/env python

# http://inform-fiction.org/source/tm/chapter12.txt

import sys
import optparse

popt = optparse.OptionParser()
(opts, args) = popt.parse_args()

if not args:
    print 'Usage: i6color source.inf'
    sys.exit(-1)

# Bit flags. It's probably silly to use a bitmask flag-set in Python,
# but I'm doing it. I precompute all the "not bit" values as well.

SBIT_COMMENT        = 1 << 16
SBIT_SINGLEQUOTE    = 1 << 17
SBIT_DOUBLEQUOTE    = 1 << 18
SBIT_STATEMENT      = 1 << 19
SBIT_AFTERMARKER    = 1 << 20
SBIT_HIGHLIGHT      = 1 << 21
SBIT_HIGHLIGHTALL   = 1 << 22
SBIT_COLORBACKTRACK = 1 << 23
SBIT_AFTERRESTART   = 1 << 24
SBIT_WAITDIRECT     = 1 << 25
SBIT_DONTKNOW       = 1 << 26

SBIT_NO_COMMENT        = 0xFFFFFFFF ^ SBIT_COMMENT
SBIT_NO_DOUBLEQUOTE    = 0xFFFFFFFF ^ SBIT_DOUBLEQUOTE
SBIT_NO_SINGLEQUOTE    = 0xFFFFFFFF ^ SBIT_SINGLEQUOTE
SBIT_NO_STATEMENT      = 0xFFFFFFFF ^ SBIT_STATEMENT
SBIT_NO_AFTERMARKER    = 0xFFFFFFFF ^ SBIT_AFTERMARKER
SBIT_NO_HIGHLIGHT      = 0xFFFFFFFF ^ SBIT_HIGHLIGHT
SBIT_NO_HIGHLIGHTALL   = 0xFFFFFFFF ^ SBIT_HIGHLIGHTALL
SBIT_NO_COLORBACKTRACK = 0xFFFFFFFF ^ SBIT_COLORBACKTRACK
SBIT_NO_AFTERRESTART   = 0xFFFFFFFF ^ SBIT_AFTERRESTART
SBIT_NO_WAITDIRECT     = 0xFFFFFFFF ^ SBIT_WAITDIRECT
SBIT_NO_DONTKNOW       = 0xFFFFFFFF ^ SBIT_DONTKNOW

COL_FOREGROUND = '.'
COL_SINGLEQUOTE = '\''
COL_DOUBLEQUOTE = '"'
COL_COMMENT = '!'
COL_PROPERTY = 'p'
COL_DIRECTIVE = 'D'
COL_FUNCTION = 'F'
COL_FUNCTIONDELIM = 'f'
COL_CODE = 'C'

class I6ColorSpan:
    def __init__(self, text, color, startline=False):
        self.text = text
        self.color = color
        self.startline = startline
    def __repr__(self):
        prefix = 'NL: ' if self.startline else ''
        return '<%s%s: %s>' % (prefix,
                               I6SyntaxColor.color_names[self.color],
                               repr(self.text))

class I6SyntaxColor:
    bit_names = [
        'comment', 'singlequote', 'doublequote', 'statement', 'aftermarker',
        'highlight', 'highlightall', 'colorbacktrack', 'afterrestart',
        'waitdirect', 'dontknow',
    ]

    color_names = {
        COL_FOREGROUND: 'foreground',
        COL_SINGLEQUOTE: 'singlequote',
        COL_DOUBLEQUOTE: 'doublequote',
        COL_COMMENT: 'comment',
        COL_PROPERTY: 'property',
        COL_DIRECTIVE: 'directive',
        COL_FUNCTION: 'function',
        COL_FUNCTIONDELIM: 'functiondelim',
        COL_CODE: 'code',
    }

    @staticmethod
    def show_state(state):
        bits = []
        for ix in range(len(I6SyntaxColor.bit_names)):
            if state & (1 << (ix+16)):
                bits.append(I6SyntaxColor.bit_names[ix])
        res = hex(state & 0xFFFF)
        if bits:
            res = res + ',' + ','.join(bits)
        return res
    
    def scanner(self, state, ch):
        newcolor = None
        
        if state & SBIT_COMMENT:
            if ch == '\n':
                state &= SBIT_NO_COMMENT
            return (None, state)
        if state & SBIT_DOUBLEQUOTE:
            if ch == '"':
                state &= SBIT_NO_DOUBLEQUOTE
            return (None, state)
        if state & SBIT_SINGLEQUOTE:
            if ch == '\'':
                state &= SBIT_NO_SINGLEQUOTE
            return (None, state)
        if ch == '\'':
            state |= SBIT_SINGLEQUOTE
            return (None, state)
        if ch == '"':
            state |= SBIT_DOUBLEQUOTE
            return (None, state)
        if ch == '!':
            state |= SBIT_COMMENT
            return (None, state)
        
        if state & SBIT_STATEMENT:
            if ch == ']':
                state &= SBIT_NO_STATEMENT
                return (None, state)
            if not state & SBIT_AFTERRESTART:
                return (None, state)
            (term, state) = self.innerstate(state, ch)
            newcolor = None
            if term and (state & 0xF00):
                newcolor = (COL_FUNCTION, (state & 0x7FFF)>>8)
                state |= SBIT_COLORBACKTRACK
                state &= SBIT_NO_AFTERRESTART
            if ch == ';':
                state &= SBIT_NO_AFTERRESTART
            return (newcolor, state)
        else:
            if ch == '[':
                state |= SBIT_STATEMENT
                if not state & SBIT_AFTERRESTART:
                    state |= SBIT_AFTERRESTART
                return (None, state)
            (term, state) = self.innerstate(state, ch)
            newcolor = None
            if term:
                instate = (state & 0xFFFF)
                if instate == 2:
                    newcolor = (COL_DIRECTIVE, 2)
                    state |= SBIT_AFTERMARKER
                    state |= SBIT_COLORBACKTRACK
                    state &= 0xFFFF0000
                elif instate == 3:
                    newcolor = (COL_DIRECTIVE, 1)
                    state |= SBIT_AFTERMARKER
                    state |= SBIT_COLORBACKTRACK
                    state &= 0xFFFF0000
                elif instate == 0x8404:
                    newcolor = (COL_DIRECTIVE, (instate & 0x7FFF)>>8)
                    state |= SBIT_AFTERMARKER
                    state |= SBIT_COLORBACKTRACK
                    state |= SBIT_HIGHLIGHT
                    state &= SBIT_NO_HIGHLIGHTALL
                elif instate == 0x8313 or instate == 0x8525:
                    newcolor = (COL_DIRECTIVE, (instate & 0x7FFF)>>8)
                    state |= SBIT_AFTERMARKER
                    state |= SBIT_COLORBACKTRACK
                    state &= SBIT_NO_HIGHLIGHT
                    state |= SBIT_HIGHLIGHTALL
                else:
                    if state & SBIT_WAITDIRECT:
                        newcolor = (COL_DIRECTIVE, (instate & 0x7FFF)>>8)
                        state |= SBIT_COLORBACKTRACK
                        state &= SBIT_NO_WAITDIRECT
                    elif state & SBIT_HIGHLIGHTALL:
                        newcolor = (COL_PROPERTY, (instate & 0x7FFF)>>8)
                        state |= SBIT_COLORBACKTRACK
                    elif state & SBIT_HIGHLIGHT:
                        newcolor = (COL_PROPERTY, (instate & 0x7FFF)>>8)
                        state |= SBIT_COLORBACKTRACK
                        state &= SBIT_NO_HIGHLIGHT
    
                if ch == ';':
                    state |= SBIT_WAITDIRECT
                    state &= SBIT_NO_AFTERMARKER
                    state &= SBIT_NO_AFTERRESTART
                    state &= SBIT_NO_HIGHLIGHT
                    state &= SBIT_NO_HIGHLIGHTALL
                elif ch == ',':
                    state |= SBIT_AFTERMARKER
                    state |= SBIT_HIGHLIGHT
            return (newcolor, state)
        
        raise Exception('scanner reached illegal state')
    
    def innerstate(self, state, ch):
        instate = (state & 0xFFFF)
        termflag = False
    
        if instate >= 0x8000:
            instate = 0
        
        if instate == 0:
            if ch == '-':
                instate = 1
            elif ch == '*':
                instate = 3
                termflag = True
            elif ch.isspace():
                instate = 0
            elif ch == '_':
                instate = 0x100
            elif ch == 'w':
                instate = 0x101
            elif ch == 'h':
                instate = 0x111
            elif ch == 'c':
                instate = 0x121
            elif ch.isalpha():
                instate = 0x100
            else:
                instate = 0xFF
        elif instate == 1:
            if ch == '>':
                instate = 2
                termflag = True
            else:
                instate = 0xFF
        elif instate == 2:
            instate = 0
        elif instate == 3:
            instate = 0
        elif instate == 0xFF:
            if ch.isspace():
                instate = 0
            else:
                instate = 0xFF
        elif instate >= 0x100 and instate < 0x8000:
            if not (ch.isalnum() or ch == '_'):
                instate += 0x8000
                termflag = True
            elif instate == 0x101:
                instate = 0x202 if (ch == 'i') else 0x200
            elif instate == 0x202:
                instate = 0x303 if (ch == 't') else 0x300
            elif instate == 0x303:
                instate = 0x404 if (ch == 'h') else 0x400
            elif instate == 0x111:
                instate = 0x212 if (ch == 'a') else 0x200
            elif instate == 0x212:
                instate = 0x313 if (ch == 's') else 0x300
            elif instate == 0x121:
                instate = 0x222 if (ch == 'l') else 0x200
            elif instate == 0x222:
                instate = 0x323 if (ch == 'a') else 0x300
            elif instate == 0x323:
                instate = 0x424 if (ch == 's') else 0x400
            elif instate == 0x424:
                instate = 0x525 if (ch == 's') else 0x500
            else:
                if ch.isalnum():
                    instate += 0x100
        elif instate >= 0x8000:
            instate = 0
        else:
            raise Exception('scanner reached illegal state')
        state = (state & 0xFFFF0000) | instate
        return (termflag, state)
    
    def charcolor(self, state, ch):
        if state & SBIT_SINGLEQUOTE:
            return COL_SINGLEQUOTE
        if state & SBIT_DOUBLEQUOTE:
            return COL_DOUBLEQUOTE
        if state & SBIT_COMMENT:
            return COL_COMMENT
        if state & SBIT_STATEMENT:
            if ch == '[' or ch == ']':
                return COL_FUNCTIONDELIM
            if ch == '\'':
                return COL_SINGLEQUOTE
            if ch == '"':
                return COL_DOUBLEQUOTE
            return COL_CODE
        else:
            if ch in (',', ';', '*', '>'):
                return COL_DIRECTIVE
            if ch == '[' or ch == ']':
                return COL_FUNCTIONDELIM
            if ch == '\'':
                return COL_SINGLEQUOTE
            if ch == '"':
                return COL_DOUBLEQUOTE
            return COL_FOREGROUND
    
    def parse(self, fl):
        state = SBIT_WAITDIRECT
        color = COL_DIRECTIVE
        spans = []
    
        startline = True
        ls = []
        
        while True:
            ch = fl.read(1)
            if ch == '':
                break
            (backtup, state) = self.scanner(state, ch)
            if state & SBIT_COLORBACKTRACK:
                assert (backtup is not None)
                (backcol, backdist) = backtup
                state &= SBIT_NO_COLORBACKTRACK
                assert (backdist > 0)
                assert (len(ls) >= backdist)
                prels = ls[ 0 : -backdist ]
                ls = ls[ -backdist : ]
                if prels:
                    spans.append(I6ColorSpan(''.join(prels), color, startline))
                    startline = False
                color = backcol
            newcol = self.charcolor(state, ch)
            if newcol != color or ch == '\n':
                if ls:
                    spans.append(I6ColorSpan(''.join(ls), color, startline))
                    ls = []
                    startline = False
                color = newcol
            if ch == '\n':
                startline = True
            else:
                ls.append(ch)
            
        if ls:
            spans.append(I6ColorSpan(''.join(ls), color, startline))
            ls = []
            startline = False
    
        return spans

def printspans(spans):
    texts = []
    colors = []
    for span in spans:
        if span.startline:
            print ''.join(texts)
            print ''.join(colors)
            texts = []
            colors = []
        text = span.text.replace('\t', '    ')
        coltext = span.color * len(text)
        texts.append(text)
        colors.append(coltext)
    print ''.join(texts)
    print ''.join(colors)

fl = open(args[0], 'U')
spans = I6SyntaxColor().parse(fl)
fl.close()

printspans(spans)
