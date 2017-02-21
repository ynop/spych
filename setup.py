from setuptools import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(name='spych',
      version='0.1',
      description='Spych is a set of tools for tasks related to automatic speech recognition.',
      url='http://github.com/ynop/spych',
      author='Matthias Buechi',
      author_email='m.buechi@outlook.com',
      classifiers=[
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3 :: Only',
          'Topic :: Scientific/Engineering :: Human Machine Interfaces'
      ],
      keywords='utterance kaldi lexicon asr voxforge fst srgs pronunciation speech recognition jsgf phone synthesis',
      license='MIT',
      packages=['spych'],
      install_requires=required,
      include_package_data=True,
      zip_safe=False,
      test_suite='nose.collector',
      tests_require=['nose'],
      entry_points={
          'console_scripts': ['spych=spych.cli.main:run', 'nspych=spych.ncli.main:run'],
      }
      )
