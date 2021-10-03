#!/usr/bin/env python3

import sys
import argparse

import page
import epsonfx


"""
TODO:
put the front-end in here.

Command line arguments to add:

    --printer |-P epson
    --presenter | -p <tty | pdf | html>
    [--output | -o] <filename | ->
  
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
    parser.add_argument("--printer", "-P", help="Default printer type to emulate, epson or ibm", default="epson")
    parser.add_argument("--output", "-o", help="Output file, defaults to 'default.pdf' for PDF, or stdout otherwise")
    parser.add_argument("--input", "-i", help="Input file, defaults to stdin")
    
    args = parser.parse_args()    
    print("Verbose:", args.verbose)
    print("Printer:", args.printer)
    print("Size:", args.size)
    print("Presenter", args.presenter)

    if args.output:
        fdout = open(args.output, "wb")
    else:
        fdout = sys.stdout

    if args.input:
        fdin = open(args.input, 'rb')
    else:
        fdin = open(0, 'rb') # stdin
    outfile = args.output or 'default.pdf'
    
    
    if args.printer.lower() == "epson":
        from epsonfx import EpsonProcessor as proc
    elif args.printer.lower() == "ibm":
        from ibm import ProprinterProcessor as proc
    else:
        sys.stderr.write("No known printer detected. Try 'epson' or 'ibm'")
        # usage()
        sys.exit(127)
    
    if args.presenter.lower()=="pdf":
        from presenter import PdfPresenter as pres
    else:
        from presenter import PlainTextPresenter as pres
    
    # get down on it
    
    p = proc(fdin, pres(size=args.size, filename=outfile))
    p.process()
if __name__=="__main__":
    main()
    