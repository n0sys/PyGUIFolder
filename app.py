import tkinter as tk
from tkinter import ttk
import os
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo
import ntpath
import json
import uuid
from tkinter import messagebox
from tkinter import Menu

# Tkinter Source Code: https://github.com/python/cpython/blob/3.11/Lib/tkinter/
# Tkinter colors: https://www.plus2net.com/python/tkinter-colors.php
# Tkinter tuto: https://realpython.com/python-gui-tkinter/
# root.geometry('550x250')
# Tkinter messagebox: https://docs.python.org/3/library/tkinter.messagebox.html

class File(tk.Button):
    def __init__(self, path, master=None, cnf={}, **kw):
        super().__init__(master, cnf={}, **kw)
        self.path = path

class Folder(tk.Button):
    def __init__(self, id=None, master=None, cnf={}, **kw):
        super().__init__(master, cnf={}, **kw)
        if not id:
            self.id = str(uuid.uuid4())
        else:
            self.id = id

class App(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        # Assign root object
        self.window = master

        # Define current folder
        self.current_folder = None

        # Save last right clicked widget
        self.last_right_clicked_widget = None

        # Get file dir path
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        
        self.log_objects = {}
        # Navbar Frame
        self.navbar_frame = tk.Frame(
                    master=master,
                    relief=tk.FLAT,
                    background="ghostwhite"
                )
        self.navbar_frame.pack(fill=tk.X)
        
        # Handle close before saving
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Create save button
        self.btn_save = tk.Button(master=self.navbar_frame, text="Save", command=self.save)
        self.btn_save.grid(column=0, row=0, sticky="w")

        # Folders Frame
        self.folders_frame = tk.Frame(
                    master=master,
                    relief=tk.RAISED,
                    background="gray24"
                )
        self.folders_frame.pack(fill=tk.X)

        ## Folder frame's menu
        self.folder_frame_menu = Menu(root, tearoff = 0)
        self.folder_frame_menu.add_command(label ="Rename", command=self.rename_folder)
        #TODO: label.config(text="newtext")

        # Create add new folder button
        self.new_folder_btn = tk.Button(master=self.folders_frame, text="New Folder", command=self.get_new_folder_name, bg='khaki', fg='gray23')
        self.new_folder_btn.grid(column=1, row=0, sticky="ew")

        # Files Frame
        self.files_frame = tk.Frame(
                    master=master,
                    relief=tk.FLAT,
                    background="gray28",
                    width=300, 
                    height=300
                )
        
        self.files_frame.pack(fill=tk.BOTH, expand = True, ipady=20)

        # Create newFile button
        self.new_file_btn = tk.Button(master=self.files_frame, text="+", command=self.get_new_file_path)
        self.new_file_btn.grid(column=1, row=0, sticky="ew", padx=5, pady=10)

        # try to load any saved files or folders
        self.load_saved_objects()

        # saved content var
        self.saved = True

    def handle_file_btn_keypress(self, path):
        #Try to open the file
        os.system(f"\"{path}\"")
    
    def get_new_file_path(self):
        
        if not self.current_folder:
            messagebox.showerror("Failed", "Where do you want us to put your files dude ? CREATE A FOLDER")
            return

        filetypes = (
            ('All files', '*.txt'),
            ('All files', '*.*')
        )

        filename = fd.askopenfilename(
            title='Open a file',
            initialdir='C:/Users/hnassar/OneDrive - ADUNEO/Bureau/priv/pyGuiFolder',
            filetypes=filetypes)
        
        if filename:
            # Add file to the grid
            self.add_new_file(filename)

            # Save file to the logs
            self.log_objects[self.current_folder.id]["files"].append({
                #"name":new_btn_File1["text"],
                "path":filename
                }
                )

    def add_new_file(self, filename):
        # Get the number of files added and calculate row and column
        file_position = self.get_new_file_loc()
        file_row = file_position // 5
        file_column = file_position % 5

        # Create the new button
        new_btn_File1 = File(master=self.files_frame, text=ntpath.basename(filename), path=filename)
        new_btn_File1.grid(column=file_column, row=file_row, sticky="ew", padx=5, pady=10)

        # Add button onclick function
        new_btn_File1.bind("<Button-1>", lambda _= "Open File": self.handle_file_btn_keypress(new_btn_File1.path))
        print("Added a new file")

        # Update position of addFiles button
        self.new_file_btn.grid(column=file_column + 1, row=file_row, sticky="ew", padx=5, pady=10)

        self.saved = False
    
    #Continue
    def get_new_folder_name(self):

        # Get the number of files added and calculate row and column
        file_position = self.get_new_folder_loc()
        file_column = file_position

        # Create label to register folder name
        folder_label = tk.Entry(master=self.folders_frame)
        folder_label.grid(column=file_column, row=0, sticky="ew")

        contents = tk.StringVar()
        contents.set("FolderName ?")
        folder_label["textvariable"] = contents

        folder_label.bind('<FocusIn>', lambda _= "Delete text on focus": contents.set(""))
        folder_label.bind('<FocusOut>', lambda _= "Add text on unfocus": contents.set("FolderName ?"))
        folder_label.bind('<Key-Return>', lambda _= "Create new folder": self.create_new_folder(foldername=contents.get(), folderlabel=folder_label))
    
    def create_new_folder(self, foldername, id=None, folderlabel=None):

        if folderlabel:
            folderlabel.destroy()

        if not foldername:
            return
        
        # Get the number of files added and calculate row and column
        file_position = self.get_new_folder_loc()
        file_column = file_position

        # Create the new Folder
        new_folder = Folder(master=self.folders_frame, text=foldername, id=id)
        new_folder.grid(column=file_column, row=0, sticky="ew")

        # Add button onclick function
        new_folder.bind("<Button-1>", lambda _= "Switch folders": self.switch_folders(new_folder))
        new_folder.bind("<Button-3>", lambda event= "Drop down menu": self.do_popup(event, new_folder))
        print("Added a new folder")
        
        # Update position of new folder button
        self.new_folder_btn.grid(column=file_column + 1, row=0, sticky="ew")
        
        if not self.current_folder:
            self.current_folder = new_folder

        # add entry of new folder in logs
        if not self.log_objects.get(new_folder.id):
            self.log_objects[new_folder.id] = {
                "name":new_folder["text"],
                "files":[]
            }

        self.saved = False

    def get_new_file_loc(self):
        return len(self.files_frame.winfo_children()) - 1
    
    def get_new_folder_loc(self):
        return len(self.folders_frame.winfo_children()) - 1

    def switch_folders(self, new_folder):
        # Check if the current folder is the same as the new folder
        if self.current_folder.id == new_folder.id:
            return
        
        self.current_folder = new_folder
        for item in self.files_frame.winfo_children():
            if isinstance(item, File):
                item.destroy()

        for file in self.log_objects[new_folder.id].get("files"):
            self.add_new_file(file.get("path"))

    def save(self):
        # Try to create .pyguifolder directory
        try:
            os.mkdir(f"{self.dir_path}/.pyguifolder")
        except FileExistsError as e:
            pass
        except Exception as e:
            messagebox.showerror("Failed", f"Error while creating directory {e}")
        
        # Create logs file and add 
        with open(f"{self.dir_path}/.pyguifolder/pyguilogs.txt", "w") as logfile:
            logfile.write(json.dumps(self.log_objects))

        messagebox.showinfo("Success", f"Folders saved successfully")

        self.saved = True

    def load_saved_objects(self):
        if os.path.isdir(f"{self.dir_path}/.pyguifolder"):
            try:
                with open(f"{self.dir_path}/.pyguifolder/pyguilogs.txt", "r") as logfile:
                    saved_objects = json.loads(logfile.readline())

                if not saved_objects:
                    return
                
                self.log_objects = saved_objects

                for folder in saved_objects:
                    self.create_new_folder(foldername=saved_objects[folder].get("name"), id=folder)
                
                for file in saved_objects[self.current_folder.id].get("files"):
                    self.add_new_file(file.get("path"))
            except FileNotFoundError:
                return
    
    def on_closing(self):
        if not self.saved:
            if messagebox.askyesno("Quit", "Do you want to quit without saving ?"):
                self.window.destroy()
        else:
            self.window.destroy()

    def do_popup(self, event, widget=None):
        # Get location from widget
        try:
            self.folder_frame_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.folder_frame_menu.grab_release()
        self.last_right_clicked_widget = widget

    # Continue
    def rename_folder(self):
        print(self.last_right_clicked_widget)

root = tk.Tk(className="PyGuiFolder")
root.geometry('300x300')
myapp = App(root)

myapp.mainloop()