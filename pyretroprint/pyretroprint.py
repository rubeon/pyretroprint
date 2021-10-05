#!/usr/bin/env python3

import sys
import argparse

import pyretroprint.page as page
import pyretroprint.epsonfx as epsonfx


"""
TODO:
put the front-end in here.

Command line arguments to add:

    --printer |-P epson
    --presenter | -p <terminal | pdf >
    [--output | -o <filename | -]
  
For now, run the esponfx.py script directly and it will create a PDF
of your PRN file called "default.pdf"  
  
"""

def main():
        
    verbose = False
    
    parser = argparse.ArgumentParser(description='Process old-school printer jobs')
    
    parser.add_argument("-v", "--verbose", help="increase output verbosity",
                        action="store_true")
    parser.add_argument("--presenter", "-p", help="name of target output, currently plaintext or pdf", default="terminal")
    parser.add_argument("--size", "-s", help="Page size for output, a4 or letter", default="Letter")
    parser.add_argument("--printer", "-P", help="Default printer type to emulate: epson, atari, or ibm", default="epson")
    parser.add_argument("--output", "-o", help="Output file, defaults to stdout")
    parser.add_argument("--input", "-i", help="Input file, defaults to stdin")
    
    args = parser.parse_args()    

    if args.output:
        if args.output == "-":
            fdout = sys.stdout.buffer
        else:
            fdout = open(args.output, "wb")
    else:
        fdout = sys.stdout.buffer

    if args.input:
        fdin = open(args.input, 'rb')
    else:
        fdin = open(0, 'rb') # stdin
    
    # outfile = args.output or 'default.pdf'
    
    
    if args.printer.lower() == "epson":
        from pyretroprint.epsonfx import EpsonProcessor as proc
    elif args.printer.lower() == "ibm":
        from pyretroprint.ibm import ProprinterProcessor as proc
    elif args.printer.lower() == "atari":
        from pyretroprint.atari import AtariProcessor as proc
    else:
        sys.stderr.write("No known printer detected. Try 'epson' or 'ibm'")
        # usage()
        sys.exit(127)
    
    if args.presenter.lower()=="pdf":
        from pyretroprint.presenter import PdfPresenter as pres
    else:
        from pyretroprint.presenter import PlainTextPresenter as pres
    
    # get down on it
    
    p = proc(fdin, pres(size=args.size, fdout=fdout))
    p.process()
if __name__=="__main__":
    main()
    