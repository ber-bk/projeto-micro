"""
Módulo para visualizar missões antigas
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
import servidor.database as db
import captura.gravacao_video as gravacao_video
import captura.gravacao_audio as gravacao_audio
import servidor.sensor_arduino as sensor_arduino


class VisualizarMissoesWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Visualizar Missões Antigas")
        self.window.geometry("900x600")

        # Criar interface
        self.criar_interface()
        self.carregar_missoes()

    def criar_interface(self):
        """Cria a interface da janela"""
        # Frame principal
        main_frame = tk.Frame(self.window, bg='#f0f0f0', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Título
        titulo = tk.Label(main_frame, text="Missões de Mergulho",
                         font=('Arial', 16, 'bold'),
                         bg='#f0f0f0', fg='#1a5490')
        titulo.pack(pady=(0, 15))

        # Frame para a tabela
        tree_frame = tk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # Scrollbars
        scroll_y = tk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        scroll_x = tk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)

        # Treeview (tabela)
        self.tree = ttk.Treeview(tree_frame,
                                columns=('Identificador', 'Mergulhador', 'Nome da Missão', 'Início', 'Fim', 'Status'),
                                show='headings',
                                yscrollcommand=scroll_y.set,
                                xscrollcommand=scroll_x.set)

        scroll_y.config(command=self.tree.yview)
        scroll_x.config(command=self.tree.xview)

        # Configurar colunas
        self.tree.heading('Identificador', text='Identificador')
        self.tree.heading('Mergulhador', text='Mergulhador')
        self.tree.heading('Nome da Missão', text='Nome da Missão')
        self.tree.heading('Início', text='Data/Hora Início')
        self.tree.heading('Fim', text='Data/Hora Fim')
        self.tree.heading('Status', text='Status')

        self.tree.column('Identificador', width=180)
        self.tree.column('Mergulhador', width=150)
        self.tree.column('Nome da Missão', width=150)
        self.tree.column('Início', width=150, anchor=tk.CENTER)
        self.tree.column('Fim', width=150, anchor=tk.CENTER)
        self.tree.column('Status', width=100, anchor=tk.CENTER)

        # Layout
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Frame de botões
        btn_frame = tk.Frame(main_frame, bg='#f0f0f0')
        btn_frame.pack(pady=15)

        tk.Button(btn_frame, text="Ver Detalhes",
                 command=self.ver_detalhes,
                 bg='#1a5490', fg='white',
                 font=('Arial', 11, 'bold'),
                 width=15, cursor='hand2').pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="Visualizar Missão",
                 command=self.visualizar_missao,
                 bg='#2c5aa0', fg='white',
                 font=('Arial', 11, 'bold'),
                 width=18, cursor='hand2').pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="Finalizar Missão",
                 command=self.finalizar_missao,
                 bg='#4a7ba7', fg='white',
                 font=('Arial', 11, 'bold'),
                 width=15, cursor='hand2').pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="Fechar",
                 command=self.window.destroy,
                 bg='#999999', fg='white',
                 font=('Arial', 11, 'bold'),
                 width=12, cursor='hand2').pack(side=tk.LEFT, padx=5)

    def carregar_missoes(self):
        """Carrega as missões do banco de dados"""
        # Limpar tabela
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Buscar missões
        missoes = db.listar_missoes()

        if not missoes:
            messagebox.showinfo("Info", "Nenhuma missão cadastrada.")
            return

        for missao in missoes:
            id_missao, identificador, nome_missao, data_inicio, data_fim, nome_merg, idade, sexo = missao

            # Formatar datas
            try:
                dt_inicio = datetime.strptime(data_inicio, "%Y-%m-%d %H:%M:%S")
                inicio_fmt = dt_inicio.strftime("%d/%m/%Y %H:%M")
            except:
                inicio_fmt = data_inicio

            if data_fim:
                try:
                    dt_fim = datetime.strptime(data_fim, "%Y-%m-%d %H:%M:%S")
                    fim_fmt = dt_fim.strftime("%d/%m/%Y %H:%M")
                    status = "Finalizada"
                except:
                    fim_fmt = data_fim
                    status = "Finalizada"
            else:
                fim_fmt = "Em andamento"
                status = "Em andamento"

            # Armazenar o id_missao como dado oculto (iid) e mostrar o identificador  - Pq isso?
            self.tree.insert('', tk.END, iid=str(id_missao), values=(
                identificador,
                f"{nome_merg} ({idade}a, {sexo})",
                nome_missao,
                inicio_fmt,
                fim_fmt,
                status
            ))

    def ver_detalhes(self):
        """Mostra detalhes da missão selecionada"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione uma missão da lista!")
            return

        # O iid contém o id_missao
        id_missao = int(selection[0])

        # Buscar dados completos
        missao = db.buscar_missao(id_missao)
        medicoes = db.listar_medicoes_por_missao(id_missao)
        videos = db.listar_videos_por_missao(id_missao)
        audios = db.listar_audios_por_missao(id_missao)

        # Criar janela de detalhes
        det_window = tk.Toplevel(self.window)
        det_window.title(f"Detalhes da Missão #{id_missao}")
        det_window.geometry("700x600")

        # Texto com scroll
        text_area = scrolledtext.ScrolledText(det_window, font=('Courier', 10), wrap=tk.WORD)
        text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Montar informações
        id_m, identificador, id_merg, nome_missao, dt_ini, dt_fim, nome, idade, sexo = missao

        info = f"{'=' * 70}\n"
        info += f"DETALHES DA MISSÃO: {identificador}\n"
        info += f"{'=' * 70}\n\n"

        info += f"DADOS DO MERGULHADOR:\n"
        info += f"  Nome: {nome}\n"
        info += f"  Idade: {idade} anos\n"
        info += f"  Sexo: {sexo}\n\n"

        info += f"DADOS DA MISSÃO:\n"
        info += f"  Identificador: {identificador}\n"
        info += f"  Nome da Missão: {nome_missao}\n"
        info += f"  Data/Hora Início: {dt_ini}\n"
        info += f"  Data/Hora Fim: {dt_fim if dt_fim else 'Em andamento'}\n\n"

        # Vídeos
        info += f"VÍDEOS ({len(videos)}):\n"
        if videos:
            for idx, video in enumerate(videos, 1):
                info += f"  {idx}. {video[2]}\n"
        else:
            info += "  Nenhum vídeo cadastrado.\n"
        info += "\n"

        # Áudios
        info += f"ÁUDIOS ({len(audios)}):\n"
        if audios:
            for idx, audio in enumerate(audios, 1):
                info += f"  {idx}. {audio[2]}\n"
        else:
            info += "  Nenhum áudio cadastrado.\n"
        info += "\n"

        # Medições
        info += f"MEDIÇÕES DE SENSORES ({len(medicoes)}):\n"
        info += f"{'-' * 70}\n"
        if medicoes:
            info += f"{'ID':<8} {'Data/Hora':<20} {'Temp (°C)':<12} {'Pressão (psi)':<15}\n"
            info += f"{'-' * 70}\n"
            for med in medicoes:
                id_med, _, timestamp, temp, press = med
                info += f"{id_med:<8} {timestamp:<20} {temp:<12.2f} {press:<15.2f}\n"

            # Estatísticas
            stats = db.get_estatisticas_medicoes(id_missao)
            if stats and stats[0] > 0:
                total, temp_min, temp_max, temp_avg, press_min, press_max, press_avg = stats
                info += f"\n{'-' * 70}\n"
                info += f"ESTATÍSTICAS:\n"
                info += f"  Total de medições: {total}\n"
                info += f"  Temperatura - Mín: {temp_min:.2f}°C | Máx: {temp_max:.2f}°C | Média: {temp_avg:.2f}°C\n"
                info += f"  Pressão - Mín: {press_min:.2f} psi | Máx: {press_max:.2f} psi | Média: {press_avg:.2f} psi\n"
        else:
            info += "  Nenhuma medição registrada.\n"

        info += f"\n{'=' * 70}\n"

        text_area.insert(tk.END, info)
        text_area.config(state=tk.DISABLED)

    def visualizar_missao(self):
        """Visualiza vídeo (missão finalizada) ou abre câmera (missão em andamento)"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione uma missão da lista!")
            return

        # O iid contém o id_missao
        id_missao = int(selection[0])
        item = self.tree.item(selection[0])
        status = item['values'][5]  # Coluna Status

        if status == "Finalizada":
            # Missão finalizada: abrir vídeo salvo
            self.abrir_video(id_missao)
        else:
            # Missão em andamento: abrir câmera ao vivo
            self.abrir_camera()

    def abrir_video(self, id_missao):
        """Reproduz todos os vídeos e áudios da missão em sequência sincronizada"""
        try:
            import cv2
            import pyaudio
            import wave
            import threading
        except ImportError as e:
            messagebox.showerror("Erro", f"Biblioteca não instalada: {e}")
            return

        import os

        # Buscar vídeos e áudios da missão
        videos = db.listar_videos_por_missao(id_missao)
        audios = db.listar_audios_por_missao(id_missao)

        if not videos:
            messagebox.showwarning("Aviso", "Nenhum vídeo cadastrado para esta missão!")
            return

        # Ordenar por ID
        videos_ordenados = sorted(videos, key=lambda x: x[0])
        audios_ordenados = sorted(audios, key=lambda x: x[0])

        # Buscar informações da missão
        missao = db.buscar_missao(id_missao)
        identificador = missao[1] if missao else f"Missão #{id_missao}"

        print(f"[REPRODUÇÃO] Iniciando reprodução de {len(videos_ordenados)} vídeo(s) e {len(audios_ordenados)} áudio(s)")

        # Flag para controlar reprodução de áudio
        self.parar_audio = False

        def reproduzir_audio(caminho_audio):
            """Reproduz áudio em thread separada"""
            try:
                wf = wave.open(caminho_audio, 'rb')
                p = pyaudio.PyAudio()

                stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                               channels=wf.getnchannels(),
                               rate=wf.getframerate(),
                               output=True)

                # Ler e reproduzir em chunks
                CHUNK = 1024
                data = wf.readframes(CHUNK)

                while data and not self.parar_audio:
                    stream.write(data)
                    data = wf.readframes(CHUNK)

                stream.stop_stream()
                stream.close()
                p.terminate()
                wf.close()
            except Exception as e:
                print(f"[ÁUDIO ERRO] Falha ao reproduzir áudio: {e}")

        # Reproduzir cada segmento
        for idx in range(max(len(videos_ordenados), len(audios_ordenados))):
            # Pegar vídeo e áudio correspondentes
            video = videos_ordenados[idx] if idx < len(videos_ordenados) else None
            audio = audios_ordenados[idx] if idx < len(audios_ordenados) else None

            if video:
                id_video, _, caminho_video = video

                if not os.path.exists(caminho_video):
                    print(f"[AVISO] Vídeo {idx+1} não encontrado")
                    continue

                print(f"[REPRODUÇÃO] Segmento {idx+1}: Vídeo + Áudio")

                # Iniciar reprodução de áudio em thread separada
                self.parar_audio = False
                audio_thread = None

                if audio:
                    _, _, caminho_audio = audio
                    if os.path.exists(caminho_audio):
                        audio_thread = threading.Thread(target=reproduzir_audio, args=(caminho_audio,))
                        audio_thread.daemon = True
                        audio_thread.start()
                    else:
                        print(f"[AVISO] Áudio {idx+1} não encontrado")

                # Reproduzir vídeo
                cap = cv2.VideoCapture(caminho_video)

                if not cap.isOpened():
                    print(f"[ERRO] Não foi possível abrir vídeo")
                    self.parar_audio = True
                    continue

                fps = cap.get(cv2.CAP_PROP_FPS) or 30
                delay = int(1000 / fps)

                titulo = f"{identificador} - Segmento {idx+1} - [Q]Sair [N]Próximo"
                cv2.namedWindow(titulo, cv2.WINDOW_NORMAL)

                while True:
                    ret, frame = cap.read()

                    if not ret:
                        break

                    texto = f"Segmento {idx+1} - VIDEO + AUDIO"
                    cv2.putText(frame, texto, (10, frame.shape[0] - 20),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

                    cv2.imshow(titulo, frame)

                    key = cv2.waitKey(delay) & 0xFF
                    if key == ord('q'):
                        self.parar_audio = True
                        cap.release()
                        cv2.destroyAllWindows()
                        if audio_thread:
                            audio_thread.join(timeout=1)
                        print("[REPRODUÇÃO] Cancelada pelo usuário")
                        return
                    elif key == ord('n'):
                        break

                cap.release()
                cv2.destroyWindow(titulo)

                # Parar áudio do segmento atual
                self.parar_audio = True
                if audio_thread:
                    audio_thread.join(timeout=1)

        cv2.destroyAllWindows()
        print(f"[REPRODUÇÃO] Finalizada!")

    def abrir_camera(self):
        """Abre a câmera ao vivo usando OpenCV"""
        try:
            import cv2
        except ImportError:
            messagebox.showerror("Erro",
                               "Biblioteca OpenCV não instalada!\n\n"
                               "Instale com: pip install opencv-python")
            return

        # Verificar se há gravação em andamento
        gravador = gravacao_video.get_gravador()
        if gravador.esta_gravando():
            # Exibir frames da gravação em andamento
            self.visualizar_gravacao_ao_vivo(cv2, gravador)
        else:
            # Abrir câmera diretamente (missão sem gravação - não deve acontecer)
            self.visualizar_camera_direta(cv2)

    def visualizar_gravacao_ao_vivo(self, cv2, gravador):
        """Exibe os frames que estão sendo gravados em tempo real"""
        try:
            info = gravador.get_info_gravacao()
            titulo = f"Gravação ao Vivo - {info['identificador']} - Pressione 'Q' para sair"
            cv2.namedWindow(titulo)

            while True:
                # Obter o último frame capturado pela gravação
                frame = gravador.get_ultimo_frame()

                if frame is not None:
                    # Adicionar texto indicando que é visualização da gravação
                    cor_verde_claro = (100, 255, 100)
                    cv2.putText(frame, "AO VIVO", (10, frame.shape[0] - 25),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.8, cor_verde_claro, 2, cv2.LINE_AA)

                    cv2.imshow(titulo, frame)

                # Pressionar 'q' para sair
                if cv2.waitKey(30) & 0xFF == ord('q'):
                    break

                # Verificar se a gravação ainda está ativa
                if not gravador.esta_gravando():
                    messagebox.showinfo("Info", "A gravação foi finalizada.")
                    break

            cv2.destroyAllWindows()

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao visualizar gravação:\n{e}")

    def visualizar_camera_direta(self, cv2):
        """Abre a câmera diretamente (quando não há gravação)"""
        try:
            # Abrir câmera (0 = câmera padrão)
            cap = cv2.VideoCapture(0)

            if not cap.isOpened():
                messagebox.showerror("Erro", "Não foi possível abrir a câmera!")
                return

            cv2.namedWindow("Missão ao Vivo - Pressione 'Q' para sair")

            while True:
                ret, frame = cap.read()

                if not ret:
                    break

                # Adicionar texto na tela
                cor_verde_claro = (100, 255, 100)
                cv2.putText(frame, "AO VIVO", (10, 40),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, cor_verde_claro, 2, cv2.LINE_AA)

                cv2.imshow("Missão ao Vivo - Pressione 'Q' para sair", frame)

                # Pressionar 'q' para sair
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            cap.release()
            cv2.destroyAllWindows()

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir câmera:\n{e}")

    def finalizar_missao(self):
        """Finaliza uma missão (adiciona data/hora de término)"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Aviso", "Selecione uma missão da lista!")
            return

        # O iid contém o id_missao
        id_missao = int(selection[0])
        item = self.tree.item(selection[0])
        status = item['values'][5]

        if status == "Finalizada":
            messagebox.showinfo("Info", "Esta missão já foi finalizada!")
            return

        # Confirmar
        resposta = messagebox.askyesno("Confirmar",
                                       f"Deseja finalizar a Missão #{id_missao}?\n\n"
                                       "Isso marcará a data/hora atual como término da missão.")

        if resposta:
            # Parar leitura de sensores
            sensor = sensor_arduino.get_sensor()
            sensor_parado = False
            if sensor.lendo:
                sensor.parar_leitura()
                sensor_parado = True

            # Parar gravação automática de vídeo
            gravador_video = gravacao_video.get_gravador()
            video_parado = False
            if gravador_video.esta_gravando():
                gravador_video.parar_gravacao()
                video_parado = True

            # Parar gravação automática de áudio
            gravador_audio = gravacao_audio.get_gravador()
            audio_parado = False
            if gravador_audio.esta_gravando():
                gravador_audio.parar_gravacao()
                audio_parado = True

            # Mensagem de status
            parados = []
            if video_parado:
                parados.append("Vídeo")
            if audio_parado:
                parados.append("Áudio")
            if sensor_parado:
                parados.append("Sensores")

            if parados:
                msg_gravacao = f"\n{', '.join(parados)} finalizado(s)."
            else:
                msg_gravacao = ""

            # Atualizar banco de dados
            data_hora_fim = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            db.atualizar_fim_missao(id_missao, data_hora_fim)

            messagebox.showinfo("Sucesso",
                               f"Missão #{id_missao} finalizada com sucesso!"
                               f"{msg_gravacao}")
            self.carregar_missoes()
