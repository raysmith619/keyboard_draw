#keyboard_draw_exec_base.py  07May2025  crs, Author
"""
Test KeyboardDraw exec "language"
"""
import os
import tkinter as tk
import pathlib

from select_trace import SlTrace
from keyboard_draw import KeyboardDraw
from file_string_exec import FileStringExec

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
# command functions
def moveto(*args, **kwargs):
    SlTrace.lg(f"moveto({args = }, {kwargs=})")
    kb_draw.moveto(*args)

def letter_string(*args, **kwargs):
    SlTrace.lg(f"letter_string({args = }, {kwargs=})")
    kb_draw.letter_string(*args)

def setnewline(x_cor=None, y_cor=None, heading=None):
    SlTrace.lg(f"setnewline({x_cor = }, {y_cor=})")
    kb_draw.setnewline(x_cor=x_cor, y_cor=y_cor, heading=heading)
        
        
ecmd = FileStringExec(string=cmd_str, globals=globals())
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

ecmd = FileStringExec(string=cmd_str, globals=globals())
if not ecmd.run():
    SlTrace.lg("Test Failed")
    exit(1)
        
SlTrace.lg("End of test")
mw.mainloop()