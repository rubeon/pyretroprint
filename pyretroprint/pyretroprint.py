"""
Main file for pyretroprint
"""
import sys
import argparse
import io
import logging

from pyretroprint.epsonfx import EpsonProcessor
# from pyretroprint.ibm import ProprinterProcessor
from pyretroprint.atari import AtariProcessor
from pyretroprint.presenter import PdfPresenter
from pyretroprint.presenter import PlainTextPresenter

LOGGER = logging.getLogger(__name__)

class PrintOutFile:
    """
    Context manager for handling output files
    """
    filename = None
    file = None
    def __init__(self, printfile):
        """
        setup
        """
        # if this is buffered writer, return it
        LOGGER.debug("printoutfile: __init__ called (%s)", printfile)
        if isinstance(printfile, io.BufferedWriter) or printfile is None:
            LOGGER.debug("printoutfile: Detected io.BufferedWriter")
            self.file = sys.stdout.buffer
        # if it's a pathlike, return binary handle
        elif isinstance(printfile, str):
            LOGGER.debug("printoutfile: Detected filename")
            self.filename = printfile
        else:
            LOGGER.debug("printoutfile: Couldn't detect filetype")
            self.file = sys.stdout.buffer

    def __enter__(self):
        """
        called when context manager started
        """
        LOGGER.debug("printoutfile: __enter__ called (%s)", self.file)
        if self.filename:
            self.file = open(self.filename, 'wb')
        return self.file

    def __exit__(self, exc_type, exc_val, exc_tb):
        LOGGER.debug("printoutfile: exc_type %s", exc_type)

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

    fdoutput = sys.stdout.buffer

    if args.output:
        if args.output == "-":
            pass
        else:
            fdoutput = args.output
    LOGGER.debug("main::Using output %s", fdoutput)
    if args.input:
        fdinput = args.input
    else:
        fdinput = 0 # stdin

    if args.presenter.lower()=="pdf":
        LOGGER.debug("prp::using pdf")
        pres = PdfPresenter
    else:
        pres = PlainTextPresenter

    with open(fdinput, 'rb') as infile, PrintOutFile(args.output) as outfile:
        processor = proc(infile, pres(size=args.size, fdout=outfile))
        processor.process()
        print(processor.presenter)


if __name__=="__main__":
    main()
