#!/usr/bin/env python3

# i7tortf.py: Format Inform 7 source code in a nice way.
# Created by Andrew Plotkin (erkyrath@eblong.com)
# This script is in the public domain.

# This script depends on the Pygments syntax-colorer (http://pygments.org/).
# You must install Python 3 and Pygments 2 to use it.

import sys
import optparse
import pygments
import pygments.style
from pygments.lexers.int_fiction import Inform7Lexer
from pygments.formatters.rtf import RtfFormatter
from pygments.token import Token

popt = optparse.OptionParser(usage='usage: i7tortf.py [OPTIONS] story.ni [ story2.ni ... ]')

popt.add_option('-o', '--output',
                action='store', dest='outfile',
                help='name for generated RTF file (default: stdout)')
popt.add_option('-c', '--color',
                action='store_true', dest='colorize',
                help='add color to the generated RTF file')

(opts, args) = popt.parse_args()

if not args:
    print('usage: ' + popt.usage)
    sys.exit(-1)

class ZarfI7Lexer(pygments.lexer.Lexer):
    name = 'ZarfI7Lexer'
    aliases = []
    filenames = ['*.ni', '*.i7x']

    i7sectionnames = set(['volume', 'book', 'part', 'chapter', 'section'])
    
    def get_tokens_unprocessed(self, text):
        linestyle = Token.Text
        pos = 0
        last = 0
        lentext = len(text)
        lastch = ''
        while True:
            if pos >= len(text):
                if pos > last:
                    yield (last, linestyle, text[last:pos])
                    last = pos
                break
            ch = text[pos]
            if ch == '-' and lastch == '(':
                pos -= 1
                if pos > last:
                    yield (last, linestyle, text[last:pos])
                    last = pos
                last = pos
                pos += 2
                lastch = ''
                while pos < lentext:
                    ch = text[pos]
                    if ch == ')' and lastch == '-':
                        break
                    if ch == '"':
                        if pos > last:
                            yield (last, Token.Other, text[last:pos])
                            last = pos
                        pos += 1
                        while pos < lentext:
                            if text[pos] == '"':
                                break
                            pos += 1
                        pos += 1
                        yield (last, Token.String.Other, text[last:pos])
                        last = pos
                        lastch = ''
                        continue
                    if ch == '\'':
                        if pos > last:
                            yield (last, Token.Other, text[last:pos])
                            last = pos
                        pos += 1
                        while pos < lentext:
                            if text[pos] == '\'':
                                break
                            pos += 1
                        pos += 1
                        yield (last, Token.String.Single, text[last:pos])
                        last = pos
                        lastch = ''
                        continue
                    if ch == '!':
                        if pos > last:
                            yield (last, Token.Other, text[last:pos])
                            last = pos
                        pos += 1
                        while pos < lentext:
                            if text[pos] == '\n':
                                break
                            pos += 1
                        pos += 1
                        yield (last, Token.Comment.Single, text[last:pos])
                        last = pos
                        lastch = ''
                        continue
                    pos += 1
                    lastch = ch
                pos += 1
                yield (last, Token.Other, text[last:pos])
                last = pos
                lastch = ''
                continue
            if ch == '[':
                if pos > last:
                    yield (last, linestyle, text[last:pos])
                    last = pos
                pos += 1
                depth = 1
                while pos < lentext:
                    if text[pos] == '[':
                        depth += 1
                    if text[pos] == ']':
                        depth -= 1;
                        if depth == 0:
                            break
                    pos += 1
                pos += 1
                yield (last, Token.Comment, text[last:pos])
                last = pos
                lastch = ''
                continue
            if ch == '"':
                if pos > last:
                    yield (last, linestyle, text[last:pos])
                    last = pos
                pos += 1
                while pos < lentext:
                    if text[pos] == '"':
                        break
                    if text[pos] == '[':
                        if pos > last:
                            yield (last, Token.String, text[last:pos])
                            last = pos
                        pos += 1
                        while pos < lentext:
                            if text[pos] == ']':
                                break
                            pos += 1
                        pos += 1
                        yield (last, Token.String.Interpol, text[last:pos])
                        last = pos
                        continue
                    pos += 1
                pos += 1
                yield (last, Token.String, text[last:pos])
                last = pos
                lastch = ''
                continue
            pos += 1
            lastch = ch
            if ch == '\n' or ch == '\r':
                if pos > last:
                    yield (last, linestyle, text[last:pos])
                    last = pos
                val = text.find(' ', pos)
                if val >= pos and text[pos:val].lower() in self.i7sectionnames:
                    linestyle = Token.Generic.Heading
                else:
                    linestyle = Token.Text
        return

# Inform's styles are a little hard to express in Pygment's model.
# Here's how I've set it up:

# Token.Generic.Heading: Inform 7 section heading ("Volume", "Book", etc)
# Token.Comment: Inform 7 comment.
# Token.String: Inform 7 string.
# Token.String.Interpol: [Interpolation] in an Inform 7 string.
# Token.Other: Inform 6 inclusion.
# Token.Comment.Single: Inform 6 comment.
# Token.String.Other: Inform 6 string.
# Token.String.Single: Inform 6 dict word.

# The style definitions are also warped to fit my formatter model.
# "Underline" actually means a larger font, and "border:#888" means
# fixed-width font.

class ZarfI7Style(pygments.style.Style):
    default_style = ''
    styles = {
        Token.Comment: 'italic #060',
        Token.Comment.Single: 'italic border:#888 #060',
        Token.Other: 'border:#888 #00C',
        Token.String: 'bold #800',
        Token.String.Interpol: 'bold italic #660',
        Token.String.Other: 'border:#888 bold #060',
        Token.String.Single: 'border:#888 bold #660',
        Token.Generic.Heading: 'bold underline',
    }

class ZarfRtfFormatter(pygments.formatter.Formatter):
    name = 'ZRTF'
    aliases = ['zrtf']
    filenames = ['*.rtf']

    def __init__(self, **options):
        pygments.formatter.Formatter.__init__(self, **options)
        self.monochrome = pygments.util.get_bool_opt(options, 'monochrome', False)
        #self.fontface = options.get('fontface') or ''
        #self.fontsize = get_int_opt(options, 'fontsize', 0)

    def _escape(self, text):
        return text.replace(u'\\', u'\\\\') \
                   .replace(u'{', u'\\{') \
                   .replace(u'}', u'\\}')

    def _escape_text(self, text):
        # empty strings, should give a small performance improvment
        if not text:
            return u''

        # escape text
        text = self._escape(text)

        buf = []
        for c in text:
            cn = ord(c)
            if cn < (2**7):
                # ASCII character
                buf.append(str(c))
            elif (2**7) <= cn < (2**16):
                # single unicode escape sequence
                buf.append(u'{\\u%d}' % cn)
            elif (2**16) <= cn:
                # RTF limits unicode to 16 bits.
                # Force surrogate pairs
                buf.append(u'{\\u%d}{\\u%d}' % _surrogatepair(cn))

        return u''.join(buf).replace(u'\n', u'\\par\n')

    def format_unencoded(self, tokensource, outfile):
        # rtf 1.8 header
        outfile.write(u'{\\rtf1\\ansi\\uc0\\deff0'
                      u'{\\fonttbl{\\f0\\froman\\fprq1\\fcharset0 %s;}}'
                      u'{\\fonttbl\\f0\\froman\\fcharset0 %s;\\f1\\froman\\fcharset0 %s;}'
                      % (self._escape('Palatino'), self._escape('Palatino'), self._escape('Courier')))

        if not self.monochrome:
            outfile.write(u'{\\colortbl;')
            # convert colors and save them in a mapping to access them later.
            color_mapping = {}
            offset = 1
            for _, style in self.style:
                for color in style['color'], style['bgcolor'], style['border']:
                    if color and color not in color_mapping:
                        color_mapping[color] = offset
                        outfile.write(u'\\red%d\\green%d\\blue%d;' % (
                            int(color[0:2], 16),
                            int(color[2:4], 16),
                            int(color[4:6], 16)
                        ))
                        offset += 1
            outfile.write(u'}')
        outfile.write(u'\\f0 \\fs%d' % (20,))

        # highlight stream
        for ttype, value in tokensource:
            while not self.style.styles_token(ttype) and ttype.parent:
                ttype = ttype.parent
            style = self.style.style_for_token(ttype)
            buf = []
            if style['bgcolor'] and not self.monochrome:
                buf.append(u'\\cb%d' % color_mapping[style['bgcolor']])
            if style['color'] and not self.monochrome:
                buf.append(u'\\cf%d' % color_mapping[style['color']])
            if style['bold']:
                buf.append(u'\\b')
            if style['italic']:
                buf.append(u'\\i')
            if style['underline']:
                buf.append(u'\\fs24')
            if style['border']:
                buf.append(u'\\f1\\fs18')
            start = u''.join(buf)
            if start:
                outfile.write(u'{%s ' % start)
            outfile.write(self._escape_text(value))
            if start:
                outfile.write(u'}')

        outfile.write(u'}')


# Read in all the source code.
dat = ''
for filename in args:
    fl = open(filename)
    dat = dat + fl.read() + '\n'
    fl.close()

# Create the lexer and formatter.
lexer = ZarfI7Lexer()
form = ZarfRtfFormatter(style=ZarfI7Style, monochrome=(not opts.colorize))

# Do the job.

if opts.outfile:
    outfl = open('story.rtf', 'w')
else:
    outfl = sys.stdout

pygments.highlight(dat, lexer, form, outfile=outfl)

if opts.outfile:
    outfl.close()
