__printer_class__="Epson FX-80"
import sys
import os
import logging

from pyretroprint.presenter import PlainTextPresenter, PdfPresenter, HtmlPresenter
import pyretroprint.page

ESCAPE = 0x1b

CODES = {
    
}

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)


class PrintFile(object):
    """
    """
    def __init__self(fd):
        """
        """
        self.fd = fd

    def read(self, bytes=1):
        next_byte = self.fd.read(bytes)

class EpsonProcessor(object):
    """
    esc/p and esc/p 2 processor
    """
    clear_on_line = []
    escape_state = None
    commands = {
        "%": {
                "params_count": 1,
                "description": "Select user-defined set"
            },
        "$": {
                "params_count": 2,
                "description": "ESC $: set abs. HPOS"
            },
        "t": 1,
        "R": 1,
        "k": 1,
        "!": 1,
        "x": 1,
        "C": 1        
        
    }
    params_count = {
        "%": 1,
        "$": 2,
        "t": 1,
        "R": 1,
        "k": 1,
        "!": 1,
        "x": 1,
        "C": 1,
        "+": 1,
        "p": 1,
        "3": 1,
        "-": 1,
        "S": 1,
        "L": "NLDK",
        "Y": "NLDK",
        "Z": "NLDK",
        "D": None, # NUL terminated
        
    }
    
    params = []
    
    defined_unit = 72.0 / 60.0 # 1 / 60 in. in points
    
    def __init__(self, pf, presenter, size="Letter"):
        """
        """
        self.printfile = pf
        self.presenter = presenter # initialized presenter
        self.initialize_printer()

    def handle_command(self, byte, params):
        """
        """
        command = byte.decode("cp850")
        msg = ""
        if command == "%":
            msg = "Select user-defined set"
        elif command == "@":
            msg = "Initialize printer"
            self.initialize_printer()
            return
        elif command == "$":
            msg = "Set abs. HPOS"
            self.set_hpos(params)
            return
        elif command == "t":
            msg = "Select character table"
        elif command =="6":
            msg = "Enable printing of upper control codes"
            self.enable_upper()
            return
        elif command =="R":
            msg = "Select an international character set"
            self.select_intl_charset(params[0])
            return
        elif command =="2":
            msg = "Select 1/6-inch line spacing"
            self.set_lpi(6)
            return
        elif command == "k":
            msg = "Select typeface"
        elif command == "!":
            msg = "Master select"
            self.master_select(params[0])
            return
        elif command == "x":
            msg = "Select LQ or Draft"
            self.set_lq(params[0])
            return
        elif command == "C":
            msg = "Set page length in lines"
            self.set_page_lines(params[0])
            return
        elif command == "+":
            msg = "Set n/360th in. line spacing"
            self.set_linespacing(params[0], 360)
            return
        elif command == "E":
            msg = "Set the weight attribute of the font to bold"
            self.set_bold(1)
            return
        elif command == "F":
            msg = "Cancel bold font"
            self.set_bold(0)
            return
        elif command == "p":
            msg = "Turn proportional off/on"
            self.set_proportional(params[0])
            return
        elif command == "T":
            msg = "Cancel super-/subscript"
            self.set_supersub(-1)
            return
            
        elif command == "P":
            msg = "Select 10.5-point, 10-cpi"
            self.set105_10cpi()
            return
        elif command == "3":
            msg = "Set n/216-inch line spacing"
            self.set_linespacing(params[0], 216)
            return
        elif command == "Y" or command == "L":
            msg = "Set 120 dpi double-speed graphics"
            self.set_dpi(120, params)
            return
        elif command == "4":
            msg = "Set italic"
            self.set_italic(1)
            return
        elif command == "G":
            msg = "Set doublestrike"
            self.set_bold(1)
            return
        elif command == "H":
            msg = "Cancel doublestrike"
            self.set_bold(0)
            return
    
        elif command == "Z":
            msg = "Set 240 dpi graphics %s bytes" % (len(params))
            self.set_dpi(240, params)
            return
        elif command == "5":
            msg = "Cancel italic"
            self.set_italic(0)
            return
        elif command == "-":
            msg = "Cancel italic"
            self.set_underline(params[0])
            return
        elif command == "D":
            msg = "Set tabs"
            self.set_tabs(params)
            return
        elif command == "S":
            msg = "Select superscript/subscript printing"
            self.set_supersub(params[0])
            return
        else:
            msg = "ESC %s not handled" % command
        logger.debug("Not handled: ESC %s %s %s", command, params, msg)

    def set_page_lines(self, value):
        """
        """
        self.page_lines = value
        self.presenter.page_lines = value

    def handle_escape(self):
        """
        """
        self.escape_state = True

    def set_tabs(self, params):
        """
        """
        logger.debug("epson::set_tabs entered")

    def set_supersub(self, value):
        """
        """
        logger.debug("epson::set_supersub entered with %s", value)
        if value in [1, 49]:
            logger.debug("epson::set_supersub setting super")
            self.presenter.superscript = True
            self.presenter.subscript = False
            return
        if value in [0, 48]:
            logger.debug("epson::set_supersub setting sub")
            self.presenter.subscript = True 
            self.presenter.superscript = False 
            return
        
        self.presenter.superscript = False            
        self.presenter.subscript = False

    def master_select(self, value):
        """
        """
        logger.debug("epson::master_select entered")
        value & 1 and  \
            self.presenter.set_font_width(7.2)  \
            or self.presenter.set_font_width(6) 
        
        self.set_proportional(value & 2)
        self.set_condensed(value & 4)
        self.set_bold(value & 8)
        self.set_bold(value & 16)
        self.set_double_width(value & 32)
        self.set_italic(value & 64)
        self.set_underline(value & 128)

    def set_lq(self, value):
        """
        """
        logger.debug("epson::set_lq entered")
        value in [0, 48] and self.presenter.set_low_quality(1)
        value in [1, 49] and self.presenter.set_low_quality(0)

    def set_condensed(self, value):
        """
        """
        logger.debug("epson::set_condensed entered with %s", value)
        self.presenter.set_condensed(value)
        
    def set105_10cpi(self):
        """
        
        """
        logger.debug("epson::set105_10cpi entered")
        # 72 points per inch, 10 CPI would be 7.2pts right?
        self.presenter.set_font_size(10.5)
        self.presenter.stretch_x = 1.0
        self.presenter.set_font_width(7.2)        
        

    def set_double_width(self, value):
        logger.debug("epson::set_double_width entered")
        if value:
            self.presenter.stretch_x = 2.0
        else:
            self.presenter.stretch_x = 1.0
    
    def set_underline(self, value):
        logger.debug("epson::set_underline entered")
        if value in [1,49]:
            self.presenter.set_underline(True)
        else:
            self.presenter.set_underline(False)
    
    def select_intl_charset(self, charset):
        """
        0 USA
        1 France
        2 Germany
        3 United Kingdom
        4 Denmark I
        5 Sweden
        6 Italy
        7 Spain I
        8 Japan (English)
        9 Norway
        10 Denmark II
        11 Spain II
        12 Latin America
        13 Korea
        64 Legal
        """
        logger.debug("epson::set_intl_charset entered")
        self.presenter.set_charset(charset)
        
    def initialize_printer(self):
        """
        """
        logger.debug("epson::initialize_printer entered")
        self.set_bold(0)
        self.set_proportional(0)
        self.set_italic(0)
        self.defined_unit = 72.0 / 60.0
        self.presenter.set_font_size(10.5)
        self.set_linespacing(1, 6)

    def enable_upper(self):
        """
        """
        logger.debug("epson::enable_upper entered")
        
    def set_proportional(self, value):
        """
        """
        logger.debug("epson::set_proportional entered w/ %s", value)
        prop = int(value) in [1,49]
        self.presenter.set_proportional(prop)

    def set_italic(self, value):
        """
        """
        logger.debug("epson::set_italic entered")
        self.presenter.set_italic(value)
    
    def set_lpi(self, value):
        """
        """
        logger.debug("epson::set_lpi entered with %s", value)
        linespacing = 72.0/value  # value in points
        self.presenter.set_linespacing(linespacing)

    def set_dpi(self, value, params):
        """
        """
        # not really relevant on a virtual printer...
        logger.debug("epson::set_dpi entered with %s", value)
        self.presenter.dpi = value
        logger.debug("%s bytes of data for %s", len(params), value)
        if len(params):
            logger.debug("%s...%s", params[0], params[-1])

    def set_bold(self, value):
        """
        """
        logger.debug("epson::set_bold entered")
        self.presenter.set_bold(value)
    
    def set_hpos(self, params):
        """
        """
        logger.debug("epson::set_hpos entered")
        
        nL = params[0]
        nH = params[1]
        
        lm = self.presenter.page.margin_l
        # lm = self.presenter.page_list[self.presenter.cur_page].margin_l
        du = self.defined_unit
        
        hpos = (((nH * 256) + nL) * du) + lm
        logger.debug("Setting hpos to %s", hpos)
        self.presenter.set_hpos(hpos)

    def set_linespacing(self, param, base):
        """
        Sets the line spacing in points on the presenter
        """
        logger.debug("epson::set_linespacing entered: %s/%s", param, base)
        n = param
        sp_inches = n / base
        logger.debug("sp_inches = %s", sp_inches)
        # self.set_lpi(sp_inches)
        self.presenter.set_linespacing(sp_inches * 72.0) # linespacing in points

    def process(self):
        """
        """
        logger.debug("epson::process entered")
        logger.debug("Processing...")
        while True:
            byte = self.printfile.read(1)
            if self.escape_state:
                params = []
                count = self.params_count.get(byte.decode("cp850"), 0)
                
                while count and count not in  ["NLDK",]:
                    params.append(int.from_bytes(self.printfile.read(1), "big"))
                    count = count - 1
                    
                if count == None:
                    # null termed parm list
                    # read params until it's NUL
                    parm = None
                    while True:
                        parm = self.printfile.read(1)
                        if parm == b'\x00':
                            break
                        params.append(parm)
                elif count == "NLDK":
                    logger.debug("NLDK %s", byte)
                    
                    params = []
                    nL = int.from_bytes(self.printfile.read(1), "big") # 
                    logger.debug("nL:%s", nL)
                    nH = int.from_bytes(self.printfile.read(1), "big") # 
                    logger.debug("nH:%s", nH)
                    graphcols = nH * 256 + nL

                    i = 0
                    quick = False # ESC Y skips every other dot (urgh)
                    this_byte = None
                    if byte in [b'Y']:
                        quick = True
                    logger.debug("q:%s graphcols:%s", quick, graphcols)
                    while i < int(graphcols):
                        # get d1..dk
                        this_byte = self.printfile.read(1)
                        params.append(this_byte)
                        i = i + 1
                    logger.debug("Got %d bytes graphics data", len(params))
                    
                self.escape_state = False
                self.handle_command(byte, params)
            elif byte == b'\x1b':
                self.handle_escape()
            elif byte == b'\x0e':
                self.set_double_width(True)
                self.clear_on_line.append(self.set_double_width)
            elif self.escape_state:
                self.escape_state = False
                self.handle_command(byte)
            elif byte == b'':
                break
            # check for some control codes
            elif byte == b'\x9b':
                self.presenter.newline()
                [f(False) for f in self.clear_on_line]
                self.clear_on_line = []
            elif byte == b'\x0f':
                logger.debug("XXX: SETTING CONDENSED")
                self.set_condensed(True)
            elif byte == b'\x12':
                self.set_condensed(False)
            else:
                self.handle_byte(byte)
 
    def handle_byte(self, byte):
        self.presenter.add_text(byte)


if __name__=="__main__":
    # getopt etc.
    printfile = open(sys.argv[-1], 'rb')
    print("Reading", sys.argv[-1])
    print("Processing for PDF")
    presenter = PdfPresenter()
    proc = EpsonProcessor(printfile, presenter, size="Letter")
    # proc = EpsonProcessor(printfile, PlainTextPresenter)
    proc.process()
    print(proc.presenter)