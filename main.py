import os
import datetime
from datetime import datetime, timedelta
import sqlite3
import tkinter as tk
from tkinter import PhotoImage, ttk
from tkcalendar  import DateEntry
import tkinter.messagebox as messagebox
from functools import partial
import re

conn = sqlite3.connect('data.db')
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS produtos (
                    id INTEGER PRIMARY KEY,
                    nome TEXT NOT NULL,
                    quantidade INTERGER NOT NULL,
                    validade DATE NOT NULL,
                    setor TEXT NOT NULL
                )''')

cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (
                    id INTEGER PRIMARY KEY,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL
                )''')

itens = []
contador_ql6 = 0
contador_vencidos = 0
user_login = {
    "ad": "ad",
}

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')  

def verificar_login(usuario, senha):
    global notAdmin, isAdmin
    cursor.execute('''SELECT * FROM usuarios WHERE username = ? AND password = ?''', (usuario, senha))
    user = cursor.fetchone()
    if usuario in user_login and user_login[usuario] == senha:
        isAdmin = True
        return True
    else:
        return False

def adicionar_produto(nome, quantidade, validade, setor):
    cursor.execute('''INSERT INTO produtos (nome, validade, quantidade, setor) VALUES (?, ?, ?)''', (nome, quantidade, validade, setor))
    conn.commit()

def remover_produto(id):
    cursor.execute('''DELETE FROM produtos WHERE id = ?''', (id,))
 
def fazer_login(usuario_entry, senha_entry, janela_login):
    usuario = usuario_entry.get()  
    senha = senha_entry.get()  
    
    if verificar_login(usuario, senha) :
        print("Login normal bem-sucedido!")
        janela_login.destroy()  
        iniciar_menu_principal()
    else:
        print(f"Tentativa de login com usuário: {usuario} e senha: {senha}")

def iniciar_login():\
    
    janela_login = tk.Tk()
    janela_login.geometry("1024x500+300+200")
    janela_login.title("Login")
    janela_login.configure(bg='white')  

    imagem = tk.PhotoImage(file="assets/images/login.png")  
    label_imagem = tk.Label(janela_login, image=imagem, bg='white', highlightthickness=0)  
    label_imagem.grid(row=0, column=0, rowspan=5, padx=50, pady=50)
    
    texto = tk.Label(janela_login, text="SEJA BEM-VINDO", font=('microsoft yaHei UI Light', 17,"bold"),  bg='white') 
    texto.grid(row=0, column=1, columnspan=2, padx=50, pady=50)
    
    usuario_entry = tk.Entry(janela_login, width=30, font=('microsoft yaHei UI Light', 15))
    usuario_entry.grid(row=1, column=1, columnspan=2, padx=10, pady=10)
    usuario_entry.insert(0, 'Usuário')
    
    senha_entry = tk.Entry(janela_login, show="*", width=30, font=('microsoft yaHei UI Light', 15))
    senha_entry.grid(row=2, column=1, columnspan=2, padx=10, pady=10)
    senha_entry.insert(0, 'Senha')
    
    botao = tk.Button(janela_login, text="Login", command=lambda: fazer_login(usuario_entry, senha_entry, janela_login),
    bg='#57a1f8', fg='white', width=20, pady=5, border=0)
    botao.grid(row=3, column=1, columnspan=2, padx=10, pady=10)
    
    def on_enter_user(e):
        if usuario_entry.get() == 'Usuário':
            usuario_entry.delete(0, 'end')
    
    def on_leave_user(e):
        if usuario_entry.get() == '':
            usuario_entry.insert(0, 'Usuário')
    
    def on_enter_pass(e):
        if senha_entry.get() == 'Senha':
            senha_entry.delete(0, 'end')
    
    def on_leave_pass(e):
        if senha_entry.get() == '':
            senha_entry.insert(0, 'Senha')
    
    usuario_entry.bind('<FocusIn>', on_enter_user)
    usuario_entry.bind('<FocusOut>', on_leave_user)
    senha_entry.bind('<FocusIn>', on_enter_pass)
    senha_entry.bind('<FocusOut>', on_leave_pass)
    janela_login.mainloop()

def iniciar_menu_principal():
    root = tk.Tk()
    app = FullScreenApp(root)
    root.mainloop()

class FullScreenApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Sistema de validade")
        self.master.geometry("800x600")
        
        self.titulo = tk.StringVar()
        self.titulo.set("Menu Principal")  
        
        self.title_label = tk.Label(master, textvariable=self.titulo, font=("Helvetica", 24))
        self.title_label.pack(side=tk.TOP, pady=20)

        self.button_frame = tk.Frame(master)
        self.button_frame.pack(expand=True, padx=20, pady=20)  

        self.center_window()

        self.conn = sqlite3.connect('data.db')
        self.cursor = self.conn.cursor()
        
        self.create_main_menu_buttons()
        self.create_return_button()  

        texto_abaixo_botao_menu = tk.Label(self.master, text="Bem vindo ao sistema de validade do Grupo Pão de Açúcar", font=('Helvetica', 11))
        texto_abaixo_botao_menu.pack(side=tk.TOP, pady=10)

    def center_window(self):
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        x = (screen_width - 800) // 2  
        y = (screen_height - 600) // 2  
        self.master.geometry(f"800x600+{x}+{y}") 

    def create_main_menu_buttons(self):
        self.titulo.set("Menu Principal")  

        for widget in self.button_frame.winfo_children():
            widget.destroy()
            
        self.buttons = []
        button_size = 120  
        button_functions = [self.adicionar_item, self.remover_item, self.listar_item, self.listar_itens_vencidos, self.mostrar_proximos_vencimentos]  
        image_files = ["assets/images/image1.png", "assets/images/image2.png", "assets/images/image3.png", "assets/images/image4.png", "assets/images/image5.png"]
        button_titles = ["Adicionar Item", "Remover Item", "Listar Item", "Listar Itens Vencidos", "Vencimentos Próximos "]

        for i in range(len(button_functions)):
            image = tk.PhotoImage(file=image_files[i])
            image = image.subsample(6)
            
            button_frame = tk.Frame(self.button_frame)
            button_frame.grid(row=i // 3, column=i % 3, padx=50, pady=40)
            
            button = tk.Button(button_frame, image=image, height=button_size, width=button_size,
                            command=lambda func=button_functions[i]: self.update_content(func))
            button.image = image
            button.pack()
            
            title_label = tk.Label(button_frame, text=button_titles[i], font=("Arial", 10)) 
            title_label.pack(pady=(15, 10), padx=(0, 5))  
        
    def create_return_button(self):
        return_image = tk.PhotoImage(file="assets/images/menu.png")
        return_image = return_image.subsample(6)
        return_button = tk.Button(self.master, image=return_image, command=self.return_to_main_menu, borderwidth=0, highlightthickness=0)
        return_button.image = return_image
        return_button.place(x=15, y=15)  

    def return_to_main_menu(self):
        self.create_main_menu_buttons()

    def update_content(self, func, *args):
        for widget in self.button_frame.winfo_children():
            widget.destroy()
        func(*args)

    def adicionar_item(self):
        fonte = ('Helvetica', 12)  
        self.titulo.set("Adicionar itens")
        
        nome_label = tk.Label(self.button_frame, text="Nome do Item:", font=fonte)
        nome_label.grid(row=1, column=0, padx=10, pady=20)
        nome_entry = tk.Entry(self.button_frame, font=fonte, width=18, relief='solid', border=0, highlightthickness=1 )
        nome_entry.grid(row=1, column=1, padx=10, pady=5)
        nome_entry.configure(highlightbackground="#9E9A91", highlightcolor="#9E9A91")   

        quantidade_label = tk.Label(self.button_frame, text="Quantidade:", font=fonte )
        quantidade_label.grid(row=2, column=0, padx=10, pady=20)
        validate_qtd = self.master.register(self.only_numbers) 
        quantidade_entry = tk.Entry(self.button_frame, font=fonte, width=18, relief='solid', borderwidth=1, validate="key", validatecommand=(validate_qtd, '%P'), border=0, highlightthickness=1 )
        quantidade_entry.grid(row=2, column=1, padx=10, pady=5)
        quantidade_entry.configure(highlightbackground="#9E9A91", highlightcolor="#9E9A91")

        validade_label = tk.Label(self.button_frame, text="Validade:", font=fonte)
        validade_label.grid(row=3, column=0, padx=10, pady=20)

        self.validade_entry = DateEntry(self.button_frame, font=fonte, width=16, date_pattern='DD/MM/YYYY')
        self.validade_entry.grid(row=3, column=1, padx=10, pady=5)
        self.validade_entry.delete(0, tk.END)       

        setor_label = tk.Label(self.button_frame, text="Setor:", font=fonte)
        setor_label.grid(row=4, column=0, padx=10, pady=20)
        setor_var = tk.StringVar(self.button_frame)
        setor_var.set("Selecione o setor")  
        setores = ["Liquida", "Mercearia", "Limpeza", "Perecíveis","Padaria"]  
        setor_dropdown = ttk.Combobox(self.button_frame, textvariable=setor_var, width=12, values=setores, font=fonte, state="readonly")
        setor_dropdown.grid(row=4, column=1, padx=10, pady=5, sticky="ew")

        style = ttk.Style()
        style.theme_use('clam')  
        style.configure('TCombobox', width=27, fieldbackground='white', relief='flat', foreground='black' ) 
        style.map('TCombobox', fieldbackground=[('readonly', 'white')])  

        def convert_date_format(date_str):
            try:
                date_object = datetime.strptime(date_str, "%d/%m/%Y")
                return date_object.strftime("%Y/%m/%d")
            except ValueError:
                return None

        def addButton():
            nome = nome_entry.get()
            quantidade = quantidade_entry.get()
            data_validade = self.validade_entry.get()
            setor = setor_dropdown.get()

            if nome and quantidade and data_validade != "DD/MM/YYY" and setor != "Selecione o setor":
                converted_date = convert_date_format(data_validade)
                if converted_date:
                    item = {
                        "nome": nome,
                        "quantidade": quantidade,
                        "data_validade": converted_date,
                        "setor": setor.lower()  
                    }
                    itens.append(item)

                    cursor.execute('''INSERT INTO produtos (nome, quantidade, validade, setor) VALUES (?, ?, ?, ?)''', (nome, quantidade, converted_date, setor))
                    conn.commit()
                    messagebox.showinfo("Produto Adicionado", f"Nome: {nome}\nQuantidade: {quantidade}\nValidade: {data_validade}\nSetor: {setor}")
                else:
                    messagebox.showerror("Erro", "Formato de data inválido. Por favor, use o formato DD/MM/YYYY.")
            else:
                messagebox.showerror("Erro", "Por favor, preencha todos os campos.")

        salvar_button = tk.Button(self.button_frame, text="Adicionar", command=addButton)
        salvar_button.config(relief=tk.RAISED, borderwidth=3, background='#57A1F8', foreground='white', width=10, height=1, font=10)
        salvar_button.grid(row=5, column=0, columnspan=2, padx=5, pady=20)

    def only_numbers(self, value):
        if value.isdigit() or value == "":
            return True
        else:
            return False

    def remover_item(self):
            fonte = ('Helvetica', 12)  
            
            self.titulo.set("Remover itens")

            setor_var = tk.StringVar(self.button_frame)
            setores = ["Liquida", "Mercearia", "Limpeza", "Perecíveis","Padaria"]

            setor_var.set("Selecione um setor")
            
            def load_items_from_database():
                selected_setor = setor_var.get()
                
                if not selected_setor == "Selecione um setor":
                    cursor.execute("SELECT * FROM produtos WHERE setor = ? ORDER BY validade ASC", (selected_setor,))
                items = cursor.fetchall()

                self.listbox.delete(0, tk.END)

                for item in items:
                    data_validade = datetime.strptime(item[3], '%Y/%m/%d').strftime('%d/%m/%Y')
                    formatted_item = f"ID: {item[0]}  Produto: {item[1]}  Qtd: {item[2]}  Validade: {data_validade}  Setor: {item[4]}"
                    self.listbox.insert(tk.END, formatted_item)

            setor_dropdown = ttk.Combobox(self.button_frame, textvariable=setor_var, width=25, values=setores, font=fonte, state="readonly")
            setor_dropdown.grid(row=0, column=1, padx=(0, 10), pady=5, sticky='e')

            setor_dropdown.bind("<<ComboboxSelected>>", lambda event: load_items_from_database())

            self.listbox = tk.Listbox(self.button_frame, font=fonte, width=80, height=15, relief='solid', borderwidth=1)
            self.listbox.grid(row=1, column=0, columnspan=2, padx=10, pady=5)
            self.listbox.configure(highlightbackground="#9E9A91", highlightcolor="#9E9A91", border=0, activestyle="none")
            
            scrollbar = tk.Scrollbar(self.button_frame, orient="vertical", command=self.listbox.yview)
            scrollbar.grid(row=1, column=2, sticky='ns')
            self.listbox.config(yscrollcommand=scrollbar.set)

            def remButton():
                selected_item_index = self.listbox.curselection()
                if selected_item_index:
                    selected_item = self.listbox.get(selected_item_index)
                    item_id = selected_item.split()[1]  
                    
                    try:
                        item_id = int(item_id)
                    except ValueError:
                        #print('Erro: ID do item não é um número válido.')
                        return
                    
                    messagebox.showinfo("Produto Removido", f"Produto Removido: {selected_item}")

                    cursor.execute("DELETE FROM produtos WHERE id = ?", (item_id,))
                    conn.commit()  
                    load_items_from_database()
                else:
                    messagebox.showerror("Aviso", "Nenhum item selecionado.")

            remover_button = tk.Button(self.button_frame, text="Remover", command=remButton)
            remover_button.config(relief=tk.RAISED, borderwidth=3, background='#57A1F8', foreground='white', width=10, height=1, font=10)
            remover_button.grid(row=5, column=0, columnspan=2, padx=5, pady=20)

    def listar_item(self):
        fonte = ('Helvetica', 12)  
        
        self.titulo.set("Listar itens")

        setor_var = tk.StringVar(self.button_frame)
        setores = ["Liquida", "Mercearia", "Limpeza", "Perecíveis","Padaria"]

        setor_var.set("Selecione um setor")
        
        def load_items_from_database():
            selected_setor = setor_var.get()
            
            if not selected_setor == "Selecione um setor":
                cursor.execute("SELECT * FROM produtos WHERE setor = ? ORDER BY validade ASC", (selected_setor,))
        
            items = cursor.fetchall()

            self.listbox.delete(0, tk.END)

            for item in items:
                data_validade = datetime.strptime(item[3], '%Y/%m/%d').strftime('%d/%m/%Y')
                formatted_item = f"ID: {item[0]}  Produto: {item[1]}  Qtd: {item[2]}  Validade: {data_validade}  Setor: {item[4]}"
                self.listbox.insert(tk.END, formatted_item)
    
        
        setor_dropdown = ttk.Combobox(self.button_frame, textvariable=setor_var, width=25, values=setores, font=fonte, state="readonly")
        setor_dropdown.grid(row=0, column=1, padx=(0, 10), pady=5, sticky='e')
        
        setor_dropdown.bind("<<ComboboxSelected>>", lambda event: load_items_from_database())

        self.listbox = tk.Listbox(self.button_frame, font=fonte, width=80, height=15, relief='solid', borderwidth=1)
        self.listbox.grid(row=1, column=0, columnspan=2, padx=10, pady=5)
        self.listbox.configure(highlightbackground="#9E9A91", highlightcolor="#9E9A91", border=0, activestyle="none")
        
        scrollbar = tk.Scrollbar(self.button_frame, orient="vertical", command=self.listbox.yview)
        scrollbar.grid(row=1, column=2, sticky='ns')
        self.listbox.config(yscrollcommand=scrollbar.set)

    def listar_itens_vencidos(self):
        fonte = ('Helvetica', 12)  
        self.titulo.set("Itens Vencidos")

        today = datetime.today().strftime('%Y/%m/%d')
        cursor.execute("SELECT * FROM produtos WHERE validade <= ? ORDER BY validade ASC", (today,))
        items = cursor.fetchall()

        for widget in self.button_frame.winfo_children():
            widget.destroy()

        self.listbox = tk.Listbox(self.button_frame, font=fonte, width=80, height=15, relief='solid', borderwidth=1)
        self.listbox.grid(row=1, column=0, columnspan=2, padx=10, pady=5)
        self.listbox.configure(highlightbackground="#9E9A91", highlightcolor="#9E9A91", border=0, activestyle="none")

        scrollbar = tk.Scrollbar(self.button_frame, orient="vertical", command=self.listbox.yview)
        scrollbar.grid(row=1, column=2, sticky='ns')
        self.listbox.config(yscrollcommand=scrollbar.set)
        
        for item in items:
            data_validade = datetime.strptime(item[3], '%Y/%m/%d').strftime('%d/%m/%Y')
            formatted_item = f"ID: {item[0]}  Produto: {item[1]}  Qtd: {item[2]}  Validade: {data_validade}  Setor: {item[4]}"
            self.listbox.insert(tk.END, formatted_item)
        

    def mostrar_proximos_vencimentos(self):
        fonte = ('Helvetica', 12)  
        self.titulo.set(f"Próximos Vencimentos ({7} dias)")
        
        today = datetime.today().strftime('%Y/%m/%d')
        future_date = (datetime.today() + timedelta(days=7)).strftime('%Y/%m/%d')
        
        setor_var = tk.StringVar(self.button_frame)
        setores = ["Liquida", "Mercearia", "Limpeza", "Perecíveis","Padaria"]
        setor_var.set("Selecione um setor")
        
        def load_items_from_database():
            selected_setor = setor_var.get()
            
            if not selected_setor == "Selecione um setor":
                cursor.execute("SELECT * FROM produtos WHERE setor = ? AND validade BETWEEN ? AND ?", (selected_setor, today, future_date))

            items = cursor.fetchall()

            self.listbox.delete(0, tk.END)

            for item in items:
                data_validade = datetime.strptime(item[3], '%Y/%m/%d').strftime('%d/%m/%Y')
                formatted_item = f"ID: {item[0]}  Produto: {item[1]}  Qtd: {item[2]}  Validade: {data_validade}  Setor: {item[4]}"
                self.listbox.insert(tk.END, formatted_item)

        for widget in self.button_frame.winfo_children():
            widget.destroy()

        setor_dropdown = ttk.Combobox(self.button_frame, textvariable=setor_var, width=25, values=setores, font=fonte, state="readonly")
        setor_dropdown.grid(row=0, column=1, padx=(0, 10), pady=5, sticky='e')
        
        setor_dropdown.bind("<<ComboboxSelected>>", lambda event: load_items_from_database())
        
        self.listbox = tk.Listbox(self.button_frame, font=fonte, width=80, height=15, relief='solid', borderwidth=1)
        self.listbox.grid(row=1, column=0, columnspan=2, padx=10, pady=5)
        self.listbox.configure(highlightbackground="#9E9A91", highlightcolor="#9E9A91", border=0, activestyle="none")

        scrollbar = tk.Scrollbar(self.button_frame, orient="vertical", command=self.listbox.yview)
        scrollbar.grid(row=1, column=2, sticky='ns')
        self.listbox.config(yscrollcommand=scrollbar.set)
        
def main():
    iniciar_login()

if __name__ == "__main__":
    main()