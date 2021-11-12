# dm_square.py    26Feb2021  crs  drawing objects
"""
Square marker
"""
from tkinter import *

from select_trace import SlTrace

from dm_marker import DmMarker

""" Support for square(rectangle) marker turtle style
"""
class DmSquare(DmMarker):    
    def __init__(self, drawer, **kwargs
                  ):
        """ Setup basic marker state
        :drawer: drawing control
        :kwargs: basic DmMarker args
        """
        super().__init__(drawer, draw_type=super().DT_SQUARE, **kwargs)

    def __str__(self):
        return super().__str__()

    def draw(self):
        """ Draw square
        """
        super().draw()      # Ground work
        self.add_square()

if __name__ == "__main__":
    from dm_drawer import DmDrawer
    
    root = Tk()
    side = 50
    side_h = side
    side_v = side*2
    drawer = DmDrawer(root)
    colors = ["red", "orange", "yellow", "green", "blue", "indigo", "violet"]
    dms = []
    ns = 7
    beg=0
    nsquare = ns - beg + 1
    extent_h = nsquare*side_h
    extent_v = nsquare*side_v
    x_cor_start = side_h/2-extent_h/2
    y_cor_start = side_v/2-extent_v/2
    dm_base = DmSquare(drawer,
                        heading=0, color=colors[0], line_width=2,
                     side_h=side_h, side_v=side_v,
                     x_cor=x_cor_start, y_cor=y_cor_start)
    
    for i in range(beg, beg+nsquare):
        color = colors[i%len(colors)]
        if i == 0:
            dm = dm_base
        else:
            dm_prev = dms[i-1]
            dm = dm_prev.change(color=color,
                    x_cor = dm_prev.x_cor+dm_prev.side_h,
                    y_cor = dm_prev.y_cor+dm_prev.side_v)
        dms.append(dm)
        
    for dm in dms:
        SlTrace.lg(f"\ndm:{dm}")
        dm.draw()
        root.update()
        pass 
    
    mainloop()       
