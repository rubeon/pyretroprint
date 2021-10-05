import sys

import math
import cairo
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)

DEFAULT_CHARSET="cp850"

from .page import LetterPage, A4Page

"""
Thoughts:
create a document suitable for the presenter type
as you stream the print file, add elements to the 
document, presenting as it streams

Think of what a "page" is; this is relevant even 
for interactive presenters, like Terminal

Scaling is also a factor; old documents think in
terms of pages, and they don't necessarily do
things like proper form feeds. I see that with 
AtariWriter+, which seems to walk donw the page
a bit.

"""

class BasePresenter(object):
    """
    Abstract class for presenter objects
    """
    page_list = []
    default_page_size = "A4"    
    cur_page = 0
    dpi = 300
    linespacing = 12
    font_height = 8
    page_lines = None
    superscript = False
    subscript = False
    underline = False


    font_state = {
        "bold": False,
        "italic": False,
        "family": "monospace",
        "size": 10,
    }
    
    print_stream = None
    
    def __init__(self, stream, **kwargs):
        self.print_stream = stream
        

    def initalize(self):
        """
        """
        raise NotImplementedError
    

    def set_underline(self, enable):
        """
        """
        raise NotImplementedError
    
    def carriage_return(self):
        """
        """
        raise NotImplementedError

    def set_condensed(self, enable):
        """
        """
        raise NotImplementedError

    def set_font_size(self, *args):
        """
        """
        raise NotImplementedError


    def set_low_quality(self, enable):
        """
        """
        raise NotImplementedError


    def set_bold(self, value):
        """
        """
        self.bold = value
    
    def newline(self):
        """
        """
        self.carriage_return()
        self.linefeed()

    def set_italic(self, value):
        """
        """
        self.italic = value    
    def set_family(self, enable):
        raise NotImplementedError
    
    def set_font_height(self, value):
        self.font_height = value
    
    def set_font_width(self, value):
        self.font_width = value

    def set_size(self, size):
        """
        """
        raise NotImplementedError
    def set_proportional(self, value):
        """
        """
        self.proportional = value        
    def handle_formfeed(self, count=1):
        """
        """
        raise NotImplementedError
    
    def add_text(self, text):
        """
        """
        raise NotImplementedError

    def set_linespacing(self, linespacing):
        """
        set my linespacing in points
        """
        raise NotImplementedError

    def set_charset(self, charset):
        raise NotImplementedError

    def set_hpos(self, pos):
        raise NotImplementedError
        
    def backspace(self, numspaces=1):
        raise NotImplementedError

class color:
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    DARKCYAN = '\033[36m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

        
class PlainTextPresenter(BasePresenter):
    """
    Prints text with no formatting codes, just basic margins
    """
    outfile = None
    linespacing = 1 # character cells, eh
    page_width = 72    
    
    def __init__(self, **kwargs):
        """
        """
        self.outfile = kwargs.get('outfile', sys.stdout)
        size = kwargs.get("size", self.default_page_size)
        self.new_page(size)        
        self.separator = kwargs.get("separator", "\f")

    def new_page(self, size):
        logger.debug("plaintext::new_page entered with %s", size)
        new_page = None
        if size == "Letter":
            new_page = LetterPage()
        else:
            new_page = A4Page()

        self.page_list.append(new_page)
        self.cur_page = len(self.page_list) - 1

    def add_text(self, byte):
        logger.debug("plaintext::add_text entered")
        if type(byte) == type(b""):
            byte = byte.decode(DEFAULT_CHARSET)
        if byte == "\n":
            byte = byte * self.linespacing
        self.page_list[self.cur_page].text = \
            self.page_list[self.cur_page].text + byte

    def set_bold(self, value):
        """
        """
        logger.debug("plaintext::set_bold entered")
        if value:
            self.add_text(color.BOLD)
        else:
            self.add_text(color.END)
    def set_condensed(self, value):
        """
        """
        logger.debug("plaintext::set_condensed entered with %s (n/a/)", value)
        return

    def set_underline(self, value):
        """
        """
        logger.debug("plaintext::set_underline entered with %s", value)
        if value:
            self.add_text(color.UNDERLINE)
        else:
            self.add_text(color.END)
    
    def __str__(self):
        return "\f".join([t.text for t in self.page_list])
    
    def set_hpos(self, value):
        """
        workaround for now
        """
        logger.debug("plaintext::set_hpos entered with %s", value)
        self.add_text(" ")
    
    def linefeed(self):
        """
        """
        logger.debug("plaintext::linefeed entered")
        self.add_text("\n")

    def carriage_return(self):
        logger.debug("plaintext::cr entered")
        self.add_text("\r")
    
    def set_linespacing(self, linespacing):
        """
        set my linespacing in points
        """
        logger.debug("plaintext::linespacing entered")
        self.linespacing = self.linespacing
    
    def set_font_size(self, *args):
        """
        """
        logger.debug("plaintext::set_font_size entered")
        pass

    def set_low_quality(self, value):
        logger.debug("plaintext::set_low_value entered with %s", value)

    def set_charset(self, value):
        """
        """
        logger.debug("plaintext::charset entered with %s", value)
        
class TerminalPresenter(BasePresenter):
    """
    terminal viewer for documents
    """

class PdfPresenter(BasePresenter):
    """
    PDF-Based presenter
    """
    default_font_family = "Courier New"
    authentic = True
    default_font_size = 8
    default_line_height = 8
    default_proportional = True
    condensed = False
    bold = False
    italic = False
    font_width = None    
    page_list = []
    page_size = None
    page_lines = 9999
    cur_line = 0
    cur_page = None
    stretch_x = 1.0
    stretch_y = 1.0
    x = 0
    y = 0
    linespacing = 72.0 / 6.0 # defaults to 1/"
    
    def __init__(self, **kwargs):
        """
        """
        size = kwargs.get("size", self.default_page_size)
        # self.filename = kwargs.get("filename", "default.pdf")
        self.fd = kwargs.get("fdout")
        logger.debug("pdf::init using %s", self.fd)
        logger.debug("pdf::init kwargs %s", kwargs)
        self.font_family = self.default_font_family
        self.font_size = self.default_font_size
        self.proportional = self.default_proportional
        self.page_size = size
        self.em = 0	# width of em-space
        self.en = 0 	# width of en-space

        if size == "Letter":
            self.page = LetterPage()
        else:
            self.page = A4Page()        

        # defaults
        

        # set up cairo stuff
        # self.ps = cairo.PDFSurface(self.fd or self.filename, self.page.width, self.page.height)
        self.ps = cairo.PDFSurface(self.fd, self.page.width, self.page.height)
        self.ctx = cairo.Context(self.ps)
        self.ctx.select_font_face(self.font_family)
        self.ctx.set_font_size(self.font_size)
        self.ctx.set_source_rgb(0, 0, 0)
        self.line_height = self.default_line_height        
        self.home()
        # print(self.x, self.y)

    def set_font_size(self, size):
        self.font_size = size
        

    def newline(self):
        """
        """
        self.carriage_return()
        self.linefeed()

    def carriage_return(self):
        """
        """
        self.x = 0   
        self.cur_line = self.cur_line + 1
        if self.cur_line and self.cur_line > self.page_lines:
            logger.debug("carriage_return out of lines %s/%s", self.cur_line, self.page_lines)
            self.cur_line = 0
            self.new_page()
        
    def linefeed(self):
        """
        """
        logger.debug("pdf::linefeed entered")
        self.y = self.y + self.linespacing * self.stretch_y # + self.line_height * self.stretch_y
        if (self.y + self.page.margin_b) > (self.page.height - self.page.margin_b):
            self.new_page()
        
    def set_hpos(self, pos):
        """
        """
        self.x = pos
    
    def home(self):
        """
        """
        self.y = self.font_size
        self.x = 0

    def add_text(self, byte):
        # do some text handling...
        text = byte.decode(DEFAULT_CHARSET)
        if 0x00 <= ord(text) < 0x1f:
            if text == "\n":
                self.linefeed()
                return
            elif text == "\r":
                self.carriage_return()
                return
            elif text == "\f":
                self.new_page()
                return
            else:
                logger.warn("Not adding text: %s", text)
            logger.debug("Can't print character %s", byte)
            return

        self.set_font()        
        x_advance = self.get_x_advance(text)
        
        if (self.x + x_advance > self.page.width - self.page.margin_r):
            self.newline()
            self.carriage_return()
            self.linefeed()
        scale_modifier = 1.0
        if self.superscript:
            # move up a litte
            y_modifier = self.font_size/-3
        elif self.subscript:
            y_modifier = self.font_size/3 # self.font_size
        else:
            y_modifier = 0

        self.ctx.save()
        self.ctx.move_to(self.page.margin_l + self.x, self.page.margin_t + self.y + self.font_size + y_modifier)
        self.ctx.scale(self.stretch_x, self.stretch_y)
        self.ctx.show_text(text)
        if self.underline:
            # draw a line there...
            start_y = self.y + self.font_size * 1.2 # just an estimate
            start_x = self.x
            self.ctx.move_to(start_x, start_y)
            self.ctx.line_to(start_x + x_advance, start_y)
            self.ctx.set_line_width(0.2)
            self.ctx.stroke()
        self.ctx.restore()
        self.x = self.x + x_advance
        logger.debug("T:'%s' x:%s, y:%s p:%s x_adv: %s b:'%s' l:%s ln:%s/%s lsp:%s x<->:%s y<->:%s sm:%s sub:%s sup:%s" % (text, int(self.x), int(self.y), self.proportional, int(x_advance), self.bold, self.line_height, self.cur_line, self.page_lines, self.linespacing, self.stretch_x, self.stretch_y, scale_modifier, self.superscript, self.subscript))

    def get_x_advance(self, text, proportional=True):
        """
        """
        if proportional and self.proportional:
            res = self.ctx.text_extents(text).x_advance or \
                self.ctx.text_extents(" ").x_advance
        else:
            # update em
            self.em = self.ctx.text_extents("M").width
            res = self.em
        return res * self.stretch_x
        
        
    def set_font(self):
        logger.debug("pdf::set_font entered")
        if self.italic:
            slant =  cairo.FONT_SLANT_ITALIC
        else:
            slant = cairo.FONT_SLANT_NORMAL
                    
        if self.bold:
            weight = cairo.FONT_WEIGHT_BOLD
        else:
            weight = cairo.FONT_SLANT_NORMAL
        
        self.ctx.select_font_face(self.font_family, slant, weight)
        logger.debug("font_size: %s", self.font_size)
        self.ctx.set_font_size(self.font_size)
        self.ctx.set_source_rgb(0, 0, 0)

        # calculate em and en
        self.em = self.get_x_advance("M", proportional=False)
        logger.debug("EM: %d", self.em)
        self.en = self.get_x_advance("N", proportional=False)
        logger.debug("EN: %d", self.em)
            
    def new_page(self):
        """
        """
        logger.debug("pdf::new_page entered")
        self.cur_line = 0
        self.ctx.show_page()
        self.home()

    def set_low_quality(self, *args):
        """
        """
        pass

    def set_underline(self, value):
        self.underline = value

    def set_bold(self, value):
        self.bold = value

    def set_italic(self, value):
        self.italic = value

    def set_proportional(self, value):
        logger.debug("pdf::set_proportional entered with %s", value)
        if value:
            logger.debug("pdf::setting sans-serif")
            self.ctx.select_font_face("sans-serif")
        else:
            logger.debug("pdf::setting %s", self.default_font_family)
            self.ctx.select_font_face(self.default_font_family)

    def set_linespacing(self, value):
        logger.debug("pdf::set_linespacing entered with %s", value)
        # self.linespacing = value - self.font_size + 2
        self.linespacing = value
        self.line_height = self.font_size
    
    def save(self):
        self.ctx.show_page()
    
    def set_charset(self, value):
        logger.debug("chrst: %s", value)

    def set_condensed(self, value):
        logger.debug("pdf::set_condensed entered with %s", value)
        self.stretch_x = value and 0.5 or 1.0
    
    def backspace(self, value):
        """
        moves back x. em-spaces
        """
        logger.debug("pdf::backspace entered")
        self.x = self.x - value * self.em
    
class HtmlPresenter(BasePresenter):
    default_font_family = "monospace"
    body = ""
    
    def __init__(self, **kwargs):
        self.font_family = self.default_font_family

    def linefeed(self):
        self.body = self.body + "</p><p>"

    def set_charset(self, value):
        self.charset = value
        
    def add_text(self, byte):
        text = byte.decode(DEFAULT_CHARSET)
        if text == "\n":
            self.linefeed()
            return
        self.body = self.body + text
    
    def save(self):
        print(self.body)
    
    def set_linespacing(self, value):
        self.linespacing = value
        