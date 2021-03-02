# dm_circle.py    26Feb2021  crs  drawing objects
"""
Circle marker
"""
from tkinter import *

from select_trace import SlTrace

from draw_marker import DrawMarker

""" Support for circle marker turtle style
"""
class DmCircle(DrawMarker):    
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
        """ Draw circle
        """
        super().draw()      # Ground work
        self.add_circle()

if __name__ == "__main__":
    root = Tk()
    
    canvas = Canvas(root, width=1000, height=1000)
    canvas.pack()
    class Drawer:
        heading = 0
        side = 100
        width = 2
        x_cor = 50
        y_cor = 500
        tu_canvas = canvas
        
        def next_color(self):
            return "red"
         
    drawer = Drawer()
    ncircle = 8
    ncircle = 7
    colors = ["red", "orange", "yellow", "green", "blue", "indigo", "violet"]
    dms = []
    
    dm_base = DmCircle(drawer, heading=0, color="pink", line_width=20,
                     side=200)
    beg=3
    for i in range(beg, beg+ncircle):
        ang =  i*360/ncircle
        icolor = i % len(colors)
        color = colors[icolor]   
        dm = dm_base.change(heading=ang, color=color, line_width=(i+1)*2,
                     side=(i+1)*20)
        dms.append(dm)
        
    for dm in dms:
        SlTrace.lg(f"\ndm:{dm}")
        dm.draw() 
    
    mainloop()       
