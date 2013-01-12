#!/usr/bin/env python

from __future__ import unicode_literals

import sys
import os
import io
import json


def find(node):

    if len(node) == 2:
        yield node[1]

    for key in node[0]:
        find(node[0][key])


def search(needle, haystack):

    if needle[0] not in haystack:
        return False

    node = haystack[needle[0]]
    needle = needle[1:]
    i, j = 0, 0

    while j < len(needle):

        if needle[i:j+1] in node[0]:
            node = node[0][needle[i:j+1]]
            i = j + 1

        j += 1

    if i != j:
        return False

    if len(node) == 2:
        print 'exact match:', node[1]

    rest = []
    for key in node[0]:
        rest.append(list(find(node[0][key])))
    print 'partial match:', sum(sum(rest, []), [])


if __name__ == '__main__':

    if len(sys.argv) < 3:
        print 'usage: %s /path/to/[a-z].js keyword' % sys.argv[0]
        sys.exit(1)

    with io.open(sys.argv[1]) as fp:
        tree = {os.path.basename(sys.argv[1])[0]: json.load(fp)}

    search(sys.argv[2].decode('utf-8'), tree)
