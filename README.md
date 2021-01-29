# keyboard_draw
Initial example of a simple (for the young 3-8 years old) drawing program with mostly
keyboard or touch-screen entry.  The goal was to provide the  user a simple drawing
tool which could be used via the keyboard or touch screen.

Some screen shots
 - Docs/keyboard_draw.PNG - Initial screen shot
 - Docs/screen_kbd.PNG - Screen keyboard view
 - Docs/keyboard_draw_help.txt - simple "help" instructions - sent to stdout when "h" is pressed
 
 Requirements:
  - Basic Python 3
  - tkinter (included with most Python distributions)
  - Pillow (friendly PIL fork) - installed via pip install Pillow - still uses PIL names

The required files are:
  - src/keyboard_draw.py - main program

  - From resource_lib repository:
      - screen_keybd.py - screen alternative to keyboard (mouse or touch screen)
      - images/keys/* - key image files for screen_keybd.py
      - images/animals/* - image files for image markers for keyboard_draw.py
