# -*- coding: utf-8 -*-

from acrylamid.views import tag


describe "Tags":

    it "produces a tag cloud":

        tags = {'foo': range(1), 'bar': range(2)}
        cloud = tag.Tagcloud(tags, steps=4, max_items=100, start=0)
        lst = [(t.name, t.step) for t in cloud]

        assert ('foo', 3) in lst
        assert ('bar', 0) in lst

        tags = {'foo': range(1), 'bar': range(2), 'baz': range(4), 'spam': range(8)}
        cloud = tag.Tagcloud(tags, steps=4, max_items=4, start=0)
        lst = [(t.name, t.step) for t in cloud]

        assert ('foo', 3) in lst
        assert ('bar', 2) in lst
        assert ('baz', 1) in lst
        assert ('spam', 0) in lst
