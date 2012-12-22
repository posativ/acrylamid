# -*- encoding: utf-8 -*-
#
# Copyright 2012 Martin Zimmermann <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses -- see LICENSE.

from functools import partial
from itertools import imap, chain
from collections import defaultdict

from acrylamid.core import cache
from acrylamid.utils import hash

__orig_refs = None
__seen_refs = None
__entry_map = None


def load(*entries):
    """Initialize references, load previous state."""
    global __orig_refs, __seen_refs, __entry_map

    __seen_refs = defaultdict(set)
    __orig_refs = cache.memoize('references') or defaultdict(set)
    __entry_map = dict((hash(entry), entry) for entry in chain(*entries))


def save():
    """Save new references state to disk."""
    global __seen_refs
    cache.memoize('references', __seen_refs)


def modified(key, references):
    """Check whether an entry hash `key` has modified `references`. This
    function takes the return values from :func:`refernces`."""

    global __orig_refs, __entry_map

    if not references:
        return False

    if __orig_refs[key] != __seen_refs[key]:
        return True

    try:
        return any(__entry_map[ref].modified for ref in references)
    except KeyError:
        return True


def references(entry):
    """Return hash for entry and the referenced entries' hashes."""
    global __seen_refs
    return hash(entry), __seen_refs.get(hash(entry), set())


def track(func):
    """A syntactic-sugar decorator to automatically track yielded
    references from an entry. See :class:`Translation` in
    :mod:`acrylamid.views.entry` for an example."""

    def dec(entry, item):
        append(entry, item)
        return item

    return lambda entry, **kw: imap(partial(dec, entry), func(entry, **kw))


def append(entry, *references):
    """Appenf `references` to `entry`."""
    global __seen_refs

    for ref in references:
        __seen_refs[hash(entry)].add(hash(ref))
