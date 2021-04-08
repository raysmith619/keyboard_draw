#dm_drawer.py
"""
Hopefully simple drawing control for the DmMarker
family of classes to develop, test and demonsrate
In the interest of simplifying the non-image classes
the image support will be placed in the derived 
class DmDrawerImage

DmDrawer class is a toy class to facilitate
development and self testing DmMarker and
classes based on DmMarker
"""
import tkinter as tk

from select_trace import SlTrace
from select_error import SelectError
from select_window import SelectWindow

from attr_change import AttrChange, Attribute

class DmDrawer(SelectWindow):
    def __init__(self, master, title=None,
                 kbd_master=None, canvas=None,
                 draw_x=20, draw_y=20,
                 draw_width=1500, draw_height=1000,
                 kbd_win_x=0, kbd_win_y=0,
                 kbd_win_width=350, kbd_win_height=200,
                 side=100,
                 width=20,
                 hello_drawing_str=None,
                 with_screen_kbd=True,
                 show_help=True,
                 **kwargs
                 ):
        """ Drawing tool
        with simple functional interface
        Note that a number of parameters, e.g., keyboard_master,
        are unused as they are for a more extensive drawing class
        (e.g. KeyboardDraw)
        """
        if canvas is None:
            canvas = tk.Canvas(master=master,
                               width=draw_width, height=draw_height,
                               bd=2, bg="white", relief="ridge")
            canvas.pack(expand=True, fill=tk.BOTH)
        self.draw_width = draw_width
        self.draw_height = draw_height
        self.canv = canvas
        self.canvas_width = draw_width    # Fudge
        self.canvas_height = draw_height   # Fudge
        self.x_cor = 0
        self.y_cor = 0
        self.side = side
        self.line_width = width
        self.heading = 0
        self.attr_chg = AttrChange()    # Setup attributes
        attr = Attribute("color", 
            ["red", "orange", "yellow", "green",
                "blue", "indigo", "violet"])
        self.attr_chg.add_attr(attr) 
        attr = Attribute("shape", 
            ["line", "square", "triangle", "circle"])
        self.attr_chg.add_attr(attr)
        
        
    def get_canvas(self):
        """ Get our working canvas
        """
        return self.canv
    
    def get_heading(self):
        return self.heading

    def get_x_cor(self):
        return self.x_cor

    def get_y_cor(self):
        return self.y_cor

    def get_next(self, name):
        """ Get next attribute value
        :name: attribute name
        :return: attribute value
        """
        return self.attr_chg.get_next(name)

    def get_copy_move(self):
        return self.copy_move
    
    def set_copy_move(self, copy_move):
        self.copy_move = copy_move
        
    def get_loc(self):
        return (self.get_x_cor(), self.get_y_cor())
        
    def get_side(self):
        return self.side

    def get_width(self):
        return self.line_width
    
    def set_heading(self, heading):
        self.heading = heading
                


    def set_side(self, side):
        self.side = side

    def set_width(self, line_width):
        self.line_width = line_width


    def set_size(self, side=None, line_width=None):
        if side is not None:
            self.set_side(side)
        if line_width is not None:
            self.set_width(line_width)
