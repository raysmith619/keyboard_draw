pyinstaller cli.py ^
 --name=keyboard_draw ^
 --onefile ^
 --paths ../../resource_lib/src ^
 --add-data keyboard_draw_hello.txt;. ^
 --add-data ../../resource_lib/images;./images
