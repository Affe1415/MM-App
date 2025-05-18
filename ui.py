import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from tkinter.scrolledtext import ScrolledText
import unicodedata
import theme
import storage

def normalize_text(text):
    """ Tar bort accenter och gör texten lowercase """
    return unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8').lower()

class TemplateApp:
    def __init__(self, root):
        self.root = root
        theme.setup_theme(self.root)
        self.root.title('Email Template Manager')
        self.root.geometry('900x650')
        self.root.minsize(800, 600)

        # Stilar
        self.setup_styles()
        self.root.configure(bg=self.root.bg_color)

        self.category_var = tk.StringVar()
        self.subcategory_var = tk.StringVar()
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self.filter_templates())
        self.status_var = tk.StringVar(value='Redo')

        self.categories = []
        self.subcategories = []
        self.current_template_id = None

        self.create_widgets()
        self.load_categories()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('.', background=self.root.bg_color)
        style.configure('TFrame', background=self.root.bg_color)
        style.configure('TLabel', background=self.root.bg_color, foreground=self.root.text_color)
        style.configure('TButton', padding=6, background=self.root.primary_color, foreground='white')
        style.configure('TCombobox', fieldbackground='white')
        style.configure('TEntry', fieldbackground='white')
        style.map('TButton',
            background=[('active', self.root.secondary_color), ('disabled', '#cccccc')],
            foreground=[('active', 'white'), ('disabled', '#888888')]
        )
        style.configure('Header.TLabel', font=('Helvetica', 12, 'bold'), foreground=self.root.primary_color)
        style.configure('Status.TLabel', font=('Helvetica', 9), relief=tk.SUNKEN, padding=5)

    def create_widgets(self):
        # Header
        header = ttk.Label(self.root, text="Mallhanterare", style='Header.TLabel', anchor='w')
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 0))

        main_frame = ttk.Frame(self.root)
        main_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=20)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Övre del med kategorier och sök
        top_frame = ttk.Frame(main_frame)
        top_frame.grid(row=0, column=0, sticky="ew")

        # Kategorier
        category_frame = ttk.LabelFrame(top_frame, text=" Kategorier ", padding=10)
        category_frame.grid(row=0, column=0, sticky="ew")

        ttk.Label(category_frame, text='Huvudkategori:').grid(row=0, column=0, sticky='w', pady=2)
        self.category_menu = ttk.Combobox(category_frame, textvariable=self.category_var, state='readonly')
        self.category_menu.grid(row=0, column=1, padx=5, sticky='ew')
        self.category_menu.bind('<<ComboboxSelected>>', lambda e: self.select_category(self.category_var.get()))

        ttk.Label(category_frame, text='Underkategori:').grid(row=1, column=0, sticky='w', pady=2)
        self.subcategory_menu = ttk.Combobox(category_frame, textvariable=self.subcategory_var, state='readonly')
        self.subcategory_menu.grid(row=1, column=1, padx=5, sticky='ew')
        self.subcategory_menu.bind('<<ComboboxSelected>>', lambda e: self.select_subcategory(self.subcategory_var.get()))

        # Knappar för kategorihantering
        cat_btn_frame = ttk.Frame(category_frame)
        cat_btn_frame.grid(row=0, column=2, rowspan=2, padx=10, sticky="ns")
        ttk.Button(cat_btn_frame, text='Ny kategori', command=self.add_category).pack(fill=tk.X, pady=2)
        ttk.Button(cat_btn_frame, text='Ta bort', command=self.delete_category).pack(fill=tk.X, pady=2)
        ttk.Button(cat_btn_frame, text='Ny underkategori', command=self.add_subcategory).pack(fill=tk.X, pady=2)
        ttk.Button(cat_btn_frame, text='Ta bort', command=self.delete_subcategory).pack(fill=tk.X, pady=2)

        category_frame.grid_columnconfigure(1, weight=1)

        # Sökfält
        search_frame = ttk.LabelFrame(top_frame, text=" Sök ", padding=10)
        search_frame.grid(row=0, column=1, sticky="ew", padx=(10, 0))
        ttk.Label(search_frame, text='🔍', font=('Segoe UI', 13)).pack(side=tk.LEFT, padx=(0, 6))
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, font=('Segoe UI', 11))
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        search_entry.bind('<Return>', lambda e: self.filter_templates())

        top_frame.grid_columnconfigure(0, weight=1)
        top_frame.grid_columnconfigure(1, weight=1)

        # Huvudinnehåll
        content_frame = ttk.Frame(main_frame)
        content_frame.grid(row=1, column=0, sticky="nsew")
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        # Malllista
        list_frame = ttk.LabelFrame(content_frame, text=" Mallar ", padding=10)
        list_frame.grid(row=0, column=0, sticky="nsw")
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        self.template_listbox = ttk.Treeview(
            list_frame,
            columns=('title',),
            show='headings',
            selectmode='browse',
            height=20
        )
        self.template_listbox.heading('title', text='Malltitel')
        self.template_listbox.column('title', anchor='w', width=200)
        self.template_listbox.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.template_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.template_listbox.config(yscrollcommand=scrollbar.set)

        # Minimalistiska knappar för mallhantering
        list_btn_frame = ttk.Frame(list_frame)
        list_btn_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(5, 0))
        ttk.Button(list_btn_frame, text='Lägg till', command=self.add_template, style='TButton').grid(row=0, column=0, sticky="ew", padx=(0, 2), ipadx=8, ipady=2)
        ttk.Button(list_btn_frame, text='Ta bort', command=self.delete_template, style='TButton').grid(row=0, column=1, sticky="ew", ipadx=8, ipady=2)
        list_btn_frame.grid_columnconfigure(0, weight=1)
        list_btn_frame.grid_columnconfigure(1, weight=1)

        # Textredigerare
        editor_frame = ttk.LabelFrame(content_frame, text=" Redigera mall ", padding=10)
        editor_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)

        # Formateringsknappar
        format_btn_frame = ttk.Frame(editor_frame)
        format_btn_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))

        ttk.Button(format_btn_frame, text='𝐁', command=self.make_bold, width=3).grid(row=0, column=0, padx=2)
        ttk.Button(format_btn_frame, text='𝘐', command=self.make_italic, width=3).grid(row=0, column=1, padx=2)
        ttk.Button(format_btn_frame, text='U̲', command=self.make_underline, width=3).grid(row=0, column=2, padx=2)
        ttk.Label(format_btn_frame, text='Textstorlek:').grid(row=0, column=3, padx=(10,2))
        self.font_size_var = tk.IntVar(value=10)
        font_size_spin = ttk.Spinbox(format_btn_frame, from_=8, to=48, width=4, textvariable=self.font_size_var, command=self.change_font_size)
        font_size_spin.grid(row=0, column=4)

        self.text_area = ScrolledText(
            editor_frame,
            wrap=tk.WORD,
            font=('Arial', self.font_size_var.get()),
            padx=10,
            pady=10,
            bg='white',
            width=50,
            height=20
        )
        self.text_area.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)

        # Knappar för redigering
        edit_btn_frame = ttk.Frame(editor_frame)
        edit_btn_frame.grid(row=2, column=0, sticky="ew", pady=(5, 0))
        ttk.Button(edit_btn_frame, text='Spara ändringar', command=self.save_template).grid(row=0, column=0, padx=2)
        ttk.Button(edit_btn_frame, text='Kopiera till urklipp', command=self.copy_to_clipboard).grid(row=0, column=1, padx=2)
        ttk.Button(edit_btn_frame, text='Exportera mallar', command=self.export_templates).grid(row=0, column=2, padx=2)

        editor_frame.grid_rowconfigure(1, weight=1)
        editor_frame.grid_columnconfigure(0, weight=1)

        # Statusrad
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        ttk.Label(
            status_frame,
            textvariable=self.status_var,
            style='Status.TLabel',
            anchor=tk.W
        ).pack(fill=tk.X, padx=8, pady=4)

    def update_status(self, message):
        self.status_var.set(message)
        self.root.after(3000, lambda: self.status_var.set('Redo'))

    def load_categories(self):
        data = storage.load_data()
        self.categories = data["categories"]
        self.category_menu['values'] = self.categories
        if self.categories:
            self.category_var.set(self.categories[0])
            self.select_category(self.categories[0])
            self.update_status(f"Laddade {len(self.categories)} kategorier")
        else:
            self.update_status("Inga kategorier hittades")

    def select_category(self, category):
        self.category_var.set(category)
        self.load_subcategories()

    def load_subcategories(self):
        cat = self.category_var.get()
        data = storage.load_data()
        self.subcategories = [sub for sub in data["subcategories"] if sub["category"] == cat]
        sub_names = [sub["name"] for sub in self.subcategories]
        self.subcategory_menu['values'] = sub_names
        if sub_names:
            self.subcategory_var.set(sub_names[0])
            self.select_subcategory(sub_names[0])
        else:
            self.subcategory_var.set('')
            self.template_listbox.delete(*self.template_listbox.get_children())
            self.text_area.delete('1.0', 'end')

    def select_subcategory(self, subcategory):
        self.subcategory_var.set(subcategory)
        self.load_templates()

    def add_category(self):
        name = simpledialog.askstring('Ny kategori', 'Kategori-namn:')
        if name:
            data = storage.load_data()
            if name not in data["categories"]:
                data["categories"].append(name)
                storage.save_data(data)
                self.load_categories()
                self.update_status(f"Kategori '{name}' tillagd")
            else:
                messagebox.showerror('Fel', 'Kategorin finns redan.')
                self.update_status("Kategorin finns redan")

    def add_subcategory(self):
        cat = self.category_var.get()
        if not cat:
            messagebox.showwarning('Välj kategori', 'Välj först en kategori.')
            return
        name = simpledialog.askstring('Ny underkategori', 'Underkategori-namn:')
        if name:
            data = storage.load_data()
            if not any(sub["name"] == name and sub["category"] == cat for sub in data["subcategories"]):
                data["subcategories"].append({"name": name, "category": cat})
                storage.save_data(data)
                self.load_subcategories()
                self.update_status(f"Underkategori '{name}' tillagd")
            else:
                messagebox.showerror('Fel', 'Underkategorin finns redan.')
                self.update_status("Underkategorin finns redan")

    def delete_category(self):
        cat = self.category_var.get()
        if messagebox.askyesno('Bekräfta', f'Radera kategori {cat} inklusive underkategorier och mallar?'):
            data = storage.load_data()
            # Ta bort mallar och underkategorier kopplade till denna kategori
            data["templates"] = [tpl for tpl in data["templates"] if tpl["category"] != cat]
            data["subcategories"] = [sub for sub in data["subcategories"] if sub["category"] != cat]
            if cat in data["categories"]:
                data["categories"].remove(cat)
            storage.save_data(data)
            self.load_categories()
            self.update_status(f"Kategori '{cat}' borttagen")

    def delete_subcategory(self):
        sub = self.subcategory_var.get()
        cat = self.category_var.get()
        if sub and messagebox.askyesno('Bekräfta', f'Radera underkategori {sub} och dess mallar?'):
            data = storage.load_data()
            data["templates"] = [tpl for tpl in data["templates"] if tpl["subcategory"] != sub or tpl["category"] != cat]
            data["subcategories"] = [s for s in data["subcategories"] if not (s["name"] == sub and s["category"] == cat)]
            storage.save_data(data)
            self.load_subcategories()
            self.update_status(f"Underkategori '{sub}' borttagen")

    def load_templates(self):
        sub = self.subcategory_var.get()
        cat = self.category_var.get()
        data = storage.load_data()
        templates = [tpl for tpl in data["templates"] if tpl["subcategory"] == sub and tpl["category"] == cat]
        self.template_listbox.delete(*self.template_listbox.get_children())
        self.templates = {}
        for i, tpl in enumerate(templates):
            item_id = self.template_listbox.insert('', 'end', values=(tpl["title"],))
            self.templates[item_id] = tpl
        if templates:
            self.update_status(f"Laddade {len(templates)} mallar")
        else:
            self.update_status("Inga mallar hittades")
            self.text_area.delete('1.0', 'end')
        self.filter_templates()

    def add_template(self):
        title = simpledialog.askstring('Ny mall', 'Mallens titel:')
        if title:
            sub = self.subcategory_var.get()
            cat = self.category_var.get()
            if not sub:
                messagebox.showwarning('Ingen underkategori', 'Välj en underkategori först.')
                return
            data = storage.load_data()
            data["templates"].append({
                "title": title,
                "content": "",
                "category": cat,
                "subcategory": sub
            })
            storage.save_data(data)
            self.load_templates()
            self.update_status(f"Mall '{title}' tillagd")

    def delete_template(self):
        selected = self.template_listbox.selection()
        if selected:
            item_id = selected[0]
            tpl = self.templates[item_id]
            if messagebox.askyesno('Bekräfta', f'Radera mall {tpl['title']}?'):
                data = storage.load_data()
                data["templates"] = [t for t in data["templates"] if not (t["title"] == tpl["title"] and t["subcategory"] == tpl["subcategory"] and t["category"] == tpl["category"])]
                storage.save_data(data)
                self.load_templates()
                self.text_area.delete('1.0', 'end')
                self.update_status(f"Mall '{tpl['title']}' borttagen")

    def show_template(self, event):
        selected = self.template_listbox.selection()
        if selected:
            item_id = selected[0]
            tpl = self.templates[item_id]
            self.text_area.delete('1.0', 'end')
            self._markdown_to_text(tpl["content"])
            self.current_template_id = tpl
            self.update_status(f"Visar mall '{tpl['title']}'")
            self.highlight_search_terms()

    def _markdown_to_text(self, content):
        import re
        self.text_area.delete('1.0', 'end')
        self.text_area.tag_remove("bold", "1.0", "end")
        self.text_area.tag_remove("italic", "1.0", "end")
        self.text_area.tag_remove("underline", "1.0", "end")
        self.text_area.tag_remove("highlight", "1.0", "end")
        self.text_area.mark_set("insert", "1.0")

        # Regex för att hitta __understruken__, **fet**, *kursiv*
        pattern = re.compile(r'(__.+?__)|(\*\*.+?\*\*)|(\*.+?\*)', re.DOTALL)
        idx = 0
        while idx < len(content):
            match = pattern.search(content, idx)
            if not match:
                # Ingen mer taggad text, lägg in resten som vanlig text
                self.text_area.insert("insert", content[idx:])
                break
            # Lägg in text före tagg som vanlig text
            if match.start() > idx:
                self.text_area.insert("insert", content[idx:match.start()])
            tag_text = match.group()
            start = self.text_area.index("insert")
            # Ta bort markdown-taggarna
            if tag_text.startswith('__'):
                clean = tag_text[2:-2]
                self.text_area.insert("insert", clean)
                end = self.text_area.index("insert")
                self.text_area.tag_add("underline", start, end)
            elif tag_text.startswith('**'):
                clean = tag_text[2:-2]
                self.text_area.insert("insert", clean)
                end = self.text_area.index("insert")
                self.text_area.tag_add("bold", start, end)
            elif tag_text.startswith('*'):
                clean = tag_text[1:-1]
                self.text_area.insert("insert", clean)
                end = self.text_area.index("insert")
                self.text_area.tag_add("italic", start, end)
            idx = match.end()

    def save_template(self):
        selected = self.template_listbox.selection()
        if selected:
            item_id = selected[0]
            tpl = self.templates[item_id]
            data = storage.load_data()
            # Hämta texten från text_area och konvertera till markdown
            content = self._text_to_markdown(self.text_area.get('1.0', 'end-1c'))
            # Uppdatera rätt mall i data["templates"]
            for t in data["templates"]:
                if (
                    t["title"] == tpl["title"]
                    and t["subcategory"] == tpl["subcategory"]
                    and t["category"] == tpl["category"]
                ):
                    t["content"] = content
            storage.save_data(data)
            self.update_status(f"Mall '{tpl['title']}' sparad")

    def _text_to_markdown(self, content):
        # Fetstil
        for start, end in self._get_tag_ranges('bold'):
            bold_text = self.text_area.get(start, end)
            content = content.replace(bold_text, f'**{bold_text}**', 1)
        # Kursiv
        for start, end in self._get_tag_ranges('italic'):
            italic_text = self.text_area.get(start, end)
            content = content.replace(italic_text, f'*{italic_text}*', 1)
        # Understruken
        for start, end in self._get_tag_ranges('underline'):
            underline_text = self.text_area.get(start, end)
            content = content.replace(underline_text, f'__{underline_text}__', 1)
        return content

    def _get_tag_ranges(self, tag):
        ranges = []
        tag_ranges = self.text_area.tag_ranges(tag)
        for i in range(0, len(tag_ranges), 2):
            start = tag_ranges[i]
            end = tag_ranges[i+1]
            ranges.append((start, end))
        return ranges

    def copy_to_clipboard(self):
        content = self.text_area.get('1.0', 'end').strip()
        if content:
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            self.update_status("Innehåll kopierat till urklipp")
        else:
            self.update_status("Inget innehåll att kopiera")

    def highlight_search_terms(self):
        self.text_area.tag_remove('highlight', '1.0', 'end')  # Ta bort gamla highlights
        search_term = normalize_text(self.search_var.get())
        if not search_term:
            return
        content = self.text_area.get('1.0', 'end')
        normalized_content = normalize_text(content)
        start_idx = 0
        while True:
            match_idx = normalized_content.find(search_term, start_idx)
            if match_idx == -1:
                break
            start = f"1.0+{match_idx}c"
            end = f"1.0+{match_idx + len(search_term)}c"
            self.text_area.tag_add('highlight', start, end)
            start_idx = match_idx + len(search_term)
        self.text_area.tag_config('highlight', background='#ffe680')  # Gul bakgrund

    def filter_templates(self):
        search_term = normalize_text(self.search_var.get())
        sub = self.subcategory_var.get()
        cat = self.category_var.get()
        if not sub or not cat:
            return
        data = storage.load_data()
        templates = [tpl for tpl in data["templates"] if tpl["subcategory"] == sub and tpl["category"] == cat]
        self.template_listbox.delete(*self.template_listbox.get_children())
        self.templates = {}
        for tpl in templates:
            normalized_title = normalize_text(tpl["title"])
            normalized_content = normalize_text(tpl["content"])
            if search_term in normalized_title or search_term in normalized_content:
                item_id = self.template_listbox.insert('', 'end', values=(tpl["title"],))
                self.templates[item_id] = tpl
        if len(self.template_listbox.get_children()) == 0:
            self.update_status("Inga mallar matchar din sökning")
        else:
            self.update_status(f"Hittade {len(self.template_listbox.get_children())} mallar")

    def export_templates(self):
        path = filedialog.asksaveasfilename(
            defaultextension='.txt',
            filetypes=[('Textfiler', '*.txt'), ('Alla filer', '*.*')]
        )
        if path:
            data = storage.load_data()
            with open(path, 'w', encoding='utf-8') as f:
                for tpl in data["templates"]:
                    f.write(f'### {tpl["title"]} ###\n{tpl["content"]}\n\n')
            self.update_status(f"Mallar exporterade till {path}")

    def make_bold(self):
        try:
            start, end = self.text_area.index("sel.first"), self.text_area.index("sel.last")
            self.text_area.tag_add("bold", start, end)
        except tk.TclError:
            return
        self.text_area.tag_config("bold", font=('Arial', self.font_size_var.get(), 'bold'))

    def make_italic(self):
        try:
            start, end = self.text_area.index("sel.first"), self.text_area.index("sel.last")
            self.text_area.tag_add("italic", start, end)
        except tk.TclError:
            return
        self.text_area.tag_config("italic", font=('Arial', self.font_size_var.get(), 'italic'))

    def make_underline(self):
        try:
            start, end = self.text_area.index("sel.first"), self.text_area.index("sel.last")
            self.text_area.tag_add("underline", start, end)
        except tk.TclError:
            return
        self.text_area.tag_config("underline", font=('Arial', self.font_size_var.get(), 'underline'))

    def change_font_size(self):
        size = self.font_size_var.get()
        self.text_area.config(font=('Arial', size))
        # Uppdatera taggar så de får rätt storlek
        self.text_area.tag_config("bold", font=('Arial', size, 'bold'))
        self.text_area.tag_config("italic", font=('Arial', size, 'italic'))
        self.text_area.tag_config("underline", font=('Arial', size, 'underline'))