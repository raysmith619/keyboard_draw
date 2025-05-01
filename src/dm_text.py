# dm_text.py    28Feb2021  crs  drawing objects
"""
Square marker
"""
import tkinter as tk
import tkinter as tk

import tkinter.font
from tkinter import *
from PIL import ImageTk, Image
from PIL import ImageDraw, ImageFont

from select_trace import SlTrace

from dm_image import DmImage
from dm_square import DmSquare

""" Support for image marker turtle style
"""
class DmText(DmImage):    
    def __init__(self, drawer, text=None,
                 side_h=None, side_v=None,
                  **kwargs):
        """ Setup text marker state
        :drawer: drawing control
        :text: text to display
        :side_h: Horizontal length default:drawer.side_h
        :side_v: vertical length default: side_h*2
        :kwargs: basic DrawMarker args
        """
        self.text = text
        super().__init__(drawer, draw_type=super().DT_TEXT,
                         marker_type="letter",
                         **kwargs)
        if side_h is None:
            side_h = drawer.get_side_h()
        self.side_h = side_h
        if side_v is None:
            side_v = side_h*2
        self.side_v = side_v
        self.set_text_image(text)
        
        
        
    def set_text_image(self, text):
        """ Setup base image to represent text
        :text:
        """
        self.text = text
        text_size_h = self.side_h
        text_size_v = self.side_v
        text_font = ImageFont.truetype("arial.ttf", size=int(text_size_h))
        #text_font = ImageFont.truetype("courbd.ttf", size=text_size)
        #text_font = ImageFont.truetype("tahoma.ttf", size=text_size)
        text_color = self.color
        if text_color is None:
            text_color = "black"
        text_bg = ""    

        ###xy = (x0,y0)
        image = Image.new("RGB", (int(text_size_h), int(text_size_v)), (255,255,255))
        draw = ImageDraw.Draw(image)      # Setup ImageDraw access
        ###draw.text((10,-25), self.text, anchor="mt",      ###TFD
        draw.text((text_size_h/2,text_size_v*.7), self.text, anchor="mb",
                  fill=text_color, font=text_font,
                  bg=text_bg)
        image = image.resize((int(self.side_h), int(self.side_v)))
        self.set_image_base(image)
        

    def __str__(self):
        return self.text + ":" + super().__str__()

    def change(self, text=None, **kwargs):
        """ Change object attibutes, returning changed object
            initial object is unchanged
            :text: new text/letter
            :kwargs: reminder of args
        """
        new_obj = super().change(**kwargs)
        if text is not None:
            new_obj.set_text_image(text)
        return new_obj
        
        
if __name__ == "__main__":
    from dm_drawer_image import DmDrawerImage
    
    root = Tk()
    
    vert_change = 1.    # inclined
    ###vert_change = 0     # flat - vertical change 
    drawer = DmDrawerImage(root)
    line_width = 2   # line thickness
    side = 100
    ###side = 25     
    nsquare = 7
    colors = ["red", "orange", "yellow", "green", "blue", "indigo", "violet"]
    dms = []
    dmxs = []   # squares for comparison
    beg=0
    extent = side*nsquare
    x_beg = 1.2*side-extent/2
    y_beg = x_beg-.4*side
    dm_base = DmText(drawer, text="a", color=colors[0],
                     side_h=side/2, side_v = side,
                     x_cor=x_beg, y_cor=y_beg)
    dm_base_sq = DmSquare(drawer, color=colors[0],
                     line_width=line_width,
                     side_h = side/2, side_v=side,
                     x_cor=x_beg, y_cor=y_beg)
    for i in range(beg, beg+nsquare):
        ###ang =  i*360/nsquare
        ang =  0
        icolor = i % len(colors)
        color = colors[icolor]
        text = chr(ord(dm_base.text)+i)
        if i == 0:
            dm = dm_base
            dmx = dm_base_sq
        else:
            dm_prev = dms[i-1]
            if vert_change == 0:
                y_cor = None 
            else:
                y_cor = dm_prev.y_cor + vert_change*dm_prev.side_v    
            dm = dm_prev.change(heading=ang,
                            color=color,
                            line_width=line_width,
                            x_cor=dm_prev.x_cor+dm_prev.side_h,
                            y_cor=y_cor,
                            text=text)
            dmx_prev = dmxs[i-1]
            if vert_change == 0:
                y_cor = None 
            else:
                y_cor = dmx_prev.y_cor + vert_change*dmx_prev.side_v
            dmx = dmx_prev.change(heading=ang,
                            color=color,
                            line_width=line_width,
                            x_cor=dmx_prev.x_cor+dm_prev.side_h,
                            y_cor=y_cor
                            )
        dms.append(dm)
        dmxs.append(dmx)
    
    for i in range(len(dms)):   
        dm = dms[i]
        dmx = dmxs[i]
        SlTrace.lg(f"\ndm:{dm}")
        SlTrace.lg(f"\ndmx:{dmx}")
        dmx.draw()
        dm.draw()
        root.update() 
    
    mainloop()       
