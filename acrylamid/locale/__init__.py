# -*- encoding: utf-8 -*-
#
# Copyright 2013 Martin Zimmermann <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses -- see LICENSE.

import re
import locale
import difflib
import gettext
import contextlib

from os.path import dirname
from acrylamid import log

translations = None
available = ['ach', 'ca', 'de', 'el', 'en', 'es', 'fa', 'fr', 'hr', 'it', 'ja',
             'pl', 'pt_BR', 'ru', 'tr_TR', 'zh_CN']


def guess(lang):
    """Guess language code.  If :param:`lang` matches C lib encoding names (see
    cpython/Lib/locale.py:locale_alias (derieved from X.org). If not, search
    for locale aliases and fallback to `C` (but show similar matches)."""

    if re.match(r'^[a-z]{2,}_[A-Z]{2,}\.[^.]+$', lang):
        return str(lang)  # str because of Python 2.X (XXX not sure about 3.X)

    try:
        return locale.locale_alias[lang.lower()]
    except KeyError:
        log.warn('no such locale %s, falling back to C. Maybe you meant %s?', lang,
            ', '.join(difflib.get_close_matches(lang, locale.locale_alias)))
        return 'C'


def setlocale(lang):
    """Try to set language to :param:`lang`, if succeded, use it and return
    the language name again, but only the first two letters (except for `C`)."""

    lang = str(guess(lang))

    try:
        locale.setlocale(locale.LC_ALL, lang)
    except (locale.Error, TypeError):
        # lang is not available, use system's default
        try:
            locale.setlocale(locale.LC_ALL, '')
        except locale.Error:
            pass  # hope this makes Travis happy
        log.info('notice  your OS does not support %s, fallback to %s', lang, locale.getlocale()[0])

    if locale.getlocale()[0] is not None:
        lang = locale.getlocale()[0]
        if lang not in available:
            lang = lang.split('_')[0]
    else:
        # getlocale() is (None, None) aka 'C'
        lang = 'en'

    global translations
    if translations is None:
        translations = gettext.translation('nikola', dirname(__file__), languages=[lang])

    return lang


@contextlib.contextmanager
def context(lang):
    tmp = '.'.join(locale.getlocale(locale.LC_ALL))
    locale.setlocale(locale.LC_ALL, guess(lang))
    yield
    locale.setlocale(locale.LC_ALL, tmp)
