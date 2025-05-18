import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from tkinter.scrolledtext import ScrolledText
import sqlite3
import database

class TemplateApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Email Template Manager')
        self.root.geometry('900x650')
        self.root.minsize(800, 600)
        
        # Färgtema
        self.bg_color = '#f5f5f5'
        self.primary_color = '#2c3e50'
        self.secondary_color = '#3498db'
        self.accent_color = '#e74c3c'
        self.text_color = '#333333'
        
        # Stilar
        self.setup_styles()
        self.root.configure(bg=self.bg_color)
        
        database.setup_database()

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
        
        style.configure('.', background=self.bg_color)
        style.configure('TFrame', background=self.bg_color)
        style.configure('TLabel', background=self.bg_color, foreground=self.text_color)
        style.configure('TButton', padding=6, background=self.primary_color, foreground='white')
        style.configure('TCombobox', fieldbackground='white')
        style.configure('TEntry', fieldbackground='white')
        
        style.map('TButton',
            background=[('active', self.secondary_color), ('disabled', '#cccccc')],
            foreground=[('active', 'white'), ('disabled', '#888888')]
        )
        
        style.configure('Header.TLabel', font=('Helvetica', 12, 'bold'), foreground=self.primary_color)
        style.configure('Status.TLabel', font=('Helvetica', 9), relief=tk.SUNKEN, padding=5)

    def create_widgets(self):
        # Huvudcontainer
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Övre del med kategorier och sök
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))

        # Kategorier
        category_frame = ttk.LabelFrame(top_frame, text=" Kategorier ", padding=10)
        category_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

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
        cat_btn_frame.grid(row=0, column=2, rowspan=2, padx=10)

        ttk.Button(cat_btn_frame, text='Ny kategori', command=self.add_category).pack(fill=tk.X, pady=2)
        ttk.Button(cat_btn_frame, text='Ta bort', command=self.delete_category).pack(fill=tk.X, pady=2)
        ttk.Button(cat_btn_frame, text='Ny underkategori', command=self.add_subcategory).pack(fill=tk.X, pady=2)
        ttk.Button(cat_btn_frame, text='Ta bort', command=self.delete_subcategory).pack(fill=tk.X, pady=2)

        # Sökfält
        search_frame = ttk.LabelFrame(top_frame, text=" Sök ", padding=10)
        search_frame.pack(side=tk.LEFT, fill=tk.X, padx=(10, 0))

        ttk.Label(search_frame, text='Sök mall:').pack(side=tk.LEFT)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        search_entry.bind('<Return>', lambda e: self.filter_templates())

        # Huvudinnehåll
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Malllista
        list_frame = ttk.LabelFrame(content_frame, text=" Mallar ", padding=10)
        list_frame.pack(side=tk.LEFT, fill=tk.Y)

        self.template_listbox = tk.Listbox(
            list_frame,
            width=30,
            height=20,
            bg='white',
            selectbackground=self.secondary_color,
            selectforeground='white',
            font=('Arial', 10)
        )
        self.template_listbox.pack(fill=tk.BOTH, expand=True)
        self.template_listbox.bind('<<ListboxSelect>>', self.show_template)

        # Scrollbar för lista
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.template_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.template_listbox.config(yscrollcommand=scrollbar.set)

        # Knappar för mallhantering
        list_btn_frame = ttk.Frame(list_frame)
        list_btn_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Button(list_btn_frame, text='Ny mall', command=self.add_template).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(list_btn_frame, text='Ta bort', command=self.delete_template).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Textredigerare
        editor_frame = ttk.LabelFrame(content_frame, text=" Redigera mall ", padding=10)
        editor_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))

        self.text_area = ScrolledText(
            editor_frame,
            wrap=tk.WORD,
            font=('Arial', 10),
            padx=10,
            pady=10,
            bg='white',
            width=50,
            height=20
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)

        # Knappar för redigering
        edit_btn_frame = ttk.Frame(editor_frame)
        edit_btn_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Button(edit_btn_frame, text='Spara ändringar', command=self.save_template).pack(side=tk.LEFT)
        ttk.Button(edit_btn_frame, text='Kopiera till urklipp', command=self.copy_to_clipboard).pack(side=tk.LEFT, padx=5)
        ttk.Button(edit_btn_frame, text='Exportera mallar', command=self.export_templates).pack(side=tk.RIGHT)

        # Statusrad
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(5, 0))

        ttk.Label(
            status_frame,
            textvariable=self.status_var,
            style='Status.TLabel',
            anchor=tk.W
        ).pack(fill=tk.X)

    def update_status(self, message):
        self.status_var.set(message)
        self.root.after(3000, lambda: self.status_var.set('Redo'))

    def load_categories(self):
        conn = database.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT name FROM categories WHERE parent_id IS NULL')
        self.categories = [row[0] for row in cursor.fetchall()]
        conn.close()

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
        conn = database.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM categories WHERE name=? AND parent_id IS NULL', (cat,))
        cat_id = cursor.fetchone()
        if cat_id:
            cursor.execute('SELECT name FROM categories WHERE parent_id=?', (cat_id[0],))
            self.subcategories = [row[0] for row in cursor.fetchall()]
        else:
            self.subcategories = []
        conn.close()

        self.subcategory_menu['values'] = self.subcategories
        if self.subcategories:
            self.subcategory_var.set(self.subcategories[0])
            self.select_subcategory(self.subcategories[0])
        else:
            self.subcategory_var.set('')
            self.template_listbox.delete(0, 'end')
            self.text_area.delete('1.0', 'end')

    def select_subcategory(self, subcategory):
        self.subcategory_var.set(subcategory)
        self.load_templates()

    def add_category(self):
        name = simpledialog.askstring('Ny kategori', 'Kategori-namn:')
        if name:
            try:
                conn = database.connect()
                cursor = conn.cursor()
                cursor.execute('INSERT INTO categories (name) VALUES (?)', (name,))
                conn.commit()
                conn.close()
                self.load_categories()
                self.update_status(f"Kategori '{name}' tillagd")
            except sqlite3.IntegrityError:
                messagebox.showerror('Fel', 'Kategorin finns redan.')
                self.update_status("Kategorin finns redan")

    def add_subcategory(self):
        cat = self.category_var.get()
        if not cat:
            messagebox.showwarning('Välj kategori', 'Välj först en kategori.')
            return
        name = simpledialog.askstring('Ny underkategori', 'Underkategori-namn:')
        if name:
            try:
                conn = database.connect()
                cursor = conn.cursor()
                cursor.execute('SELECT id FROM categories WHERE name=? AND parent_id IS NULL', (cat,))
                parent_id = cursor.fetchone()[0]
                cursor.execute('INSERT INTO categories (name, parent_id) VALUES (?, ?)', (name, parent_id))
                conn.commit()
                conn.close()
                self.load_subcategories()
                self.update_status(f"Underkategori '{name}' tillagd")
            except sqlite3.IntegrityError:
                messagebox.showerror('Fel', 'Underkategorin finns redan.')
                self.update_status("Underkategorin finns redan")

    def delete_category(self):
        cat = self.category_var.get()
        if messagebox.askyesno('Bekräfta', f'Radera kategori {cat} inklusive underkategorier och mallar?'):
            conn = database.connect()
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM categories WHERE name=? AND parent_id IS NULL', (cat,))
            cat_id = cursor.fetchone()[0]
            cursor.execute('DELETE FROM templates WHERE category_id IN (SELECT id FROM categories WHERE parent_id=?)', (cat_id,))
            cursor.execute('DELETE FROM categories WHERE parent_id=?', (cat_id,))
            cursor.execute('DELETE FROM categories WHERE id=?', (cat_id,))
            conn.commit()
            conn.close()
            self.load_categories()
            self.update_status(f"Kategori '{cat}' borttagen")

    def delete_subcategory(self):
        sub = self.subcategory_var.get()
        if sub and messagebox.askyesno('Bekräfta', f'Radera underkategori {sub} och dess mallar?'):
            conn = database.connect()
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM categories WHERE name=?', (sub,))
            sub_id = cursor.fetchone()[0]
            cursor.execute('DELETE FROM templates WHERE category_id=?', (sub_id,))
            cursor.execute('DELETE FROM categories WHERE id=?', (sub_id,))
            conn.commit()
            conn.close()
            self.load_subcategories()
            self.update_status(f"Underkategori '{sub}' borttagen")

    def load_templates(self):
        sub = self.subcategory_var.get()
        conn = database.connect()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM categories WHERE name=?', (sub,))
        result = cursor.fetchone()
        if result:
            sub_id = result[0]
            cursor.execute('SELECT id, title FROM templates WHERE category_id=?', (sub_id,))
            templates = cursor.fetchall()
        else:
            templates = []
        conn.close()
        
        self.template_listbox.delete(0, 'end')
        self.templates = {}
        for template_id, title in templates:
            self.template_listbox.insert('end', title)
            self.templates[title] = template_id
        
        if templates:
            self.update_status(f"Laddade {len(templates)} mallar")
        else:
            self.update_status("Inga mallar hittades")
            self.text_area.delete('1.0', 'end')

    def add_template(self):
        title = simpledialog.askstring('Ny mall', 'Mallens titel:')
        if title:
            sub = self.subcategory_var.get()
            if not sub:
                messagebox.showwarning('Ingen underkategori', 'Välj en underkategori först.')
                return
            conn = database.connect()
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM categories WHERE name=?', (sub,))
            sub_id = cursor.fetchone()[0]
            cursor.execute('INSERT INTO templates (title, content, category_id) VALUES (?, ?, ?)', (title, '', sub_id))
            conn.commit()
            conn.close()
            self.load_templates()
            self.update_status(f"Mall '{title}' tillagd")

    def delete_template(self):
        selected = self.template_listbox.curselection()
        if selected:
            title = self.template_listbox.get(selected)
            if messagebox.askyesno('Bekräfta', f'Radera mall {title}?'):
                conn = database.connect()
                cursor = conn.cursor()
                cursor.execute('DELETE FROM templates WHERE id=?', (self.templates[title],))
                conn.commit()
                conn.close()
                self.load_templates()
                self.text_area.delete('1.0', 'end')
                self.update_status(f"Mall '{title}' borttagen")

    def show_template(self, event):
        selected = self.template_listbox.curselection()
        if selected:
            title = self.template_listbox.get(selected)
            conn = database.connect()
            cursor = conn.cursor()
            cursor.execute('SELECT content FROM templates WHERE id=?', (self.templates[title],))
            content = cursor.fetchone()[0]
            conn.close()
            self.text_area.delete('1.0', 'end')
            self.text_area.insert('1.0', content)
            self.current_template_id = self.templates[title]
            self.update_status(f"Visar mall '{title}'")

    def save_template(self):
        selected = self.template_listbox.curselection()
        if selected:
            title = self.template_listbox.get(selected)
            content = self.text_area.get('1.0', 'end').strip()
            conn = database.connect()
            cursor = conn.cursor()
            cursor.execute('UPDATE templates SET content=? WHERE id=?', (content, self.templates[title]))
            conn.commit()
            conn.close()
            self.update_status(f"Mall '{title}' sparad")

    def copy_to_clipboard(self):
        content = self.text_area.get('1.0', 'end').strip()
        if content:
            self.root.clipboard_clear()
            self.root.clipboard_append(content)
            self.update_status("Innehåll kopierat till urklipp")
        else:
            self.update_status("Inget innehåll att kopiera")

    def filter_templates(self):
        search_term = self.search_var.get().lower()
        for i in range(self.template_listbox.size()):
            title = self.template_listbox.get(i)
            if search_term in title.lower():
                self.template_listbox.itemconfig(i, foreground='black')
            else:
                self.template_listbox.itemconfig(i, foreground='#cccccc')

    def export_templates(self):
        path = filedialog.asksaveasfilename(
            defaultextension='.txt',
            filetypes=[('Textfiler', '*.txt'), ('Alla filer', '*.*')]
        )
        if path:
            conn = database.connect()
            cursor = conn.cursor()
            cursor.execute('SELECT title, content FROM templates')
            rows = cursor.fetchall()
            conn.close()
            with open(path, 'w', encoding='utf-8') as f:
                for title, content in rows:
                    f.write(f'### {title} ###\n{content}\n\n')
            self.update_status(f"Mallar exporterade till {path}")