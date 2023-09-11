import tkinter as tk
import os
from tkinter import filedialog as fd
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

#TODO: bind CTRL+S > save 
#TODO add navbar https://python-course.eu/tkinter/menus-in-tkinter.php | https://www.tutorialspoint.com/python/tk_menu.htm | https://koor.fr/Python/Tutoriel_Tkinter/tkinter_menu.wp

class File(tk.Button):
    def __init__(self, path, id=None, master=None, **kw):
        super().__init__(master, **kw)
        self.path = path
        if not id:
            self.id = str(uuid.uuid4())
        else:
            self.id = id

class Folder(tk.Button):
    def __init__(self, id=None, master=None, **kw):
        super().__init__(master, **kw)
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

        # Get file dir path
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        
        self.log_objects = {}
        
        # Handle close before saving
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.window.bind("<Button-3>", lambda _: self.window.focus_set())

        # Create navbar
        menu = Menu(master=master)
        self.window.config(menu=menu)

        # Add file main item to navbar
        filemenu = Menu(master=menu, tearoff=0)
        menu.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="Save", command=self.save)
        filemenu.add_command(label="Exit", command=self.exit)

        # Folders Frame
        self.folders_frame = tk.Frame(
                    master=master,
                    relief=tk.RAISED,
                    background="gray24"
                )
        self.folders_frame.pack(fill=tk.X)

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
            filetypes=filetypes
            )
        
        if filename:
            # Add file to the grid
            self.create_and_update_file(filename)

    def create_file(self, filename, id=None):
        # Get the number of files added and calculate row and column
        file_position = self.get_new_file_loc()
        file_row = file_position // 5
        file_column = file_position % 5

        # Create the new button
        new_btn_File1 = File(master=self.files_frame, text=ntpath.basename(filename), path=filename, id=id)
        new_btn_File1.grid(column=file_column, row=file_row, sticky="ew", padx=5, pady=10)

        # Add button onclick functionalities
        new_btn_File1.bind("<Button-1>", lambda _= "Open File": self.handle_file_btn_keypress(new_btn_File1.path))
        new_btn_File1.bind("<Button-2>", self.remove_file)

        print("Added a new file")

        # Update position of addFiles button
        self.new_file_btn.grid(column=file_column + 1, row=file_row, sticky="ew", padx=5, pady=10)

        self.saved = False

        return new_btn_File1.id


    def create_and_update_file(self, filename):
        file_id = self.create_file(filename)

        # Save file to the logs
        self.log_objects[self.current_folder.id]["files"].append({
            "file_id":file_id,
            "path":filename
            }
            )


    def get_new_folder_name(self):

        # Get the number of files added and calculate row and column
        file_position = self.get_new_folder_loc()
        file_column = file_position

        # Create label to register folder name
        folder_label = tk.Entry(master=self.folders_frame)
        folder_label.grid(column=file_column+1, row=0, sticky="ew")
        folder_label.focus_set()

        contents = tk.StringVar()
        contents.set("FolderName ?")
        folder_label["textvariable"] = contents

        # Remove new folder button
        self.new_folder_btn.grid_remove()

        folder_label.bind('<FocusIn>', lambda _= "Delete text on focus": contents.set(""))
        folder_label.bind('<FocusOut>', lambda _= "Add text on unfocus": contents.set("FolderName ?"))
        folder_label.bind('<Key-Return>', lambda _= "Create new folder": self.create_new_folder(foldername=contents.get(), folderlabel=folder_label))
        folder_label.bind('<Escape>', lambda _= "Create new folder": self.create_new_folder(foldername="", folderlabel=folder_label))
    
    def create_new_folder(self, foldername, id=None, folderlabel=None, column=None):

        # Get the number of files added and calculate row and column
        if column is None:
            file_position = self.get_new_folder_loc()
            column = file_position

        if folderlabel:
            folderlabel.destroy()

        if not foldername:
            # Add button again
            self.new_folder_btn.grid(column=column, row=0, sticky="ew")
            return
        
        # Create the new Folder
        new_folder = Folder(master=self.folders_frame, text=foldername, id=id)
        new_folder.grid(column=column, row=0, sticky="ew")

        # Add button onclick function
        new_folder.bind("<Button-1>", lambda _= "Switch folders": self.switch_folders(new_folder))

        # Rename folder with left click
        new_folder.bind("<Button-3>", self.rename_folder)

        # Delete folder with middle mouse
        new_folder.bind("<Button-2>", self.delete_folder)

        print("Added a new folder")
        
        # Update position of new folder button
        self.update_new_folder_button()
        
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
            self.create_file(file.get("path"))

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

        self.saved = True

    def exit(self):
        pass

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
                    self.create_file(file.get("path"), file.get("file_id"))
            except FileNotFoundError:
                return
    
    def on_closing(self):
        if not self.saved:
            if messagebox.askyesno("Quit", "Do you want to quit without saving ?"):
                self.window.destroy()
        else:
            self.window.destroy()

    def rename_folder(self, event):

        renamed_widget = event.widget

        # Get folder's column and row
        info = renamed_widget.grid_info()
        column = info.get("column")
        #row = info.get("row")

        # Get folder's id
        id = renamed_widget.id

        # Remove folder from grid
        renamed_widget.grid_remove()
        
        # Replace folder with label
        folder_label = tk.Entry(master=self.folders_frame)
        folder_label.grid(column=column, row=0, sticky="ew")
        folder_label.focus_set()
        
        contents = tk.StringVar()
        contents.set("FolderName ?")
        folder_label["textvariable"] = contents

        folder_label.bind('<FocusIn>', lambda _= "Delete text on focus": contents.set(""))
        folder_label.bind('<FocusOut>', lambda _= "Add text on unfocus": contents.set("FolderName ?"))
        folder_label.bind('<Key-Return>', lambda _= "Create new folder": self.update_folder_name(foldername=contents.get(),
                                                                                                  folderlabel=folder_label, 
                                                                                                  id=id, 
                                                                                                  folder=renamed_widget)
                                                                                                  )
        folder_label.bind('<Escape>', lambda _= "Create new folder": self.update_folder_name(foldername="",
                                                                                                  folderlabel=folder_label, 
                                                                                                  id=id, 
                                                                                                  folder=renamed_widget)
                                                                                                  )
    
    def update_folder_name(self, foldername, id, folderlabel, folder):
        
        # Get label column
        column = folderlabel.grid_info().get("column")

        # If no name supplied re add the folder and keep its name
        if not foldername:
            folderlabel.destroy()
            folder.grid(column=column,row=0, sticky="ew")
            return
        
        # If new name
        folderlabel.destroy()
        self.create_new_folder(foldername=foldername, id=id, column=column)
        folder.destroy()

        # Update current logs
        self.log_objects[id]['name'] = foldername
    
    def update_new_folder_button(self):
        
        # Get number of children in folder frame
        n_widgets = self.get_new_folder_loc()

        self.new_folder_btn.grid(column=n_widgets+1, row=0, sticky="ew")

    def remove_file(self, event):
        
        file = event.widget

        file_id = file.id
        folder_id = self.current_folder.id
        
        # Delete file widget
        file.destroy()

        # Remove file log
        current_folder_files = self.log_objects[folder_id].get('files')
        for file in current_folder_files:
            if file['file_id'] == file_id:
                print("Removing file")
                current_folder_files.remove(file)
                continue

        # Update saved var
        self.saved = False

    def delete_folder(self, event):
        if not messagebox.askyesno(title="Delete Folder", message="Are you sure you want to delete this folder ?"):
            return
        
        # Get folder id
        folder = event.widget
        folder_id = folder.id

        # Delete folder
        folder.destroy()

        # Switch folders
        try:
            self.switch_folders(self.folders_frame.winfo_children()[1])
        # Error when there's no longer any folders
        except IndexError:
            self.current_folder = None
            self.clear_all_files()

        # Update logs
        del self.log_objects[folder_id]

        self.saved = False

    def clear_all_files(self):
        for file in self.files_frame.winfo_children():
            if isinstance(file, File):
                file.destroy()

root = tk.Tk(className="PyGuiFolder")
root.geometry('500x400')
myapp = App(root)

myapp.mainloop()