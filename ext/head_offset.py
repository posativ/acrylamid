# -*- coding: utf-8 -*-
from re import sub

def h(input):
    '''will return html with all headers increased by 1'''

    def f(m):
        l = lambda i: i if i not in [str(x) for x in range(1, 6)] else str(int(i)+1) if int(i) < 5 else '6'
        return ''.join([l(i) for i in m.groups()])

    return sub('(<h)(\d)(>)(.+)(</h)(\d)(>)', f, input)

def cb_prepare(request):

    config = request._config
    data = request._data
    
    t = data.get('type', 'item')
    
    for i, entry in enumerate(data['entry_list']):
        
        if t in ['item', 'page']:
            data['entry_list'][i]['body'] = h(entry['body'])
        elif t == 'feed':
            data['entry_list'][i]['body'] = h(h(entry['body']))
            
    return request