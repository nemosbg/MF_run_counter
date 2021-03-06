import sys
import tkinter as tk
import win32gui
from tkinter import messagebox, ttk
import system_hotkey
from utils import tk_dynamic as tkd, other_utils


class Hotkeys(tkd.Frame):
    def __init__(self, main_frame, timer_frame, drop_frame, parent=None, **kw):
        tkd.Frame.__init__(self, parent, kw)
        self.main_frame = main_frame
        self.modifier_options = system_hotkey.modifier_options
        self.character_options = system_hotkey.character_options
        self.hk = system_hotkey.SystemHotkey()

        lf = tkd.Frame(self, height=20, width=179)
        lf.pack(expand=True, fill=tk.BOTH)
        lf.propagate(False)
        tkd.Label(lf, text='Action', font='Helvetica 11 bold', justify=tk.LEFT).pack(side=tk.LEFT)
        tkd.Label(lf, text='Key          ', font='Helvetica 11 bold', justify=tk.LEFT, width=9).pack(side=tk.RIGHT)
        tkd.Label(lf, text=' Modifier', font='Helvetica 11 bold', justify=tk.LEFT, width=7).pack(side=tk.RIGHT)

        self.add_hotkey(label_name='Start new run', keys=other_utils.safe_eval(main_frame.cfg['KEYBINDS']['start_key']), func=timer_frame.stop_start)
        self.add_hotkey(label_name='End run', keys=other_utils.safe_eval(main_frame.cfg['KEYBINDS']['end_key']), func=timer_frame.stop)
        self.add_hotkey(label_name='Delete prev', keys=other_utils.safe_eval(main_frame.cfg['KEYBINDS']['delete_prev_key']), func=timer_frame.delete_prev)
        self.add_hotkey(label_name='Pause', keys=other_utils.safe_eval(main_frame.cfg['KEYBINDS']['pause_key']), func=timer_frame.pause)
        self.add_hotkey(label_name='Add drop', keys=other_utils.safe_eval(main_frame.cfg['KEYBINDS']['drop_key']), func=drop_frame.add_drop)
        self.add_hotkey(label_name='Reset lap', keys=other_utils.safe_eval(main_frame.cfg['KEYBINDS']['reset_key']), func=timer_frame.reset_lap)
        self.add_hotkey(label_name='Make unclickable', keys=other_utils.safe_eval(main_frame.cfg['KEYBINDS']['make_unclickable']), func=main_frame.set_clickthrough)

    def add_hotkey(self, label_name, keys, func):
        if keys[0].lower() not in map(lambda x: x.lower(), self.modifier_options) or keys[1].lower() not in map(lambda x: x.lower(), self.character_options):
            messagebox.showerror('Invalid hotkey', 'One or several hotkeys are invalid. Please edit/delete mf_config.ini')
            sys.exit()
        default_modifier, default_key = keys
        action = label_name.replace(' ', '_').lower()
        setattr(self, '_' + action, keys)
        lf = tkd.LabelFrame(self, height=30, width=179)
        lf.propagate(False)
        lf.pack(expand=True, fill=tk.BOTH)

        lab = tkd.Label(lf, text=label_name)
        lab.pack(side=tk.LEFT)

        setattr(self, action + '_e', tk.StringVar())
        key = getattr(self, action + '_e')
        key.set(default_key)
        drop2 = ttk.Combobox(lf, textvariable=key, state='readonly', values=self.character_options)
        drop2.bind("<FocusOut>", lambda e: drop2.selection_clear())
        drop2.config(width=9)
        drop2.pack(side=tk.RIGHT, fill=tk.X, padx=2)

        setattr(self, action + '_m', tk.StringVar())
        mod = getattr(self, action + '_m')
        mod.set(default_modifier)
        drop1 = ttk.Combobox(lf, textvariable=mod, state='readonly', values=self.modifier_options)
        drop1.bind("<FocusOut>", lambda e: drop1.selection_clear())
        drop1.config(width=7)
        drop1.pack(side=tk.RIGHT)

        mod.trace_add('write', lambda name, index, mode: self.re_register(action, getattr(self, '_' + action), func))
        key.trace_add('write', lambda name, index, mode: self.re_register(action, getattr(self, '_' + action), func))
        if default_key.lower() != 'no_bind':
            reg_key = [keys[1].lower()] if keys[0] == '' else list(map(lambda x: x.lower(), keys))
            self.hk.register(reg_key, callback=lambda event: '' if win32gui.FindWindow(None, 'Add drop') else self.main_frame.queue.put(func))

    def re_register(self, event, old_hotkey, func):
        new_hotkey = [getattr(self, event + '_m').get(), getattr(self, event + '_e').get()]
        new_lower = list(map(lambda x: x.lower(), new_hotkey))
        if new_lower in [list(x) for x in list(self.hk.keybinds.keys())]:
            messagebox.showerror('Reserved bind', 'This keybind is already in use.')
            m = getattr(self, event + '_m')
            e = getattr(self, event + '_e')
            m.set(old_hotkey[0])
            e.set(old_hotkey[1])
        else:
            if old_hotkey[1].lower() != 'no_bind':
                unreg = [old_hotkey[1].lower()] if old_hotkey[0] == '' else list(map(lambda x: x.lower(), old_hotkey))
                self.hk.unregister(unreg)
            if new_hotkey[1].lower() != 'no_bind':
                reg = [new_hotkey[1].lower()] if new_hotkey[0] == '' else new_lower
                self.hk.register(reg, callback=lambda event: self.main_frame.queue.put(func), overwrite=True)
            setattr(self, '_' + event, new_hotkey)