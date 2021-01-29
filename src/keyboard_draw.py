#keyboard_draw.py    12Dec2020  crs
"""
Drawing on turtle window, using keyboard
"""
import os
import re
import math
import tkinter as tk
from tkinter import colorchooser
from PIL import ImageTk, Image
import turtle

from select_trace import SlTrace
from select_list import SelectList
from screen_kbd import ScreenKbd
from image_hash import ImageHash
from Lib.pickle import NONE, TRUE

undomax = 2000      # Maximum turtle undo count

""" Marker/Shape info
    for undo / rotate operations
"""
class MoveInfo:
    def __init__(self, drawer, marker=None, shape=None, image_info=None,
                 scale=None, line_width=None):
        """  Marker/Shape info for undo / rotate operations
        :marker: marker type
                default: drawer..marker_current
        :shape: shape type
                default: drawer.shape_current
        :image_info: image information (key, image)
                default: drawer.image_chosen
        :scale: scale multiplier
                default: 1.0
        :line_width: line width
                default: drawer.side
        """
        self.drawer = drawer
        if marker is None:
            marker = drawer.marker_current
        self.marker = marker
        if shape is None:
            shape = drawer.shape_current
        self.shape = shape
        if image_info is None:
            image_info = drawer.image_chosen
        self.image_info = image_info
        if scale is None:
            scale = 1.0
        self.scale = scale
        if line_width is None:
            line_width = drawer.current_width
        self.line_width = line_width
            
class KeyboardDraw:
    def __init__(self, master, kbd_master=None, canvas=None,
                 side=100,
                 width=20,
                 hello_drawing_str=None,
                 ):
        """ Keyboard Drawing tool
        :master: master
        :kbd_master: screen keyboard master, if present
                    must be grid managed
                    default: create Toplevel
        :canvas: base canvas
                default: create 500x500
        :side: starting line side length
            default: 100
        :width: starting line width
                default: 20
        :hello_drawing_str: Beginning display command string
                default: HI...
        """
        if canvas is None:
            canvas = tk.Canvas(master=master,
                               width=1500, height=1000)
            canvas.pack()
        self.tu_canvas = canvas
        self.tu_canvas.bind ("<ButtonPress>", self.mouse_down)
        self.tu_screen = turtle.TurtleScreen(self.tu_canvas)
        self.tu = turtle.RawTurtle(self.tu_canvas)
        self.tu.setundobuffer(undomax)
        self.draw_undo_counts = [self.tu.undobufferentries()] # undo counts
        self.master = master
        self.side = side
        self.current_width = width
        self.do_trace = False    # Set True to do debugging trace
        self.do_trace = True
        ###self.turtle_cv = self.tu.getcanvas()
        ###SlTrace.lg(f"turtle: width:{self.turtle_cv.canvwidth} height:{self.turtle_cv.canvheight}")
        self.set_key_mapping()
        x_start = -500
        y_start = 350
        side = self.side
        width = self.current_width
        if hello_drawing_str is None:
            x_start -= 2*side  # Fudge because of  unexpcted size
            hello_drawing_str = f"""
            # Beginning screen pattern
            minus
            line({side},{width})        # Set side, width
            moveto({x_start},{y_start})
            shape(line)
            plus
            image();q
            image()
            image();q
            image()
            image();q
            image()
            image();q
            image()
            image();a
            image()
            minus
            line({side},{width})        # Set side: 100; width: 20
            shape(line)
            # HI in middle of screen
            moveto({x_start+200},{y_start-150})
            
            shape(line)
            plus
            w
            Down;Down;Down;Down;Up;Up;Right;Right;Up;Up;Down;Down
            Down;Down;Up;Up;minus;Right;Right;plus;Up;Up;Down;Down
            Down;Down
            
            # Line under
            minus;Right;Right;Right;Down;Down
            line({side},{4})
            plus
            Left
            t;=#ff0000;shape(rotate)
            t;=#0ff000;shape()
            t;=#00ff00;shape()
            t;=#000ff0;shape()
            t;=#0000ff;shape()
            t;=#f0f0f0;shape()
            t;=#af0f0f;shape(line)
            line({side},{width})        # Set side,width to starting
            w
            check
            
            """
        self.hello_drawing_str = hello_drawing_str
        
        self.marker_order = [
            "line",
            "shape",
            "image",
             ]
    
        self.shapes = {
            "line" : self.shape_line,
            "square" : self.shape_square,
            "circle" : self.shape_circle,
            "triangle" : self.shape_triangle,
            }
        self.shape_order = [
            "circle",
            "triangle",
            "square",
            ]
        # a rotating color pattern
        self.colors = ["red", "orange", "green",
                  "blue", "indigo", "violet"]
        
        # Rotating pattern of custom colors
        self.custom_colors = []
        self.key_fun_name = {
            '=' : "color",
            ':' : "line",
            'moveto:' : 'moveto',
            }
    
        self.fun_by_name = {
            'color' : self.color_set,
            'image' : self.image_next,
            'line' : self.line_set,
            'marker' : self.set_marker,
            'moveto' : self.moveto_set,
            'shape' : self.shape_next,
            }

        self.setup_image_access()
        self.moves_canvas_tags = []  # Init for canvas part of draw_undo
        self.clear_all()
        
        self.bound_keys = {}     # functions, bound to keys
        
        
        self.enlarge_fraction = .2   # Enlargement fraction
        self.track_keys()
        if kbd_master is None:
            kbd_master = tk.Toplevel()
        self.kbd_master = kbd_master
        self.screen_keyboard = ScreenKbd(kbd_master, on_kbd=self.do_key,
                                          title="Let's Make a Drawing!")
        self.do_keys(self.hello_drawing_str)
        self.help()

    def help(self):
        print("""
    h - print this help message
    color keys:
        r : red, o-range, y-yellow, g-green, b-blue,
        i : indigo, v-violet
        w : changing colors
        - : make lines invisible(white)
        + : make lines visible(previous color)
        = : Set line color from color chooser
            Colors can be changed via arrow keys
            Press <space> to select color, <ENTER> to
            choose the color The Mouse can also be used.
    side size keys:
        : or ; : Interactively Set line length and width in pixels
            from script (:width[:length])
                         e.g. :100:5 for len 100 width 5 
        q : increase marker size (10%)
        a : decrease-marker size (undo a previous 10% increase)
        t : increase current line thickness by two
        x : decrease current line thickness by two
    move keys:
        m : move to location script: moveto[:][x][:y]
            Move to x,y location (-512..512)
                default: no movement in direction if direction is empty
                    example: moveto::500 just moves to y=500, x unchanged
            m, moveto alone prompts user for values
                    
        arrows : in direction of arrow(Up,Down,Right,Left)
        Digits : 1-9 for directions of keypad
                7 8 9
                4   6
                1 2 3  for example 9-diagonal up to right
            5 : rotate 45 deg to left, then draw line
            0 : rotate 45 deg to right, then draw line 
            space : rotate 180 deg (reverse direction)
        u : "undo" - take back last graphic action
                    Note: Most drawing actions use
                          several graphics actions
        c : move to center
        s : "shape" - set shape to next
        d : "determine" choose shape - via dialog
        f : "fan" - set shape to rotate as we move
        z : clear screen of drawing, reset to original values
        
    Image Keys
        w : set colors to change each move
        s : Set shapes to change each move
        d : Change to a particular shape
        j : Select an animal picture for each move
        k : Change animal picture each press
        
    Special keys /commands
        ., check - used for debugging
        """)
        ###SlTrace.lg(f"turtle: width:{self.turtle_cv.canvwidth} height:{self.turtle_cv.canvheight}")
    
    
    def trace(self, tstring):
        """ trace info (debugging) when we can't use select_trace
        Place info on next line as a comment line
        :tstring: trace string
        """
        if self.do_trace:
            print(f"\n#{tstring}")

    def setup_image_access(self, image_dir=None):
        """ Setup image access for markers
        :image_dir: image file directory
        """
        if image_dir is None:
            image_dir="../../resource_lib/images/animals"
            
        SlTrace.lg("Image Files")
        data_files_dir="../../resource_lib/images/animals"
        image_files_dir = os.path.abspath(data_files_dir)
        if not os.path.exists(image_files_dir):
            SlTrace.lg(f'__file__:{__file__}')
            src_dir = os.path.dirname(os.path.abspath(__file__))
            SlTrace.lg(f"Assuming images are in src_dir")
            SlTrace.lg(f'src_dir:{src_dir}')
            prj_dir = os.path.dirname(src_dir)
            SlTrace.lg(f'prj_dir:{prj_dir}')
            image_dir = prj_dir
        self.image_dir = os.path.abspath(image_dir)
        SlTrace.lg(f"image_dir:{image_dir}")
        self.select_image_hash = ImageHash(image_dir=self.image_dir)
        self.select_image_files = self.select_image_hash.get_image_files()
        """ Marker images
            stored at twice size to facilitate rotation without
            loss of picture
            NOTE: needs work to support side size changes
        """
        self.marker_image_hash = ImageHash(image_dir=self.image_dir)
        self.marker_image_files = self.select_image_hash.get_image_files()
        self.image_index = len(self.marker_image_files)    # will wrap to 0
        self.photo_images = {}      # Keeping references
        self.marker_image_tags = []
        self.image_chosen = None 
            
    def ignore_key(self):
        """ ignore key
        """
        self.trace("ignore key")
    
    def add_custom_color(self, colr):
        """ Add new custom color
        :colr: new custom color
        """
        self.color_current = "2"
        self.custom_colors.append(colr)
        self.color_index = len(self.custom_colors)-1
        self.set_color()
                
    def set_color(self, colr=None, changing=None):
        """ set color, with no move
        :colr: new color
             default: use current color(w,2, or color string
            based on:
            self.color_current:
                w : rotate through colors[], using self.color_index
                2 : rotate though self.custom_colors[], using self.color_index
                other : use self.color_current
            self.color_index: index within
                w : colors[]
                2 : self.custom_colors
        :colr: color
                w : set current color to w standard
                2 : set current color to 2 custom
                other : set self.color_current to colr
        :changing: True - color change
                    False - color remains constant
                    default: use self.color_changing
        """
        if changing is None:
            changing = self.color_changing
            
        if colr is None:
            if self.color_current is None:
                return
            else:
                colr = self.color_current 
        self.trace(f"set_color:{colr}")
        if colr == "w":
            self.color_current = "w"
            self.color_changing = True
        elif colr == "2" or colr == "=":
            self.color_current = "2"
            self.color_changing = True
        else:
            self.color_current = colr
            self.color_changing = changing
        new_color = self.next_color()    
        self.tu.color(new_color)

    def next_color(self, colr=None, changing=None):
        """ Get next color based on color_current, color_changing
        :colr: color
                default: use self.color_current
        :changing: is color changing
                default: use self.color_changing
        """
        if colr is None:
            colr = self.color_current
        self.color_current = colr
        if changing is None:
            changing = self.color_changing
        self.color_changing = changing
        if self.color_current == 'w':
            if self.color_changing:
                self.color_index += 1
            if self.color_index >= len(self.colors):
                self.color_index = 0        # wrap around
            new_color = self.colors[self.color_index]
        elif self.color_current == '2':
            if changing:
                self.color_index += 1
            if self.color_index >= len(self.custom_colors):
                self.color_index = 0
            new_color = self.custom_colors[self.color_index]
        else:
            new_color = self.color_current
            if type(new_color) != str:
                SlTrace.report(f"new_color:{new_color} not str")
                return
        SlTrace.lg(f"new_color:{new_color}"
                   f" color_current:{self.color_current}"
                   f" color_index:{self.color_index}"
                   f" color_changing:{self.color_changing}")
        return new_color
                
    def set_visible_color(self, colr):
        """ Set visible color based on colr
        :colr: color to be
                - set invisible (white)
                + set visible current color
        """
        if colr == "-":
            self.move_minus()
        elif colr == "+":
            self.move_plus()
        else:
            self.set_color(colr)

    def marker_set(self, marker=None, changing=None, choose=None):
        """ Event marker setting
        :marker: marker to set
        :changing: auto changing markers
        :choose: True: prompt user for marker
        """
        if choose:
            """ Prompt user for marker
            """
            x0 = 300
            y0 = 400
            width = 200
            height = 400
            SlTrace.lg(f"x0={x0}, y0={y0}, width={width}, height={height}", "select_list")

            app = SelectList(items=self.select_image_files, image_hash=self.select_image_hash,
                             default_to_files=True,
                             title="Marker Images",
                             position=(x0, y0),
                             size=(width, height))
            selected_field = app.get_selected(return_text=True)
            SlTrace.lg(f"image_image: selected_field:{selected_field}")
            if selected_field is None:
                return
            
            self.image_chosen = self.image_file_to_info(selected_field)
            if self.image_chosen is None:
                SlTrace.report(f"Sorry, can't load image {selected_field}")
                return

            self.marker_chosen = selected_field
            SlTrace.lg(f"self.image_chosen={self.image_chosen}")
            self.set_marker(marker="image", changing=False)
        else:
            self.set_marker(marker=marker, changing=changing)
            
                        
    def set_marker(self, marker=None, changing=None):
        """ set set curent marker
        marker type , e.g. line, shape, image
        is done via do_marker()
        
        :marker: new marker
             default: use current marker
            based on:
            self.marker_current and self.marker_changing
        """
        if changing is None:
            changing = self.marker_changing
        marker = self.next_marker(marker=marker, changing = changing)
        self.marker_current = marker
        self.trace(f"set_marker:{marker}")
        

    def next_marker(self, marker=None, changing=None):
        """ Get next marker
        :marker: desired marker, if one
                default:
                
        :changing: are the markers changing
                default: use self.marker_changing
                
        """
        if changing is None:
            changing = self.marker_changing
        self.marker_changing = changing
        if marker is None:
            marker = self.marker_current
        self.marker_current = marker
        if changing:
            if marker in self.marker_order:
                self.marker_index = self.marker_order.find(marker)
                self.marker_index += 1
                if self.marker_index >= len(self.marker_order):
                    self.marker_index = 0
                self.marker_current = self.marker_order[self.marker_index]
        return self.marker_current
    
    def draw_postaction(self):
        """ drawing action that
        changes location
        """
        self.new_pendown = False
        self.cur_x, self.cur_y = self.tu.position()
        self.start_animation()
        
    def draw_preaction(self):
        """ Before drawing action
        """
        self.stop_animation()
        self.draw_undo_counts.append(self.tu.undobufferentries())
        self.moves_canvas_tags.append([])   # start move canvas tag list
        
        self.x_cor = self.tu.xcor()
        self.y_cor = self.tu.ycor()
        self.set_color()
        self.set_marker()
        self.move_current = MoveInfo(self)

    def stop_animation(self):
        """ Stop animation (speed up)
        """
        self.tu_screen_delay = self.tu_screen.delay()
        self.tu_screen.delay(0)                # stop animation delay

    def start_animation(self):
        """ Start animation (slow to previous)
        """
        self.tu_screen.update()
        self.tu_screen.delay(self.tu_screen_delay)        # Restore animation delay
        
    def do_marker(self, marker=None):
        """ display, if pendown, current marker
        :marker: symbol/shape/image to use
                default:self.marker_current
        """
        if marker is None:
            marker = self.marker_current
        if self.marker_current == "line":
            self.do_line()
        elif self.marker_current == "shape":
            self.do_shape()
        elif self.marker_current == "image":
            self.do_image()
        else:
            SlTrace.lg(f"do_marker: unrecognized marker:{marker} - ignored")

    def do_line(self):
        """ do line marker
        """
        self.shape_line()
        
    def do_shape(self):
        """ Do shape marker
        """
        self.shape_next()
        
    def do_image(self, image_info=None, move_to_next=True):
        """ Do image marker
        """
        if self.tu.isdown():
            self.do_image_display(image_info=image_info)
        if move_to_next:
            self.jump_to_next()
    
    def do_image_display(self, image_info=None):
        """ Do image marker display
        """
        self.image_heading_default = 0
        if image_info is None:
            image_key, image = self.get_marker_image()
        self.marker_image_width = self.side*2   # allow rotation
        self.marker_image_width = self.side     # Workaround untill...
        self.marker_image_height = self.marker_image_width
        image = image.resize((int(self.marker_image_width), int(self.marker_image_height)),
                             Image.ANTIALIAS)
        rotation = self.heading + self.image_heading_default
        image = image.rotate(rotation)
        self.photo_image = ImageTk.PhotoImage(image)
        if image_key not in self.photo_images:
            self.photo_images[image_key] = []
        self.photo_images[image_key].append(self.photo_image)
        canvas_x, canvas_y = self.tu_canvas_coords((self.tu.position()))
        #canvas_x, canvas_y = self.x_cor, self.y_cor
        #canvas_x, canvas_y = 0,0
        #test_tag = self.tu_canvas.create_line(0,0,300,300)
        #test_tag2 = self.tu_canvas.create_line(0,0,100,200)
        #test_tag3 = self.tu_canvas.create_line(0,0,-100,-200)
        canvas_width = self.tu_canvas.winfo_width()
        canvas_height = self.tu_canvas.winfo_height()
        adj_x = -canvas_width/2
        adj_y = -canvas_height/2
        canvas_x += adj_x
        canvas_y += adj_y
        self.marker_image_tag = self.tu_canvas.create_image(
            canvas_x, canvas_y,
            ###anchor="nw",
            image=self.photo_image)
        """ Save for undo, but also for image reference """
        if len(self.moves_canvas_tags) == 0:
            self.moves_canvas_tags.append([])   # empty - add list
        self.moves_canvas_tags[-1].append(self.marker_image_tag)

        self.tu_canvas.update()
        
    def image_next(self, image=None, choose=None):
        """ Go to next image and change per image parameter
            Sets self.image_chosen
        :image:
            'nextone' - select next image as the one
            'rotate' change image and make new image
            'rotateinplace' - change image of current marker
            'same" keep current image
            default: 'rotateinplace' 
        """
        if image is None:
            image = 'rotateinplace'
        elif image == 'same':
            self.set_marker(marker="image", changing=False)
        elif image is not None and image != "" and image in self.marker_image_files:
                self.image_chosen = self.pick_next_image()
        elif choose:
            SlTrace.lg("Don't know how to choose images yet")
            return
        elif image is None or image == "":
            if self.image_current == "rotate":
                self.image_chosen = self.pick_next_image()
            elif self.image_current in self.images:
                self.image_chosen = self.image_current     
        elif image == "nextone":
            self.set_marker(marker="image")
            self.image_chosen = self.pick_next_image()
            self.image_current = self.image_chosen
            self.erase_move()
        elif image == "rotate":
            self.set_marker(marker="image")
            self.image_current = "rotate"
            self.image_chosen = self.pick_next_image()
        elif image == "rotateinplace":
            self.set_marker(marker="image")
            self.image_current = "rotate"
            self.erase_move()
            self.image_chosen = self.pick_next_image()
        else:
            self.image_chosen = self.pick_next_image()
        self.draw_preaction()
        self.set_pen_state()
        self.do_image()
        self.set_pen_state()


    def pick_next_image(self):
        """ Get next from image list (self.image_files)
        :returns: imageinfo (key, image)
        """
        self.select_image_files
        nimage = len(self.select_image_files)
        self.image_index += 1
        if self.image_index >= nimage:
            self.image_index = 0
        display_file = self.select_image_files[self.image_index]
        return self.image_file_to_info(display_file)

    def image_file_to_info(self, display_file):
        """ Convert file name(key) to image_info(key, image)
        :display_file: display file name/key
        :returns: image_info (key, image)
                    None if can't get it
        """
        image = self.marker_image_hash.get_image(
                            key=display_file,
                            photoimage=False)
        if image is None:
            SlTrace.report(f"Can't load image:{display_file}")
            return None
        
        return (display_file, image)
        
    def get_marker_image(self, image_name=None):
        """ get image based on image type/name
            For now just give latest chosen image
            :returns: image_info (key, image)
        """
        image_info = self.image_chosen
        return image_info
    
    def do_pendown(self):
        """ Do pendown and remember
        """
        self.new_pendown = True
        self.tu.pendown()
    
    def do_backward(self, side):
        """ Do backward operation
        :side: distance
        """
        self.draw_preaction()
        self.tu.backward(side)
        self.draw_postaction()
        
    def do_forward(self, side):
        self.draw_preaction()
        self.tu.forward(side)
        self.draw_postaction()
        
    def clear_all(self):
        """ Clear screen
        """
        self.tu.speed("fastest")
        self.stop_animation()       # Record speed
        self.start_animation()      # Restart animation
        self.nk = 0
        self.new_pendown = True      # Set to indicate pen just down
        self.is_pendown_orig = True
        self.is_pendown = self.is_pendown_orig       # Drawing pen state
        self.heading_orig = 0
        self.heading = self.heading_orig             # Current heading
        self.side_orig = 100
        self.side = self.side_orig              # Default distance
        self.current_width_orig = 2
        self.current_width = self.current_width_orig  # Current line width
        self.color_changing = True
        self.color_current_orig = "w"     # Default to changing std colors
        self.color_index_orig = 0         # index of current color
        self.color_index = self.color_index_orig
        self.color_current = self.color_current_orig
        self.nth_shape = 0          # Number of previous shapes
        self.shape_index_orig = 0
        self.shape_index = self.shape_index_orig
        self.shape_current_orig = "line"
        self.shape_current = self.shape_current_orig
        
        self.marker_changing = False     # Unchanging
        self.marker_index_orig = 0
        self.marker_index = self.marker_index_orig
        self.marker_current = self.marker_order[self.marker_index]
        """ Undo canvas (e.g. image) actions if any """
        while len(self.moves_canvas_tags) > 0:
            canvas_tags = self.moves_canvas_tags.pop()
            for canvas_tag in canvas_tags:
                self.tu_canvas.delete(canvas_tag)
        self.image_index = len(self.marker_image_files)    # will wrap to 0
        self.image_current = "rotate"
        self.marker_image_tags = []
        self.photo_images = {}      # Keeping references
        

        self.draw_preaction()
        self.tu.clear()
        self.tu.penup()
        self.tu.home()
        self.do_pendown()
        self.draw_postaction()
        
    def col(self, colr):
        """ Change color/line attributes as a move
        :colr: color string, e.g. "red", "orange"
                =[color spec]
        """
        if colr is None:
            colr = self.color_current
        if colr == "w":
            self.color_current = "w"
            self.color_changing = True
        elif colr == "2":
            self.color_current = "2"
            self.color_changing = True 
        elif colr == "-":
            self.set_pen_state(False)
        elif colr == "+":
            self.set_pen_state(True)
        elif colr.startswith("="):
            color_spec = colr[1:]       # Remainder, if any is spec
            if color_spec == "":
                color_choice = colorchooser.askcolor()
                self.trace(f"color_choice: {color_choice}")            
                if color_choice[1] is None:
                    return
                self.add_custom_color(color_choice[1])
                return
            
            else:
                colr = color_spec
            self.color_current = colr            
            self.color_changing = False       # Force using current color
        else:        
            self.color_current = colr
            if colr in self.colors:
                self.color_index = self.colors.index(colr)
            else:
                self.color_changing = False  # Not in list set as fixed
        ###self.set_visible_color(colr)
        
    def col_r(self):
        self.col("red")
    
    def col_o(self):
        self.col("orange")
    
    def col_y(self):
        self.col("yellow")
    
    def col_g(self):
        self.col("green")
    
    def col_b(self):
        self.col("blue")
    
    def col_i(self):
        self.col("indigo")
    
    def col_v(self):
        self.col("violet")
    
    def col_w(self):
        self.col("w")    # Changing color
    def col_minus(self):
        """ - => invisible(white)
        """
        self.col("-")
        
    def col_plus(self):
        """ + => visible (previous color)
        """
        self.col("+")
        
    def col_equals(self):
        """ = => color chooser for current color
        """
        self.color_set(choose=True)
    
    def color_set(self, colr=None, choose=None):
        """ Set color specification
        :colr: color string
        :choose: prompt user for color default: no choice
        """
        if choose:
            self.col("=")
        else:
            self.col(colr)
            
    def line_set(self, leng=None, wid=None, choose=None):
        """Set line specification (size)
        :leng: line length default: current length
        :wid: line width default: current width
        :choose: Prompt user to choose default: use current
        """
        if choose:
            while True:
                try:
                    inp = self.tu.textinput("Line Size",f"Enter line length[{self.side}]")
                    if inp is None or inp == "":                    
                        inp = str(self.side)
                    self.side = int(inp)
                    break
                except:
                    print(f"{inp} not a legal number - please try again")
                
            while True:
                try:
                    inp = self.tu.textinput("Line Size",
                                     f"Enter line width[{self.current_width}]")
                    if inp is None or inp == "":                    
                        inp = str(self.current_width)
                    self.current_width = int(inp)
    
                    break
                except:
                    print(f"{inp} not a legal number - please try again")
            self.trace(f"line length:{self.side} width: {self.current_width}")
            self.tu.listen()        # textinput does its own keybd capture
        else:
            if leng is None or (type(leng) == str and leng == ""):
                leng_new = self.side
            else:
                leng_new = int(leng)
            self.side = leng_new
            if wid is None or (type(wid) == str and wid == ""):
                wid_new = self.current_width
            else:
                self.current_width = int(wid)
        self.tu.width(self.current_width)
        self.trace(f"End of line_set width:{self.current_width}, leng:{self.side}")
            
    def moveto_set(self, x=None, y=None, choose=None):
        """ move pen to location
        :x: move to x coordinate default: leave x unchanged
            int or str -> converted to int
        :y: move to y coordinate default: leave  y unchanged
            int or str -> converted to int
        :choose: prompt user for location default: don't ask
        """
        x_cur = self.tu.xcor()
        y_cur = self.tu.ycor()
        if choose:
            while True:
                try:
                    inp = self.tu.textinput("X",f"Enter x position[{x_cur:.0f}]")
                    if inp is None or inp == "":                    
                        inp = str(int(x_cur))
                    x_new = int(inp)
                    break
                except:
                    print(f"{inp} not a legal number - please try again")
                
            while True:
                try:
                    inp = self.tu.textinput("Y", f"Enter y position[{y_cur:.0f}]")
                    if inp is None or inp == "":                    
                         inp = str(int(y_cur))
                    y_new = int(inp)
    
                    break
                except:
                    print(f"{inp} not a legal number - please try again")
            self.trace(f"Position x:{x_new} y: {y_new}")
            self.tu.listen()        # textinput does its own keybd capture
        else:
            if x is None or (type(x) == str and x == ""):
                x_new = x_cur
            else:
                x_new = int(x)
            if y is None or (type(y) == str and y == ""):
                y_new = y_cur
            else:
                y_new = int(y)
        self.move_to(x_new, y_new)
        self.trace(f"Position x:{x_new} y: {y_new}")
        self.trace(f"End of move_set key")

    def move_to(self, x,  y):
        """ Move to position
        :x: new x position
        :y: new y position
        """
        self.x_cur = x
        self.y_cur = y
        self.tu.setposition(x, y)
    
    def line_setting(self):
        self.line_set(choose=True)
    
    def moveto_setting(self):
        self.moveto_set(choose=True)
    
    def set_pen_state(self, pendwn=None):
        """ Set pen to or back to drawing state
                self.is_pendown
        :pendown: target pen state
                default: current  drawing state
        """
        pen_target = self.is_pendown
        if pendwn is not None:
            pen_target = pendwn
            
        if pen_target:
            if not self.tu.isdown():
                self.tu.pendown()
        else:
            if self.tu.isdown():
                self.tu.penup()
        self.is_pendown = pen_target
                
    def jump_to(self, heading=None, distance=0,
                pendwn=False):
        """ Move pen from current (immediate) location
            :heading: move direction default: current heading
            :distance: distance in direction of heading
            :pendwn: True lower pen, False Raise pen
                    Leave pen in original state after
                    default: raise pen
        """
        if pendwn:
            if not self.tu.isdown():
                self.tu.pendown()
        else:
            if self.tu.isdown():
                self.tu.penup()
        if heading is None:
            heading = self.heading
        self.tu.setheading(heading)
        self.tu.forward(distance)
        self.tu.setheading(self.heading)        # Restore heading       
        self.set_pen_state()            # Restore pen state
                
    def jump_to_next(self):
        """ Move to next position, invisibly
        """
        
        if self.tu.isdown():
            self.tu.penup()
        self.tu.setheading(self.heading)
        theta = math.radians(self.heading)
        x_chg = self.side*math.cos(theta)
        y_chg = self.side*math.sin(theta)
        new_x = self.x_cor + x_chg
        new_y = self.y_cor + y_chg
        self.move_to(new_x, new_y) 
        self.set_pen_state()
        
    def shape_circle(self):
        """ Display circle
            Circle of current side diameter, in direction of current heading,
            color,...
        """
        #self.erase_move()
        cir_heading = self.heading + 90
        self.tu.setheading(cir_heading)
        self.tu.circle(-self.side/2)
        self.tu.setheading(self.heading)
        self.jump_to_next()

    def shape_image(self, name=None):
        """ Display image/animal
        D                C
                  
              image
                  
                  
        A                B
            image's right side in direction of current heading,
            color,...
        """
        #self.erase_move()
        #self.tu.begin_fill()
        self.jump_to(heading=self.heading, distance=self.side/2)
        self.jump_to_next()

    def shape_square(self):
        """ Display square
        D                C
                  
                  
                  
                  
        A                B
            square in direction of current heading,
            color,...
        """
        #self.erase_move()
        #self.tu.begin_fill()
        self.jump_to(heading=self.heading-90, distance=self.side/2)
        self.tu.forward(self.side)
        our_heading = self.heading
        for _ in range(3):
            our_heading += 90     # 90,90,90
            self.tu.setheading(our_heading)
            self.tu.forward(self.side)
        self.tu.end_fill()
        self.tu.setheading(self.heading)    # Insure going right direction
        ###self.jump_to(heading=self.heading+90, distance=self.side/2)
        self.jump_to_next()

    def shape_line(self):
        SlTrace.lg("shape_line")
        """ Display line
            line, in direction of current heading,
            color,...
        """
        #self.erase_move()
        
        SlTrace.lg(f"shape_line from: x_cor,y_cor:{self.tu.xcor():.0f}, {self.tu.ycor():.0f}")
        self.tu.setheading(self.heading)
        self.tu.forward(self.side)
        SlTrace.lg(f"shape_line  to: x_cor,y_cor:{self.tu.xcor():.0f}, {self.tu.ycor():.0f}")
        
                
    def shape_triangle(self):
        """ Display triangle
        B          A


        A            C

                  
        D
            Triangle in direction of current heading,
            color,...
        """
        #self.erase_move()
        our_heading = self.heading+90
        self.jump_to(heading=our_heading,
                      distance=self.side/2)
        #self.tu.begin_fill()
        for _ in range(3):
            our_heading -= 120     # 60,60,60
            self.tu.setheading(our_heading)
            self.tu.forward(self.side)
        self.tu.end_fill()
        ###self.jump_to(heading=self.heading-90,
        ###              distance=self.side/2)
        self.tu.setheading(self.heading)    # Insure going right direction
        ###self.jump_to(heading=self.heading-90, distance=self.side/2)
        self.jump_to_next()

    def pick_next_shape(self):
        """ Get next from shape list
        :returns: return next shape
        """
        if self.nth_shape > 0:
            self.shape_index += 1
        self.nth_shape  += 1
        nshape = len(self.shape_order)
        if self.shape_index >= nshape:
            self.shape_index = 0
        display_shape = self.shape_order[self.shape_index]
        return display_shape

    def set_shape(self, shape=None, choose=None, changing=None):
        """ Set shape - not much - initially to be in line with
            set_marker
        """
        self.shape_next(shape=shape, choose=choose)

    def marker_next(self):
        """ Go to next marker if that is changing,
            else to the next shape if that is changing
            else to the next line
            and do the appropriate marker/shape/line
        """
        if self.marker_changing:
            self.set_marker(changing=self.marker_changing)
        if self.marker_current == "image":
            self.do_marker()
        elif self.marker_current == "shape":
            self.color_set()
            self.shape_next()
        elif self.marker_current == "line":
            self.color_set()
            self.do_line()
        else:
            SlTrace.lg(f"Unrecognized marker: {self.marker_current} - ignored")

    def line_next(self, shape=None, choose=None):
        """ Set line "shape"
        """
        self.set_marker("line")
        
    def shape_next(self, shape=None, choose=None):
        """ Go to next shape and change current side to
        that shape
        :shape:
            'nextone' - select next shape as the one
            'rotate' change shape and make new shape
            'rotateinplace' - change shape of current image 
        """
        if shape is not None and shape != "" and shape in self.shapes:
                display_shape = shape
                self.shape_current = display_shape
        elif choose:
            SlTrace.lg("Don't know how to choose shapes yet")
            return
        elif shape is None or shape == "":
            if self.shape_current == "rotate":
                display_shape = self.pick_next_shape()
            elif self.shape_current in self.shapes:
                display_shape = self.shape_current     
        elif shape == "nextone":
            self.set_marker(marker="shape")
            display_shape = self.pick_next_shape()
            self.shape_current = display_shape
            self.erase_move()
        elif shape == "rotate":
            self.set_marker(marker="shape")
            self.shape_current = "rotate"
            display_shape = self.pick_next_shape()
        elif shape == "rotateinplace":
            self.set_marker(marker="shape")
            self.shape_current = "rotate"
            self.erase_move()
            display_shape = self.pick_next_shape()
        else:
            display_shape = self.shape_current
        shape_fun = self.shapes[display_shape]
        self.draw_preaction()
        self.set_pen_state()
        shape_fun()
        self.set_pen_state()
        
    def shape_change(self, shape_str=None, choose=None):
        """Set shape
        :shape_str: shape string (name)
            'next' - go to next
            'rotate' - rotate through shapes as movement
            'line'  - line
            'circle' -  circle
            'triangle' - triangle pointing in direction
            'square' - square
            
        :choose: Prompt user to choose
        """
        if choose:
            print("SORRY - choose shapes not yet operational - see  you soon!")
            return
            
            while True:
                try:
                    inp = self.tu.textinput("shape",
                                    f"Enter shape[{self.shape_current}]")
                    if inp is None or inp == "":                    
                        inp = self.shape_current
                    self.shape_current = inp
                    break
                except:
                    print(f"{inp} not a legal number - please try again")
                
            while True:
                try:
                    inp = self.tu.textinput("Line Size",
                                     f"Enter line width[{self.current_width}]")
                    if inp is None or inp == "":                    
                        inp = str(self.current_width)
                    self.current_width = int(inp)
    
                    break
                except:
                    print(f"{inp} not a legal number - please try again")
            self.trace(f"line length:{self.side} width: {self.current_width}")
            self.tu.listen()        # textinput does its own keybd capture
        else:
            if shape_str == 'next':
                self.shape_next()
            elif shape_str == 'rotate':
                self.shape_rotate()
            elif shape_str == 'line':
                self.shape_line()
            elif shape_str == 'circle':
                self.shape_circle()
            elif shape_str == 'triangle':
                self.shape_triangle()
            elif shape_str == 'square':
                self.shape_square()
        self.trace(f"End of shape set shape: {self.shape_current}")
    
    def erase_move(self):
        """ Erase last move
            Currently just a simple turtle undo but soon to be more robust 
        """
        self.trace("erase_side")
        self.draw_undo()
        
    def erase_side(self):
        """ Erase side, for possible overwriting
        width, length, and heading remain unchanged
        Position is at beginning of original line
        """
        self.trace("erase_side")
        self.tu.undo()
        
    def move(self, direct):
        """ move a general direction
        using current shape
        :direct: direction Up, Left, Right, Down
        """
        self.trace(f"move: '{direct}'")
        self.draw_preaction()
        if direct == 'Up':
            self.heading = 90
        elif direct == 'Left':
            self.heading = 180
        elif direct == 'Right':
            self.heading = 0
        elif direct == 'Down':
            self.heading = 270
        elif direct in "12346789": # Digit moves
            dig2head = {'6':0, '9':45, '8':90,
                        '7':135, '4':180, '1':225,
                        '2':270, '3':315, '6':0,
                        }
            self.heading = dig2head[direct]
        elif direct == '5':     # rotate 45 deg left
            self.heading += 45
        elif direct == '0':     # rotate 45 deg right
            self.heading -= 45
        elif direct == 'space':
            self.erase_side()
            self.heading += 180
        elif direct == 'c':
            self.tu.penup()
            self.tu.home()
            self.do_pendown()
            return
        
        else:
            print(f"Sorry, I don't know what '{direct}' means")
            return      # Do nothing
    
        if self.heading < 0 or self.heading >= 360:
            self.heading = self.heading % 360    # Keep in 0 < 360
        '''
        if self.color_current == "w":    # Changing color
            ###self.trace(f"check for 'w': self.color_current:{self.color_current}")
            self.color_index += 1
            self.color_index = self.color_index % len(self.colors)
        if self.color_index == -1:
            self.set_visible_color(self.color_current)
        else:    
            self.set_visible_color(self.colors[self.color_index])
        '''
        self.tu.setheading(self.heading)
        ###self.do_forward(self.side)
        self.marker_next()
        self.draw_postaction()
        
    def move_up(self):
        self.move('Up')
        
    def move_left(self):
        self.move('Left')
        
    def move_right(self):
        self.move('Right')
        
    def move_down(self):
        self.move('Down')
    
    def move_minus(self):
        self.trace("move_minus")
        self.set_pen_state(False)
    
    def check(self, key):
        print(f"\n#{key}")  # Force even if self.trace is False
        print("check")
    
    def checking(self):
        """ Debugging catch
        """
        self.check("check")
    
    def dotrace(self, key):
        """ Flip tracing setting
        """
        
        self.do_trace = not self.do_trace
        
    def tracing(self):
        """ Debugging catch
        """
        self.dotrace("trace")
        
    def move_plus(self):
        self.trace("move_plus")
        self.set_pen_state(True)
        
    def move_0(self):
        self.move('0')
    
    def move_1(self):
        self.move('1')
    
    def move_2(self):
        self.move('2')
    
    def move_3(self):
        self.move('3')
    
    def move_4(self):
        self.move('4')
    
    def move_5(self):
        self.move('5')
    
    def move_6(self):
        self.move('6')
    
    def move_7(self):
        self.move('7')
    
    def move_8(self):
        self.move('8')
    
    def move_9(self):
        self.move('9')
    
    def move_space(self):
        self.move('space')
    
    def move_c(self):
        self.move('c')

    def line_narrow(self):
        if self.current_width > 2:
            if not self.new_pendown:
                self.erase_move()      # Erase current leg
            self.current_width -= 2
            self.tu.width(self.current_width)
            self.shape_next()

    def line_widen(self):
        if not self.new_pendown:
            self.erase_move()      # Erase current leg
        self.current_width += 2
        self.tu.width(self.current_width)
        self.shape_next()
            
    def marker_enlarge(self):       # 't'
        move = self.move_current
        if move.marker == "line":
            if not self.new_pendown:
                self.erase_move()      # Erase current leg
            self.side *= 1.1
            self.shape_next()
        elif move.marker == "shape":
            if not self.new_pendown:
                self.erase_move()      # Erase current leg
            self.side *= 1.1
            self.shape_next()
        elif move.marker == "image":
            if not self.new_pendown:
                self.erase_move()      # Erase current leg
            self.side *= 1.1
            self.image_next('same')
        
    def marker_shrink(self):
        """ Change current and subsequent lines to a thinner line
        """
        move = self.move_current
        if move.marker == "line":
            if not self.new_pendown:
                self.erase_move()      # Erase current leg
            self.side /= 1.1
            self.shape_next()
        elif move.marker == "shape":
            if not self.new_pendown:
                self.erase_move()      # Erase current leg
            self.side /= 1.1
            self.shape_next()
        elif move.marker == "image":
            if not self.new_pendown:
                self.erase_move()      # Erase current leg
            self.side /= 1.1
            self.image_next('same')
                
    def make_side(self, sz):
        """ Make side (move) dimension
        :sz: new side size
        """
        self.side = sz
    
    def enlarge_side(self):
        """ Enlarge size a bit
        """
        if not self.new_pendown:
            self.tu.undo()      # Remove previous side
        self.make_side(self.side*(1+self.enlarge_fraction))
        self.do_forward(self.side)
    
    def reduce_side(self):
        """ Reduce size back to before enlarge_size
        """
        if not self.new_pendown:
            self.tu.undo()
        self.make_side(self.side/(1+self.enlarge_fraction))
        self.do_forward(self.side)

    def rotate_marker(self, angle=None):
        """ Rotate current (last created) marker
        :angle: counter clockwise angle (degrees)
                default: 45 degrees
        """
        if angle is None:
            angle = 45
            
        self.erase_move()
        
    def move_shift(self):
        pass
    def expand_key(self, key):
        """ Expand key to functional form: name(arg,arg,...)
        """
        if re.match(r'^\w+\(.*\)', key):
            return key      # Already in function form
        
        for short_name in self.key_fun_name:
            if key.startswith(short_name):
                fun_name = self.key_fun_name[short_name]
                arg_str = key[len(short_name):]
                name = f"{fun_name}({arg_str})"
                return name
            
        return key      # Unchanged
        
    nk = 0          # length key spaces so far
    def print_key(self, key):
        """ Print key
        :key: key string
        """
        if self.nk > 0:
            if self.nk > 40:
                print()
                self.nk = 0
            else:
                print(";", end="")
        exp_key = self.expand_key(key)
        self.nk += len(exp_key)
        print(exp_key, end="")
        
    def do_key(self, key):
        """ Process key by
        calling keyfun, echoing key
        :key: key (descriptive string) pressed
                or special "key" e.g. =<color spec>
        """
        if key == 'check':
            self.print_key(key)
            self.check(key)
            return
        
        fun_mat = re.match(r'^(\w+)\((.*)\)$', key)
        if fun_mat:
            self.print_key(key)
            args_str = fun_mat.group(2)
            fun_name = fun_mat.group(1)
            if fun_name in self.fun_by_name:
                fun_fun = self.fun_by_name[fun_name]
            else:
                print(f"We don't recognize function {fun_name} in {key}")
                return 
            
            fun_args = re.split(r'\s*,\s*', args_str)
            fun_fun(*fun_args)
            return
        
        if re.match(r'^moveto:?.*', key):
            self.print_key(key)
            self.moveto_set(key)        # move with/without specification
            return
        
        if re.match(r'^=.+', key):
            self.print_key(key)
            self.col(key)        # color with specification
            return
        
        if re.match(r'^:.+', key):
            self.print_key(key)
            self.line_set(key)        # color with specification
            return
        
        
        elif key in self.bound_keys:
            keyfun = self.bound_keys[key]
        else:
            print(f"key '{key}' is not yet bound - ignored")
            return
        self.print_key(key)
        keyfun()
    
    
    def bind_key(self, keyfun, key):
        """ bind/unbind key to function
        Binds key to function, if present
        else unbind key
        :keyfun: "No arg" function bound to key
        :key: key pressed
        """
        if keyfun is None:
            del self.bound_keys[key]        
        else:
            self.bound_keys[key] = keyfun  # First or New binding
            
        self.tu_screen.onkey(lambda  : self.do_key(key), key)
    
    def do_keys(self, keystr):
        """ Do action based on keystr
            comas or newline used as separators
            Empty areas between separators are ignored
            lines starting with # are printed but removed
            text starting with "\s+.*" are removed
        :keystr: string of key(values) must match track_key
                interpretations e.g. Up for up-arrow,
                minus for "-"
        """
        rawkeylines = keystr.split('\n')
        code_keylines = []
        for rawkeyline in rawkeylines:
            if re.match(r'^\s*#', rawkeyline):
                code_keylines.append(rawkeyline)    # Pass comment line
                continue
            eol_com_match = re.match(r'^(.*\S)(\s+#.+)$', rawkeyline)
            if eol_com_match:
                code_keylines.append(eol_com_match.group(1))
                code_keylines.append(eol_com_match.group(2)) # remove trailing comment
                continue 
            code_keylines.append(rawkeyline)
        for code_keyline in code_keylines:
            if re.match(r'\s*#', code_keyline):
                print(f"\n{code_keyline}")
                continue
            keys = re.split(r'\s*;\s*|\s+', code_keyline)
            for key in keys:
                if key != "":
                    self.do_key(key)

    def set_key_mapping(self):
        """ Setup key to function mapping
        TBD
        """
        # key, function [, *parameters], 
        key_mapping = [
            ['h', self.help],
            ]
                    
    def track_key(self, keyfun, key):
        """ connect key with function
        key is echoed whenever pressed
        :keyfun: "No argument" function to be executed when key pressed
        :key: key text
        """
        self.bind_key(keyfun, key)
        
    def track_keys(self):
        """ Setup key tracking
        """    
        self.track_key(self.marker_shrink, 'a')
        self.track_key(self.col_b, 'b')
        self.track_key(self.move_c, 'c')
        self.track_key((lambda : self.shape_next('nextone')), 'd')
        self.track_key(self.line_next, 'f')
        self.track_key(self.col_g, 'g')
        self.track_key(self.help, 'h')        
        self.track_key(self.col_i, 'i')
        self.track_key((lambda : self.marker_set(choose=True)), 'j')
        self.track_key((lambda : self.image_next('rotateinplace')), 'k')
        self.track_key(self.moveto_setting, 'm')
        self.track_key(self.col_o, 'o')
        self.track_key(self.marker_enlarge, 'q')
        self.track_key(self.col_r, 'r')
        self.track_key((lambda : self.shape_next('rotateinplace')), 's')
        self.track_key(self.line_widen, 't')
        self.track_key(self.draw_undo, 'u')
        self.track_key(self.col_v, 'v')
        self.track_key(self.col_w, 'w')   # Changing colors
        self.track_key(self.line_narrow, 'x')
        self.track_key(self.col_y, 'y')
        self.track_key(self.clear_all, 'z')
        self.track_key(self.move_up, 'Up')
        self.track_key(self.move_left, 'Left')
        self.track_key(self.move_right, 'Right')
        self.track_key(self.move_down, 'Down')
        self.track_key(self.move_minus, 'minus')
        self.track_key(self.move_plus, 'plus')
        self.track_key(self.col_equals, '=')
        self.track_key(self.line_setting, ':')
        self.track_key(self.line_setting, ';')    # lower case :
        self.track_key(self.checking, '.')        # Converted to >
        self.track_key(self.tracing, '!')
        self.track_key(self.move_shift, '')
        self.track_key(self.move_space, 'space')
        self.track_key(self.move_0, '0')
        self.track_key(self.move_1, '1')
        self.track_key(self.move_2, '2')
        self.track_key(self.move_3, '3')
        self.track_key(self.move_4, '4')
        self.track_key(self.move_5, '5')
        self.track_key(self.move_6, '6')
        self.track_key(self.move_7, '7')
        self.track_key(self.move_8, '8')
        self.track_key(self.move_9, '9')
        

    def draw_undo(self):
        """ Undo most recent operation
        As the only handle we have on turtle objects
        is undobufferentries(), we save a stack of this
        count at the beginning of each opperation.
        Undo consists of calling undo while undobufferentries()
        returns a number greater than the stack entry
        count
        """
        """ Undo turtle actions, if any.  """
        if len(self.draw_undo_counts) > 0:        
            prev_count = self.draw_undo_counts.pop()
            while self.tu.undobufferentries() > prev_count:
                self.tu.undo()

        """ Undo canvas (e.g. image) actions if any """
        if len(self.moves_canvas_tags) > 0:
            canvas_tags = self.moves_canvas_tags.pop()
            for canvas_tag in canvas_tags:
                self.tu_canvas.delete(canvas_tag)
                
    def mouse_down (self, event):
        x_coord = event.x
        y_coord = event.y
        SlTrace.lg(f"canvas_x,y: {x_coord, y_coord}")

    def tu_canvas_coords(self, tu_coords=None):
        """ Canvas x coordinate
        :tu_coords: turtle coordinate pair
                default: use current
        :returns: canvas x_coordinates pair
        """
        if tu_coords is None:
            tu_coords = (self.x_cor, self.y_cor)
        x_cor, y_cor = tu_coords    
        canvas_width = self.tu_canvas.winfo_width()
        canvas_height = self.tu_canvas.winfo_height()
        x_coor = int(canvas_width/2 + x_cor)
        y_coor = int(canvas_height/2 - y_cor)        # canvas increases downward
        return (x_coor, y_coor)


if __name__ == "__main__":
    app = tk.Tk()   # initialise the tkinter app
    app.title("Keyboard Drawing")     # title
    app.config(bg='powder blue')    # background
    app.resizable(0, 0)     # disable resizeable property
    hello_str = None    # Use built in display
    #hello_str = ""      # Empty display
    kb_draw = KeyboardDraw(app, hello_drawing_str=hello_str)
    
    kb_draw.tu_screen.listen()
    tk.mainloop()
