from utils import tk_dynamic as tkd, tk_utils, autocompletion
import tkinter as tk
from tkinter import ttk


class Drops(tkd.Frame):
    def __init__(self, timer_tab, parent=None, **kw):
        tkd.Frame.__init__(self, parent.root, kw)
        self.parent = parent
        self.drops = dict()
        self.timer_tab = timer_tab

        self._make_widgets()
        # self.load_item_library()
        # a = 0

    def _make_widgets(self):
        lf = tkd.Frame(self)
        lf.pack(expand=1, fill=tk.BOTH)
        scrollbar = ttk.Scrollbar(lf, orient=tk.VERTICAL)

        self.m = tkd.Text(lf, height=5, yscrollcommand=scrollbar.set, font='courier 11', wrap=tk.WORD, state=tk.DISABLED, cursor='', exportselection=1, name='droplist')

        self.m.pack(side=tk.LEFT, fill=tk.BOTH, expand=1, pady=(2, 1), padx=1)
        scrollbar.config(command=self.m.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=(2, 1), padx=0)

        btn = tkd.Button(self, text='Delete selection', command=self.delete)
        btn.bind_all('<Delete>', lambda e: self.delete())
        btn.pack(side=tk.BOTTOM, pady=(1, 2))

    def add_drop(self):
        drop = autocompletion.acbox(enable=self.parent.autocomplete)
        if not drop or drop['input'] == '':
            return
        if drop['item_name'] is not None and self.parent.item_shortnames:
            shortname = autocompletion.ITEM_SHORTNAMES.get(drop['item_name'], drop['item_name'])
            drop['input'] = shortname + ' ' + drop['extra']
        print(drop)
        run_no = len(self.timer_tab.laps)
        if self.timer_tab.is_running:
            run_no += 1

        self.drops.setdefault(str(run_no), []).append(drop)
        self.display_drop(drop=drop, run_no=run_no)

    def display_drop(self, drop, run_no):
        line = 'Run %s: %s' % (run_no, drop['input'])
        if self.m.get('1.0', tk.END) != '\n':
            line = '\n' + line
        self.m.config(state=tk.NORMAL)
        self.m.insert(tk.END, line)
        self.m.yview_moveto(1)
        self.m.config(state=tk.DISABLED)

    def delete(self):
        if self.focus_get()._name == 'droplist':
            cur_row = self.m.get('insert linestart', 'insert lineend+1c').strip()
            resp = tk_utils.mbox(msg='Do you want to delete the row:\n%s' % cur_row, title='Warning')
            if resp is True:
                sep = cur_row.find(':')
                run_no = cur_row[:sep].replace('Run ', '')
                drop = cur_row[sep+2:]
                self.drops[run_no].remove(next(d for d in self.drops[run_no] if d['input'] == drop))
                self.m.config(state=tk.NORMAL)
                self.m.delete('insert linestart', 'insert lineend+1c')
                self.m.config(state=tk.DISABLED)

                self.parent.img_panel.focus_force()

    def save_state(self):
        return self.drops

    def load_from_state(self, state):
        self.m.config(state=tk.NORMAL)
        self.m.delete(1.0, tk.END)
        self.m.config(state=tk.DISABLED)
        self.drops = state.get('drops', dict())
        for k, v in self.drops.items():
            for i in range(len(v)):
                if not isinstance(v[i], dict):
                    self.drops[k][i] = {'item_name': None, 'input': v[i], 'extra': ''}
        for run in sorted(self.drops.keys(), key=lambda x: int(x)):
            for drop in self.drops[run]:
                self.display_drop(drop=drop, run_no=run)

    # def load_item_library(self):
    #     import pandas as pd
    #     lib = pd.read_csv('item_library.csv', index_col='Item')
    #     alias_cols = [c for c in lib.columns if c.lower().startswith('alias')]
    #     lib['Alias'] = lib[alias_cols].values.tolist()
    #     pre_dict = lib['Alias'].to_dict()
    #     self.item_alias = {l: k for k, v in pre_dict.items() for l in v if str(l) != 'nan'}
    #
    #     for c in alias_cols + ['Alias']:
    #         del lib[c]
    #     self.item_library = lib
    #
    # def lookup_item(self, item_alias):
    #     x = item_alias.lower()
    #     item_name = ' '.join(w.capitalize() for w in self.item_alias.get(x, x).split())
    #     return dict(Name=item_name, Alias=item_alias)