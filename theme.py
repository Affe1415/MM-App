import tkinter as tk
from tkinter import ttk

# Outlook-inspirerat färgtema och stilar
def setup_theme(root):
    style = ttk.Style()
    style.theme_use('clam')

    # Modern färgpalett
    bg_color = '#f8fafc'
    primary_color = '#2563eb'
    secondary_color = '#64748b'
    accent_color = '#38bdf8'
    text_color = '#22223b'
    frame_color = '#e0e7ef'
    entry_bg = '#ffffff'

    # Spara färger i root för enkel åtkomst i appen
    root.bg_color = bg_color
    root.primary_color = primary_color
    root.secondary_color = secondary_color
    root.accent_color = accent_color
    root.text_color = text_color
    root.frame_color = frame_color
    root.entry_bg = entry_bg

    # Grundstilar
    style.configure('.', background=bg_color)
    style.configure('TFrame', background=bg_color)
    style.configure('TLabel', background=bg_color, foreground=text_color, font=('Segoe UI', 11))
    style.configure('TButton', background=primary_color, foreground='white', font=('Segoe UI', 10, 'bold'), padding=8, borderwidth=0)
    style.configure('TCombobox', fieldbackground=entry_bg, background=entry_bg, padding=4)
    style.configure('TEntry', fieldbackground=entry_bg, background=entry_bg, padding=4)
    style.configure('TLabelframe', background=frame_color, foreground=primary_color, font=('Segoe UI', 11, 'bold'), borderwidth=0, relief='flat', padding=12)
    style.configure('TLabelframe.Label', background=frame_color, foreground=primary_color, font=('Segoe UI', 11, 'bold'))
    style.configure('Treeview', background='white', foreground=text_color, fieldbackground='white', font=('Segoe UI', 10), rowheight=28)
    style.configure('Treeview.Heading', background=primary_color, foreground='white', font=('Segoe UI', 10, 'bold'))
    style.configure('Header.TLabel', font=('Segoe UI', 16, 'bold'), foreground=primary_color, background=bg_color, padding=8)
    style.configure('Status.TLabel', font=('Segoe UI', 9), relief=tk.SUNKEN, padding=8, background=frame_color, foreground=secondary_color)

    style.map('TButton',
        background=[('active', accent_color), ('disabled', '#cccccc')],
        foreground=[('active', 'white'), ('disabled', '#888888')]
    )