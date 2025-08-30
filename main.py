import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# ----------------- Banco de Dados -----------------
conn = sqlite3.connect("agenda_tarefas.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS tarefas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    descricao TEXT,
    data_inicial TEXT,
    data_final TEXT,
    tipo TEXT,
    situacao TEXT
)
""")
conn.commit()

# ----------------- Funções -----------------
def add_placeholder(entry, text):
    entry.insert(0, text)
    entry.config(fg='gray')
    
    def on_focus_in(event):
        if entry.get() == text:
            entry.delete(0, tk.END)
            entry.config(fg='black')
    
    def on_focus_out(event):
        if entry.get() == "":
            entry.insert(0, text)
            entry.config(fg='gray')
    
    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)

def adicionar_tarefa():
    nome = entry_nome.get()
    descricao = entry_descricao.get()
    data_inicial = entry_data_inicial.get()
    data_final = entry_data_final.get()
    tipo = entry_tipo.get()
    situacao = combo_situacao.get()

    if not nome or not descricao:
        messagebox.showwarning("Aviso", "Nome e Descrição são obrigatórios!")
        return

    cursor.execute("INSERT INTO tarefas (nome, descricao, data_inicial, data_final, tipo, situacao) VALUES (?, ?, ?, ?, ?, ?)",
                   (nome, descricao, data_inicial, data_final, tipo, situacao))
    conn.commit()
    listar_tarefas()

def listar_tarefas(filtro=""):
    for i in tree.get_children():
        tree.delete(i)
    
    if filtro:
        cursor.execute("SELECT * FROM tarefas WHERE nome LIKE ? OR descricao LIKE ?", (f"%{filtro}%", f"%{filtro}%"))
    else:
        cursor.execute("SELECT * FROM tarefas")
        
    for row in cursor.fetchall():
        tree.insert("", "end", values=row)
        if row[6] == "Feito":
            tree.item(tree.get_children()[-1], tags=('feito',))
        else:
            tree.item(tree.get_children()[-1], tags=('nao_feito',))
    
    tree.tag_configure('feito', background='#d4edda')  # verde claro
    tree.tag_configure('nao_feito', background='#f8d7da')  # vermelho claro

def buscar_tarefas(event=None):
    filtro = entry_busca.get()
    listar_tarefas(filtro=filtro)

def excluir_tarefa():
    selected = tree.selection()
    if not selected:
        return
    for item in selected:
        situacao = tree.item(item)['values'][6]
        if situacao == "Não feito":
            cursor.execute("DELETE FROM tarefas WHERE id=?", (tree.item(item)['values'][0],))
            conn.commit()
        else:
            messagebox.showwarning("Atenção", "Não é possível excluir tarefas já feitas!")
    listar_tarefas()

def editar_tarefa():
    selected = tree.selection()
    if not selected:
        messagebox.showinfo("Info", "Selecione uma tarefa para editar.")
        return
    item = tree.item(selected[0])
    task_id = item['values'][0]

    entry_nome.delete(0, tk.END)
    entry_nome.insert(0, item['values'][1])
    entry_descricao.delete(0, tk.END)
    entry_descricao.insert(0, item['values'][2])
    entry_data_inicial.delete(0, tk.END)
    entry_data_inicial.insert(0, item['values'][3])
    entry_data_final.delete(0, tk.END)
    entry_data_final.insert(0, item['values'][4])
    entry_tipo.delete(0, tk.END)
    entry_tipo.insert(0, item['values'][5])
    combo_situacao.set(item['values'][6])

    btn_atualizar.config(state="normal")
    btn_atualizar.task_id = task_id

def atualizar_tarefa():
    if not hasattr(btn_atualizar, 'task_id'):
        return
    task_id = btn_atualizar.task_id
    cursor.execute("""UPDATE tarefas 
                      SET nome=?, descricao=?, data_inicial=?, data_final=?, tipo=?, situacao=?
                      WHERE id=?""",
                   (entry_nome.get(), entry_descricao.get(),
                    entry_data_inicial.get(), entry_data_final.get(),
                    entry_tipo.get(), combo_situacao.get(), task_id))
    conn.commit()
    listar_tarefas()
    btn_atualizar.config(state="disabled")
    del btn_atualizar.task_id

# ----------------- Interface -----------------
root = tk.Tk()
root.title("Agenda de Tarefas")
root.geometry("950x600")
root.configure(bg="#f0f2f5")

# ----------------- Frame Cadastro -----------------
frame_cadastro = tk.LabelFrame(root, text="Cadastro de Tarefa", padx=20, pady=20, bg="#e9ecef", font=("Arial", 12, "bold"))
frame_cadastro.pack(fill="x", padx=20, pady=10)

tk.Label(frame_cadastro, text="Nome:", bg="#e9ecef", font=("Arial", 10)).grid(row=0, column=0, sticky="w")
entry_nome = tk.Entry(frame_cadastro, width=30)
entry_nome.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_cadastro, text="Descrição:", bg="#e9ecef", font=("Arial", 10)).grid(row=1, column=0, sticky="w")
entry_descricao = tk.Entry(frame_cadastro, width=30)
entry_descricao.grid(row=1, column=1, padx=5, pady=5)

tk.Label(frame_cadastro, text="Data Inicial:", bg="#e9ecef", font=("Arial", 10)).grid(row=0, column=2, sticky="w")
entry_data_inicial = tk.Entry(frame_cadastro, width=15)
entry_data_inicial.grid(row=0, column=3, padx=5, pady=5)
add_placeholder(entry_data_inicial, "DD/MM/AAAA")

tk.Label(frame_cadastro, text="Data Final:", bg="#e9ecef", font=("Arial", 10)).grid(row=1, column=2, sticky="w")
entry_data_final = tk.Entry(frame_cadastro, width=15)
entry_data_final.grid(row=1, column=3, padx=5, pady=5)
add_placeholder(entry_data_final, "DD/MM/AAAA")

tk.Label(frame_cadastro, text="Tipo:", bg="#e9ecef", font=("Arial", 10)).grid(row=2, column=0, sticky="w")
entry_tipo = tk.Entry(frame_cadastro, width=30)
entry_tipo.grid(row=2, column=1, padx=5, pady=5)

tk.Label(frame_cadastro, text="Situação:", bg="#e9ecef", font=("Arial", 10)).grid(row=2, column=2, sticky="w")
combo_situacao = ttk.Combobox(frame_cadastro, values=["Feito", "Não feito"], width=13)
combo_situacao.grid(row=2, column=3, padx=5, pady=5)
combo_situacao.set("Não feito")

# ----------------- Botões Abaixo -----------------
frame_botoes = tk.Frame(frame_cadastro, bg="#e9ecef")
frame_botoes.grid(row=3, column=0, columnspan=4, pady=10)

btn_adicionar = tk.Button(frame_botoes, text="Adicionar Tarefa", command=adicionar_tarefa, bg="#28a745", fg="white", width=20)
btn_adicionar.grid(row=0, column=0, padx=5)

btn_editar = tk.Button(frame_botoes, text="Editar Tarefa", command=editar_tarefa, bg="#ffc107", fg="white", width=20)
btn_editar.grid(row=0, column=1, padx=5)

btn_atualizar = tk.Button(frame_botoes, text="Atualizar Tarefa", command=atualizar_tarefa, bg="#007bff", fg="white", width=20, state="disabled")
btn_atualizar.grid(row=0, column=2, padx=5)

# ----------------- Frame Busca -----------------
frame_busca = tk.Frame(root, bg="#f0f2f5")
frame_busca.pack(fill="x", padx=20, pady=5)

tk.Label(frame_busca, text="Buscar Tarefas:", bg="#f0f2f5", font=("Arial", 10)).pack(side="left")
entry_busca = tk.Entry(frame_busca, width=30)
entry_busca.pack(side="left", padx=5)
entry_busca.bind("<Return>", buscar_tarefas)

btn_buscar = tk.Button(frame_busca, text="Buscar", command=buscar_tarefas, bg="#17a2b8", fg="white")
btn_buscar.pack(side="left", padx=5)

# ----------------- Frame Lista -----------------
frame_lista = tk.LabelFrame(root, text="Lista de Tarefas", padx=10, pady=10, bg="#e9ecef", font=("Arial", 12, "bold"))
frame_lista.pack(fill="both", expand=True, padx=20, pady=10)

tree = ttk.Treeview(frame_lista, columns=("ID", "Nome", "Descrição", "Data Inicial", "Data Final", "Tipo", "Situação"), show="headings")
for col in tree["columns"]:
    tree.heading(col, text=col)
    tree.column(col, width=120)
tree.pack(fill="both", expand=True)

# ----------------- Botões Lista -----------------
frame_lista_botoes = tk.Frame(root, bg="#f0f2f5")
frame_lista_botoes.pack(pady=5)

tk.Button(frame_lista_botoes, text="Excluir Tarefa Selecionada", command=excluir_tarefa, bg="#dc3545", fg="white", width=25).grid(row=0, column=0, padx=5)
tk.Button(frame_lista_botoes, text="Listar Todas as Tarefas", command=lambda: listar_tarefas(), bg="#17a2b8", fg="white", width=25).grid(row=0, column=1, padx=5)

listar_tarefas()
root.mainloop()
