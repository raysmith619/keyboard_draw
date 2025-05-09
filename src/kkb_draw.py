#kbd_draw.py    12Dec2020  crs
"""
Draw, given a python string
"""
import os
import sys
import re
import tkinter as tk
import argparse

from select_trace import SlTrace
from select_window import SelectWindow
from kbd_cmd_proc import KbdCmdProc

""" Using ScreenKbd
from screen_kbd import ScreenKbd
"""
from screen_kbd_flex import ScreenKbdFlex

from image_hash import ImageHash
from data_files import DataFiles

dir_name = os.path.dirname(__file__)
prj_dir = os.path.dirname(dir_name)
prj_dir = os.path.abspath(prj_dir)
image_dir = os.path.join(prj_dir, "images")
SlTrace.lg(f"images dir: {image_dir}")
if not os.path.isdir(image_dir):
    SlTrace.lg(f"directory: {image_dir} does not exists")
    exit(1)
    

class KbdDraw:

    IT_FILE = "it_file"     # image from file
    IT_TEXT = "it_text"     # image generated 
    
    def __init__(self,
                 keyboard=None,
                 ):
        """ Keyboard Drawing tool
        :keyboard: display
        """
        control_prefix = "KbdDraw"
        self.x_cor = 0 
        self.y_cor = 0 
        self.heading = 0
        self.color_current = "red"
        self.color_changing = True
        self.color_index = 0
    
            
        if hello_drawing_str == "TESTX":
            tx = width    # Test x dist
            ty = height    # y moves down
            x0 = 0; y0 = side
            x_end = x0 + tx
            y_end = y0 + ty
            hello_drawing_str = f"""
            print(===============================)
            """
            markers = [(0,0, "w"), (1,0,"x"), (1,1,"y"), (0,1,"z")]
            
            for marker in markers:
                xf,yf,st = marker
                x = x0 + tx*xf
                y = y0 + ty*yf
                hello_drawing_str += f"""
                print(x={x},y={y}:{st},marker:{xf}:{yf}:{st})
                moveto({x},{y});e;{st};END;dot()
                """
            hello_drawing_str += f"""
            print(===============================)
            """
            
        elif hello_drawing_str == "BUILTIN":
            hello_drawing_str = f"""
            # Beginning screen pattern
            # Add in Family
            #minus
            #line({side},{width})        # Set side, width
            moveto({x_start},{y_start})
            plus
            setnewline();F;a;m;i;l;y;END
            newline();a;l;e;x;END;image_file(family,alex);q
            newline();d;e;c;l;a;n;END;image_file(family,declan);q
            newline();a;v;e;r;y;END;image_file(family,avery);q
            newline();c;h;a;r;l;i;e;END;image_file(family,charlie);q
            """
            xx = False
            if xx:
                more = """
                ###    # Add in animals
                ###    k
                ###    plus
                ###    k;Right;a;a
                ###    k;Right;a:a
                ###    k;Right;a;a
                ###    k;Right;a;a
                ###    k;Right;a;a
                    
                # A bit of other stuff
                check
                shorten();shorten();shorten()
                newline();END;image_file(princesses,princess);q
                image_file(other_stuff,batman) 
                image_file(other_stuff,baseball) 

                 minus
                # HI in middle of screen
                shape(line)
                marker(line)
                shape(line)
                line({hi_side},{width})        # Set side, width
                moveto({hi_stuff_x},{hi_stuff_y})
                w
                plus
                check
                Down;Down;Down;Down;Down;Down;Down;Down
                Up;Up;Up;Up; Right;Right; Up;Up;Up;Up
                Down;Down;Down;Down;Down;Down;Down;Down
                minus;Right;Right
                
                plus
                Up;Up;Up;Up;Up;Up;Up;Up
                minus
                
                line({side},{width})        # Set side, width
                Down;Down;Right;plus
                """
                
                """
                # Line under
                minus
                line({side},{4})
                moveto({int(self.canvas_width/2-side)},{int(-self.canvas_height/2+side)})
                plus
                Left
                t;=#ff0000;shape(rotate)
                t;=#0ff000;shape()
                t;=#00ff00;shape()
                t;=#000ff0;shape()
                t;=#0000ff;shape()
                t;=#f0f0f0;shape()
                t;=#af0f0f;shape(line)
                t;=#0ff000;shape()
                t;=#00ff00;shape()
                t;=#000ff0;shape()
                t;=#0000ff;shape()
                line({side},{width})        # Set side,width to starting
                w
                check
                """

        self.hello_drawing_str = hello_drawing_str

        SlTrace.lg(f"hello_drawing_str evaluated:"
                   f"\n{hello_drawing_str}")
        
        # Rotating pattern of custom colors
        self.custom_colors = []

        self.moves_canvas_tags = []  # Init for canvas part of draw_undo
        self.clear_all()            # Setup initial settings
        
        
        
        self.enlarge_fraction = .2   # Enlargement fraction
        if with_screen_kbd:
            if kbd_master is None:
                kbd_master = tk.Toplevel()
            self.kbd_master = kbd_master
            self.screen_keyboard = ScreenKbdFlex(kbd_master,
                                            on_kbd=self.do_key,
                                            win_x=kbd_win_x,
                                            win_y=kbd_win_y,
                                            win_width=kbd_win_width,
                                            win_height=kbd_win_height,
                                              title="Let's Make a Drawing!")
            self.screen_keyboard.to_top()   # Just earlier to see problems
            self.do_keys(self.hello_drawing_str)
            self.screen_keyboard.to_top()
        if show_help:
            self.help()
        
    def clear_all(self):
        """ Clear screen
        """
        self.cmd_proc.clear_all()
        
        self.is_pendown_orig = True
        self.is_pendown = self.is_pendown_orig       # Drawing pen state
        self.heading_orig = 0
        self.heading = self.heading_orig             # Current heading
        self.side_orig = 100
        self.side = self.side_orig              # Default distance
        self.current_width_orig = 2
        self.current_width = self.current_width_orig  # Current line width
        self.photo_images = {}      # Keeping references
        """ Reset image group access to first file """
        for name in self.image_group_names:
            ifg = self.get_image_file_group(name)
            ifg.set_file_index(-1)
        self.x_cor = 0
        self.y_cor = 0

    def last_command(self):
        if hasattr(self, "cmd_proc"):
            return self.cmd_proc.last_command()
        
        return None
    
    def enable_image_update(self, enable=True):
        """ Enable/Disable kbd image update
        :enable: enable update default: True
        """
        self.screen_keyboard.enable_image_update(enable)

    def help(self):
        """ Help message
        """
        if hasattr(self, "cmd_proc"):
            self.cmd_proc.help()
        else:
            SlTrace.lg("help is on the way")

    def setup_image_access(self, image_dir=None):
        """ Setup image access for markers
        :image_dir: image file directory
        """
        if image_dir is None:
            image_dir="./images"    # Distribution choice
            SlTrace.lg(f"Trying distibution image dir: {image_dir}")
            if not os.path.exists(image_dir):
                image_dir="../../resource_lib/images"
                SlTrace.lg(f"Using development image dir: {image_dir}")
        
        self.image_type = KeyboardDraw.IT_FILE
        self.image_group_names = ["animals", "family", "princesses",
                             "other_stuff"]
        self.image_group_index = len(self.image_group_names)
        if self.image_group_index >= len(self.image_group_names):
            self.image_group_index = 0
        group_name = self.image_group_names[self.image_group_index]
        
        self.ifh = DataFiles(data_dir=image_dir)
        for name in self.image_group_names:
            group_dir = os.path.join(image_dir, name)
            self.ifh.add_group(name, group_dir=group_dir)
                
        SlTrace.lg("Image Files")
        data_files_dir = os.path.join(image_dir, "animals")
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
        SlTrace.lg("ignore key")
        
                        
    def do_shift(self, shift_on=True):
        """ Shift letters
        :shift_on: Put shift on, adjust letters
                    default: True
        """
        if hasattr(self, "screen_keyboard"):
            self.screen_keyboard.do_shift(shift_on=shift_on)

    def get_image_file_groups(self):
        """ Get all image file groups (DataFileGroup)
        :returns: data groups (list of DataFileGroup)
        """
        ifh = self.ifh
        return ifh.get_groups()
     
    def get_image_files(self):
        """ get current image group's files
        """
        ifg = self.get_image_file_group()
        return ifg.image_files
     
    def get_image_file(self, group=None, file=None, next=True):
        """ get current image group's file
        :group: group name default: current group
        :file: file name default: current or next
        :next: if true get next
        """
        ifg = self.get_image_file_group(name=group)
        if file is not None:
            im_file = ifg.get_file(file=file)
            return im_file
            
        if next:
            inc = 1
        else:
            inc = 0
        im_file = ifg.get_file(inc=inc)
        SlTrace.lg(f"get_image_file: {im_file}", "image_display")
        return im_file

    def get_image_hash(self):
        """ get current image group's files
        """
        ifg = self.get_image_file_group()
        return ifg.image_hash

    def get_select_image_hash(self):
        """ get current image group's SelectList hash
        Note that these may be images whose sizes are
        for the SelectList and not for marker images
        """
        ifg = self.get_image_file_group()
        return ifg.select_image_hash


    def get_image_file_group(self, name=None):
        """ Get current marker image file group (DataFileGroup)
        :name: group name
                default: return current self.image_group
        """
        if name is None:
            name = "animals"
        ifg = self.ifh.get_group(name)
        return ifg

    def image_file_to_image(self, file):
        """ Get base image from file
        """
        image = self.marker_image_hash.get_image(
                            key=file,
                            photoimage=False)
        return image
                
    def get_canvas(self):
        """ Get our working canvas
        """
        return self.canv
    
    def select_print(self, tag, trace=None):
        """ Print select select state
        """
        """TBD"""
        
    def do_key(self, key, **kwargs):
        """ Process key by
        calling keyfun, echoing key
        :key: key (descriptive string) pressed
                or special "key" e.g. funname(args)
        :kwargs: function specific parameters
                often to "redo" adjusted undone operations
        """
        return self.cmd_proc.do_key(key, **kwargs)
    
    def do_keys(self, keystr):
        r""" Do action based on keystr
            semicolon or newline used as separators
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
        
    def track_keys_text(self):
        """ Setup keys for text input """
        """ bind screen keyboard keys """
        

    def set_key_images(self, show=False):
        self.screen_keyboard.set_images(show=show)

    def get_btn_infos(self, key=None, row=None, col=None):
        """ Get buttons
        :key: if not None, must match
        :row: if not None, must match
        :col: if not None, must match
        """
        return self.screen_keyboard.get_btn_infos(key=key, row=row, col=col)

    def set_btn_image(self, btn_infos=None, image=None):
        """ Set button (btn_infos) image displayed
        :btn_infos: ButtonInfo, or list of ButtonInfos
        :image" text - image file
                Image - image
        """
        self.screen_keyboard.set_btn_image(btn_infos=btn_infos, image=image)

            
    def mouse_down (self, event):
        x_coord = event.x
        y_coord = event.y
        SlTrace.lg(f"canvas_x,y: {x_coord, y_coord}", "mouse_down")

    def canv_coords(self, tu_coords=None):
        """ Canvas x coordinate
        :tu_coords: turtle coordinate pair
                default: use current
        :returns: canvas x_coordinates pair
        """
        if tu_coords is None:
            tu_coords = (self.x_cor, self.y_cor)
        x_cor, y_cor = tu_coords    
        canvas_width = self.canv.winfo_width()
        canvas_height = self.canv.winfo_height()
        x_coor = int(canvas_width/2 + x_cor)
        y_coor = int(canvas_height/2 - y_cor)        # canvas increases downward
        return (x_coor, y_coor)

    def cmd_clear_all(self):
        """ Clear screen
        """
        self.cmd_proc.clear_all()
        

    def display_print(self, tag, trace):
        """ display current display status
        :tag: text prefix
        :trace: trace flags
        """
                        
    
    
    """ End of legacy support
    """
            
def main():
    """ Main Program """
    data_dir = "../data"
    trace = ""
    hello_str = None
    hello_str = "TESTX"     # positioning test
    hello_str = "BUILTIN"
    hello_file = "keyboard_draw_hello.txt"
    hello_file = "hello_family.txt"
    parser = argparse.ArgumentParser()
    parser.add_argument('--trace', dest='trace', default=trace)
    parser.add_argument('--data_dir', dest='data_dir', default=data_dir)
    parser.add_argument('--hs','--hello_str', dest='hello_str', default=hello_str)
    parser.add_argument('--hf','--hello_file', dest='hello_file', default=hello_file)
    
    args = parser.parse_args()             # or die "Illegal options"
    SlTrace.lg("args: %s\n" % args)
    hello_file = args.hello_file
    hello_str = args.hello_str
    data_dir = args.data_dir
    trace = args.trace
    
    
    app = tk.Tk()   # initialize the tkinter app
    app.title("Keyboard Drawing")     # title
    app.config(bg='powder blue')    # background
    """ Using ScreenKbd
    app.resizable(0, 0)     # disable resizeable property
    """
    if hello_str is not None:
        pass
    else:
        try:
            with open(hello_file, 'r') as fin:
                hello_str = fin.read()
        except IOError as e:
            SlTrace.report(f"Problem with hello_file:{hello_file}"
                           f"\n in {os.path.abspath(hello_file)}"
                           f"\n error: {e}")
            sys.exit() 
    kb_draw = KeyboardDraw(app,  title="Keyboard Drawing",
                hello_drawing_str=hello_str,
                draw_x=100, draw_y=50,
                draw_width=1500, draw_height=1000,
                kbd_win_x=50, kbd_win_y=25,
                kbd_win_width=600, kbd_win_height=300)

    kb_draw.enable_image_update()      # Enable key image update
    
    tk.mainloop()

if __name__ == "__main__":
    main()