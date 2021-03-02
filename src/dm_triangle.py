# dm_triangle.py    26Feb2021  crs  drawing objects
"""
Triangle marker
"""
from tkinter import *

from select_trace import SlTrace

from draw_marker import DrawMarker

""" Support for Triangle marker turtle style
"""
class DmTriangle(DrawMarker):    
    def __init__(self, drawer, **kwargs
                  ):
        """ Setup basic marker state
        :drawer: drawing control
        :kwargs: basic DrawMarker args
        """
        super().__init__(drawer, draw_type=super().DT_CIRCLE, **kwargs)

    def __str__(self):
        return super().__str__()

    def draw(self):
        """ Draw Triangle
        """
        super().draw()      # Ground work
        self.add_triangle()

if __name__ == "__main__":
    from tkinter import *
    
    from keyboard_draw import KeyboardDraw
    
    root = Tk()
    
    kb_draw = KeyboardDraw(root,  title=f"Testing {__file__}",
                hello_drawing_str="",
                draw_x=100, draw_y=50,
                draw_width=1500, draw_height=1000,
                kbd_win_x=50, kbd_win_y=25,
                kbd_win_width=600, kbd_win_height=300,
                show_help=False,        # No initial help
                with_screen_kbd=False   # No screen keyboard
                           )
         
    ntriangle = 8
    ntriangle = 7
    colors = ["red", "orange", "yellow", "green", "blue", "indigo", "violet"]
    dms = []
    
    dm_base = DmTriangle(kb_draw)
    beg=0
    for i in range(beg, beg+ntriangle):
        ang =  i*360/ntriangle
        icolor = i % len(colors)
        color = colors[icolor]   
        dm = dm_base.change(heading=ang, color=color, line_width=(i+1)*2,
                     side=(i+1)*20)
        dms.append(dm)
        
    for dm in dms:
        SlTrace.lg(f"\ndm:{dm}")
        dm.draw() 
    
    mainloop()       
