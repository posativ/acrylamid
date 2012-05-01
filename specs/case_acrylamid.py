# -*- coding: utf-8 -*-

import os
import shutil
import subprocess
import tempfile

from os.path import join, isfile

describe "Acrylamid's basic CLI":

    before all:
        self.path = tempfile.mkdtemp(dir='.')
        subprocess.check_call(['acrylamid', 'init', '-q', self.path])
        os.chdir(self.path)

    it 'can restore a deleted stylesheet':

        os.remove('output/style.css')
        subprocess.check_call(['acrylamid', 'init', '-fq', 'output/style.css'])

        assert isfile('conf.py')
        assert isfile(join('output/', 'style.css'))

    it 'can compile':

        subprocess.check_call(['acrylamid', 'compile', '-q'])
        subprocess.check_call(['acrylamid', 'compile', '-fq'])

    it 'cleans only untracked files':

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
        assert count('output/') == x

        # --dry-run shoul NOT touch anything
        os.remove('content/sample-entry.txt')
        subprocess.check_call(['acrylamid', 'compile', '-q'])
        subprocess.check_call(['acrylamid', 'clean', '-nq'])
        assert count('output/') == x

        subprocess.check_call(['acrylamid', 'clean', '-q'])
        assert count('output/') != x

    after all:
        os.chdir('../')
        shutil.rmtree(self.path)
