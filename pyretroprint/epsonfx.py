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
    dot_density = {
        0: {
            "hdpi": 60,
            "vdpi": 72,
            "adj": True,
            "vres": 8 
        },
        1: {
            "hdpi": 120,
            "vdpi": 72,
            "adj": True,
            "vres": 8 
        },
        2: {
            "hdpi": 120,
            "vdpi": 72,
            "adj": False,
            "vres": 8 
        },
        3: {
            "hdpi": 240,
            "vdpi": 72,
            "adj": False,
            "vres": 8 
        },
        4: {
            "hdpi": 80,
            "vdpi": 72,
            "adj": True,
            "vres": 8 
        },
        5: {
            "hdpi": 72,
            "vdpi": 72,
            "adj": True,
            "vres": 8 
        },
        6: {
            "hdpi": 90,
            "vdpi": 72,
            "adj": True,
            "vres": 8 
        },
        7: {
            "hdpi": 144,
            "vdpi": 72,
            "adj": True,
            "vres": 8 
        },
        33: {
            "hdpi": 120,
            "vdpi": 180,
            "adj": True,
            "vres": 24 
        }
    }
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
        "J": 1,
        "K": "NLDK",
        "L": "NLDK",
        "Y": "NLDK",
        "Z": "NLDK",
        "*": "MNLDK",
        "A": 1,
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
        elif command == "A":
            msg = "Set n/72-inch line spacing"
            self.set_linespacing(params[0], 72)
            return
        elif command == "Y":
            msg = "Set 120 x 72 dpi double-speed graphics" 
            # C-187, eq. ESC * 2
            self.select_bit_image(120, 60, True, 8, params)
            return
        elif command == "K":
            msg = "Select 60-dpi graphics"
            # C-183, eq. ESC * 0
            self.select_bit_image(60, 60, True, 8, params)
            return
        elif command == "L":
            msg = "Set 120 x 60 dpi graphics"
            # self.set_dpi(120, 60, params)
            self.select_bit_image(120, 60, True, 8, params)
            return
        elif command == "4":
            msg = "Set italic"
            self.set_italic(1)
            return
        elif command == "G":
            msg = "Set doublestrike"
            # disabling for now, wordperfect seems like it has a bug?
            self.set_bold(1)
            # return
        elif command == "H":
            msg = "Cancel doublestrike"
            self.set_bold(0)
            return
        elif command == "Z":
            msg = "Set 240 x 60 dpi graphics %s bytes" % (len(params)) 
            # C-189, eq. ESC * 3
            # self.set_dpi(240, 60, params)
            # logger.debug(msg)
            self.select_bit_image(240, 60, False, 8, params)
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
        elif command == "J":
            msg = "Advance print position vertically"
            self.move_v(params[0], 180) # J is 180 dpi
            return
        elif command == "*":
            msg = "Select bit image"
            mode = params[0]
            hdpi = self.dot_density[mode]["hdpi"]
            vdpi = self.dot_density[mode]["vdpi"]
            adj = self.dot_density[mode]["adj"]
            vres = self.dot_density[mode]["vres"]
            # self.select_bit_image(hdpi, vdpi, adj, vres, params[1:])
            self.select_bit_image(120, 180, True, 24, params[1:])
            return            
        else:
            msg = "ESC %s not handled" % command
        logger.debug("Not handled: ESC %s %s %s", command, params, msg)

    def move_v(self, value, dpi):
        """
        Advances the vertical print position n/216 in.
        """
        logger.debug("epson::move_v entered with %s", value)
        advance = value / dpi * 72 # value in points
        self.presenter.y = self.presenter.y + advance

    def set_page_lines(self, value):
        """
        """
        return # FIXME
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
        logger.debug("epson::set_lq entered with %s", value)
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
        logger.debug("epson::set_double_width entered with %s", value)
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
        logger.debug("epson::set_italic entered with %s", value)
        self.presenter.set_italic(value)
    
    def set_lpi(self, value):
        """
        """
        logger.debug("epson::set_lpi entered with %s", value)
        linespacing = 72.0/value  # value in points
        self.presenter.set_linespacing(linespacing)

    def draw_dot(self, x, y, width):
        """
        puts a 1-point dot on the paper at x,y
        """
        logger.debug("epson::draw_dot at %.2f, %.2fs, %s", x, y, width)
        # self.presenter.ctx.move_to(x, y)
        # self.presenter.ctx.line_to(x + dot_pitch/2, y)
        self.presenter.ctx.set_line_width(1)
        self.presenter.ctx.rectangle(x, y, width, width)
        self.presenter.ctx.stroke()
        # back to starting point
        # self.presenter.ctx.move_to(x,y)
        
    def select_bit_image(self, hdpi, vdpi, adj, vres, bytes):
        """
        hdpi = horizontal density
        vdpi = vertical density
        adj = adjacent dot printing?
        vres = dots per column, 8, 24, or 48
        """
        logger.debug("epson::select_bit_image h:%s v:%s a:%s vr:%s", hdpi, vdpi, adj, vres)
        
        advance_x = 1 / hdpi * 72       # hdpi in points
        advance_y = 1 / vdpi * 72       # vdpi in points
        
        start_x = self.presenter.x + self.presenter.page.margin_l
        start_y = self.presenter.y + self.presenter.page.margin_t
        x = start_x
        y = start_y
        logger.debug("start_x, start_y: %s,%s|dx:%s, dy:%s", start_x, start_y, advance_x, advance_y)
        
        if len(bytes):
            logger.debug("processing %s bytes", len(bytes))
            row = 0
            for b in bytes:
                gmask = int.from_bytes(b, "big")
                # need to account for multibyte.. damn
                for i in range(8):
                    128 & gmask and self.draw_dot(x, y, advance_x / 3)
                    gmask = gmask << 1 & 255
                    y = y + advance_y
                    row = row + 1
                if row >= vres-1:
                    x = x + advance_x
                    y = start_y
                    row = 0
                logger.debug("x:%.2f y:%.2f", x, y)
            
            self.presenter.x = x
            self.presenter.y = y
                
    def set_dpi(self, hdpi, vdpi, params):
        """
        Puts params[] bytes onto page at value DPI
        TODO: this should be renamed to print bitmap
        or similar
        """
        # not really relevant on a virtual printer...
        logger.debug("epson::set_dpi entered with %sx%s (%s bytes)",hdpi, vdpi, len(params))
        advance_x = 1 / hdpi * 72
        advance_y = 1 / vdpi * 72
        start_x = self.presenter.x + self.presenter.page.margin_l
        start_y = self.presenter.y + self.presenter.page.margin_t
        x = start_x
        y = start_y
        logger.debug("start_x, start_y: %s,%s|dx:%s, dy:%s", start_x, start_y, advance_x, advance_y)
        mask = 0
                
        if len(params):
            logger.debug("processing %s params", len(params))
            row = 0 # row
            col = 0 # col
            for p in params:
                # process each byte
                gmask = int.from_bytes(p, "big")

                for i in range(8):
                    # logger.debug("x:{:.2f} y:{:.2f} byte: 0b{:08b} ({})".format(x, y, gmask, gmask))
                    128 & gmask and self.draw_dot(x, y, advance_x / 2)
                    gmask = gmask << 1 & 255 # keep it at 8 bits
                    y = y + 0.9

                x = x + advance_x
                y = start_y
                logger.debug("row:%s, x:%.2f", row, x)
                    
        # save position
        self.presenter.x = x
        self.presenter.y = y            

    def set_bold(self, value):
        """
        """
        logger.debug("epson::set_bold entered with %s", value)
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
                
                while count and count not in  ["NLDK", "MNLDK"]:
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
                elif count in ["NLDK","MNLDK"]:
                    logger.debug("(M)NLDK %s", byte)
                    
                    params = []
                    if count == "MNLDK":
                        params.append(int.from_bytes(self.printfile.read(1), "big")) # m
                    nL = int.from_bytes(self.printfile.read(1), "big") # 
                    logger.debug("nL:%s", nL)
                    nH = int.from_bytes(self.printfile.read(1), "big")
                    logger.debug("nH:%s", nH)
                    graphcols = nH * 256 + nL
                    
                    logger.debug("graphcols: %s", graphcols)
                    # following are nH * 256 + nL columns
                    # so guess each column is 72 dots high?
                    # that would be 9 bytes high...
                    # so the 
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
            elif byte in [b'\x9b', b'\x0a']:
                logger.debug("9b/0a encountered, linefeed")
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