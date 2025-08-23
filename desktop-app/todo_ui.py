import tkinter as tk
from tkinter import ttk, messagebox
from functools import partial
import db

class TodoUI(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.todo_data = db.get_todo_lists()

        # --- UI Components ---
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(expand=True, fill="both", padx=10, pady=10)

        # --- Add New List ---
        add_list_frame = ttk.Frame(self.main_frame)
        add_list_frame.pack(pady=10, fill="x")
        
        self.new_list_entry = ttk.Entry(add_list_frame)
        self.new_list_entry.pack(side="left", expand=True, fill="x")
        
        add_list_button = ttk.Button(add_list_frame, text="Create New List", command=self.add_new_list)
        add_list_button.pack(side="left", padx=5)

        # --- Todo Lists ---
        self.lists_canvas = tk.Canvas(self.main_frame)
        self.lists_frame = ttk.Frame(self.lists_canvas)
        
        self.scrollbar = ttk.Scrollbar(self.main_frame, orient="vertical", command=self.lists_canvas.yview)
        self.lists_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.lists_canvas.pack(side="left", fill="both", expand=True)
        self.lists_canvas.create_window((0,0), window=self.lists_frame, anchor="nw")

        self.lists_frame.bind("<Configure>", lambda e: self.lists_canvas.configure(scrollregion=self.lists_canvas.bbox("all")))

        self.render_todo_lists()

    def render_todo_lists(self):
        for widget in self.lists_frame.winfo_children():
            widget.destroy()

        for list_name, items in self.todo_data.items():
            self.create_list_widget(list_name, items)

    def create_list_widget(self, list_name, items):
        list_frame = ttk.LabelFrame(self.lists_frame, text=list_name, padding="10")
        list_frame.pack(pady=10, padx=10, fill="x", expand=True)

        # --- Add Item ---
        add_item_frame = ttk.Frame(list_frame)
        add_item_frame.pack(fill="x", pady=5)
        
        new_item_entry = ttk.Entry(add_item_frame)
        new_item_entry.pack(side="left", expand=True, fill="x")
        
        add_button = ttk.Button(add_item_frame, text="Add", command=lambda: self.add_item(list_name, new_item_entry))
        add_button.pack(side="left", padx=5)

        # --- Items List ---
        items_frame = ttk.Frame(list_frame)
        items_frame.pack(fill="x", expand=True)

        for item in items:
            self.create_item_widget(items_frame, list_name, item)
            
        # --- Delete List Button ---
        delete_list_button = ttk.Button(list_frame, text="Delete List", command=lambda: self.delete_list(list_name))
        delete_list_button.pack(pady=5, anchor="e")

    def create_item_widget(self, parent, list_name, item):
        item_frame = ttk.Frame(parent)
        item_frame.pack(fill="x", pady=2)

        is_done = item["done"]
        item_var = tk.BooleanVar(value=is_done)

        checkbutton = ttk.Checkbutton(item_frame, text=item["text"], variable=item_var, 
                                      command=partial(self.toggle_item, list_name, item["text"], item_var))
        checkbutton.pack(side="left")

        delete_button = ttk.Button(item_frame, text="Delete", command=lambda: self.delete_item(list_name, item["text"]))
        delete_button.pack(side="right")

    def add_new_list(self):
        list_name = self.new_list_entry.get().strip()
        if list_name and list_name not in self.todo_data:
            self.todo_data[list_name] = []
            db.save_todo_lists(self.todo_data)
            self.render_todo_lists()
            self.new_list_entry.delete(0, tk.END)
        elif list_name in self.todo_data:
            messagebox.showwarning("Warning", "A list with this name already exists.")
        else:
            messagebox.showwarning("Warning", "List name cannot be empty.")

    def delete_list(self, list_name):
        if messagebox.askyesno("Confirm", f"Are you sure you want to delete the list '{list_name}'?"):
            if list_name in self.todo_data:
                del self.todo_data[list_name]
                db.save_todo_lists(self.todo_data)
                self.render_todo_lists()

    def add_item(self, list_name, entry_widget):
        item_text = entry_widget.get().strip()
        if item_text:
            self.todo_data[list_name].append({"text": item_text, "done": False})
            db.save_todo_lists(self.todo_data)
            self.render_todo_lists()
            entry_widget.delete(0, tk.END)
        else:
            messagebox.showwarning("Warning", "Todo item cannot be empty.")

    def delete_item(self, list_name, item_text):
        self.todo_data[list_name] = [item for item in self.todo_data[list_name] if item["text"] != item_text]
        db.save_todo_lists(self.todo_data)
        self.render_todo_lists()

    def toggle_item(self, list_name, item_text, item_var):
        for item in self.todo_data[list_name]:
            if item["text"] == item_text:
                item["done"] = item_var.get()
                break
        db.save_todo_lists(self.todo_data)
        self.render_todo_lists()
