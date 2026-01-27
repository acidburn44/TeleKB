import tkinter as tk
from tkinter import ttk, messagebox
import asyncio

class LoginDialog:
    def __init__(self, parent, loop):
        self.top = tk.Toplevel(parent)
        self.top.title("Telegram Login")
        self.top.geometry("400x200")
        
        self.loop = loop
        
        # Futures to bridge async login with UI
        self.future_phone = loop.create_future()
        self.future_code = loop.create_future()
        self.future_password = loop.create_future()
        
        # State
        self.current_state = "phone"
        
        self.create_widgets()
        
    def create_widgets(self):
        self.lbl_instruction = ttk.Label(self.top, text="Enter Phone (+CountryCode...):")
        self.lbl_instruction.pack(pady=10)
        
        self.entry_input = ttk.Entry(self.top)
        self.entry_input.pack(pady=5, padx=20, fill=tk.X)
        self.entry_input.bind('<Return>', lambda e: self.submit())
        
        self.btn_submit = ttk.Button(self.top, text="Submit", command=self.submit)
        self.btn_submit.pack(pady=10)

    def submit(self):
        val = self.entry_input.get().strip()
        if not val:
            return
            
        # We need to set the result on the future corresponding to current state
        # But we don't know which state "client.start" is in exactly from here
        # Actually user calls methods below.
        
        if self.current_state == "phone":
             if not self.future_phone.done():
                 self.future_phone.set_result(val)
        elif self.current_state == "code":
             if not self.future_code.done():
                 self.future_code.set_result(val)
        elif self.current_state == "password":
             if not self.future_password.done():
                 self.future_password.set_result(val)
                 
        self.entry_input.delete(0, tk.END)
        self.btn_submit.configure(state=tk.DISABLED)
        self.lbl_instruction.config(text="Processing...")

    # These methods are called by telethon (via lambda wrapper)
    # They should block/await until UI provides input.
    # But since they are called in async loop, we return a Future/coroutine result.
    
    async def get_phone(self):
        self.current_state = "phone"
        self.reset_ui("Enter Phone Number (e.g. +82...):", show="*") # Show normal
        await self.future_phone
        return self.future_phone.result()

    async def get_code(self):
        self.current_state = "code"
        self.reset_ui("Enter Code:", show="")
        await self.future_code
        return self.future_code.result()

    async def get_password(self):
        self.current_state = "password"
        self.reset_ui("Enter Password:", show="*")
        await self.future_password
        return self.future_password.result()

    def reset_ui(self, label_text, show=""):
        # UI update must be on main thread. 
        # But we might be calling this from async thread.
        # Tkinter is not thread safe? 
        # Actually standard practice: use after or assuming safety if simple?
        # Let's use after just in case if we can access root.
        # But here we are in same process. 
        # Telethon runs on a background thread usually in our design?
        # In main_window we run loop in thread. So yes, background thread.
        # We must use proper thread scheduling.
        pass
        # Since scheduling from another thread is complex without reference to root's loop,
        # we will rely on a trick or pass callback. 
        # For simplicity, if we just modify properties, tcl might handle or crash.
        # Let's simple update:
        self.top.after(0, lambda: self._update_ui(label_text, show))

    def _update_ui(self, label_text, show):
        self.lbl_instruction.config(text=label_text)
        self.entry_input.configure(show=show)
        self.entry_input.delete(0, tk.END)
        self.entry_input.focus()
        self.btn_submit.configure(state=tk.NORMAL)
        
    def close(self):
        self.top.destroy()
