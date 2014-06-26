#!/usr/bin/env python3

"""
i7tohtml.py: Simple syntax-coloring wrapper for Inform 7
Written by Andrew Plotkin. This script is in the public domain.

This script converts Inform 7 source code to HTML, adding syntax coloring
in a way which I like. Strings, comments, and substitutions are colored
to resemble the I7 IDE. I6 source inclusions are shown in fixed-width,
with strings and comments colored but no other I6 elements called out.

(I don't try to mark I7 inclusions in the I6. Doesn't seem worth it.)

The real work is done by the Pygments syntax-coloring library. This requires
Pygments 2.0, which is unreleased (as I write this). You'll have to get it
from the source repository: http://bitbucket.org/birkenfeld/pygments-main/

(This script is Python 3. I haven't tested it in Python 2. It would probably
get Unicode wrong.)
"""

import sys
import re
import codecs
import optparse

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from pygments.token import Token, Comment, String
from pygments.filter import Filter

popt = optparse.OptionParser(usage='i7tohtml.py [options] story.ni > out.html')

popt.add_option('-T', '--title',
                action='store', dest='title', default='Game-Title',
                help='Title of game (default: "Game-Title")')
popt.add_option('--css',
                action='store', dest='cssfile', metavar='FILE',
                help='read CSS file (instead of using built-in CSS)')

(opts, args) = popt.parse_args()

if not args:
    code = sys.stdin.read()
else:
    fl = open(args[0])
    code = fl.read()
    fl.close()

css = None
if opts.cssfile:
    fl = open(opts.cssfile)
    css = fl.read()
    fl.close()

class CleanI6Filter(Filter):
    """Clean up the fruit-salad of I6 syntax coloring that Pygments normally
    applies. All I6 code winds up in the Comment.Single, String.Other, or
    Token.Other class.
    """
    def __init__(self, **options):
        Filter.__init__(self, **options)
                    
    def filter(self, lexer, stream):
        i6mode = False
        for ttype, value in stream:
            if ttype is Token.Punctuation:
                if value == '(-':
                    i6mode = True
                    yield ttype, value
                    continue
                if value == '-)':
                    i6mode = False
                    yield ttype, value
                    continue
            if i6mode:
                if ttype is Comment.Single:
                    yield ttype, value
                elif ttype is String.Double or ttype is String.Single or ttype is String.Char:
                    yield String.Other, value
                else:
                    yield Token.Other, value
            else:
                yield ttype, value

lexer = get_lexer_by_name('inform7', encoding='utf-8')
lexer.add_filter(CleanI6Filter())
formatter = HtmlFormatter(nowrap=True, classprefix='i7', lineseparator='\n')
result = highlight(code, lexer, formatter)

header_block = '''<!doctype HTML PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<html>
<head>
<title>$TITLE$: Source Code</title>
<style type="text/css">
$CSS$
</style>
</head>
<body>

'''

css_block = '''
.i7cm {
  font-style: italic;
  color: #207D20;
}
.i7c1 {
  font-family: monospace;
  font-style: italic;
  color: #207D20;
}
.i7gh {
  font-size: 1.2em;
  font-weight: bold;
}
.i7si {
  font-style: italic;
  color: #4E54FB;
}
.i7s2 {
  font-weight: bold;
  color: #095097;
}
.i7sx {
  font-family: monospace;
  font-weight: bold;
  color: #095097;
}
.i7x {
  font-family: monospace;
}
'''

footer_block = '''
</body>
</html>
'''


encode_ascii = codecs.getencoder('ascii')
spaces_re = re.compile('  +')

def spaces_replace(match):
    num = match.end() - match.start()
    if num == 0:
        return ''
    if num == 1:
        return ' '
    return ('&nbsp;' * (num-1)) + ' '

if css is None:
    css = css_block
print(header_block.replace('$CSS$', css).replace('$TITLE$', opts.title))

for ln in result.split('\n'):
    # Detab (assuming four spaces per tab).
    ln = ln.replace('\t', '    ')
    ln = ln.rstrip()

    # Convert any sequence of two or more spaces to a string of NBSP
    # followed by a normal space. This gives us correct indentation.
    ln = spaces_re.sub(spaces_replace, ln)

    # Convert non-ASCII characters to HTML encoded chars (&#NNN;)
    ln = encode_ascii(ln, 'xmlcharrefreplace')[0].decode()
    print(ln)
    print('<br>')

print(footer_block)
