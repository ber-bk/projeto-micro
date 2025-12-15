"""
Módulo para criar nova missão
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import servidor.database as db
import captura.gravacao_video as gravacao_video
import captura.gravacao_audio as gravacao_audio
import servidor.sensor_arduino as sensor_arduino


class CriarMissaoWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Criar Nova Missão")
        self.window.geometry("700x450")
        self.window.resizable(False, False)

        # Centralizar janela
        self.centralizar_janela()

        # Variáveis
        self.mergulhador_selecionado = None

        # Criar interface
        self.criar_interface()

    def centralizar_janela(self):
        """Centraliza a janela na tela"""
        self.window.update_idletasks()
        largura = self.window.winfo_width()
        altura = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (largura // 2)
        y = (self.window.winfo_screenheight() // 2) - (altura // 2)
        self.window.geometry(f'{largura}x{altura}+{x}+{y}')

    def criar_interface(self):
        """Cria a interface da janela"""
        # Frame principal
        main_frame = tk.Frame(self.window, bg='#f0f0f0', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título
        titulo = tk.Label(main_frame, text="Nova Missão de Mergulho",
                         font=('Arial', 16, 'bold'),
                         bg='#f0f0f0', fg='#1a5490')
        titulo.pack(pady=(0, 20))

        # ========== SEÇÃO MERGULHADOR ==========
        frame_mergulhador = tk.LabelFrame(main_frame, text="Dados do Mergulhador",
                                         font=('Arial', 11, 'bold'),
                                         bg='#f0f0f0', fg='#1a5490',
                                         padx=10, pady=10)
        frame_mergulhador.pack(fill=tk.X, pady=(0, 15))

        # Botões de mergulhador
        btn_frame = tk.Frame(frame_mergulhador, bg='#f0f0f0')
        btn_frame.pack(fill=tk.X, pady=5)

        tk.Button(btn_frame, text="Selecionar Mergulhador Existente",
                 command=self.selecionar_mergulhador,
                 bg='#2c5aa0', fg='white',
                 font=('Arial', 10), cursor='hand2').pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="Cadastrar Novo Mergulhador",
                 command=self.cadastrar_mergulhador,
                 bg='#4a7ba7', fg='white',
                 font=('Arial', 10), cursor='hand2').pack(side=tk.LEFT, padx=5)

        # Info mergulhador selecionado
        self.label_mergulhador = tk.Label(frame_mergulhador,
                                         text="Nenhum mergulhador selecionado",
                                         bg='#f0f0f0', fg='#666666',
                                         font=('Arial', 10))
        self.label_mergulhador.pack(pady=10)

        # ========== SEÇÃO DADOS DA MISSÃO ==========
        frame_missao = tk.LabelFrame(main_frame, text="Dados da Missão",
                                    font=('Arial', 11, 'bold'),
                                    bg='#f0f0f0', fg='#1a5490',
                                    padx=10, pady=10)
        frame_missao.pack(fill=tk.X, pady=(0, 15))

        # Nome da Missão
        tk.Label(frame_missao, text="Nome da Missão:",
                bg='#f0f0f0', font=('Arial', 10)).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.entry_responsavel = tk.Entry(frame_missao, font=('Arial', 10), width=40)
        self.entry_responsavel.grid(row=0, column=1, sticky=tk.W, pady=5, padx=10)

        # Data e hora de início
        tk.Label(frame_missao, text="Data/Hora Início:",
                bg='#f0f0f0', font=('Arial', 10)).grid(row=1, column=0, sticky=tk.W, pady=5)

        datetime_frame = tk.Frame(frame_missao, bg='#f0f0f0')
        datetime_frame.grid(row=1, column=1, sticky=tk.W, pady=5, padx=10)

        self.entry_data_inicio = tk.Entry(datetime_frame, font=('Arial', 10), width=12)
        self.entry_data_inicio.pack(side=tk.LEFT, padx=(0, 5))
        self.entry_data_inicio.insert(0, datetime.now().strftime("%d/%m/%Y"))

        self.entry_hora_inicio = tk.Entry(datetime_frame, font=('Arial', 10), width=8)
        self.entry_hora_inicio.pack(side=tk.LEFT)
        self.entry_hora_inicio.insert(0, datetime.now().strftime("%H:%M"))

        tk.Label(datetime_frame, text="(DD/MM/AAAA HH:MM)",
                bg='#f0f0f0', fg='#666666',
                font=('Arial', 8)).pack(side=tk.LEFT, padx=5)

        # ========== BOTÕES DE AÇÃO ==========
        btn_action_frame = tk.Frame(main_frame, bg='#f0f0f0')
        btn_action_frame.pack(pady=20)

        tk.Button(btn_action_frame, text="Criar Missão",
                 command=self.criar_missao,
                 bg='#1a5490', fg='white',
                 font=('Arial', 12, 'bold'),
                 width=15, height=2,
                 cursor='hand2').pack(side=tk.LEFT, padx=10)

        tk.Button(btn_action_frame, text="Cancelar",
                 command=self.window.destroy,
                 bg='#999999', fg='white',
                 font=('Arial', 12, 'bold'),
                 width=15, height=2,
                 cursor='hand2').pack(side=tk.LEFT, padx=10)

    def selecionar_mergulhador(self):
        """Abre janela para selecionar mergulhador existente"""
        mergulhadores = db.listar_mergulhadores()

        if not mergulhadores:
            messagebox.showwarning("Aviso", "Nenhum mergulhador cadastrado!\nCadastre um novo mergulhador.")
            return

        # Criar janela de seleção
        sel_window = tk.Toplevel(self.window)
        sel_window.title("Selecionar Mergulhador")
        sel_window.geometry("500x400")

        tk.Label(sel_window, text="Selecione um Mergulhador:",
                font=('Arial', 12, 'bold')).pack(pady=10)

        # Lista
        listbox = tk.Listbox(sel_window, font=('Arial', 10), height=15)
        listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        for merg in mergulhadores:
            id_m, nome, idade, sexo = merg
            listbox.insert(tk.END, f"ID: {id_m} | {nome} | {idade} anos | Sexo: {sexo}")

        def confirmar_selecao():
            if listbox.curselection():
                index = listbox.curselection()[0]
                self.mergulhador_selecionado = mergulhadores[index]
                id_m, nome, idade, sexo = self.mergulhador_selecionado
                self.label_mergulhador.config(
                    text=f"Selecionado: {nome} ({idade} anos, Sexo: {sexo})",
                    fg='#1a5490', font=('Arial', 10, 'bold'))
                sel_window.destroy()
            else:
                messagebox.showwarning("Aviso", "Selecione um mergulhador da lista!")

        tk.Button(sel_window, text="Confirmar", command=confirmar_selecao,
                 bg='#1a5490', fg='white', font=('Arial', 10, 'bold')).pack(pady=10)

    def cadastrar_mergulhador(self):
        """Abre janela para cadastrar novo mergulhador"""
        cad_window = tk.Toplevel(self.window)
        cad_window.title("Cadastrar Novo Mergulhador")
        cad_window.geometry("400x300")

        frame = tk.Frame(cad_window, padx=20, pady=20)
        frame.pack()

        tk.Label(frame, text="Cadastrar Novo Mergulhador",
                font=('Arial', 12, 'bold')).grid(row=0, column=0, columnspan=2, pady=10)

        # Nome
        tk.Label(frame, text="Nome:", font=('Arial', 10)).grid(row=1, column=0, sticky=tk.W, pady=5)
        entry_nome = tk.Entry(frame, font=('Arial', 10), width=30)
        entry_nome.grid(row=1, column=1, pady=5)

        # Idade
        tk.Label(frame, text="Idade:", font=('Arial', 10)).grid(row=2, column=0, sticky=tk.W, pady=5)
        entry_idade = tk.Entry(frame, font=('Arial', 10), width=30)
        entry_idade.grid(row=2, column=1, pady=5)

        # Sexo
        tk.Label(frame, text="Sexo:", font=('Arial', 10)).grid(row=3, column=0, sticky=tk.W, pady=5)
        sexo_var = tk.StringVar(value="M")
        sexo_frame = tk.Frame(frame)
        sexo_frame.grid(row=3, column=1, sticky=tk.W, pady=5)
        tk.Radiobutton(sexo_frame, text="Masculino", variable=sexo_var, value="M").pack(side=tk.LEFT)
        tk.Radiobutton(sexo_frame, text="Feminino", variable=sexo_var, value="F").pack(side=tk.LEFT)
        tk.Radiobutton(sexo_frame, text="Outro", variable=sexo_var, value="O").pack(side=tk.LEFT)

        def salvar_mergulhador():
            nome = entry_nome.get().strip()
            idade_str = entry_idade.get().strip()
            sexo = sexo_var.get()

            if not nome or not idade_str:
                messagebox.showerror("Erro", "Preencha todos os campos!")
                return

            try:
                idade = int(idade_str)
                if idade <= 0:
                    raise ValueError()
            except ValueError:
                messagebox.showerror("Erro", "Idade inválida!")
                return

            id_novo = db.inserir_mergulhador(nome, idade, sexo)
            self.mergulhador_selecionado = (id_novo, nome, idade, sexo)
            self.label_mergulhador.config(
                text=f"Selecionado: {nome} ({idade} anos, Sexo: {sexo})",
                fg='#1a5490', font=('Arial', 10, 'bold'))
            messagebox.showinfo("Sucesso", f"Mergulhador '{nome}' cadastrado com sucesso!")
            cad_window.destroy()

        tk.Button(frame, text="Salvar", command=salvar_mergulhador,
                 bg='#1a5490', fg='white', font=('Arial', 10, 'bold')).grid(row=4, column=0, columnspan=2, pady=20)

    def criar_missao(self):
        """Cria a missão no banco de dados"""
        # Verificar se já existe missão em andamento
        missao_em_andamento = db.verificar_missao_em_andamento()
        if missao_em_andamento:
            id_m, identificador, nome_m, data_inicio, nome_merg = missao_em_andamento
            messagebox.showerror("Erro",
                               f"Já existe uma missão em andamento!\n\n"
                               f"Identificador: {identificador}\n"
                               f"Nome: {nome_m}\n"
                               f"Mergulhador: {nome_merg}\n"
                               f"Início: {data_inicio}\n\n"
                               f"Finalize a missão atual antes de criar uma nova.")
            return

        # Validações
        if not self.mergulhador_selecionado:
            messagebox.showerror("Erro", "Selecione um mergulhador!")
            return

        nome_missao = self.entry_responsavel.get().strip()
        if not nome_missao:
            messagebox.showerror("Erro", "Informe o nome da missão!")
            return

        data_inicio = self.entry_data_inicio.get().strip()
        hora_inicio = self.entry_hora_inicio.get().strip()

        try:
            data_hora_inicio = datetime.strptime(f"{data_inicio} {hora_inicio}", "%d/%m/%Y %H:%M")
        except ValueError:
            messagebox.showerror("Erro", "Data/Hora de início inválida!\nUse o formato: DD/MM/AAAA HH:MM")
            return

        # Gerar identificador no formato Missão_DD-MM-AA_HH-MM (sem dois pontos)
        identificador = f"Missao_{data_hora_inicio.strftime('%d-%m-%y_%H-%M')}"

        # Inserir missão
        id_mergulhador = self.mergulhador_selecionado[0]
        id_missao = db.inserir_missao(id_mergulhador, nome_missao, data_hora_inicio.strftime("%Y-%m-%d %H:%M:%S"), identificador)

        # Conectar e iniciar leitura do Arduino
        sensor = sensor_arduino.get_sensor()
        if not sensor.conectado:
            sensor.conectar()  # Tenta conectar automaticamente

        sensor_ok = False
        if sensor.conectado:
            sensor_ok = sensor.iniciar_leitura(id_missao)

        # Iniciar gravação automática de vídeo
        gravador_video = gravacao_video.get_gravador()
        video_ok = gravador_video.iniciar_gravacao(id_missao, identificador)

        # Iniciar gravação automática de áudio
        gravador_audio = gravacao_audio.get_gravador()
        audio_ok = gravador_audio.iniciar_gravacao(id_missao, identificador)

        # Mensagem de status
        status = []
        if video_ok:
            status.append("Vídeo")
        if audio_ok:
            status.append("Áudio")
        if sensor_ok:
            status.append("Sensores")

        if status:
            msg_gravacao = f"\n\n{', '.join(status)} iniciado(s)!"
        else:
            msg_gravacao = "\n\nAVISO: Não foi possível iniciar gravações/sensores."

        messagebox.showinfo("Sucesso",
                           f"Missão criada com sucesso!\n\n"
                           f"Identificador: {identificador}\n"
                           f"Nome: {nome_missao}\n"
                           f"Mergulhador: {self.mergulhador_selecionado[1]}\n"
                           f"Início: {data_hora_inicio.strftime('%d/%m/%Y %H:%M')}"
                           f"{msg_gravacao}")

        self.window.destroy()
