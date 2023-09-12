import tkinter as tk
import os
from tkinter import filedialog as fd
import ntpath
import json
import uuid
from tkinter import messagebox
from tkinter import Menu
import shutil
import platform

# Tkinter Source Code: https://github.com/python/cpython/blob/3.11/Lib/tkinter/
# Tkinter colors: https://www.plus2net.com/python/tkinter-colors.php
# Tkinter tuto: https://realpython.com/python-gui-tkinter/
# Tkinter messagebox: https://docs.python.org/3/library/tkinter.messagebox.html

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
        self.window.bind("<Control-s>", self.save)
        self.window.bind("<Control-S>", self.save)

        # Create navbar
        menu = Menu(master=master)
        self.window.config(menu=menu)

        # Add file main item to navbar
        filemenu = Menu(master=menu, tearoff=0)
        menu.add_cascade(label="File", underline=1, menu=filemenu)
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
        self.new_folder_btn = tk.Button(master=self.folders_frame, text="New Folder", command=self.get_new_folder_name, bg='chocolate1', fg='azure1')
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

        # Setup local directory to save content
        try:
            os.mkdir(f"{self.dir_path}/.pyguifolder")
        except FileExistsError as e:
            pass
        except Exception as e:
            messagebox.showerror("Failed", f"Error while creating directory {e}")

        # saved content var
        self.saved = True

        # Show symlink error once
        self.symlink_error_displayed = False
        
        # Copy files instead of symlinks
        self.copy_files_instead = False

    def open_file(self, path):
        #Try to open the file
        current_platform = platform.system()
        
        # check platform to change the command to use
        if current_platform == 'Windows':
            os.system(f"\"{path}\"")
        else:
            os.system(f"open {path}")
    
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
        new_btn_File1.bind("<Button-1>", lambda _= "Open File": self.open_file(new_btn_File1.path))
        new_btn_File1.bind("<Button-2>", self.remove_file)

        print("Added a new file")

        # Update position of addFiles button
        self.new_file_btn.grid(column=file_column + 1, row=file_row, sticky="ew", padx=5, pady=10)

        self.saved = False

        return new_btn_File1.id


    # Creates a new file entry, saves to logs and copies the file to .pyguifolder
    def create_and_update_file(self, filename):

        # Copy file to safe location
        new_path, original_file_use = self.create_symlink_file(filename)

        # None if file already exists
        if new_path is None:
            return 
        
        file_id = self.create_file(new_path)
        
        # Save file to the logs
        self.log_objects[self.current_folder.id]["files"].append({
            "file_id":file_id,
            "path":new_path,
            "original_file_use":original_file_use
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
            self.change_current_folder(self.current_folder, new_folder)

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
        
        #self.current_folder = new_folder
        self.change_current_folder(self.current_folder, new_folder)

        for item in self.files_frame.winfo_children():
            if isinstance(item, File):
                item.destroy()

        for file in self.log_objects[new_folder.id].get("files"):
            self.create_file(file.get("path"))

    def save(self, event=None):
        
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
        column = self.get_widget_grid_column(renamed_widget)

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
        column = self.get_widget_grid_column(folderlabel)

        # If no name supplied re add the folder and keep its name
        if not foldername:
            folderlabel.destroy()
            folder.grid(column=column,row=0, sticky="ew")
            return
        
        # If new name
        folderlabel.destroy()

        # If current folder is the one being destroyed, change current folder to None
        if self.current_folder.id == folder.id:
            self.current_folder = None
        
        folder.destroy()
        self.create_new_folder(foldername=foldername, id=id, column=column)

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
        file_path = file.path

        # Delete file widget
        file.destroy()

        # Remove file log
        current_folder_files = self.log_objects[folder_id].get('files')
        for file in current_folder_files:
            if file['file_id'] == file_id:
                # Delete file if its not an original file
                if not file['original_file_use']:
                    self.delete_symlink_file(file_path)
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

        # Switch folders
        try:
            self.switch_folders(self.folders_frame.winfo_children()[1])
        # Error when there's no longer any folders
        except IndexError:
            self.current_folder = None
            self.clear_all_files()

        # Delete folder
        folder.destroy()

        # Update logs
        del self.log_objects[folder_id]

        self.saved = False

    def clear_all_files(self):
        for file in self.files_frame.winfo_children():
            if isinstance(file, File):
                file.destroy()

    # Copy saved file to .pyguifolder
    # TODO: create files in directories depending on their virtual folder
    def create_symlink_file(self, filename):

        # Keep track of whats saved in the logs     
        original_file_use = False
        
        # Create directory if it doesn't exist
        dest_dir = f"{self.dir_path}/.pyguifolder/saved_files"
        if not os.path.isdir(dest_dir):
            os.mkdir(dest_dir)

        new_path = f"{dest_dir}/{ntpath.basename(filename)}"
        try:
            # Either we create a symlink if its possible
            os.symlink(filename, new_path)
            return new_path, original_file_use
        except OSError:
            if os.path.exists(new_path):
                messagebox.showinfo("Not added", "File already exists in another folder")
                return None, None
            # Or we make a copy of the file if the user wants
            if not self.symlink_error_displayed:
                self.symlink_error_displayed = True
                if messagebox.askyesno("Not enough priviliges", f"Unable to create symlink to files (run as administrator to fix this).\nDo you want us to copy the files instead ? "):  
                   self.copy_files_instead = True 
                   messagebox.showinfo("Notice", f"Your pyguifolder files are now different than the ones you had.\nChanges to files opened from pyguifolder will not be saved to the original ones.") 
            if self.copy_files_instead:
                shutil.copyfile(filename, new_path)
                return new_path, original_file_use
            
        # Else we use the original file
        original_file_use = True
        return filename, original_file_use

    def delete_symlink_file(self, filepath):
        try:
            os.remove(filepath)
        except FileNotFoundError:
            pass

    def change_current_folder(self, old_folder, current_folder):

        # Change old folder style if it exists
        if old_folder is not None:
            old_folder_column = self.get_widget_grid_column(old_folder)
            old_folder['fg'] = "black"
            old_folder.grid(column=old_folder_column, row=0, sticky="ew")

        # change current folder variable
        self.current_folder = current_folder

        # Change current folder style
        current_folder_column = self.get_widget_grid_column(self.current_folder)
        self.current_folder['fg'] = "chocolate1"
        self.current_folder.grid(column=current_folder_column, row=0, sticky="ew")

    def get_widget_grid_column(self, widget):
        return widget.grid_info().get("column")

root = tk.Tk()
root.title("PyGUIFolder")
root.geometry('500x400')
myapp = App(root)

myapp.mainloop()