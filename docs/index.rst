.. spych documentation master file, created by
   sphinx-quickstart on Thu Nov 17 17:54:20 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to spych's documentation!
=================================

Spych is a set of tools for tasks related to automatic speech recognition.

**Python Codebase**: All functions are usable with python.

**CLI**: The most used functions are accessible via command line interface. The command line interface is described in chapter :ref:`section_usage`.

Functionality
-------------

* Dataset

  * Custom format "spych format"
  * Merging
  * Splitting
  * Validation
  * Fix

  * --> spych format

    * TUDA
    * SIWIS
    * VOXFORGE

  * spych format -->

    * Kaldi

* Lexicon

  * Read/Write
  * Merge
  * Generate

    * MaryTTS
    * CMUDict

* Grammar

  * Parse

    * JSGF

  * Serialize

    * SRGS
    * (FST)

* Synthesis

  * Batch synthesizing with config file

* Tools

  * MaryTTS Client

* Assets
* Utils


Requirements
------------

Spych runs with **python3** and needs the following packages:

   * modgrammar
   * beautifulsoup4
   * requests
   * cement (for the CLI)
   * httplib2
   * pystache


Contents
--------

.. toctree::
   :maxdepth: 2

   formats/index
   usage/index
   developer_documentation/index



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

