__printer_class__="Atari 8-series"
import sys
import os
import logging

from pyretroprint.presenter import PlainTextPresenter, PdfPresenter
from pyretroprint.page import LetterPage, A4Page


ESCAPE =  b'\x1b'
DEFAULT_CODEPAGE="cp850"

LOGGER=logging.getLogger(__name__)

class AtariProcessor(object):
    """
    atari 8-series processor
    - Atari 825
    """
    escape_state = False
    
    params_count = {
        0x08: 1,
        '-': 1,
    }
    
    def __init__(self, printfile, presenter, size="Letter"):
        """
        """
        self.printfile = printfile
        self.presenter = presenter
        self.presenter.set_linespacing(12) # 1/12" between lines?
        
    def handle_command(self, byte, params):
        """
        """
        command = byte # .decode(DEFAULT_CODEPAGE)
        msg = ""
        if command == b'\x01':
            msg = "Insert one dot space"
            self.send_dot_spaces(1)
            return
            
        elif command == b'\x02':
            msg = "Insert two dot spaces"
            self.send_dot_spaces(2)
            return
        elif command == b'\x03':
            msg = "Insert three dot spaces"
            self.send_dot_spaces(3)
            return
        elif command in [b'\x04', 4]:
            msg = "Insert four dot spaces"
            self.send_dot_spaces(4)
            return
        elif command in [b'\x05', 5]:
            msg = "Insert five dot spaces"
            self.send_dot_spaces(5)
            return
        elif command in [b'\x06', 6]:
            msg = "Insert six dot spaces"
            self.send_dot_spaces(6)
            return
        elif command == b'\x0a':
            msg = "Reverse line feed"
        elif command == b'\x0e':
            msg = "Set elongated print"
            self.set_double_width(1)
            return
        elif command == b'\x0f':
            msg = "Stop elongated print"
            self.set_double_width(0)
            return
        elif command == b'\x11':
            msg = "Set proportional"
            self.set_proportional()
            return
        elif command == b'\x13':
            msg = "Set 10cpi monospace"
            self.set_cpi(10)
            return
        elif command == b'\x14':
            msg = "Select condensed characters"
            self.set_condensed(1)
            return
        elif command == b'\x1c':
            msg = "Advance half a line"
        elif command == b'\x1e':
            msg = "Reverse half a line"
        elif command == b'-':
            msg = "Handle underline"
            self.set_underline(params[0])
            return
        elif command == b'\x34':
            msg = "Start italics"
            self.set_italic(1)
            return
        elif command == b'\x35':
            msg = "Stop italics"
            self.set_italic(0)
            return
        else:
            msg = "Unexpected command: %s" % command
        LOGGER.debug("Not handled: ESC %s %s %s", byte, params, msg)

    def set_linespacing(self, value):
        """
        """
        LOGGER.debug("atari::set_linespacing entered with %s", value)
        self.presenter.set_linespacing(value) # 1/12" b/w lines?

    def set_proportional(self):
        """
        """
        LOGGER.debug("atari::set_proportional entered")
        self.presenter.set_proportional(1)

    def set_italic(self, value):
        LOGGER.debug("atari::set_italic entered with %s", value)
        self.presenter.set_italic(value)

    def send_dot_spaces(self, value):
        """
        """
        LOGGER.debug("atari::send_dot_spaces entered with %s", value)
        self.presenter.x = self.presenter.x + value * 0.95 * self.presenter.stretch_x # needs to be fine tuned a little bit
    def set_bold(self, value):
        """
        """
        LOGGER.debug("atari::set_bold entered with %s", value)
        self.presenter.set_bold(value)
    def set_condensed(self, value):
        """
        """
        LOGGER.debug("atari::set_condensed entered with %s", value)
        self.presenter.set_condensed(value)

    def set_cpi(self, value):
        """
        there is only 10 or 12 here...
        """
        LOGGER.debug("atari::set_cpi entered with %s", value)
        if value == 10:
            LOGGER.debug("atari::set_cpi setting 12 pt")
            self.presenter.set_font_size(12) # 12 points in courier is about 10 cpi
        elif value == 12:
            LOGGER.debug("atari::set_cpi setting 10 pt")
            self.presenter.set_font_size(10)
        else:
            LOGGER.warn("atari::set_cpi called with unhandled value %s", value)
            sys.exit(1)
        self.presenter.stretch_x = 1.0        
        self.presenter.set_proportional(0)
            
    def set_double_width(self, value):
        LOGGER.debug("atari::set_double_width entered with %s", value)
        if value:
            self.presenter.stretch_x = 2.0
        else:
            self.presenter.stretch_x = 1.0


    def handle_escape(self):
        """
        what to do when escape is sent
        """
        LOGGER.debug("atari::handle_escape entered")
        self.escape_state = True
        
        
    def process(self):
        """
        main processing loop
        """
        LOGGER.debug("atari::process entered")
        pos = 0
        while True:
            byte = self.printfile.read(1)
            pos = pos + 1
            LOGGER.debug("pos:%s:%s", pos, byte)
            if self.escape_state:
                params = []
                count = self.params_count.get(byte.decode(DEFAULT_CODEPAGE), 0)
                while count:
                    params.append(int.from_bytes(self.printfile.read(1), "big"))
                    count = count - 1
                
                self.escape_state = False
                self.handle_command(byte, params)
            elif byte == ESCAPE:
                self.handle_escape()
            elif byte == b'\x08':
                LOGGER.debug("Backspace n spaces")
                num_spaces = int.from_bytes(self.printfile.read(1), "big")
                self.send_dot_spaces(-num_spaces)
            elif byte == b'\x0a':
                LOGGER.debug("Advance one line")
                self.presenter.linefeed()
            elif byte == b'\x0d':
                self.presenter.carriage_return()
            elif byte == b'\x0e':
                LOGGER.debug("Stop underlining")
                self.set_underline(0)
            elif byte == b'\x0f':
                LOGGER.debug("Start underlining")
                self.set_underline(1)
            elif byte == b'\x9b':
                LOGGER.debug("nbsp/lf")
                self.presenter.newline()
            elif byte == '' or len(byte)==0:
                LOGGER.debug("EOF")
                break
            else:
                self.handle_byte(byte)

    def handle_byte(self, byte):
        self.presenter.add_text(byte)

    def set_underline(self, value):
        LOGGER.debug("atari::set_underline entered with %s", value)
        if value:
            self.presenter.set_underline(True)
        else:
            self.presenter.set_underline(False)

    def backspace(self, num_spaces):
        LOGGER.debug("atari::backspace entered with %s", num_spaces)
        self.presenter.backspace(num_spaces)

if __name__=="__main__":
    # getopt etc.

    printfile = open(sys.argv[-1], 'rb')
    print("Reading", sys.argv[-1])
    print("Processing for PDF")
    presenter = PdfPresenter()
    proc = AtariProcessor(printfile, presenter, size="Letter")
    proc.process()
    print(proc.presenter)
    