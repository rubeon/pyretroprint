"""
Main file for pyretroprint
"""
import sys
import argparse
from pyretroprint.epsonfx import EpsonProcessor
# from pyretroprint.ibm import ProprinterProcessor
from pyretroprint.atari import AtariProcessor
from pyretroprint.presenter import PdfPresenter
from pyretroprint.presenter import PlainTextPresenter

def main():
    """
    Main program logic
    """
    parser = argparse.ArgumentParser(
        description='Process old-school printer jobs'
    )
    parser.add_argument("-v", "--verbose", help="increase output verbosity",
                        action="store_true")
    parser.add_argument("--presenter", "-p",
                        help="name of target output, plaintext or pdf",
                        default="terminal")
    parser.add_argument("--size", "-s", help="Page size for output, a4 or letter",
                        default="Letter")
    parser.add_argument("--printer", "-P",
                        help="Default printer type to emulate: epson, atari, or ibm",
                        default="epson")
    parser.add_argument("--output", "-o", help="Output file, defaults to stdout")
    parser.add_argument("--input", "-i", help="Input file, defaults to stdin")

    args = parser.parse_args()

    processors = {
        "epson": EpsonProcessor,
        # "ibm": IbmProcessor,
        "atari": AtariProcessor
    }

    proc = processors.get(args.printer)
    if not proc:
        sys.stderr.write(f"Unknown printer: {args.printer}")
        sys.stderr.flush()
        sys.exit(1)

    if args.output:
        if args.output == "-":
            fdoutput = sys.stdout.buffer
        else:
            fdoutput = args.output
    else:
        fdout = sys.stdout.buffer

    if args.input:
        fdinput = args.input
    else:
        fdinput = 0 # stdin

    if args.presenter.lower()=="pdf":
        pres = PdfPresenter
    else:
        pres = PlainTextPresenter

    with open(fdinput, 'rb') as fdin, open(fdoutput, 'wb') as fdout:
        processor = proc(fdin, pres(size=args.size, fdout=fdout))
        processor.process()
if __name__=="__main__":
    main()
