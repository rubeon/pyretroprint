import sys

import math
import cairo
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT)

DEFAULT_CHARSET="ISO-8859-1"

from page import LetterPage, A4Page

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
    linespacing = 1
    font_height = 8

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


    def set_low_quality(self, enable):
        """
        """
        raise NotImplementedError


    def set_bold(self, value):
        """
        """
        self.bold = value
    
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


    page_width = 72    
    
    def __init__(self, **kwargs):
        """
        """
        size = kwargs.get("size", self.default_page_size)
        self.new_page(size)        
        self.separator = kwargs.get("separator", "\f")
    
    def new_page(self, size):
        new_page = None
        if size == "Letter":
            new_page = LetterPage()
        else:
            new_page = A4Page()

        self.page_list.append(new_page)
        self.cur_page = len(self.page_list) - 1

    def add_text(self, byte):
        if type(byte) == type(b""):
            byte = byte.decode(DEFAULT_CHARSET)
        if byte == "\n":
            byte = byte * self.linespacing
        self.page_list[self.cur_page].text = \
            self.page_list[self.cur_page].text + byte

    def set_bold(self, value):
        """
        """
        if value:
            self.add_text(color.BOLD)
        else:
            self.add_text(color.END)

    def set_underline(self, value):
        """
        """
        if value:
            self.add_text(color.UNDERLINE)
        else:
            self.add_text(color.END)
    
    def __str__(self):
        return "\f".join([t.text for t in self.page_list])
    
    def set_hpos(self, hpos):
        """
        workaround for now
        """
        self.add_text(" ")
        
    def set_linespacing(self, linespacing):
        """
        set my linespacing in points
        """
        self.linespacing = int(linespacing / self.font_height)
        
class TerminalPresenter(BasePresenter):
    """
    terminal viewer for documents
    """

class PdfPresenter(BasePresenter):
    """
    PDF-Based presenter
    """
    default_font_family = "monospace"
    default_font_size = 10
    default_line_height = 1.5
    
    condensed = False
    bold = False
    italic = False
        
        
    page_list = []
    page_size = None
    cur_page = None
    stretch_x = 1.0
    stretch_y = 1.0
    x = 0
    y = 0
    
    def __init__(self, **kwargs):
        """
        """
        size = kwargs.get("size", self.default_page_size)
        self.filename = kwargs.get("filename", "default.pdf")
        self.font_family = self.default_font_family
        self.font_size = self.default_font_size
        self.page_size = size

        if size == "Letter":
            self.page = LetterPage()
        else:
            self.page = A4Page()        

        # defaults
        

        # set up cairo stuff
        self.ps = cairo.PDFSurface(self.filename, self.page.width, self.page.height)
        self.ctx = cairo.Context(self.ps)
        self.ctx.select_font_face(self.font_family)
        self.ctx.set_font_size(self.font_size)
        self.ctx.set_source_rgb(0, 0, 0)
        self.ps.restrict_to_version(0)
        self.line_height = self.default_line_height * self.font_size
        
        self.home()
        
        print(self.x, self.y)

    def carriage_return(self):
        """
        """
        self.x = 0   
        
    def linefeed(self):
        """
        """
        self.y = self.y +  (self.line_height * self.stretch_y)
        if (self.y + self.page.margin_b) > (self.page.height - self.page.margin_b):
            print("XXX: linfeed -> NewPage!")
            self.new_page()
        else:
            logger.debug("linfeed: y=%s, ph=%s" % (self.y, self.page.height))
        
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
                print(text)
            logger.debug("Can't print character %s", byte)
            return

        self.set_font()        

        try:
            self.font_extents = self.ctx.text_extents(text)
        except:
            print(text)
            input("meh")

        x_advance = self.stretch_x * self.font_extents.x_advance
        
        if (self.x + x_advance > self.page.width - self.page.margin_r):
            self.carriage_return()
            self.linefeed()
        

            
        self.ctx.save()
        self.ctx.move_to(self.page.margin_l + self.x, self.page.margin_t + self.y + self.font_size)
        print("self.page.margin_t:", self.page.margin_t)
        self.ctx.scale(self.stretch_x, self.stretch_y)
        self.ctx.show_text(text)
        self.ctx.restore()
        self.x = self.x + x_advance
        logger.debug("x: %s, y:%s" % (self.x, self.y))
        # self.ctx.move_to(self.x, self.y)
        
    def set_font(self):
        args = []
        args.append(self.font_family)
        args.append(self.bold and cairo.FONT_WEIGHT_BOLD or cairo.FONT_WEIGHT_NORMAL)
        args.append(self.italic and cairo.FONT_SLANT_ITALIC or cairo.FONT_SLANT_NORMAL)
        self.ctx.select_font_face(*args)
            
    def new_page(self):
        """
        """
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
        if value:
            self.ctx.select_font_face("sans-serif")
        else:
            self.ctx.select_font_face("monospace")

    def set_linespacing(self, value):
        self.linespacing = value
        print("lspc:", value)
    
    def save(self):
        self.ctx.show_page()
    
    def set_charset(self, value):
        logger.debug("chrst: %s", value)

    def set_condensed(self, value):
        self.stretch_x = value and 0.8 or 1.0

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