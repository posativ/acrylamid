# Copyright 2011 posativ <info@posativ.org>. All rights reserved.
# License: BSD Style, 2 clauses. see lilith.py

from lilith.filters import Filter
from re import sub

class Headoffset(Filter):
    
    __name__ = 'head_offset'
    __match__ = ['h'+str(i+1) for i in range(5)]
    
    def __init__(self, **env):
        pass
        
    def __call__(self, content, request, *args):
        
        def f(m):
            '''will return html with all headers increased by 1'''
            l = lambda i: i if i not in [str(x) for x in range(1, 6)] else str(int(i)+1) if int(i) < 5 else '6'
            return ''.join([l(i) for i in m.groups()])

        offset = int(self.__matched__[1])
        
        for i in range(offset):
            content = sub('(<h)(\d)(>)(.+)(</h)(\d)(>)', f, content)

        return content