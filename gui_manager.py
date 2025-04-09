import tkinter as tk
from tkinter import messagebox
from ai_core import load_kb_from_db, get_all_facts, add_fact, update_fact, delete_fact, vector_search

def refresh_facts():
    listbox.delete(0, tk.END)
    for fact in get_all_facts():
        listbox.insert(tk.END, f"{fact[0]}: {fact[1]}")

def on_add():
    text = entry.get()
    if text:
        add_fact(text)
        refresh_facts()
        entry.delete(0, tk.END)

def on_update():
    selected = listbox.curselection()
    if selected:
        idx = selected[0]
        fact_line = listbox.get(idx)
        fact_id = int(fact_line.split(":")[0])
        new_text = entry.get()
        update_fact(fact_id, new_text)
        refresh_facts()

def on_delete():
    selected = listbox.curselection()
    if selected:
        idx = selected[0]
        fact_line = listbox.get(idx)
        fact_id = int(fact_line.split(":")[0])
        delete_fact(fact_id)
        refresh_facts()

def on_search():
    query = entry.get()
    if query:
        results = vector_search(query)
        results_box.delete(0, tk.END)
        for fact_id, fact_text, similarity in results:
            results_box.insert(tk.END, f"{fact_id}: {fact_text} - Similarity: {similarity:.4f}")

load_kb_from_db()

root = tk.Tk()
root.title("Knowledge Base Manager")

frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

listbox = tk.Listbox(frame, width=60, height=15)
listbox.pack()

entry = tk.Entry(frame, width=60)
entry.pack(pady=5)

btn_frame = tk.Frame(frame)
btn_frame.pack()

tk.Button(btn_frame, text="Добавить", command=on_add).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="Изменить", command=on_update).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="Удалить", command=on_delete).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="Поиск", command=on_search).pack(side=tk.LEFT, padx=5)

results_box = tk.Listbox(frame, width=60, height=15)
results_box.pack(pady=5)

refresh_facts()
root.mainloop()
