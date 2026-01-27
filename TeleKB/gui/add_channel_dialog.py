import tkinter as tk
from tkinter import ttk, messagebox
import threading
import concurrent.futures

class AddChannelDialog:
    def __init__(self, parent, telegram_service, db, on_add_callback):
        self.top = tk.Toplevel(parent)
        self.top.title("Add Channels")
        self.top.geometry("500x400")
        
        self.telegram_service = telegram_service
        self.db = db
        self.on_add_callback = on_add_callback
        
        self.channels_data = [] 
        
        self.create_widgets()
        self.load_channels()

    def create_widgets(self):
        # Options
        frame_opts = ttk.Frame(self.top, padding=5)
        frame_opts.pack(fill=tk.X)
        
        self.var_include_groups = tk.BooleanVar(value=False)
        chk_groups = ttk.Checkbutton(frame_opts, text="Include Groups", variable=self.var_include_groups, command=self.load_channels)
        chk_groups.pack(side=tk.LEFT)
        
        # List
        frame_list = ttk.Frame(self.top, padding=5)
        frame_list.pack(fill=tk.BOTH, expand=True)
        
        self.tree = ttk.Treeview(frame_list, columns=("title", "type", "id"), show="headings", selectmode="extended")
        self.tree.heading("title", text="Title")
        self.tree.heading("type", text="Type")
        self.tree.heading("id", text="ID")
        self.tree.column("id", width=100)
        
        scrollbar = ttk.Scrollbar(frame_list, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons
        frame_btns = ttk.Frame(self.top, padding=10)
        frame_btns.pack(fill=tk.X)
        
        btn_add = ttk.Button(frame_btns, text="Add Selected", command=self.add_selected)
        btn_add.pack(side=tk.RIGHT, padx=5)
        
        btn_close = ttk.Button(frame_btns, text="Close", command=self.top.destroy)
        btn_close.pack(side=tk.RIGHT)
        
        self.lbl_status = ttk.Label(frame_btns, text="Loading...")
        self.lbl_status.pack(side=tk.LEFT)

    def load_channels(self):
        # Run in thread
        self.tree.delete(*self.tree.get_children())
        self.lbl_status.config(text="Fetching channels from Telegram...")
        threading.Thread(target=self._fetch_channels_thread, daemon=True).start()

    def _fetch_channels_thread(self):
        try:
            # No need for asyncio loop here, service handles it.
            
            # Auth callbacks
            def _request_ui_input(prompt_type):
                f = concurrent.futures.Future()
                self.top.after(0, lambda: self._show_login_dialog(prompt_type, f))
                return f.result()

            phone_cb = lambda: _request_ui_input("phone")
            code_cb = lambda: _request_ui_input("code")
            pw_cb = lambda: _request_ui_input("password")
            
            # Connect (Sync call)
            connected = self.telegram_service.connect(
                phone_callback=phone_cb,
                code_callback=code_cb,
                password_callback=pw_cb
            )
            
            if not connected:
                self.top.after(0, lambda: self.lbl_status.config(text=f"Error: Login failed"))
                return

            include_groups = self.var_include_groups.get()
            channels = self.telegram_service.get_subscribed_channels(include_groups=include_groups)
            
            self.channels_data = channels
            self.top.after(0, self._populate_tree, channels)
            
        except Exception as e:
            print(f"Error fetching channels: {e}")
            self.top.after(0, lambda: self.lbl_status.config(text=f"Error: {e}"))

    def _show_login_dialog(self, prompt_type, future):
        dialog = tk.Toplevel(self.top)
        dialog.title("Telegram Login")
        dialog.geometry("400x150")
        
        lbl = ttk.Label(dialog, text="")
        lbl.pack(pady=10)
        
        entry = ttk.Entry(dialog)
        entry.pack(pady=5, padx=20, fill=tk.X)
        
        if prompt_type == "phone":
            lbl.config(text="Enter Phone (e.g. +82...):")
        elif prompt_type == "code":
            lbl.config(text="Enter Code:")
        elif prompt_type == "password":
            lbl.config(text="Enter Password:")
            entry.config(show="*")
            
        def submit():
            val = entry.get().strip()
            if val:
                future.set_result(val)
                dialog.destroy()
                
        entry.bind('<Return>', lambda e: submit())
        entry.focus_set()
        
        btn = ttk.Button(dialog, text="Submit", command=submit)
        btn.pack(pady=10)
        
        dialog.lift()
        dialog.attributes('-topmost', True)
        
        def on_close():
             if not future.done():
                 future.set_result("")
             dialog.destroy()
        dialog.protocol("WM_DELETE_WINDOW", on_close)

    def _populate_tree(self, channels):
        self.lbl_status.config(text=f"Found {len(channels)} channels.")
        for ch in channels:
            ctype = "Channel"
            if getattr(ch, 'megagroup', False):
                ctype = "Supergroup"
            elif getattr(ch, 'gigagroup', False):
                ctype = "Broadcast"
            self.tree.insert("", tk.END, values=(ch.title, ctype, ch.id))

    def add_selected(self):
        selected_items = self.tree.selection()
        if not selected_items:
            return
            
        self.lbl_status.config(text="Adding channels...")
        threading.Thread(target=self._add_selected_thread, args=(selected_items,), daemon=True).start()

    def _add_selected_thread(self, selected_items):
        count = 0
        try:
            # Ensure connected just in case (fast check if already connected)
            # Or assume connected since list loaded.
            
            for item_id in selected_items:
                item = self.tree.item(item_id)
                vals = item['values']
                title = vals[0]
                cid = int(vals[2])
                
                # Find entity object
                entity = None
                for ch in self.channels_data:
                    if ch.id == cid:
                        entity = ch
                        break
                
                username = getattr(entity, 'username', None)
                
                try:
                    latest_id = self.telegram_service.get_latest_message_id(cid)
                    success = self.db.add_channel(cid, title, username, latest_id)
                    if success:
                        count += 1
                except Exception as e:
                    print(f"Error adding {title}: {e}")
            
            self.top.after(0, lambda: self._finish_add(count))
            
        except Exception as e:
            print(f"Error in add thread: {e}")
            self.top.after(0, lambda: messagebox.showerror("Error", f"Failed to add channels: {e}"))
            self.top.after(0, lambda: self.lbl_status.config(text=f"Error: {e}"))

    def _finish_add(self, count):
        messagebox.showinfo("Result", f"Added {count} channels.")
        if self.on_add_callback:
            self.on_add_callback()
        self.top.destroy()
