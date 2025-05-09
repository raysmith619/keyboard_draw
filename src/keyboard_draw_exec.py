#keyboard_draw_exec.py  07May2025  crs, Author
"""
Test KeyboardDraw exec "language"
"""
import os
import tkinter as tk
import pathlib

from select_trace import SlTrace
from file_string_exec import FileStringExec

# command functions
kbd_draw = None         # Set fom KeyboardDrawExec.__init__()
def moveto(*args, **kwargs):
    SlTrace.lg(f"moveto({args = }, {kwargs=})")
    kbd_draw.moveto(*args)

def letter_string(*args, **kwargs):
    SlTrace.lg(f"letter_string({args = }, {kwargs=})")
    kbd_draw.letter_string(*args)

def setnewline(x_cor=None, y_cor=None, heading=None):
    SlTrace.lg(f"setnewline({x_cor = }, {y_cor=})")
    kbd_draw.setnewline(x_cor=x_cor, y_cor=y_cor, heading=heading)

class KeyboardDrawExec(FileStringExec):
    """ Executes command string/file
    """
    def __init__(self, k_draw,
                 file=None, string=None,
                 prefix=None, end=None,
                 list_exec_string=True,
                 my_globals=None, my_locals=None):
        global top_y
        global left_x
        global bottom_y
        global right_x
        global kbd_draw
        kbd_draw = k_draw
        top_y = kbd_draw.top_y 
        left_x = kbd_draw.left_x
        bottom_y = kbd_draw.bottom_y
        right_x = kbd_draw.right_x

        if my_globals is None:
            my_globals = globals()
        if my_locals is None:
            my_locals = locals()
        super().__init__(file=file, string=string,
                 prefix=prefix, end=end,
                 list_exec_string=list_exec_string,
                 globals=my_globals, locals=my_locals)       
        
        
        
if __name__ == '__main__':
    from keyboard_draw import KeyboardDraw
    
    SlTrace.clearFlags()

    mw = tk.Tk()   # initialize the tkinter app
    hello_str = ""

    kb_draw = KeyboardDraw(mw,  title="Keyboard Drawing Exec",
                hello_drawing_str=hello_str,
                draw_x=100, draw_y=50,
                draw_width=1500, draw_height=1000,
                kbd_win_x=50, kbd_win_y=25,
                kbd_win_width=600, kbd_win_height=300)

        
    cmd_str = """
moveto(200, 400)
setnewline()
letter_string("Family")
    """
    SlTrace.lg("Testing exec from string")
            
    ecmd = KeyboardDrawExec(kb_draw, string=cmd_str, my_globals=globals())
    if not ecmd.run():
        SlTrace.lg("Test Failed")
        exit(1)

    ###mw.mainloop()

    SlTrace.lg("\n\nFile exec")
    base_file = __file__
    base_stem = pathlib.Path(base_file).stem
    out_file = base_stem + ".test_out"
    SlTrace.lg(f"{os.path.abspath(out_file)}")
    with open(out_file, "w") as fout:
        fout.write(cmd_str)

    ecmd = KeyboardDrawExec(kb_draw, string=cmd_str, my_globals=globals())
    if not ecmd.run():
        SlTrace.lg("Test Failed")
        exit(1)
            
    SlTrace.lg("End of test")
    mw.mainloop()