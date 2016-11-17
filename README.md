# SPYCH

[http://spych.readthedocs.io/](http://spych.readthedocs.io/)

Spych is a set of tools for tasks related to automatic speech recognition.

**Python Codebase**: All functions are usable with python.

**CLI**: The most used functions are accessible via command line interface. The command line interface is described in chapter :ref:`section_usage`.

## Functionality

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

## Requirements

Spych runs with **python3** and needs the following packages:

   * modgrammar
   * beautifulsoup4
   * requests
   * cement (for the CLI)