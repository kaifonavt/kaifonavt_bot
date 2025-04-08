import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

DB_NAME = "bot.db"

class DBManagerApp:
    def __init__(self, root):
        self.conn = sqlite3.connect(DB_NAME)
        self.cursor = self.conn.cursor()

        root.title("Bot Database Manager")
        root.geometry("700x500")

        self.tab_control = ttk.Notebook(root)

        self.kb_tab = ttk.Frame(self.tab_control)
        self.history_tab = ttk.Frame(self.tab_control)

        self.tab_control.add(self.kb_tab, text='Knowledge Base')
        self.tab_control.add(self.history_tab, text='User History')
        self.tab_control.pack(expand=1, fill='both')

        self.init_kb_tab()
        self.init_history_tab()

    def init_kb_tab(self):
        self.kb_list = tk.Listbox(self.kb_tab)
        self.kb_list.pack(fill='both', expand=True, padx=10, pady=10)

        self.kb_refresh_button = ttk.Button(self.kb_tab, text="Refresh", command=self.load_knowledge)
        self.kb_refresh_button.pack(pady=5)

        frame = ttk.Frame(self.kb_tab)
        frame.pack(pady=5)

        self.title_entry = ttk.Entry(frame, width=20)
        self.title_entry.grid(row=0, column=0, padx=5)
        self.content_entry = ttk.Entry(frame, width=40)
        self.content_entry.grid(row=0, column=1, padx=5)
        ttk.Button(frame, text="Add/Update", command=self.add_kb).grid(row=0, column=2, padx=5)
        ttk.Button(frame, text="Delete", command=self.delete_kb).grid(row=0, column=3, padx=5)

        self.load_knowledge()

    def init_history_tab(self):
        self.user_id_entry = ttk.Entry(self.history_tab)
        self.user_id_entry.pack(pady=10)
        ttk.Button(self.history_tab, text="Load History", command=self.load_history).pack(pady=5)

        self.history_list = tk.Listbox(self.history_tab)
        self.history_list.pack(fill='both', expand=True, padx=10, pady=10)

    def load_knowledge(self):
        self.kb_list.delete(0, tk.END)
        self.cursor.execute("SELECT title, content FROM knowledge_base")
        for title, content in self.cursor.fetchall():
            self.kb_list.insert(tk.END, f"{title}: {content}")

    def add_kb(self):
        title = self.title_entry.get().strip()
        content = self.content_entry.get().strip()
        if not title or not content:
            messagebox.showwarning("Warning", "Title and content cannot be empty.")
            return
        self.cursor.execute("INSERT OR REPLACE INTO knowledge_base (title, content) VALUES (?, ?)", (title, content))
        self.conn.commit()
        self.load_knowledge()
        self.title_entry.delete(0, tk.END)
        self.content_entry.delete(0, tk.END)

    def delete_kb(self):
        selected = self.kb_list.curselection()
        if not selected:
            return
        entry = self.kb_list.get(selected[0])
        title = entry.split(":")[0]
        self.cursor.execute("DELETE FROM knowledge_base WHERE title = ?", (title.strip(),))
        self.conn.commit()
        self.load_knowledge()

    def load_history(self):
        self.history_list.delete(0, tk.END)
        user_id = self.user_id_entry.get().strip()
        if not user_id.isdigit():
            messagebox.showwarning("Warning", "Please enter a valid user ID.")
            return
        self.cursor.execute("SELECT role, content FROM messages WHERE user_id = ? ORDER BY timestamp", (user_id,))
        for role, content in self.cursor.fetchall():
            self.history_list.insert(tk.END, f"[{role}] {content}")

if __name__ == "__main__":
    root = tk.Tk()
    app = DBManagerApp(root)
    root.mainloop()
