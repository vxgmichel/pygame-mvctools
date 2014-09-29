#!/usr/bin/env python

from setuptools import setup, find_packages
from setuptools import Command

class UploadGhPages(Command):
    '''Command to update build and upload sphinx doc to github.'''
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        # Import
        from fabric.api import local
        # Delete gh-pages branch
        try: local('git branch -D gh-pages ')
        except: pass
        # Create gh-pages branch
        local('git checkout --orphan gh-pages ')
        # Unstage all
        local('rm .git/index')
        # Build doc
        local('python setup.py build_sphinx')
        # No jekyll file
        local('touch .nojekyll')
        local('git add .nojekyll')
        # Add html content
        local('git add docs/build/html/* -f ')
        # Move html content
        local('git mv docs/build/html/* ./ ')
        # Git commit
        local('git commit -m "build sphinx" ')
        # Git push
        local('git push --set-upstream origin gh-pages -f ')
        # Back to master
        local('git checkout master -f ')


setup(name = 'pygame-mctools',
      version = '0.1.0',
      description = 'High-level set of Python modules designed for writing games',
      packages = find_packages(),
      cmdclass = {'upload_gh_pages': UploadGhPages}
     )

