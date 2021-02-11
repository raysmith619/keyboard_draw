# keyboard_draw
Initial example of a simple (for the young 3-8 years old) drawing program with mostly
keyboard or touch-screen entry.  The goal was to provide the  user a simple drawing
tool which could be used via the keyboard or touch screen.

Some screen shots
 - Docs/keyboard_draw.PNG - Initial screen shot
 - Docs/screen_kbd.PNG - Screen keyboard view
 - Docs/resizing_keboard.PNG - Shows drawing window Plus resized screen keyboard
 - Docs/keyboard_draw_help.txt - simple "help" instructions - sent to stdout when "h" is pressed
 
 Requirements:
  - Basic Python 3
  - tkinter (included with most Python distributions)
  - Pillow (friendly PIL fork) - installed via pip install Pillow - still uses PIL names

The required files are:
  - src/keyboard_draw.py - main program

  - From resource_lib repository:
      - src/screen_kbd_flex.py -  resizable screen alternative to keyboard (mouse or touch screen) 
      - images/keys/* - key image files for screen_keybd.py
      - images/animals/* - image files for image markers for keyboard_draw.py
      - OLD: screen_keybd.py - screen alternative to keyboard (mouse or touch screen)

Program distribution
Some coding to facilitate program distribution, using PyInstaller, has been done.
Requirements:
  - PyInstaller must be installed - pip install PyInstaller
  - Files:
    - src/pyin.bat - Batch file to run
    - src/cli.py - program to call main
