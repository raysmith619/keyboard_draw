#keyboard_draw.py    12Dec2020  crs
"""
Drawing on turtle window, using keyboard
"""
import os
import sys
import re
import tkinter as tk
import argparse

from select_trace import SlTrace
from select_window import SelectWindow
from kbd_cmd_proc import KbdCmdProc
from keyboard_draw_exec import KeyboardDrawExec

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
    

class KeyboardDraw(SelectWindow):

    IT_FILE = "it_file"     # image from file
    IT_TEXT = "it_text"     # image generated 
    
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
                 show_help=False,
                 **kwargs
                 ):
        """ Keyboard Drawing tool
        :master: master
        :kbd_master: screen keyboard master, if present
                    must be grid managed
                    default: create Toplevel
        :draw_width: drawing window width default: 1500 pixels
        :draw_height: drawing window height default: 1000
        :kbd_win_x: screen keyboard initial x
        :kbd_win_y: screen keyboard initial y
        :kbd_win_width: screen keyboard width
        :kbd_win_height: screen keyboard height
        :canvas: base canvas
                default: create 500x500
        :side: starting line side length
            default: 100
        :width: starting line width
                default: 20
        :hello_drawing_str: Beginning display command string
                default: HI...
        :with_screen_kbd: Has screen keyboard control
                    default: True
        :show_help: Show help text at beginning
                    default: False
        """
        control_prefix = "KbdDraw"
        self.x_cor = 0 
        self.y_cor = 0 
        self.heading = 0
        self.color_current = "red"
        self.color_changing = True
        self.color_index = 0
        super().__init__(master,title=title,
                         control_prefix=control_prefix,
                         **kwargs)

        self.cmd_pointer = None     # marker pointer
        
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
        self.setup_image_access(image_dir=image_dir)


        self.canv.bind ("<ButtonPress>", self.mouse_down)
        self.cmd_proc = KbdCmdProc(self)
        
        self.master = master
        self.side = side
        self.current_width = width
        self.canv.update()
        canvas_width = self.canv.winfo_width()
        canvas_height = self.canv.winfo_height()
        SlTrace.lg(f"{canvas_width = } {canvas_height = }")
        x_start = side
        y_start = 2*side
        SlTrace.lg(f"{x_start = } {y_start = }")
        side = self.side
        width = self.draw_width
        height = self.draw_height
        ostuff_x = x_start + side
        ostuff_y = y_start - 6*side
        hi_stuff_x = ostuff_x+5*side
        hi_stuff_y = ostuff_y +1*side
        hi_side = side/5
        self.top_y = 300                    # Provide access to KeyboardDrawExce exec string
        self.left_x = 300
        self.bottom_y = self.canvas_height - self.top_y
        self.right_x = self.canvas_width - self.left_x
            
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
        elif hello_drawing_str == "TESTY":
            
            exec_str = """
            moveto(left_x, top_y); letter_string("w")
            moveto(right_x, top_y); letter_string("x")
            moveto(right_x, bottom_y); letter_string("y")
            moveto(left_x, bottom_y); letter_string("z")
            """
            kbe = KeyboardDrawExec(k_draw=self, string=exec_str)
            kbe.run()
            hello_drawing_str = None
        elif hello_drawing_str == "BUILTIN":
            exec_str = """
            # Beginning screen pattern
            # Add in Family
            #minus
            #line({side},{width})        # Set side, width
            moveto(left_x,top_y)
            #plus
            setnewline(); letter_string("Family")
            f = "family"
            newline(); letter_string("Alex "); image_file(f, "alex")
            newline(); letter_string("Declan "); image_file(f, "declan")
            newline(); letter_string("Avery "); image_file(f, "avery")
            newline(); letter_string("Charlie "); image_file(f, "charlie")
            """
            kbe = KeyboardDrawExec(k_draw=self, string=exec_str)
            kbe.run()
            hello_drawing_str = None
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
        if self.hello_drawing_str is not None:
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
            self.screen_keyboard.to_top()
            if self.hello_drawing_str is not None:
                self.do_keys(self.hello_drawing_str)
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


    def list_string(self, string):
        """ List string, given line numbers
        :string: string to be listed with line numbers
        :returns: string with line numbered lines
        """
        out_str = ""
        lines = string.split("\n")
        for i, line in enumerate(lines):
            out_str += f"{i+1:>2d}: {line}\n"
        return out_str

            
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

    def string_list(self, string):
        """ Do keys, list as typed
        No special keysymbols  action
        :string: list of characters
        """
        for ch in string:
            self.do_key(ch)
                    
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

    """ 
    Links to cmd_proc
    """
    
    def moveto(self, x,y):
        """ Move to location
        :x: x in pixels
        :y: y in pixels
        """
        self.cmd_proc.moveto(x, y)

    def image_file(self, group=None, file=None):
        """ create marker at current location, heading
        :group: image directory
        :group: file base name
        """
        self.cmd_proc.image_file(group=group, file=file)    # legacy name
            
    def letter_string(self, string):
        """ Process string of letters(characters) no special
        """    
        self.cmd_proc.letter_string(string)
                
    def newline(self):
        """ Move to beginning of next line
        force text mode
        """
        self.cmd_proc.newline()

    def setnewline(self, x_cor=None, y_cor=None, heading=None):
        """ Set curret location as line beginning
        to be used by jump_to_next_line
        set to text mode if not alreaty there
        :x_cor: x_cor default= current x_cor
        :y_cor: y_cor default= current y_cor
        :heading: text direction default: 0
        """
        if heading is None:
            heading = 0.
        self.cmd_proc.setnewline(x_cor=x_cor, y_cor=y_cor, heading=heading)        
        
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
    hello_str = "TESTY"     # positioning test
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