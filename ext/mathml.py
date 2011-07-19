#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import re

try:
    from xml.etree.cElementTree import Element, tostring
except ImportError:
    from xml.etree.ElementTree import Element, tostring

Element_ = Element
AtomicString_ = lambda s: s

def El(tag, text=None, *children, **attrib):
    element = Element_(tag, **attrib)

    if not text is None:
        if isinstance(text, basestring):
            element.text = AtomicString_(text)
        else:
            children = (text, ) + children

    for child in children:
        element.append(child)

    return element

number_re = re.compile('-?(\d+\.(\d+)?|\.?\d+)')

def strip_parens(n):
    if n.tag == 'mrow':
        if n[0].get('_opening', False):
           del n[0]

        if n[-1].get('_closing', False):
            del n[-1]

    return n

def is_enclosed_in_parens(n):
    return n.tag == 'mrow' and n[0].get('_opening', False) and n[-1].get('_closing', False)

def binary(operator, operand_1, operand_2, swap=False):
    operand_1 = strip_parens(operand_1)
    operand_2 = strip_parens(operand_2)
    if not swap:
        operator.append(operand_1)
        operator.append(operand_2)
    else:
        operator.append(operand_2)
        operator.append(operand_1)

    return operator

def unary(operator, operand, swap=False):
    operand = strip_parens(operand)
    if swap:
        operator.insert(0, operand)
    else:
        operator.append(operand)

    return operator

def frac(num, den):
    return El('mfrac', strip_parens(num), strip_parens(den))

def sub(base, subscript):
    subscript = strip_parens(subscript)

    if base.tag in ('msup', 'mover'):
        children = base.getchildren()
        n = El('msubsup' if base.tag == 'msup' else 'munderover', children[0], subscript, children[1])
    else:
        n = El('munder' if base.get('_underover', False) else 'msub', base, subscript)

    return n

def sup(base, superscript):
    superscript = strip_parens(superscript)

    if base.tag in ('msub', 'munder'):
        children = base.getchildren()
        n = El('msubsup' if base.tag == 'msub' else 'munderover', children[0], children[1], superscript)
    else:
        n = El('mover' if base.get('_underover', False) else 'msup', base, superscript)

    return n

def parse(s, element=Element, atomicstring=lambda s: s):
    """
Translates from ASCIIMathML (an easy to type and highly readable way to
represent math formulas) into MathML (a w3c standard directly displayable by
some web browsers).

The function `parse()` generates a tree of elements:

    >>> import asciimathml
    >>> asciimathml.parse('sqrt 2')
    <Element math at b76fb28c>

The tree can then be manipulated using the standard python library.  For
example we can generate its string representation:

    >>> from xml.etree.ElementTree import tostring
    >>> tostring(asciimathml.parse('sqrt 2'))
    '<math><mstyle><msqrt><mn>2</mn></msqrt></mstyle></math>'
    """

    global Element_, AtomicString_

    Element_ = element
    AtomicString_ = atomicstring

    s, nodes = parse_exprs(s)
    remove_invisible(nodes)
    nodes = map(remove_private, nodes)

    return El('math', El('mstyle', *nodes), xmlns='http://www.w3.org/1998/Math/MathML', display='inline')

delimiters = {'{': '}', '(': ')', '[': ']'}

def parse_string(s):
    opening = s[0]

    if opening in delimiters:
        closing = delimiters[opening]
        end = s.find(closing)

        text = s[1:end]
        s = s[end+1:]
    else:
        s, text = parse_m(s)

    return s, El('mrow', El('mtext', text))

def parse_expr(s, required=False):
    s, n = parse_m(s, required=required)

    if not n is None:
        if n.get('_opening', False):
            s, children = parse_exprs(s, [n], inside_parens=True)
            n = El('mrow', *children)

        if n.tag == 'mtext':
            s, n = parse_string(s)
        elif n.get('_arity', 0) == 1:
            s, m = parse_expr(s, True)
            n = unary(n, m, n.get('_swap', False))
        elif n.get('_arity', 0) == 2:
            s, m1 = parse_expr(s, True)
            s, m2 = parse_expr(s, True)
            n = binary(n, m1, m2, n.get('_swap', False))

    return s, n

def find_node(ns, text):
    for i, n in enumerate(ns):
        if n.text == text:
            return i

    return -1

def nodes_to_row(row):
    mrow = El('mtr')

    nodes = row.getchildren()

    while True:
        i = find_node(nodes, ',')

        if i > 0:
            mrow.append(El('mtd', *nodes[:i]))

            nodes = nodes[i+1:]
        else:
            mrow.append(El('mtd', *nodes))
            break

    return mrow

def nodes_to_matrix(nodes):
    mtable = El('mtable')

    for row in nodes[1:-1]:
        if row.text == ',':
            continue

        mtable.append(nodes_to_row(strip_parens(row)))

    return El('mrow', nodes[0], mtable, nodes[-1])

def parse_exprs(s, nodes=None, inside_parens=False):
    if nodes is None:
        nodes = []

    inside_matrix = False

    while True:
        s, n = parse_expr(s)

        if not n is None:
            nodes.append(n)

            if n.get('_closing', False):
                if not inside_matrix:
                    return s, nodes
                else:
                    return s, nodes_to_matrix(nodes)

            if inside_parens and n.text == ',' and is_enclosed_in_parens(nodes[-2]):
                inside_matrix = True

            if len(nodes) >= 3 and nodes[-2].get('_special_binary'):
                transform =  nodes[-2].get('_special_binary')
                nodes[-3:] = [transform(nodes[-3], nodes[-1])]

        if s == '':
            return '', nodes

def remove_private(n):
    _ks = [k for k in n.keys() if k.startswith('_') or k == 'attrib']

    for _k in _ks:
        del n.attrib[_k]

    for c in n.getchildren():
        remove_private(c)

    return n

def remove_invisible(ns):
    for i in range(len(ns)-1, 0, -1):
        if ns[i].get('_invisible', False):
            del ns[i]
        else:
            remove_invisible(ns[i].getchildren())

def copy(n):
    m = El(n.tag, n.text, **dict(n.items()))

    for c in n.getchildren():
        m.append(copy(c))

    return m

def parse_m(s, required=False):
    s = s.strip()

    if s == '':
        return '', El('mi', u'\u25a1') if required else None

    m = number_re.match(s)

    if m:
        number = m.group(0)
        if number[0] == '-':
            return s[m.end():], El('mrow', El('mo', '-'), El('mn', number[1:]))
        else:
            return s[m.end():], El('mn', number)

    for y in symbol_names:
        if s.startswith(y):
            n = copy(symbols[y])

            if n.get('_space', False):
                n = El('mrow',
                        El('mspace', width='1ex'),
                        n,
                        El('mspace', width='1ex'))

            return s[len(y):], n

    return s[1:], El('mi' if s[0].isalpha() else 'mo', s[0])

symbols = {}

def Symbol(input, el):
    symbols[input] = el

Symbol(input="alpha",  el=El("mi", u"\u03B1"))
Symbol(input="beta",  el=El("mi", u"\u03B2"))
Symbol(input="chi",    el=El("mi", u"\u03C7"))
Symbol(input="delta",  el=El("mi", u"\u03B4"))
Symbol(input="Delta",  el=El("mo", u"\u0394"))
Symbol(input="epsi",   el=El("mi", u"\u03B5"))
Symbol(input="varepsilon", el=El("mi", u"\u025B"))
Symbol(input="eta",    el=El("mi", u"\u03B7"))
Symbol(input="gamma",  el=El("mi", u"\u03B3"))
Symbol(input="Gamma",  el=El("mo", u"\u0393"))
Symbol(input="iota",   el=El("mi", u"\u03B9"))
Symbol(input="kappa",  el=El("mi", u"\u03BA"))
Symbol(input="lambda", el=El("mi", u"\u03BB"))
Symbol(input="Lambda", el=El("mo", u"\u039B"))
Symbol(input="mu",     el=El("mi", u"\u03BC"))
Symbol(input="nu",     el=El("mi", u"\u03BD"))
Symbol(input="omega",  el=El("mi", u"\u03C9"))
Symbol(input="Omega",  el=El("mo", u"\u03A9"))
Symbol(input="phi",    el=El("mi", u"\u03C6"))
Symbol(input="varphi", el=El("mi", u"\u03D5"))
Symbol(input="Phi",    el=El("mo", u"\u03A6"))
Symbol(input="pi",     el=El("mi", u"\u03C0"))
Symbol(input="Pi",     el=El("mo", u"\u03A0"))
Symbol(input="psi",    el=El("mi", u"\u03C8"))
Symbol(input="Psi",    el=El("mi", u"\u03A8"))
Symbol(input="rho",    el=El("mi", u"\u03C1"))
Symbol(input="sigma",  el=El("mi", u"\u03C3"))
Symbol(input="Sigma",  el=El("mo", u"\u03A3"))
Symbol(input="tau",    el=El("mi", u"\u03C4"))
Symbol(input="theta",  el=El("mi", u"\u03B8"))
Symbol(input="vartheta", el=El("mi", u"\u03D1"))
Symbol(input="Theta",  el=El("mo", u"\u0398"))
Symbol(input="upsilon", el=El("mi", u"\u03C5"))
Symbol(input="xi",     el=El("mi", u"\u03BE"))
Symbol(input="Xi",     el=El("mo", u"\u039E"))
Symbol(input="zeta",   el=El("mi", u"\u03B6"))

Symbol(input="*",  el=El("mo", u"\u22C5"))
Symbol(input="**", el=El("mo", u"\u22C6"))

Symbol(input="/", el=El("mo", u"/", _special_binary=frac))
Symbol(input="^", el=El("mo", u"^", _special_binary=sup))
Symbol(input="_", el=El("mo", u"_", _special_binary=sub))
Symbol(input="//", el=El("mo", u"/"))
Symbol(input="\\\\", el=El("mo", u"\\"))
Symbol(input="setminus", el=El("mo", u"\\"))
Symbol(input="xx", el=El("mo", u"\u00D7"))
Symbol(input="-:", el=El("mo", u"\u00F7"))
Symbol(input="@",  el=El("mo", u"\u2218"))
Symbol(input="o+", el=El("mo", u"\u2295"))
Symbol(input="ox", el=El("mo", u"\u2297"))
Symbol(input="o.", el=El("mo", u"\u2299"))
Symbol(input="sum", el=El("mo", u"\u2211", _underover=True))
Symbol(input="prod", el=El("mo", u"\u220F", _underover=True))
Symbol(input="^^",  el=El("mo", u"\u2227"))
Symbol(input="^^^", el=El("mo", u"\u22C0", _underover=True))
Symbol(input="vv",  el=El("mo", u"\u2228"))
Symbol(input="vvv", el=El("mo", u"\u22C1", _underover=True))
Symbol(input="nn",  el=El("mo", u"\u2229"))
Symbol(input="nnn", el=El("mo", u"\u22C2", _underover=True))
Symbol(input="uu",  el=El("mo", u"\u222A"))
Symbol(input="uuu", el=El("mo", u"\u22C3", _underover=True))

Symbol(input="!=",  el=El("mo", u"\u2260"))
Symbol(input=":=",  el=El("mo", u":="))
Symbol(input="lt",  el=El("mo", u"<"))
Symbol(input="<=",  el=El("mo", u"\u2264"))
Symbol(input="lt=", el=El("mo", u"\u2264"))
Symbol(input=">=",  el=El("mo", u"\u2265"))
Symbol(input="geq", el=El("mo", u"\u2265"))
Symbol(input="-<",  el=El("mo", u"\u227A"))
Symbol(input="-lt", el=El("mo", u"\u227A"))
Symbol(input=">-",  el=El("mo", u"\u227B"))
Symbol(input="-<=", el=El("mo", u"\u2AAF"))
Symbol(input=">-=", el=El("mo", u"\u2AB0"))
Symbol(input="in",  el=El("mo", u"\u2208"))
Symbol(input="!in", el=El("mo", u"\u2209"))
Symbol(input="sub", el=El("mo", u"\u2282"))
Symbol(input="sup", el=El("mo", u"\u2283"))
Symbol(input="sube", el=El("mo", u"\u2286"))
Symbol(input="supe", el=El("mo", u"\u2287"))
Symbol(input="-=",  el=El("mo", u"\u2261"))
Symbol(input="~=",  el=El("mo", u"\u2245"))
Symbol(input="~~",  el=El("mo", u"\u2248"))
Symbol(input="prop", el=El("mo", u"\u221D"))

Symbol(input="and", el=El("mtext", u"and", _space=True))
Symbol(input="or",  el=El("mtext", u"or", _space=True))
Symbol(input="not", el=El("mo", u"\u00AC"))
Symbol(input="=>",  el=El("mo", u"\u21D2"))
Symbol(input="if",  el=El("mo", u"if", _space=True))
Symbol(input="<=>", el=El("mo", u"\u21D4"))
Symbol(input="AA",  el=El("mo", u"\u2200"))
Symbol(input="EE",  el=El("mo", u"\u2203"))
Symbol(input="_|_", el=El("mo", u"\u22A5"))
Symbol(input="TT",  el=El("mo", u"\u22A4"))
Symbol(input="|--",  el=El("mo", u"\u22A2"))
Symbol(input="|==",  el=El("mo", u"\u22A8"))

Symbol(input="(",  el=El("mo", "(", _opening=True))
Symbol(input=")",  el=El("mo", ")", _closing=True))
Symbol(input="[",  el=El("mo", "[", _opening=True))
Symbol(input="]",  el=El("mo", "]", _closing=True))
Symbol(input="{",  el=El("mo", "{", _opening=True))
Symbol(input="}",  el=El("mo", "}", _closing=True))
Symbol(input="|", el=El("mo", u"|", _opening=True, _closing=True))
Symbol(input="(:", el=El("mo", u"\u2329", _opening=True))
Symbol(input=":)", el=El("mo", u"\u232A", _closing=True))
Symbol(input="<<", el=El("mo", u"\u2329", _opening=True))
Symbol(input=">>", el=El("mo", u"\u232A", _closing=True))
Symbol(input="{:", el=El("mo", u"{:", _opening=True, _invisible=True))
Symbol(input=":}", el=El("mo", u":}", _closing=True, _invisible=True))

Symbol(input="int",  el=El("mo", u"\u222B"))
# Symbol(input="dx",   el=El("mi", u"{:d x:}", _definition=True))
# Symbol(input="dy",   el=El("mi", u"{:d y:}", _definition=True))
# Symbol(input="dz",   el=El("mi", u"{:d z:}", _definition=True))
# Symbol(input="dt",   el=El("mi", u"{:d t:}", _definition=True))
Symbol(input="oint", el=El("mo", u"\u222E"))
Symbol(input="del",  el=El("mo", u"\u2202"))
Symbol(input="grad", el=El("mo", u"\u2207"))
Symbol(input="+-",   el=El("mo", u"\u00B1"))
Symbol(input="O/",   el=El("mo", u"\u2205"))
Symbol(input="oo",   el=El("mo", u"\u221E"))
Symbol(input="aleph", el=El("mo", u"\u2135"))
Symbol(input="...",  el=El("mo", u"..."))
Symbol(input=":.",  el=El("mo", u"\u2234"))
Symbol(input="/_",  el=El("mo", u"\u2220"))
Symbol(input="\\ ",  el=El("mo", u"\u00A0"))
Symbol(input="quad", el=El("mo", u"\u00A0\u00A0"))
Symbol(input="qquad", el=El("mo", u"\u00A0\u00A0\u00A0\u00A0"))
Symbol(input="cdots", el=El("mo", u"\u22EF"))
Symbol(input="vdots", el=El("mo", u"\u22EE"))
Symbol(input="ddots", el=El("mo", u"\u22F1"))
Symbol(input="diamond", el=El("mo", u"\u22C4"))
Symbol(input="square", el=El("mo", u"\u25A1"))
Symbol(input="|__", el=El("mo", u"\u230A"))
Symbol(input="__|", el=El("mo", u"\u230B"))
Symbol(input="|~", el=El("mo", u"\u2308"))
Symbol(input="~|", el=El("mo", u"\u2309"))
Symbol(input="CC",  el=El("mo", u"\u2102"))
Symbol(input="NN",  el=El("mo", u"\u2115"))
Symbol(input="QQ",  el=El("mo", u"\u211A"))
Symbol(input="RR",  el=El("mo", u"\u211D"))
Symbol(input="ZZ",  el=El("mo", u"\u2124"))
Symbol(input="f",   el=El("mi", u"f", _func=True)) # sample
Symbol(input="g",   el=El("mi", u"g", _func=True))

Symbol(input="lim",  el=El("mo", u"lim", _underover=True))
Symbol(input="Lim",  el=El("mo", u"Lim", _underover=True))
Symbol(input="sin",  el=El("mrow", El("mo", "sin"), _arity=1))
Symbol(input="sin",  el=El("mrow", El("mo", "sin"), _arity=1))
Symbol(input="cos",  el=El("mrow", El("mo", "cos"), _arity=1))
Symbol(input="tan",  el=El("mrow", El("mo", "tan"), _arity=1))
Symbol(input="sinh", el=El("mrow", El("mo", "sinh"), _arity=1))
Symbol(input="cosh", el=El("mrow", El("mo", "cosh"), _arity=1))
Symbol(input="tanh", el=El("mrow", El("mo", "tanh"), _arity=1))
Symbol(input="cot",  el=El("mrow", El("mo", "cot"), _arity=1))
Symbol(input="sec",  el=El("mrow", El("mo", "sec"), _arity=1))
Symbol(input="csc",  el=El("mrow", El("mo", "csc"), _arity=1))
Symbol(input="log",  el=El("mrow", El("mo", "log"), _arity=1))
Symbol(input="ln",   el=El("mrow", El("mo", "ln"), _arity=1))
Symbol(input="det",  el=El("mrow", El("mo", "det"), _arity=1))
Symbol(input="gcd",  el=El("mrow", El("mo", "gcd"), _arity=1))
Symbol(input="lcm",  el=El("mrow", El("mo", "lcm"), _arity=1))
Symbol(input="dim",  el=El("mo", u"dim"))
Symbol(input="mod",  el=El("mo", u"mod"))
Symbol(input="lub",  el=El("mo", u"lub"))
Symbol(input="glb",  el=El("mo", u"glb"))
Symbol(input="min",  el=El("mo", u"min", _underover=True))
Symbol(input="max",  el=El("mo", u"max", _underover=True))

Symbol(input="uarr", el=El("mo", u"\u2191"))
Symbol(input="darr", el=El("mo", u"\u2193"))
Symbol(input="rarr", el=El("mo", u"\u2192"))
Symbol(input="->",   el=El("mo", u"\u2192"))
Symbol(input="|->",  el=El("mo", u"\u21A6"))
Symbol(input="larr", el=El("mo", u"\u2190"))
Symbol(input="harr", el=El("mo", u"\u2194"))
Symbol(input="rArr", el=El("mo", u"\u21D2"))
Symbol(input="lArr", el=El("mo", u"\u21D0"))
Symbol(input="hArr", el=El("mo", u"\u21D4"))

Symbol(input="hat", el=El("mover", El("mo", u"\u005E"), _arity=1, _swap=1))
Symbol(input="bar", el=El("mover", El("mo", u"\u00AF"), _arity=1, _swap=1))
Symbol(input="vec", el=El("mover", El("mo", u"\u2192"), _arity=1, _swap=1))
Symbol(input="dot", el=El("mover", El("mo", u"."), _arity=1, _swap=1))
Symbol(input="ddot",el=El("mover", El("mo", u".."), _arity=1, _swap=1))
Symbol(input="ul", el=El("munder", El("mo", u"\u0332"), _arity=1, _swap=1))

Symbol(input="sqrt", el=El("msqrt", _arity=1))
Symbol(input="root", el=El("mroot", _arity=2, _swap=True))
Symbol(input="frac", el=El("mfrac", _arity=2))
Symbol(input="stackrel", el=El("mover", _arity=2))

Symbol(input="text", el=El("mtext", _arity=1))

symbol_names = sorted(symbols.keys(), key=lambda s: len(s), reverse=True)

def substitution(match):
    return tostring(parse(match.group(1)))

def cb_postformat(request):
    
    entry = request['entry']
    entry['body'] = re.sub(r'\$\$([^\$]*)\$\$', substitution, entry['body'])
    return request