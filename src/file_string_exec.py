# file_string_exec.py
"""
Support for python string/file exec
"""
import sys, traceback

from select_trace import SlTrace
from select_error import SelectError


class FileStringExec:
    """ Support for python string/file exec
        series of python code, including special functions
        which may be the basis of a game language
        
    """
    def __init__(self, file=None, string=None,
                 prefix=None, end=None,
                 list_exec_string=True,
                 globals=None, locals=None):
        """ Setup file/string exec
        Only ONE of 
        :file: file containing command
        :string: string containing command
        :prefix: Optional string to prefix command string
        :end: Optional string to append to command string
        :globals: globals, if present, placed in exec globals arg
        :locals: locals, if present, placed in exec locals arg
        """
        # Added to between any prefix and the compile string if trace: "puzzle_load" flag is set
        test_prefix = """
        print("dir: ", dir())
        print("globals: ", globals())
        print("locals: ", locals())
        """
         
        self.prefix = prefix
        self.end = end
        self.list_exec_string = list_exec_string
        self.set_input(file=file, string=string)
        self.globals = globals
        self.locals = locals
        self.file = None        # Set if known
        self.string = None
        self.set_input(file=file, string=string)

    def set_input(self, file=None, string=None):
        """ Setup file access
        :file: file name/stream containing puzzle specification
            OR
        :string: string containing puzzle specification
        """
        self.file_name = None        # Set to name if known
        self.string = string
        if file is None and string is None:
            raise SelectError("Neither file nor string was specified - must specify one")
        if file is not None and string is not None:
            raise SelectError(f"Only one of file({file}) or string({string}) may be specified")
        
        if file is not None:
            if isinstance(file, str):
                self.file_name = file
                try:
                    fin = open(file)
                except Exception as ex:
                    raise SelectError(f"open file {self.file_name} failed {str(ex)}")
                
            else:
                fin = file         # Input is an opened stream    
            try:
                self.string = fin.read()
                fin.close()
            except Exception as ex:
                if self.file_name is not None:
                    err_str = f"input read from file {self.file_name} failed"
                err_str += f" read error: {str(ex)}"
                raise SelectError(err_str)
        else:        
            self.string = string
        if self.string is None:
            raise SelectError(f"")
    
    def run(self):
        """ run (execute command string)
        """
        self.result = False          # Set True if OK
        if self.string is None:
            err_str = "FileStringExec Error:"
            if self.file_name is not None:
                err_str += f" while executing file {self.file_name}\n"
            err_str += "string is missing"
            raise SelectError(err_str)
        
        
        compile_str = ""
        if self.prefix is not None:
            compile_str = self.prefix
            if not compile_str.endswith("\n"):
                compile_str += "\n"         # Insure ending newline
        compile_str += self.string
        if self.end is not None:
            compile_str += self.end
        try:
            exec(compile_str, self.globals, self.locals)
            self.result = True
            return self.result
        
        except Exception as e:
            _, _, tb = sys.exc_info()
            tbs = traceback.extract_tb(tb)
            err_str = "FileStringExec Error:"
            if self.file_name is not None:
                err_str += SlTrace.lg(f"while executing text from {self.file_name}\n")
            err_str += str(e)
            SlTrace.lg(err_str)
            for tbfr in tbs:  # skip bottom (in dots_commands.py)
                tbfmt = 'File "%s", line %d, in %s' % (tbfr.filename, tbfr.lineno, tbfr.name)
                SlTrace.lg("    %s\n       %s" % (tbfmt, tbfr.line))
            if self.list_exec_string:
                SlTrace.lg(f"Exec string:\n{compile_str}")
            self.result = False
        return self.result



        
    
if __name__ == "__main__":
    import os
    import pathlib
    import tkinter as tk
    

    mw = tk.Tk()
    
    cmd_str = """
moveto(1,2)
print(3,4)
letter_string("abcdef")
    """
    SlTrace.lg("\n\nTesting exec from string")
    # command functions
    def moveto(*args, **kwargs):
        SlTrace.lg(f"moveto({args = }, {kwargs=})")
    
    def letter_string(*args, **kwargs):
        SlTrace.lg(f"letter_string({args = }, {kwargs = })")
            
    ecmd = FileStringExec(string=cmd_str, globals=globals())
    if not ecmd.run():
        SlTrace.lg("Test Failed")
        exit(1)
    
    SlTrace.lg("\n\nTesting File exec")
    base_file = __file__
    base_stem = pathlib.Path(base_file).stem
    out_file = base_stem + ".test_out"
    SlTrace.lg(f"{os.path.abspath(out_file)}")
    with open(out_file, "w") as fout:
        fout.write(cmd_str)
    
    SlTrace.lg(f"Using file: {out_file}")
    ecmd = FileStringExec(file=out_file, globals=globals())
    if not ecmd.run():
        SlTrace.lg("Test Failed")
        exit(1)
            
    SlTrace.lg("End of test")
