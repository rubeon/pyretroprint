import cairo

DEFAULT_MARGIN = 0 * 72 # 1/4" default margin in points

def pts2mm(pts):
    return float(pts) * 0.352778

def pts2in(pts):
    return float(pts) * 0.0138889


class Page(object):
    height = 0
    width = 0
    margin_l = 0
    margin_r = 0
    margin_t = 0
    margin_b = 0
    
    text = ""
    
    def __init__(self, **kwargs):
        self.margin_l = kwargs.get("margin_l", DEFAULT_MARGIN)
        self.margin_r = kwargs.get("margin_r", DEFAULT_MARGIN)
        self.margin_t = kwargs.get("margin_t", DEFAULT_MARGIN)
        self.margin_b = kwargs.get("margin_b", DEFAULT_MARGIN)
    
    @property
    def height_points(self):
        return self.height

    @property
    def height_inches(self):
        return self.height / 72.0
    
    @property
    def height_mm(self):
        return pts2mm(self.height)

    @property
    def height_inches(self):
        return self.width / 72.0
    
    @property
    def height_mm(self):
        return pts2mm(self.width)
    
class LetterPage(Page):
    height = 72 * 11 # points high
    width = 72 * 8.5 # points wide

class A4Page(Page):
    height = 72 * 11.69 # points high
    width = 72 * 8.27 # points wide


     
if __name__=="__main__":
    a4 = A4Page()
    letter = LetterPage()
    
    print("A4 page:")
    print("height: {}mm".format( pts2mm(a4.height)))
    print("width: {}mm".format( pts2mm(a4.width)))
    
    print("Letter page:")
    print("height: {}in".format( pts2in(letter.height)))
    print("width: {}in".format( pts2in(letter.width)))
    print("top margin: {}in".format( pts2in(letter.margin_t)))
    print("bottom margin: {}in".format( pts2in(letter.margin_b)))

    print("Letter page:")
    print("height: {}mm".format( pts2mm(letter.height)))
    print("width: {}mm".format( pts2mm(letter.width)))
    print("top margmm: {}mm".format( pts2in(letter.margin_t)))
    print("bottom margin: {}in".format( pts2in(letter.margin_b)))
    
    