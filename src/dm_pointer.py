# dm_pointer.py    27Feb2021  crs  drawing objects
"""
Line marker
"""
from select_trace import SlTrace

from draw_marker import DrawMarker

""" Support for line marker
"""
class DmPointer(DrawMarker):    
    def __init__(self, drawer, plen=None,
                **kwargs
                  ):
        """ Setup pointer (marker showing current point,direction)
        :drawer: drawing control
        :plen: pointer line length
            default=5
        :kwargs: basic DrawMarker args
        """
        super().__init__(drawer, draw_type=super().DT_POINTER, **kwargs)
        if plen is None:
            plen = 1
        self.plen = plen
        
    def __str__(self):
        return super().__str__()

    def draw(self):
        """ Draw line
        """
        x1,y1,x2,y2,kwargs = self.to_line_args(length=self.plen)
        
        self.create_line(x1,y1,x2,y2, arrow=LAST, **kwargs)
        

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
         
    nsquare = 8
    nsquare = 7
    colors = ["red", "orange", "yellow", "green", "blue", "indigo", "violet"]
    dms = []
    side = 100
    image_info = kb_draw.pick_next_image()
    image_file, image = image_info
    beg=0
    extent = side*nsquare
    x_beg = -extent/2
    y_beg = x_beg
    for i in range(beg, beg+nsquare):
        ang =  i*360/nsquare
        icolor = i % len(colors)
        color = colors[icolor]
        dm = DmPointer(kb_draw, heading=ang, color=color,
                            x_cor=x_beg+i*side,
                            y_cor=y_beg+i*side,
                            )
        dms.append(dm)
        
    for dm in dms:
        SlTrace.lg(f"\ndm:{dm}")
        dm.draw() 
    
    mainloop()       
