# -*- coding: utf-8 -*-

import sys; reload(sys)
sys.setdefaultencoding('utf-8')

try:
    import unittest2 as unittest
except ImportError:
    import unittest # NOQA

import os
import shutil
import subprocess
import tempfile

from os.path import join, isfile


class TestUtils(unittest.TestCase):

    def setUp(self):
        self.path = tempfile.mkdtemp(dir='.')
        subprocess.check_call(['acrylamid', 'init', '-q', self.path])
        os.chdir(self.path)

    def test_init(self):
        os.remove('output/style.css')
        subprocess.check_call(['acrylamid', 'init', '-fq', 'output/style.css'])

        self.assertTrue(isfile('conf.py'))
        self.assertTrue(isfile(join('output/', 'style.css')))

    def test_compile(self):
        subprocess.check_call(['acrylamid', 'compile', '-q'])
        subprocess.check_call(['acrylamid', 'compile', '-fq'])

    def test_clean(self):

        def count(directory):

            flist = []
            for root, dirs, files in os.walk('output/'):
                for f in files:
                    flist.append(join(root, f))
            return len(flist)

        subprocess.check_call(['acrylamid', 'compile', '-q'])
        x = count('output/')

        # should NOT remove anything
        subprocess.check_call(['acrylamid', 'clean', '-q'])
        self.assertEqual(count('output/'), x)

        # --dry-run shoul NOT touch anything
        os.remove('content/sample-entry.txt')
        subprocess.check_call(['acrylamid', 'compile', '-q'])
        subprocess.check_call(['acrylamid', 'clean', '-nq'])
        self.assertEqual(count('output/'), x)

        subprocess.check_call(['acrylamid', 'clean', '-q'])
        self.assertNotEqual(count('output/'), x)

    def tearDown(self):
        os.chdir('../')
        shutil.rmtree(self.path)