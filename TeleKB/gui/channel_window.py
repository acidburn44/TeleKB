import tkinter as tk
from tkinter import ttk, messagebox
import threading
from .add_channel_dialog import AddChannelDialog

class ChannelWindow:
    def __init__(self, parent, db, telegram_service):
        self.top = tk.Toplevel(parent)
        self.top.title("Channel Management")
        self.top.geometry("600x400")
        
        self.db = db
        self.telegram_service = telegram_service
        
        self.create_widgets()
        self._reload_tree() # Load local data immediately
        self.refresh_list()

    def create_widgets(self):
        # Toolbar
        frame_toolbar = ttk.Frame(self.top, padding=5)
        frame_toolbar.pack(fill=tk.X)
        
        btn_add = ttk.Button(frame_toolbar, text="Add Channel", command=self.open_add_dialog)
        btn_add.pack(side=tk.LEFT, padx=5)
        
        btn_remove = ttk.Button(frame_toolbar, text="Delete Channel", command=self.delete_channel)
        btn_remove.pack(side=tk.LEFT, padx=5)
        
        btn_refresh = ttk.Button(frame_toolbar, text="Refresh", command=self.refresh_list)
        btn_refresh.pack(side=tk.RIGHT, padx=5)
        
        # List
        self.tree = ttk.Treeview(self.top, columns=("id", "title", "enabled", "last_msg"), show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("title", text="Title")
        self.tree.heading("enabled", text="Enabled")
        self.tree.heading("last_msg", text="Last Msg ID")
        
        self.tree.column("id", width=100)
        self.tree.column("enabled", width=80)
        self.tree.column("last_msg", width=100)
        
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.lbl_status = ttk.Label(self.top, text="Ready")
        self.lbl_status.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

    def refresh_list(self):
        # Run sync in thread
        if self.top.winfo_exists():
            self.lbl_status.config(text="Syncing with Telegram...")
        
        threading.Thread(target=self._sync_refresh_thread, daemon=True).start()

    def _sync_refresh_thread(self):
        try:
            # 1. Get local channels
            local_channels = self.db.get_channels(only_enabled=False) # Get all
            local_map = {c['channel_id']: c for c in local_channels}
            
            if not local_map:
                if self.top.winfo_exists():
                     self.top.after(0, self._reload_tree)
                return

            # 2. Get remote channels (subscribed)
            # This might require auth. Using service.connect if needed? 
            # service.get_subscribed_channels calls connect internally but needs callbacks if auth required.
            # Assuming already authenticated if using this window, or it might fail if session invalid.
            # Let's try to pass dummy callbacks or reuse the ones if we had them (we don't stored them).
            
            # Simple connect check
            # We can't easily pop up login dialog from here without importing MainWindow logic or duplicating.
            # For "Refresh", let's assume session is valid. If not, it might fail/return empty.
            
            try:
                # We need to include groups if we want to sync groups too.
                # But get_subscribed_channels filters based on arg.
                # We should get ALL dialogs to be safe? 
                # Or just call twice?
                # Let's call with include_groups=True to get everything user might have added.
                remote_channels = self.telegram_service.get_subscribed_channels(include_groups=True)
            except Exception as e:
                print(f"Sync error (remote fetch): {e}")
                # Fallback to local reload
                if self.top.winfo_exists():
                    self.top.after(0, self._reload_tree)
                return

            remote_map = {c.id: c.title for c in remote_channels}
            
            # 3. Compare and Update
            updates_count = 0
            for cid, local_data in local_map.items():
                if cid in remote_map:
                    remote_title = remote_map[cid]
                    local_title = local_data['title']
                    
                    if remote_title != local_title:
                        print(f"Updating title for {cid}: {local_title} -> {remote_title}")
                        self.db.update_channel_title(cid, remote_title)
                        updates_count += 1
            
            if updates_count > 0:
                print(f"Updated {updates_count} channel titles.")
                
            if self.top.winfo_exists():
                self.top.after(0, self._reload_tree)
            
        except Exception as e:
            print(f"Sync error: {e}")
            if self.top.winfo_exists():
                self.top.after(0, self._reload_tree)

    def _reload_tree(self):
        if not self.top.winfo_exists():
            return
            
        try:
            self.tree.delete(*self.tree.get_children())
            channels = self.db.get_channels(only_enabled=False) # Show all
            
            for ch in channels:
                status = "Enabled" if ch['is_enabled'] else "Disabled"
                self.tree.insert("", tk.END, values=(ch['channel_id'], ch['title'], "Active", ch['last_message_id']))
                
            self.lbl_status.config(text=f"Loaded {len(channels)} channels.")
        except Exception as e:
            print(f"Reload tree error: {e}")

    def open_add_dialog(self):
        AddChannelDialog(self.top, self.telegram_service, self.db, self.refresh_list)

    def delete_channel(self):
        selected = self.tree.selection()
        if not selected:
            return
            
        if not messagebox.askyesno("Confirm", "Are you sure you want to delete the selected channels?\nThis will remove them from the database."):
            return

        for item_id in selected:
            item = self.tree.item(item_id)
            cid = item['values'][0]
            self.db.delete_channel(cid)
            
        self.refresh_list()
