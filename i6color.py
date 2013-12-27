#!/usr/bin/env python

"""
Python implementation of the Inform 6 syntax-coloring algorithm.
Written by Andrew Plotkin (erkyrath@eblong.com).
This code is in the public domain.

This is based on Graham Nelson's algorithm in the Inform Technical Manual
(http://inform-fiction.org/source/tm/chapter12.txt). However, that chapter
is not completely clear, and requires some tweaks for correctness as well.
Andrew Hunter's code in the MacOS I7 IDE was helpful in resolving the
issues.
"""

import sys
import re
import optparse

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

# Color constants. These are single-character strings, suitable for printing
# by the print_as_lines() function. The algorithm just uses them as constants,
# though.
COL_FOREGROUND    = '.'  # data at the top level
COL_SINGLEQUOTE   = '\'' # a single-quoted string constant (dict word)
COL_DOUBLEQUOTE   = '"'  # a double-quoted string constant
COL_COMMENT       = '!'  # a comment
COL_PROPERTY      = 'p'  # a property name
COL_DIRECTIVE     = 'D'  # a directive keyword
COL_FUNCTION      = 'F'  # the name of a function
COL_FUNCTIONDELIM = 'f'  # the brackets delimiting a function body
COL_CODE          = 'C'  # code or data within a function
COL_TEXTESCAPE    = '\\' # escape char in a string constant

class I6ColorSpan:
    """I6ColorSpan: Represents one "span" of text -- a string of characters
    of the same style.

    Spans do not extend across multiple lines. (That is, you can have two
    adjacent spans of the same style, if there's a line break in the source
    between them). The span object never contains line breaks. Instead,
    they're indicated by the startline field: a nonfalse value indicates
    that this span is the start of a new line. If the value is greater than
    1, it indicates how many blank lines occur before the span.
    """
    def __init__(self, text, color, startline=False):
        assert (len(text) > 0)
        self.text = text
        self.color = color
        self.startline = startline
    def __repr__(self):
        prefix = ''
        if self.startline:
            if self.startline > 1:
                prefix = '%d*NL:' % (self.startline,)
            else:
                prefix = 'NL:'
        return '<%s%s: %s>' % (prefix,
                               I6SyntaxColor.color_names[self.color],
                               repr(self.text))

class I6SyntaxColor:
    """I6SyntaxColor: The syntax colorer.
    """

    # Human-readable names for the state bit flags.
    bit_names = [
        'comment', 'singlequote', 'doublequote', 'statement', 'aftermarker',
        'highlight', 'highlightall', 'colorbacktrack', 'afterrestart',
        'waitdirect', 'dontknow',
    ]

    # Human-readable names for the colors.
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
        COL_TEXTESCAPE: 'textescape',
    }

    # Group of escape characters in a string.
    re_stringescapes = re.compile('[~^\\\\]+')

    @staticmethod
    def show_state(state):
        """Convert a state value to a human-readable string.
        """
        bits = []
        for ix in range(len(I6SyntaxColor.bit_names)):
            if state & (1 << (ix+16)):
                bits.append(I6SyntaxColor.bit_names[ix])
        res = hex(state & 0xFFFF)
        if bits:
            res = res + ',' + ','.join(bits)
        return res
    
    
    def parse(self, fl):
        """Top-level handler for parsing a file. (The argument must be
        an open file, or otherwise support the read(n) method.)

        Returns a list of I6ColorSpan objects.
        """
        state = SBIT_WAITDIRECT
        color = COL_DIRECTIVE
        spans = []
    
        startline = 1
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
                    startline = 0
                color = backcol
            newcol = self.charcolor(state, ch)
            if newcol != color or ch == '\n':
                if ls:
                    spans.append(I6ColorSpan(''.join(ls), color, startline))
                    ls = []
                    startline = 0
                color = newcol
            if ch == '\n':
                startline += 1
            else:
                ls.append(ch)
            
        if ls:
            spans.append(I6ColorSpan(''.join(ls), color, startline))
            ls = []
            startline = 0

        spans = self.refine(spans)
        return spans
    
    def scanner(self, state, ch):
        """Middle-level state machine for processing characters. Given a
        state value and an input character, computes a new state value.

        This returns a pair (backtrack, newstate). If the COLORBACKTRACK
        bit of newstate is set, the backtrack value will itself be a pair
        (color, backlength). This means to mark the previous backlength
        characters as being of the given color. (The backlength will
        not cross a line boundary.)
        """
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
        """Low-level state machine for processing characters. This
        updates the "inner state" (low 16 bits) of the state value.
        It returns a pair (termflag, newstate). If termflag is True,
        then we have reached the end of an identifier, "*", or "->"
        token.
        """
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

    def refine(self, spans):
        """Given a list of spans, split some of them up into more detailed
        span-groups. Return an updated list.
        """
        res = []
        for span in spans:
            if span.color in (COL_SINGLEQUOTE, COL_DOUBLEQUOTE):
                # Locate escape sequences in the string.
                text = span.text
                col = span.color
                startline = span.startline
                pos = 0
                while pos < len(text):
                    match = self.re_stringescapes.search(text, pos)
                    if not match:
                        break
                    if pos < match.start():
                        span = I6ColorSpan(text[pos:match.start()], col, startline)
                        res.append(span)
                        startline = 0
                    span = I6ColorSpan(text[match.start():match.end()], COL_TEXTESCAPE, startline)
                    res.append(span)
                    startline = 0
                    pos = match.end()    
                if pos < len(text):
                    span = I6ColorSpan(text[pos:], col, startline)
                    res.append(span)
            else:
                res.append(span)
        return res
    
    def charcolor(self, state, ch):
        """Given a character and a state (returned from scanner()),
        determine the color for the character.
        """
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
    

def print_as_lines(spans):
    """A simple output model: displays a program with style characters under
    each line of output. For example:

        Object bar class Superclass;
        DDDDDD.....DDDDD.ppppppppppD

    Because of the slightly goofy representation of line breaks in our
    spans array, this trims blank lines at the very beginning and end of
    the program.
    """
    texts = None
    colors = None
    for span in spans:
        if texts is None:
            # Very first line: there's no accumulated data to print.
            # Set up the accumulator arrays.
            texts = []
            colors = []
        elif span.startline:
            # Start of a line (after the first). Print the accumulated
            # data from the preceding line. Then clear the arrays.
            print ''.join(texts)
            print ''.join(colors)
            texts = []
            colors = []
            if span.startline > 1:
                # Python's print statement adds an extra newline, plus
                # there was a newline after the print statements above.
                print '\n' * (span.startline-2)
        text = span.text.replace('\t', '    ')
        coltext = span.color * len(text)
        texts.append(text)
        colors.append(coltext)
    # The last line's accumulated data needs to be printed.
    print ''.join(texts)
    print ''.join(colors)

# The top level of the script -- argument-parsing.
    
popt = optparse.OptionParser()
(opts, args) = popt.parse_args()

if not args:
    print 'Usage: i6color.py source.inf'
    sys.exit(-1)

fl = open(args[0], 'U')
spans = I6SyntaxColor().parse(fl)
fl.close()

print_as_lines(spans)
