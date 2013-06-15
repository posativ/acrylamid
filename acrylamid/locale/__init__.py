# -*- encoding: utf-8 -*-
#
# Copyright 2013 Martin Zimmermann <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses -- see LICENSE.

import locale
import gettext
import contextlib

from os.path import dirname
from acrylamid import log

translations = None
available = ['ach', 'ca', 'de', 'el', 'en', 'es', 'fa', 'fr', 'hr', 'it', 'ja',
             'pl', 'pt_BR', 'ru', 'tr_TR', 'zh_CN']


def setlocale(lang):
    """Try to set language to :param:`lang`, if succeded, use it and return
    the language name again (may differ depending on system's locale aliases)."""

    # try language set in LANG, if set correctly use it
    try:
        locale.setlocale(locale.LC_ALL, lang)
    except (locale.Error, TypeError):
        # try if LANG is an alias
        try:
            locale.setlocale(locale.LC_ALL, locale.locale_alias[lang.lower()])
        except (locale.Error, KeyError):
            # LANG is not an alias, so we use system's default
            try:
                locale.setlocale(locale.LC_ALL, '')
            except locale.Error:
                pass  # hope this makes Travis happy
            log.info('notice  your OS does not support %s, fallback to %s', conf.get('lang', ''),
                     locale.getlocale()[0])

    if locale.getlocale()[0] is not None:
        # import ipdb; ipdb.set_trace()
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
    tmp = locale.getlocale(locale.LC_ALL)
    setlocale(locale.LC_ALL, lang)
    yield
    setlocale(locale.LC_ALL, tmp)
