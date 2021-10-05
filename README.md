# PyRetroPrint

![PyRetroPrint, Your Atari Print Button!](https://raw.githubusercontent.com/rubeon/pyretroprint/main/docs/px/doc2pdf.png)

Welcome to PyRetroPrint, your one-stop shop for Reagan-era hardcopy!

## Introduction

Retro-printing emulation in python!

This utility is designed be used in a printing pipeline from obsolete
software.  Anything that is equipped to print to an Epson FX-80 IBM
Proprinter, or HP Laserjet I or II can now use your modern CUPS-supported
printer, or simply output PDF documents.

For applications that support Atari 825, FX-80 and Compatibles, you can:

* Render PRN files or streams to PDF
* Print formatted text to the terminal
* Send PDF output to networked printers
* Be used as a pipe for [AtariSIO][asio]'s `atariserver`
* Print directly from Atari 800XL to e.g. CUPS-compatible printers

## Installation

PyRetroPrint can be installed using [pip][pip]:
```bash
	pip install pyretroprint
```

For development versions (recommended):

```bash
	python3 -mvenv prptest
	cd prptest
	. bin/activate
	pip install cairo
	pip install -i https://test.pypi.org/simple/ pyretroprint
```

## How to Use

Once the software is installed, simply pipe output of your prints to the
main script:

```bash
	|pyretroprint -p pdf -o /tmp/myretroprint.pdf
```

`--input` or `-i`, specifies the source PRN file (defaults to `stdin`).

`--size` or `-s`, sets A4 or Letter sizes, defaults to A4.

`--printer` or `-P` will tell PyRetroPrint which printer type to emulate.

`--presenter` or `-p` determines which output type to use: `pdf` or `terminal`
which prints formatted text to the terminal (default).

`--output` or `-o`, specifies the destination file (defaults to
`default.pdf` for PDF, or `stdout` for terminal).

## Philosophy

We think you should be able boot your Atari 800 XL, start
[AtariWriter+][awplus] and type in your document, hit print, and walk over
to your networked laser printer and pick up your beautiful, monospaced
hard-copy.

The same goes for your old term paper, your 80s diary, or anything else you
might have on a computer or piece of software specced out before 1990.

[awplus]:https://www.atarimagazines.com/compute/issue72/review_atariwriter_plus.php
[pip]:https://pypi.org/
[asio]:https://github.com/HiassofT/AtariSIO
