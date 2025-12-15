"""
Sistema de Monitoramento de Mergulhos
Arquivo Principal - Interface Gráfica
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import servidor.database as db
from interface.criar_missao import CriarMissaoWindow
from interface.visualizar_missoes import VisualizarMissoesWindow


class SistemaMergulhoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Monitoramento de Mergulhos")
        self.root.geometry("600x500")
        self.root.resizable(False, False)

        # Centralizar janela na tela
        self.centralizar_janela()

        # Configurar estilo
        self.configurar_estilo()

        # Inicializar banco de dados
        db.inicializar_banco()

        # Criar interface
        self.criar_interface()

    def centralizar_janela(self):
        """Centraliza a janela na tela"""
        self.root.update_idletasks()
        largura = self.root.winfo_width()
        altura = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (largura // 2)
        y = (self.root.winfo_screenheight() // 2) - (altura // 2)
        self.root.geometry(f'{largura}x{altura}+{x}+{y}')

    def configurar_estilo(self):
        """Configura o estilo da interface"""
        style = ttk.Style()
        style.theme_use('clam')

        # Estilo para botões principais
        style.configure('Main.TButton',
                       font=('Arial', 12, 'bold'),
                       padding=15,
                       background='#1a5490',
                       foreground='white')

        style.map('Main.TButton',
                 background=[('active', '#2c5aa0')])

        # Estilo para labels
        style.configure('Title.TLabel',
                       font=('Arial', 20, 'bold'),
                       foreground='#1a5490',
                       background='#f0f0f0')

        style.configure('Subtitle.TLabel',
                       font=('Arial', 10),
                       foreground='#666666',
                       background='#f0f0f0')

    def criar_interface(self):
        """Cria a interface principal"""
        # Frame principal com cor de fundo
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Título
        titulo = ttk.Label(main_frame,
                          text="Sistema de Monitoramento",
                          style='Title.TLabel')
        titulo.pack(pady=(20, 5))

        subtitulo = ttk.Label(main_frame,
                             text="de Mergulhos",
                             style='Title.TLabel')
        subtitulo.pack(pady=(0, 10))

        # Data atual
        data_atual = datetime.now().strftime("%d/%m/%Y - %H:%M")
        data_label = ttk.Label(main_frame,
                              text=f"Data: {data_atual}",
                              style='Subtitle.TLabel')
        data_label.pack(pady=(0, 30))

        # Frame para os botões
        botoes_frame = tk.Frame(main_frame, bg='#f0f0f0')
        botoes_frame.pack(pady=20, expand=True)

        # Botão: Criar Nova Missão
        btn_criar = tk.Button(botoes_frame,
                             text="Criar Nova Missão",
                             command=self.criar_nova_missao,
                             font=('Arial', 14, 'bold'),
                             bg='#1a5490',
                             fg='white',
                             activebackground='#2c5aa0',
                             activeforeground='white',
                             width=25,
                             height=2,
                             cursor='hand2',
                             relief=tk.RAISED,
                             bd=3)
        btn_criar.pack(pady=15)

        # Botão: Visualizar Missões
        btn_visualizar = tk.Button(botoes_frame,
                                  text="Visualizar Missões",
                                  command=self.visualizar_missao,
                                  font=('Arial', 14, 'bold'),
                                  bg='#2c5aa0',
                                  fg='white',
                                  activebackground='#3d6bb0',
                                  activeforeground='white',
                                  width=25,
                                  height=2,
                                  cursor='hand2',
                                  relief=tk.RAISED,
                                  bd=3)
        btn_visualizar.pack(pady=15)

        # Rodapé
        rodape_frame = tk.Frame(main_frame, bg='#f0f0f0')
        rodape_frame.pack(side=tk.BOTTOM, pady=10)

        rodape = ttk.Label(rodape_frame,
                          text="Projeto de Microcontroladores - 2025",
                          style='Subtitle.TLabel')
        rodape.pack()

        # Informação do banco
        info_db = ttk.Label(rodape_frame,
                           text=f"Banco de dados: {db.DB_PATH}",
                           style='Subtitle.TLabel',
                           font=('Arial', 8))
        info_db.pack()

    def criar_nova_missao(self):
        """Abre a janela para criar uma nova missão"""
        CriarMissaoWindow(self.root)

    def visualizar_missao(self):
        """Abre a janela para visualizar missões antigas"""
        VisualizarMissoesWindow(self.root)


def main():
    """Função principal"""
    root = tk.Tk()
    app = SistemaMergulhoApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
