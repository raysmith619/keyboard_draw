# drawing_command.py
"""
Basic drawing command morphed from ExtendedModeler: EMBCommand
 * Implement basic Command Interface/command to support Undo/Redo
 * @author raysm
 *
"""
import math

from select_trace import SlTrace
from select_error import SelectError
from dm_marker import DmMarker, tp
        
class DrawingCommand:
    """
    static EMBCommandManager command_manager
    String action                # Unique action name
    boolean can_undo            # Command can be undone
    MarkerSelect prev_select        # Previously selected
    MarkerSelect newSelect        # selected after execution
    EMMarkerGroup prevMarkers    # Markers which may change or deleted
    EMMarkerGroup new_markers    # New blocks - may be redundant
    """
    command_manager = None
    display_controller = None
    SlTrace.lg(f"command_manager: {command_manager}")
    dc_id = 0               # Unique command id
    @classmethod
    def set_command_manager(cls, cmd_mgr):
        """ Setup command manager link
        :cmd_mgr: command manager instance
        """
        cls.command_manager = cmd_mgr
        SlTrace.lg(f"setting cls.command_manager - cls {cls.command_manager}")

    @classmethod
    def set_drawing_conroller(cls, controller):
        """ Setup drawing controller link
        :cmd_mgr: command manager instance
        """
        cls.drawing_controller = controller
        
        
    def __init__(self, action, dc_id=None):
        """ Create new command
        :dc_id: Use this id instead of creating unique id
                Generally for short lived execute copy
                default: create new unique id
        """
        if dc_id is None:
            DrawingCommand.dc_id += 1
            dc_id = DrawingCommand.dc_id
        self.dc_id = dc_id
        self.action = action
        if DrawingCommand.command_manager is None:
            raise SelectError("No DrawingCommandManager")
        """ Local control for brevity """
        self.set_drawing_conroller(self.command_manager.drawing_controller)
        self.b_can_undo = True
        self.prev_select = []
        self.new_select = []    # Default  - no change
        self.prev_markers = []
        self.new_markers = []
        self.prev_loc = self.drawing_controller.get_loc()
        self.new_loc = None     # New location (x,y)
        self.prev_heading = self.drawing_controller.get_heading()
        self.heading = None # New heading
        self.change_mode = None   # Command is copy or move
        self.side_h = None
        self.side_v = None
        self.x_cor = None 
        self.y_cor = None 
         
        
    def copy(self, dc_id=None):
        """ Make copy - new unique object unless dc_id passed in
        """
        new_obj = DrawingCommand(self.action, dc_id=dc_id)
        new_obj.prev_select = self.prev_select
        new_obj.new_select = self.new_select
        new_obj.prev_markers = DmMarker.copy_markers(self.prev_markers)
        new_obj.new_markers = DmMarker.copy_markers(self.new_markers)
        new_obj.new_loc = self.new_loc
        new_obj.prev_loc = self.prev_loc
        new_obj.heading = self.heading 
        new_obj.prev_heading = self.heading
        return new_obj

    def reverse_copy(self):
        """ Create copy which will reverse effect of command
        Used to generate revsible changes
        """

        new_obj = self.copy(dc_id=self.dc_id)
        new_obj.new_select = self.prev_select
        new_obj.prev_select = self.new_select
        
        new_obj.new_markers = self.prev_markers
        new_obj.prev_markers = self.new_markers
        
        new_obj.new_loc = self.prev_loc
        new_obj.prev_loc = self.new_loc
        
        new_obj.heading = self.prev_heading 
        new_obj.prev_heading = self.heading
        
        return new_obj

    def no_drawn(self):
        """ Remove drawing artifacts
        """
        for marker in self.prev_markers:
            marker.drawn = None     # No ref to drawn artifacts
        for marker in self.new_markers:
            if marker.drawn is not None:
                for image in marker.drawn.images:
                    marker.image_stores.append(image)   # Avoid loss
            marker.drawn = None     # No ref to drawn artifacts
        

    """
     * Set can_undo
    """
    def set_can_undo(self, can_undo=True):
        self.b_can_undo = can_undo
    

    
    
    """
     * Execute constructed command
     * without modifying command_stack.
     * All commands capable of undo/redo call this
     * without storing it for redo
    """
    def execute(self):
        self.drawing_controller.display_update(cmd=self)
        self.command_manager.display_print(f"execute({self.action})", "execute")
        self.command_manager.select_print(f"execute({self.action}) AFTER", "execute")
        self.command_manager.cmd_stack_print(f"execute({self.action}) AFTER", "execute")
        ###SmMem.ck("execute", SmMem.Type.End)
        return True
    

    
    
    def undo(self):
        """ Remove the effects of the most recently done command
         0. command was poped from command_stack
         1. copy command
         2. reverse change requests in command copy
         3. execute command copy
         4. if OK add command to undo_stack
         5. if OK return True
        """
        try:
            cmd = self.copy()    # Create "disposable" copy of command
        except Exception as e:
            SlTrace.lg(f"undo except: {e}")
            return False
        
        temp = cmd.new_markers
        cmd.new_markers = cmd.prev_markers
        cmd.prev_markers = temp
        
        temp = cmd.get_heading()
        cmd.heading = cmd.prev_heading
        cmd.heading = temp
        
        temp = cmd.get_next_loc()
        cmd.new_loc = cmd.prev_loc
        cmd.prev_loc = temp
        
        temp_sel = cmd.new_select
        cmd.new_select = cmd.prev_select
        cmd.prev_select = temp_sel
        
        res = cmd.execute()
        if res:
            self.command_manager.undo_stack.push(self)
        return res
    
    
    
    """
     * Create checkpoint command, which when "undone", will
     * recreate current command state
     * @throws EMMarkerError 
    """
    def check_point_cmd(self):
        cmd = DrawingCommand("emc checkpoint")    # Create "disposable" copy of command
        cmd.prevMarkers  = self.command_manager.getDisplay().getMarkers()
        return cmd
    
    
    
    """
     * Redo last undo - reverse the effects of the latest  undo
     * The command_manager has already popped command from undo stack
     * @return
    """
    def redo(self):
        if self.can_redo():
            return self.do_cmd()
        
        return False
    
    def get_repeat(self):
        """ Get a copy which will "repeat" last command
        This supports possible modification before
        actual execution.
        
        The plan is to create duplicate marker(s)
        in a location relocated by one length in the
        current heading with the marker's other
        parameters unchanged.
        """
        new_cpy = self.copy()
        chg_markers = []    # Make copied markers
                            # independent 
        for marker in new_cpy.new_markers:
            chg_marker = marker.change(move_it=True)
            chg_marker.record()     # Record as new marker
            chg_markers.append(chg_marker)
        new_cpy.new_markers = chg_markers
        new_cpy.set_new_loc()
        new_cmd = new_cpy
        return new_cmd 
    
    def repeat(self):
        """ repeat last command
        The plan is to create duplicate marker(s)
        in a location relocated by one length in the
        current heading with the marker's other
        parameters unchanged.
        """
        new_cmd = self.get_repeat()
        res = new_cmd.do_cmd()
        return res 

    def add_prev_marker(self, marker):
        """ Add block to remove from display
        :marker: to remove
        """
        self.prev_markers.append(marker.copy())
        return marker
        
    def add_marker(self, markers):
        """ Add one or a list of markers
        :markers: marker or list to add
        :returns: markers
        """
        if not isinstance(markers, list):
            markers = [markers]     # list of one
        for marker in markers:
            if marker.is_recorded():
                SlTrace.lg(f"add_marker: already recorded:{marker}")
            else:
                marker.record()
            self.new_markers.append(marker)
        return markers
        
    def add_prev_markers(self, markers):
        """ Add one or a list of markers to prev_markers
        :markers: marker or list to add
        """
        if not isinstance(markers, list):
            markers = [markers]     # list of one
        for marker in markers:
            self.add_prev_marker(marker)
        return markers

    def get_heading(self):
        """ Get heading, if one
            else the heading of the last marker
        """
        if self.heading is not None:
            return self.heading 
        
        markers = self.get_markers()
        if len(markers) > 0:
            return markers[-1].heading%360
        
        return 0

    def set_heading(self, heading):
        """ Set heading
            1. if self.heading then adjust this
            2. else set heading of last marker
        :heading: new heading in degrees
        """
        if self.heading is not None:
            self.heading = heading
            return
        
        markers = self.get_markers()
        if len(markers) > 0:
            markers[-1].heading = heading
            return
        
        self.heading = heading      # No markers
    
    def get_markers(self):
        """ Get our markers
        """
        return self.new_markers
    

    """
     * Selection Management
    """
    def add_select(self, marker):
        self.new_select.append(marker)
    
    

    """
     * Get marker, given index
    """
    def mkr(self, id):
        return self.command_manager.mkr(id)
    
    
    
    def remove_select(self, marker):
        ns = []
        for mk in self.new_select:
            if mk == marker:
                pass
            else:
                ns.append(mk)
        self.new_select = ns 
        return True
    
    
    """
     * Select block
     * @param id - id of block to select
     * @param keep - Keep previously selected blocks iff True
    """
    def select_marker(self, marker, keep=False):
        if not keep:
            self.new_select = []
        
        self.new_select.append(marker)
    
    
    
    def toggle_selection(self, id):
        '''TBD
        if (self.new_select.hasIndex(id)):
            self.new_select.removeIndex(id)
         else:
            self.new_select.addIndex(id)
        '''
    
    
    
    """
     * Display updated selection
    """
    def display_selection(self, new_select, prev_select):
        return self.command_manager.display_update(new_select, prev_select)
    
    def display_update(self, cmd=None):
        """ Update display, based on executed command
        :cmd: currently executed command
                default: command on top of command stack
        """
        self.display_controller.display_update(cmd=self)

          
     
    """
     * Do command, storing, if command can be undone or repeated, for redo,repeat
    """
    def do_cmd(self):
        res = self.execute()
        if (res):
            if self.can_undo() or self.can_repeat():
                SlTrace.lg(f"do_cmd command_stack.push({self})",
                           "execute")
                self.command_manager.command_stack.push(self)
                self.command_manager.cmd_stack_print(f"do_cmd({self.action}) AFTER", "execute")
            else:
                SlTrace.lg(f"do_cmd({self.action}) can't undo/repeat", "execute")
        return res
    
    def add_pt(self, x1=None, y1=None, side_h=None,
               heading=None):
        """ Calculate x2,y2 from x1,y1,heading
        :side_h: side horizontal (in heading) 
        :returns: x2,y2
        """
        if x1 is None:
            x1 = self.get_x_cor()
        if y1 is None:
            y1 = self.get_y_cor()
        if side_h is None:
            side_h = self.get_side_h()
        if heading is None:
            heading = self.get_heading()
        theta = math.radians(heading)
        x_chg = side_h*math.cos(theta)
        y_chg = side_h*math.sin(theta)
        x2 = x1 + x_chg
        y2 = y1 + y_chg
        return x2,y2
    

    """
     Utility functions to get data from or add data to command
    """
    def get_change_mode(self):
        if self.change_mode is not None:
            return self.change_mode
        
        return self.drawing_controller.get_change_mode()
    
    def get_side_h(self):
        if self.side_h is not None:
            return self.side_h
         
        if len(self.new_markers) > 0:
            side_h = self.new_markers[-1].get_side_h()
            return side_h
        
        return self.drawing_controller.get_side_h()
    
    def get_side_v(self):
        if self.side_v is not None:
            return self.side_v
         
        if len(self.new_markers) > 0:
            side_v = self.new_markers[-1].get_side_v()
            return side_v
        
        return self.drawing_controller.get_side_v()

    def get_loc(self):
        return (self.get_x_cor(), self.get_y_cor())
            
    def get_x_cor(self):
        if self.x_cor is not None:
            return self.x_cor 
         
        if len(self.new_markers) > 0:
            x_cor = self.new_markers[-1].get_x_cor()
            return x_cor
        
        return self.drawing_controller.get_x_cor()
        
    def set_x_cor(self, new_val):
        if self.x_cor is not None:
            self.x_cor = new_val         
        elif len(self.new_markers) > 0:
            self.new_markers[-1].x_cor = new_val
        else:
            self.x_cor = new_val

    def get_y_cor(self):
        if self.y_cor is not None:
            return self.y_cor 

        if len(self.new_markers) > 0:
            y_cor = self.new_markers[-1].get_y_cor()
            return y_cor
        
        return self.drawing_controller.get_y_cor()
        
    def set_y_cor(self, new_val):
        if new_val is not None:
            self.y_cor = new_val         
        elif len(self.new_markers) > 0:
            self.new_markers[-1].y_cor = new_val
        else:
            self.y_cor = new_val
    
    def get_center(self):
        """ get center of command - last marker
        """
        markers = self.get_markers()
        if len(markers) > 0:
            center = markers[-1].get_center()
        else:
            center = 0,0           
        return center
    
    def get_next_center(self):
        """ get center of next command - last marker
        """
        if self.new_loc is not None:
            x1,y1= self.new_loc
            return self.add_pt(x1=x1, y1=y1)
        
        markers = self.get_markers()
        if len(markers) > 0:
            loc = markers[-1].get_next_loc()
        else:
            loc = self.add_pt()            
        x1,y1 = loc
        return self.add_pt(x1=x1, y1=y1)
    
    def get_next_loc(self):
        """ get location of next command - last marker
        """
        if self.new_loc is not None:
            return self.new_loc
        
        markers = self.get_markers()
        if len(markers) > 0:
            loc = markers[-1].get_next_loc()
        else:
            loc = self.add_pt()            
        return loc

    def set_new_loc(self, loc=None):
        """ Set destination location of command
        :loc: (x_cor, y_cor) of command
            default: loc of last marker
        """
        if loc is None:
            markers = self.get_markers()
            if len(markers) > 0:
                loc = markers[-1].get_next_loc()
        if loc is None:
            loc = (0,0)
        self.new_loc = loc
                
    """
     * Get currently selected
    """
    def get_selected(self):
        return self.command_manager.get_selected()
    
    
    
    def save_selection(self, ):
        """ Save selected items for possible restoration
        Include section criterion to support restoration of "selected" state
        """
        
    

    """
     * Save command for undo/redo...
    """
    def saveCmd(self):
        self.command_manager.saveCmd(self)    


    def any_selected(self):
        return self.command_manager.any_selected()
    

    def can_redo(self):
        return self.can_undo()                # Default - can redo if we can undo
    


    def can_undo(self):
        return self.b_can_undo
    


    def can_repeat(self):
        return self.can_undo()
    

    """
     * Command Description String
    """
    def __str__(self):
        cmd_str = self.action
        cmd_str += f" dc_id:{self.dc_id}"
        cmd_str += f" heading:{self.get_heading()}"
        cmd_str += f" to={tp(self.get_next_loc())}"
        if len(self.new_markers) > 0:
            cmd_str += " new_markers:"
            for marker in self.new_markers:
                cmd_str += f"\n    {marker}"
        if len(self.prev_markers) > 0:
            cmd_str += " prev_markers:"
            for marker in self.prev_markers:
                cmd_str += f"\n    {marker}"
        
        return cmd_str

    def is_visible(self):
        """ Check if command is visible -
        if any of markers is visible command is visible
        """
        if len(self.new_markers) > 0:
            for marker in self.new_markers:
                if marker.is_visible():
                    return True 
            
        return False

    def check_point(self):
        self.command_manager.check_point()

    def update(self):
        """ update tkinter display
            mostly for debugging to visualize current state
        """
        self.drawing_controller.update()

    def use_locale(self, cmd):
        """ create self copy, then change to locale values
        used by last marker  In essence give new marker the locale
        of marker (location, heading...) - shorthand for change()
        :cmd: later adjustments by command e.g. heading
                default: no adjustments
        """
        new_cmd = self.copy()
        if cmd is None:
            return new_cmd
        
        if len(new_cmd.new_markers)  == 0:
            return new_cmd
        
        if len(cmd.new_markers) == 0:
            return new_cmd
        
        marker = new_cmd.new_markers[-1]
        marker_new = cmd.new_markers[-1]
        marker = marker.use_locale(marker=marker_new)
        new_cmd.new_markers[-1] = marker
        return new_cmd
        
if __name__ == "__main__":
    from tkinter import *
    from dm_drawer import DmDrawer
    from command_manager import CommandManager
    from dm_circle import DmCircle
    from dm_image import DmImage
    from dm_line import DmLine
    from dm_square import DmSquare
    from dm_text import DmText
    from dm_triangle import DmTriangle
    from dm_marker import DmMarker
    from dm_move_key import DmMoveKey
    root = Tk()
    
    drawer = DmDrawer(root,  title="Testing DrawingCommand")
    drawer.color_current = "w"
    
    mgr = CommandManager(drawer)
    SlTrace.lg(f"command_manager - DC: {DrawingCommand.command_manager}")
    DrawingCommand.set_command_manager(mgr)
    SlTrace.lg(f"command_manager - DC: {DrawingCommand.command_manager}")

    cmd1 = DrawingCommand("first_test_command")
    SlTrace.lg(f"cmd1={cmd1}")
    
    def cmd_key(keysym):
        """ Simple command tests based on key
        Movement depends on previous command.
        1. If previous heading unchanged
            then move one side in current direction
        2. Else if previous marker is a line,shape or image
            then set heading and location that the
            next such object will be flush
            with the previous objec but have
            the new heading
         
        :keysym: key event keysym
        """
        if (keysym == "Up" or keysym == "Down"
               or keysym == "Left" or keysym == "Right"):
            prev_heading = drawer.get_heading()
            marker = DmMoveKey(drawer, keysym=keysym)
            new_heading = marker.heading
            if new_heading != prev_heading:
                marker = marker.change(side=0)
            cmd = DrawingCommand(f"cmd_{keysym}")
            cmd.add_marker(marker)
            SlTrace.lg(f"cmd={cmd}", "cmd_trace")
            cmd.do_cmd() 
        else:
            raise SelectError(f"Don't understand keysym:{keysym}")    
    def setup_scene():
        """ Setup a scene with a few markers
        """
        markers = [
                DmLine(drawer),
                DmSquare(drawer),
                DmCircle(drawer),
                DmTriangle(drawer),
                DmText(drawer, text="A"),
                ]
    
        beg_x = -5*markers[0].side
        beg_y = -1*markers[0].side
        for i, marker in enumerate(markers):
            x_cor = beg_x+i*marker.side
            y_cor = beg_y+i*marker.side 
            cmd = DrawingCommand(f"cmd_{marker}")
            cmd.add_marker(marker.change(x_cor=x_cor, y_cor=y_cor))
            SlTrace.lg(f"cmd={cmd}", "cmd_trace")
            cmd.do_cmd() 
    
    def on_key_press(event):
        inchar = event.char
        keysym = event.keysym
        keycode = event.keycode
        prev_marker = mgr.last_command()
        x_cor, y_cor = drawer.get_loc()
        SlTrace.lg(f"on_text_entry: keysym: {keysym} keycode: {keycode}")
        if keysym == 'i':
            image_info = drawer.pick_next_image()
            image_file, image = image_info
            marker = DmImage(drawer, file=image_file, image_base=image,
                      x_cor=x_cor, y_cor=y_cor)
            cmd = DrawingCommand(f"cmd_{marker}")
            cmd.add_marker(marker)
            SlTrace.lg(f"cmd={cmd}")
            cmd.do_cmd() 
        elif keysym == 'u':
            mgr.undo()
        elif keysym == 'r':
            mgr.redo()
        elif keysym == 's':
            marker = DmSquare(drawer)
            cmd = DrawingCommand(f"cmd_{marker}")
            cmd.add_marker(marker.change(x_cor=x_cor, y_cor=y_cor))
            SlTrace.lg(f"cmd={cmd}")
            cmd.do_cmd() 
        elif keysym == 't':
            marker = DmTriangle(drawer)
            cmd = DrawingCommand(f"cmd_{marker}")
            cmd.add_marker(marker.change(x_cor=x_cor, y_cor=y_cor))
            SlTrace.lg(f"cmd={cmd}")
            cmd.do_cmd() 
        elif keysym == "f":         # (fix)Setup scene
            setup_scene()    
        elif keysym == 'space':
            mgr.repeat()
        elif keysym == "x":
            mgr.undo_all()
        elif (keysym == "Up" or keysym == "Down"
               or keysym == "Left" or keysym == "Right"):
            cmd_key(keysym)
        else:
            SlTrace.lg("??")
    
    drawer.set_loc(-400, 0)
        
    root.bind('<KeyPress>', on_key_press)
    root.mainloop()   



