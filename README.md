# PyRetroPrint

Welcome to PyRetroPrint, your one-stop shop for Reagan-era hardcopy!

## Introduction

Retro-printing emulation in python!

This utility is designed be used in a printing pipeline from obsolete
software.  Anything that is equipped to print to an Epson FX-80 IBM
Proprinter, or HP Laserjet I or II can now use your modern CUPS-supported
printer, or simply output PDF documents.

## Installation

PyRetroPrint can be installed using [pip][pip]:
```bash
	pip install pyretroprint
```

## How to Use

Once the software is installed, simply pipe output of your prints to the
main script:

```bash
	|pyretroprint --default-printer epson --prettify
```

`--default-printer` will tell PyRetroPrint which printer to use if
autodetect fails.

`--prettify` will try to replace single- and double- quotes and other
characters with typographically attractive replacements.

## Philosophy

We think you should be able boot your Atari 800 XL, start
[AtariWriter+][awplus] and type in your document, hit print, and walk over
to your networked laser printer and pick up your beautiful, monospaced
hard-copy.

The same goes for your old term paper, your 80s diary, or anything else you
might have on a computer or piece of software specced out before 1990.

[awplus]:https://www.atarimagazines.com/compute/issue72/review_atariwriter_plus.php
[pip]:https://pypi.org/
