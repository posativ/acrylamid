#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# Copyright 2011 posativ <info@posativ.org>. All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 
#    1. Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
# 
#    2. Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
# 
# The views and conclusions contained in the software and documentation are
# those of the authors and should not be interpreted as representing official
# policies, either expressed or implied, of posativ <info@posativ.org>.

VERSION = "0.1-stable"
VERSION_SPLIT = tuple(VERSION.split('-')[0].split('.'))

import sys
reload(sys); sys.setdefaultencoding('utf-8')

from lilith import Lilith
from lilith.tools import check_conf, ColorFormatter

import yaml, logging
from optparse import OptionParser, make_option

options = [
    make_option("-c", "--config-file", dest="conf", metavar="FILE",
                      help="an alternative conf to use", default="lilith.conf"),
    make_option("-l", "--layout_dir", dest="layout", metavar="DIR",
                      help="force overwrite", default=False),
    make_option("-q", "--quit", action="store_const", dest="verbose",
                      help="be silent (mostly)", const=logging.WARN,
                      default=logging.INFO),
    make_option("--debug", action="store_const", dest="verbose",
                      help="debug information", const=logging.DEBUG)
    ]
    
if __name__ == '__main__':
    
    parser = OptionParser(option_list=options)
    (options, args) = parser.parse_args()
    
    console = logging.StreamHandler()
    console.setFormatter(ColorFormatter('[%(levelname)s] %(name)s.py: %(message)s'))
    if options.verbose == logging.DEBUG:
        fmt = '%(msecs)d [%(levelname)s] %(name)s.py:%(lineno)s:%(funcName)s %(message)s'
        console.setFormatter(ColorFormatter(fmt))
    log = logging.getLogger('lilith')
    log.addHandler(console)
    log.setLevel(options.verbose)
        
    conf = yaml.load(open(options.conf).read())
    if options.layout:
        conf['layout_dir'] = options.layout
    assert check_conf(conf)
    
    l = Lilith(conf=conf, env={'VERSION': VERSION, 'VERSION_SPLIT': VERSION_SPLIT},
               data={})
    l.run()
