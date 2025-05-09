# draw_marker.py    26Feb2021  crs  drawing objects
"""
Start generalizing as we might have done before_move
"""
from tkinter import *
import copy
import math

from select_trace import SlTrace
from select_error import SelectError
from importlib import resources

""" Marker info for do / modifications / undo
"""
class DrawMarker:
    DT_UNKNOWN = "dt_unknown"
    DT_LINE = "dt_line"
    DT_SQUARE = "dt_square"
    DT_TRIANGLE = "dt_triangle"
    DT_CIRCLE = "dt_circle"
    DT_DOT = "dt_dot"
    DT_IMAGE = "dt_image"
    DT_TEXT = "dt_text"     # letter but possibley more
    DT_POINTER = "dt_pointer"   # turtle pointer
    
    def __init__(self, drawer, draw_type=None,
                 heading=None, side=None, line_width=None,
                 color=None,
                 x_cor=None,  y_cor=None
                  ):
        """ Setup basic marker state
        :drawer: drawing control
        :draw_type: marker drawing type
                    REQUIRED
        :heading: marker direction default: drawer.heading
        :side: marker side size default: drawer.side
        :line_width: marker's line width defalt:drawer.side
        :color: marker's color default: drawer.
        :x_cor: marker's base x_coordinate default: drawer.x_cor
        :y_cor: marker's base y_coordinate default: drawer.y_cor
        """
        self.drawer = drawer
        if draw_type is None:
            raise SelectError("DrawMarker: draw_type missing")
        self.draw_type = draw_type
        if heading is None:
            heading = drawer.heading
        self.heading = heading
        if side is None:
            side = drawer.side
        self.side = side
        if line_width is None:
            line_width = drawer.current_width
        self.line_width = line_width
        if color is None:
            color = self.drawer.next_color()
        self.color = color
        if x_cor is None:
            x_cor = drawer.x_cor
        self.x_cor = x_cor
        if y_cor is None:
            y_cor = drawer.x_cor
        self.y_cor = y_cor
        self.tags = []          # Keep canvas tags, if any
        self.images = []          # Keep images, if any
        ####self.update_tur_scale()
    
    def __str__(self):
        str_str = self.__class__.__name__
        str_str += f" {self.color}"
        str_str += f" heading={self.heading:.1f}"
        str_str += f" side={self.side:.0f}"
        str_str += f" line_width={self.line_width:.0f}"
        str_str += f" x={self.x_cor:.0f} y={self.y_cor:.0f}"
        return str_str

    def copy(self):
        """ Copy sufficient to support drawing
        Shallow copy of tags and images
        draw MUST clear these out by calling undraw
        :returns: copied object
        """
        new_obj = copy.copy(self)
        return new_obj

    def change(self, heading=None, side=None, line_width=None,
                 color=None, x_cor=None,  y_cor=None):
        """ Return a changed version of this object with the 
        non-None parameters changed
        """
        new_obj = self.copy()
        if heading is not None:
            new_obj.heading = heading
        if side is not None:
            new_obj.side = side
        if line_width is not None:
            new_obj.line_width = line_width
        if color is not None:
            new_obj.color = color
        if x_cor is not None:
            new_obj.x_cor = x_cor
        if y_cor is not None:
            new_obj.y_cor = y_cor
        return new_obj

    def args_to_kwargs(self, color=None, width=None, dkwargs=None):
        """ Adjust / check  args and kwargs for canvas_create...
        :dkwargs: returnable dictionary of kwargs
                    Adjusted if applicable
        """
                
        if color is not None:
            if 'fill' in dkwargs:
                raise SelectError(f"Can't have color: {color}"
                                  f" fill: {dkwargs['fill']}")
            dkwargs['fill'] = color
        else:
            dkwargs['fill'] = self.color
        if width is not None:
            if 'width' in dkwargs:
                raise SelectError(f"Can't have width: {color}"
                                  f" and dkwargs['width']: {dkwargs['width']}")
            dkwargs['width'] = width
        else:
            dkwargs['width'] = self.line_width
        
    def to_line_args(self, x1=None, y1=None,
                     length=None, heading=None,
                     color=None, width=None,
                     **kwargs):
        """ Calculate create_line args, based on origin, heading, side
        :x1: x origin coordinate default: self.x_cor
        :y1: y origin coordinate default: self.y_cor
        :length: length of line default: self.side
        :color: line color default: from kwargs['fill'], else self.color
        :width: line width default: from kwargs['width'], else self.line_width
        :heading: heading in deg default: self.heading
        :kwargs: dictionary  additional parameters
                defaults: color - self.color, else black
                        width - self.line_width, else 1
        :returs: x1,y1,x2,y2, kwargs as adjusted by defaults
        """
        if x1 is None:
            x1 = self.x_cor
        if y1 is None:
            y1 = self.y_cor
        if length is None:
            length = self.side
        self.length = length
        if heading is None:
            heading = self.heading
        
        if color is not None:
            if 'fill' in kwargs:
                raise SelectError(f"Can't have color: {color}"
                                  f" fill: {kwargs['fill']}")
            kwargs['fill'] = color
        else:
            kwargs['fill'] = self.color
        if width is not None:
            if 'width' in kwargs:
                raise SelectError(f"Can't have width: {color}"
                                  f" and kwargs['width']: {kwargs['width']}")
            kwargs['width'] = width
        else:
            kwargs['width'] = self.line_width
            
        """ Calculate x2,y2 from x1,y1,heading """
        theta = math.radians(heading)
        x_chg = self.length*math.cos(theta)
        y_chg = self.length*math.sin(theta)
        x2 = x1 + x_chg
        y2 = y1 + y_chg
        return x1,y1,x2,y2,kwargs

    def vadd(self, x1=None, y1=None, heading=None, length=None):
        """ Vector add to get x2,y2, uses to_Line_args
        :x1,y1: x,y origin coordinates    default: x_cor, y_cor
        :heading: heading default: self.heading
        :length: distance default: self.side
        :returns: x2,y2
        """
        _,_,x2,y2,_ = self.to_line_args(x1=x1, y1=y1,
                                               heading=heading,
                                               length=length)
        return x2,y2
    
    def add_circle(self, x1=None, y1=None,
                     length=None, heading=None,
                     color=None, width=None,
                     **kwargs):
        """ Add circle turtle style
        :x1: x origin coordinate default: self.x_cor
        :y1: y origin coordinate default: self.y_cor
        :length: length of line default: self.side (diameter)
        :color: line color default: from kwargs['fill'], else self.color
        :width: line width default: from kwargs['width'], else self.line_width
        :heading: heading in deg default: self.heading (of bounding box)
        :kwargs: additional parameters
                defaults: color - self.color, else black
                        width - self.line_width, else 1
        """
        corners = self.get_square(x1=x1, y1=y1,
                     length=length, heading=heading)
        ptxy = []
        for x,y in corners:
            ptxy.extend([x,y])
        self.create_polygon(*ptxy, width=1, fill="", outline="red")    # TFD - bounding box 
        ov_x0, ov_y0 = corners[3]
        ov_x1, ov_y1 = corners[1]
        self.args_to_kwargs(color=color, width=width, dkwargs=kwargs)
        self.create_oval(ov_x0, ov_y0, ov_x1, ov_y1, **kwargs)
        SlTrace.lg(f"create_oval: {ov_x0:.0f}, {ov_y0:.0f}, {ov_x1:.0f}, {ov_y1:.0f}, {kwargs}")

    def add_line(self, x1=None, y1=None,
                     length=None, heading=None,
                     color=None, width=None,
                     **kwargs):
        """ Add line origin,heading... as in to_line_args
        :x1: x origin coordinate default: self.x_cor
        :y1: y origin coordinate default: self.y_cor
        :length: length of line default: self.side
        :color: line color default: from kwargs['fill'], else self.color
        :width: line width default: from kwargs['width'], else self.line_width
        :heading: heading in deg default: self.heading
        :kwargs: additional parameters
                defaults: color - self.color, else black
                        width - self.line_width, else 1
        """
        x1,y1,x2,y2,k2args = self.to_line_args(
                        x1=x1, y1=y1,
                        length=length, heading=heading,
                        color=color, width=width, **kwargs)
        self.create_line(x1,y1,x2,y2, **k2args)

    def add_triangle(self, x1=None, y1=None,
                     length=None, heading=None,
                     color=None, width=None,
                     **kwargs):
        """ Add triangle turtle style
        :x1: x origin coordinate default: self.x_cor
        :y1: y origin coordinate default: self.y_cor
        :length: length of line default: self.side (diameter)
        :color: line color default: from kwargs['fill'], else self.color
        :width: line width default: from kwargs['width'], else self.line_width
        :heading: heading in deg default: self.heading (of bounding box)
        :kwargs: additional parameters
                defaults: color - self.color, else black
                        width - self.line_width, else 1
        """
        if x1 is None:
            x1 = self.x_cor
        if y1 is None:
            y1 = self.y_cor
        if length is None:
            length = self.side
        if heading is None:
            heading = self.heading

        # Use square as basis, left verticle is base
        # center of right vertical is peak        
        corners = self.get_square(x1=x1, y1=y1,
                     length=length, heading=heading,
                     color=color, width=width)
        ptxy = []
        x,y = corners[0]
        ptxy.extend([x,y])
        p2 = ((corners[1][0]+corners[2][0])/2,
               (corners[1][1]+corners[1][1])/2)
        ptxy.extend([p2[0],p2[1]])
        x,y = corners[3]
        ptxy.extend([x,y])
        
        self.args_to_kwargs(color=color, width=width, dkwargs=kwargs)
        outline = kwargs['fill']
        kwargs['fill'] = ""
        kwargs['joinstyle'] = MITER
        self.create_polygon(*ptxy, outline=outline, **kwargs) 

    def add_square(self, x1=None, y1=None,
                     length=None, heading=None,
                     color=None, width=None,
                     **kwargs):
        """ Add square turtle style
        :x1: x origin coordinate default: self.x_cor
        :y1: y origin coordinate default: self.y_cor
        :length: length of line default: self.side (diameter)
        :color: line color default: from kwargs['fill'], else self.color
        :width: line width default: from kwargs['width'], else self.line_width
        :heading: heading in deg default: self.heading (of bounding box)
        :kwargs: additional parameters
                defaults: color - self.color, else black
                        width - self.line_width, else 1
        """
        if x1 is None:
            x1 = self.x_cor
        if y1 is None:
            y1 = self.y_cor
        if length is None:
            length = self.side
        if heading is None:
            heading = self.heading
        
        corners = self.get_square(x1=x1, y1=y1,
                     length=length, heading=heading,
                     color=color, width=width)
        ptxy = []
        for x,y in corners:
            ptxy.extend([x,y])
        self.args_to_kwargs(color=color, width=width, dkwargs=kwargs)
        outline = kwargs['fill']
        kwargs['fill'] = ""
        kwargs['joinstyle'] = MITER
        self.create_polygon(*ptxy, outline=outline, **kwargs) 

    def get_square(self, x1=None, y1=None,
                     length=None, heading=None,
                     color=None, width=None,
                     **kwargs):
        """ Get square turtle style array of xi,yi: i=0,1,2,3
            i=3    i=2
            
            i=0    i=1
        :x1: x origin coordinate default: self.x_cor
        :y1: y origin coordinate default: self.y_cor
        :length: length of line default: self.side (diameter)
        :color: line color default: from kwargs['fill'], else self.color
        :width: line width default: from kwargs['width'], else self.line_width
        :heading: heading in deg default: self.heading (of bounding box)
        :kwargs: additional parameters
                defaults: color - self.color, else black
                        width - self.line_width, else 1
        :returns: list of corners (xi,yi) for i=1 in range(4)
        """
        if x1 is None:
            x1 = self.x_cor
        if y1 is None:
            y1 = self.y_cor
        if length is None:
            length = self.side
        if heading is None:
            heading = self.heading
        
        corners = []    
        for _ in range(4):
            SlTrace.lg(f"add_line(): x1={x1:.0f}, y1={y1:.0f}",
                       f" length={length:.0f}, heading={heading:.0f}")
            corners.append((x1,y1))
            x1,y1 = self.vadd(x1, y1, heading=heading, length=length)
            heading += 90
        SlTrace.lg(f"x1={x1:.0f}, y1={y1:.0f}, length={length:.0f}, heading={heading:.0f} AFTER")
        return corners

        def create_image(self, x, y, image,
                         to_scale=False,
                         **kwargs):
            """link to tkinter create_image
            :x,y: x,y coordinates
            :image: image to place
            :tu_scale: scale from turtle to canvas 
                        default: False
            :kwargs: additional arguments
            """
            canvas = self.get_canvas()
            ####x,y = self.tur_scale(to_scale, [x, y])
            image_tag = canvas.create_image(x, y, image=image,
                                            **kwargs)
            self.tags.append(image_tag)

    def tur_scale(self, to_scale, xys):
        """ scale x,y, point pairs if to_scale
        from turtle coordinates to Canvas coordinates
        xc = 0 xt=-win_width/2           xc=win_width xt=win_width/2
        yc = 0 yt=win_height/2           yc=0 yt=win_height/2
        
        
        
        
        
                            xc=win_width/2 xt=0
                            yc=win_height/2 yt=0
                            
                            
                            
                            
                            
        xc=0 xt=-win_width/2            xc=win_height xt=win_height/2
        yc=win_height yt=-win_height/2  yc=win_height yt=-win_height/2
        
        :to_scale: do scaling if True
        :pxy: list of x,y point coordinate pairs
        :returns: return list of scaled x,y coordinate pairs
        """
        if not to_scale:
            return xys      # No scaling - return original values
        
        pair_list = []
        count = 0 
        for coord in xys:
            count += 1
            if count % 2 == 1:
               x = coord 
            else:
               pair_list.append((x, coord))
        xys2 = []
        for xt,yt in pair_list:
            xc = xt + self.canvas_width/2
            yc = -yt + self.canvas_height/2
            xys2.append(xc)
            xys2.append(yc)
        return xys2

    def update_tur_scale(self):
        """ Called to recalibrate scaling between turtle
        coordinates and canvas coordinates
        """
        canvas = self.get_canvas()
        self.canvas_width = canvas.winfo_width()
        resized = False
        if self.canvas_width < 500:
            self.canvas_width = 500
            resized = True
        self.canvas_height = canvas.winfo_height()
        if self.canvas_height < 500:
            self.canvas_height = 500
            resized = True
        if resized:
            canvas.configure(width=self.canvas_width,
                             height=self.canvas_height)
        SlTrace.lg(f"canvas: width:{self.canvas_width}"
                   f"  height:{self.canvas_height}")
            
    def create_image(self, x, y, image, to_scale=True,
                     **kwargs):
        """ Link to Canvas create_image
        :x,y: turtle coordinates
        :image: photo image
        :to_scale: scale to canvas from turtle
        :kwargs: additional parameters
        """
        canvas = self.get_canvas()
        ####x, y = self.tur_scale(to_scale, (x,y))
        tag = canvas.create_image(x,y, image=image,
                                  anchor=SE, **kwargs)
        SlTrace.lg(f"create_image: x={x:.0f}, y={y:.0f} tag={tag}")
        self.tags.append(tag)
        
    def create_line(self, x1, y1, x2, y2, **kwargs):
        """ link to tkinter create_line
        """
        canvas = self.get_canvas()
        SlTrace.lg(f"create_line: x1={x1:.0f}, y1={y1:.0f}, x2={x2:.0f} y2={y2:.0f} tag=?")
        ####x1, y1, x2, y2 = self.tur_scale(True, (x1, y1, x2, y2))
        tag = canvas.create_line(x1,y1,x2,y2, **kwargs)
        self.tags.append(tag)
        SlTrace.lg(f"create_line: x1={x1:.0f}, y1={y1:.0f}, x2={x2:.0f} y2={y2:.0f} tag={tag}")
        
    def create_oval(self, x1, y1, x2, y2, **kwargs):
        """ link to tkinter create_oval
        """
        canvas = self.get_canvas()
        ####x1, y1, x2, y2 = self.tur_scale(True, (x1, y1, x2, y2))
        tag = canvas.create_oval(x1,y1,x2,y2, **kwargs)
        self.tags.append(tag)

    def create_polygon(self, *ptxy, **kwargs):
        """ link to tkinter create_line
        """
        canvas = self.get_canvas()
        ####ptxy = self.tur_scale(True, ptxy)
        tag = canvas.create_polygon(*ptxy, **kwargs)
        self.tags.append(tag)
        ptxy_str = ""
        for pt in ptxy:
            if ptxy_str != "":
                ptxy_str += ", "
            ptxy_str += f"{pt:.0f}"
        SlTrace.lg(f"create_polygon: ptxy: {ptxy_str} tag={tag}")
                
    def get_canvas(self):
        """ Get our working canvas
        """
        return self.drawer.tu_canvas

    def draw(self):
        """ Draw/Redraw figure
        first removing any preexisting artifacts
        """
        self.undraw()
        
    def undraw(self):
        """ Remove drawn artifacts and resources
        """
        canvas = self.get_canvas()
        for tag in self.tags:
            canvas.delete(tag)
        self.tags = []
        
        for image in self.images:
            del(image)
        self.images = []
            