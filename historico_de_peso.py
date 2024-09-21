import tkinter as tk
from tkinter import messagebox
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

FILE_NAME = 'save/historico.csv'

# Recupera arquivo correspondente ao histórico
def carregar_dados():
    try:
        df = pd.read_csv(FILE_NAME)
    except FileNotFoundError:
        df = pd.DataFrame(columns=['Data', 'Peso', 'Comparação'])
    return df

# Adiciona arquivo ao histórico
def salvar_dados(df):
    df.to_csv(FILE_NAME, index=False)

# Cria uma nova linha na tabela de pesos
def adicionar_peso():
    try:
        peso_atual = float(entry_peso.get())
    except ValueError:
        messagebox.showerror("Erro", "Insira um valor numérico válido.")
        return
    
    data_atual = datetime.now().strftime("%d/%m/%Y")
    
    df = carregar_dados()

    if data_atual in df['Data'].values:
        indice = df[df['Data'] == data_atual].index[0]
        peso_anterior = df.iloc[indice - 1]['Peso'] if indice > 0 else None
        if peso_anterior is not None:
            if peso_atual > peso_anterior:
                comparacao = '>'
            elif peso_atual < peso_anterior:
                comparacao = '<'
            else:
                comparacao = '='
        else:
            comparacao = '-'

        df.at[indice, 'Peso'] = peso_atual
        df.at[indice, 'Comparação'] = comparacao

    else:
        if not df.empty:
            peso_anterior = df.iloc[-1]['Peso']
            if peso_atual > peso_anterior:
                comparacao = '>'
            elif peso_atual < peso_anterior:
                comparacao = '<'
            else:
                comparacao = '='
            diferenca = peso_atual - peso_anterior
        else:
            comparacao = '-'
            diferenca = 0.0 

        nova_linha = pd.DataFrame({'Data': [data_atual], 'Peso': [peso_atual], 'Comparação': [comparacao], 'Diferença': [diferenca]})
        df = pd.concat([df, nova_linha], ignore_index=True)
    
    salvar_dados(df)
    atualizar_tabela(df)
    entry_peso.delete(0, tk.END)

# Dá reload na tabela para ser exibida corretamente ao adicionar um novo peso
def atualizar_tabela(df):
    if 'Diferença' not in df.columns:
        df['Diferença'] = df['Peso'] - df['Peso'].shift(1)
        df['Diferença'] = df['Diferença'].fillna(0)

    df = df.sort_values(by='Data', ascending=False).reset_index(drop=True)

    for widget in frame_tabela.winfo_children():
        widget.destroy()

    for i, col in enumerate(df.columns):
        label = tk.Label(frame_tabela, text=col, borderwidth=1, relief="solid", width=15)
        label.grid(row=0, column=i)

    for i, row in df.iterrows():
        for j, val in enumerate(row):
            if j == 1:  
                val = f"{val}kg" 
            if j == 2: 
                if val == '>':
                    fg_color = 'green'
                elif val == '<':
                    fg_color = 'red'
                else:
                    fg_color = 'black'
            if j == 3:
                val = f"{val}kg"
            else:
                fg_color = 'black'

            label = tk.Label(frame_tabela, text=val, borderwidth=1, relief="solid", width=15, fg=fg_color)
            label.grid(row=i + 1, column=j)

# Gera gráfico de linha em relação ao peso ganho/perdido no período
def exibir_grafico(df):
    if df.empty or 'Diferença' not in df.columns:
        messagebox.showerror("Erro", "Não há dados suficientes para gerar o gráfico.")
        return
    
    df = df.sort_values(by='Data', ascending=True)
    
    datas = df['Data']
    diferencas = df['Diferença']
    
    plt.figure(figsize=(8, 6))
    plt.plot(datas, diferencas, marker='o', linestyle='-', color='b')
    
    plt.title("Diferença de Peso ao Longo do Tempo")
    plt.xlabel("Data")
    plt.ylabel("Diferença de Peso (kg)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    plt.show()


# Funcionalidades da interface gráfica
root = tk.Tk()
root.iconbitmap("assets/icon.ico")
root.title("Evolução corporal (em kg)")

frame_entrada = tk.Frame(root)
frame_entrada.pack(pady=10)

label_peso = tk.Label(frame_entrada, text="Peso (kg):")
label_peso.grid(row=0, column=0, padx=5)

entry_peso = tk.Entry(frame_entrada)
entry_peso.grid(row=0, column=1, padx=5)

btn_adicionar = tk.Button(frame_entrada, text="Adicionar peso atual", command=adicionar_peso)
btn_adicionar.grid(row=0, column=2, padx=5)

btn_grafico = tk.Button(frame_entrada, text="Visualizar gráfico", command=lambda: exibir_grafico(carregar_dados()))
btn_grafico.grid(row=0, column=3, padx=5)

frame_tabela = tk.Frame(root)
frame_tabela.pack(pady=10, padx=20)

df_inicial = carregar_dados()
atualizar_tabela(df_inicial)

root.mainloop()