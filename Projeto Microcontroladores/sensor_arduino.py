"""
Módulo para leitura de dados do Arduino (temperatura e pressão)
"""

import serial
import serial.tools.list_ports
import threading
import time
import re
from datetime import datetime
import database as db


class SensorArduino:
    """Classe para gerenciar leitura de sensores do Arduino"""

    # Instância única (singleton)
    _instancia = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instancia is None:
            with cls._lock:
                if cls._instancia is None:
                    cls._instancia = super().__new__(cls)
        return cls._instancia

    def __init__(self):
        # Evitar reinicialização
        if hasattr(self, 'initialized'):
            return

        self.initialized = True
        self.conectado = False
        self.lendo = False
        self.porta_serial = None
        self.thread_leitura = None
        self.parar_flag = False

        # Últimas leituras
        self.ultima_temperatura = None
        self.ultima_pressao = None
        self.ultima_tensao = None
        self.ultimo_timestamp = None

        # Dados da missão
        self.id_missao = None

        # Controle de salvamento no banco (1 vez por minuto)
        self.ultimo_salvamento = None
        self.intervalo_salvamento = 60  # 60 segundos = 1 minuto

        # Lock para acesso thread-safe
        self.dados_lock = threading.Lock()

    def listar_portas_disponiveis(self):
        """Lista todas as portas COM disponíveis"""
        portas = serial.tools.list_ports.comports()
        return [(porta.device, porta.description) for porta in portas]

    def conectar(self, porta=None, baudrate=9600):
        """Conecta ao Arduino em uma porta específica"""
        if self.conectado:
            print("[SENSOR] Já existe uma conexão ativa!")
            return False

        # Se não especificar porta, tentar detectar automaticamente
        if porta is None:
            portas = self.listar_portas_disponiveis()
            if not portas:
                print("[SENSOR ERRO] Nenhuma porta serial encontrada!")
                return False

            # Tentar conectar na primeira porta encontrada
            porta = portas[0][0]
            print(f"[SENSOR] Tentando conectar automaticamente em: {porta}")

        try:
            self.porta_serial = serial.Serial(porta, baudrate, timeout=1)
            time.sleep(2)  # Aguardar Arduino resetar
            self.conectado = True
            print(f"[SENSOR] Conectado com sucesso em {porta}")
            return True
        except Exception as e:
            print(f"[SENSOR ERRO] Falha ao conectar em {porta}: {e}")
            return False

    def desconectar(self):
        """Desconecta do Arduino"""
        if self.lendo:
            self.parar_leitura()

        if self.porta_serial and self.porta_serial.is_open:
            self.porta_serial.close()
            self.conectado = False
            print("[SENSOR] Desconectado")

    def iniciar_leitura(self, id_missao=None):
        """Inicia leitura contínua dos sensores"""
        if not self.conectado:
            print("[SENSOR ERRO] Arduino não está conectado!")
            return False

        if self.lendo:
            print("[SENSOR] Já está lendo dados!")
            return False

        self.id_missao = id_missao
        self.parar_flag = False
        self.lendo = True

        # Resetar contador de salvamento para nova missão
        self.ultimo_salvamento = None

        # Iniciar thread de leitura
        self.thread_leitura = threading.Thread(
            target=self._ler_dados_continuamente,
            daemon=True
        )
        self.thread_leitura.start()

        print("[SENSOR] Leitura de dados iniciada")
        return True

    def parar_leitura(self):
        """Para a leitura contínua"""
        if not self.lendo:
            return

        print("[SENSOR] Parando leitura...")
        self.parar_flag = True
        self.lendo = False

        if self.thread_leitura and self.thread_leitura.is_alive():
            self.thread_leitura.join(timeout=5)

        print("[SENSOR] Leitura parada")

    def _ler_dados_continuamente(self):
        """Thread que lê dados continuamente do Arduino"""
        try:
            while not self.parar_flag and self.porta_serial.is_open:
                try:
                    # Ler linha da serial
                    linha = self.porta_serial.readline().decode('utf-8', errors='ignore').strip()

                    if linha and '|' in linha:
                        # Parsear dados
                        temperatura, pressao, tensao = self._parsear_linha(linha)

                        if temperatura is not None and pressao is not None:
                            # Atualizar dados
                            with self.dados_lock:
                                self.ultima_temperatura = temperatura
                                self.ultima_pressao = pressao
                                self.ultima_tensao = tensao
                                self.ultimo_timestamp = datetime.now()

                            print(f"[SENSOR] Temp: {temperatura:.1f}°C | Pressão: {pressao:.2f} psi")

                            # Salvar no banco de dados se houver missão ativa
                            # Salva apenas de minuto em minuto
                            if self.id_missao:
                                agora = time.time()

                                # Primeira leitura ou passou 1 minuto desde último salvamento
                                if self.ultimo_salvamento is None or (agora - self.ultimo_salvamento) >= self.intervalo_salvamento:
                                    try:
                                        timestamp_str = self.ultimo_timestamp.strftime("%Y-%m-%d %H:%M:%S")
                                        db.inserir_medicao(self.id_missao, timestamp_str, temperatura, pressao)
                                        self.ultimo_salvamento = agora

                                        # Calcular minutos desde o início
                                        if self.ultimo_salvamento == agora and self.ultimo_salvamento is not None:
                                            minutos = 1
                                        else:
                                            minutos = int((agora - self.ultimo_salvamento) / 60) + 1

                                        print(f"[SENSOR BANCO] Medição salva no banco de dados")
                                    except Exception as e:
                                        print(f"[SENSOR ERRO] Falha ao salvar medição: {e}")

                except Exception as e:
                    print(f"[SENSOR ERRO] Erro na leitura: {e}")
                    time.sleep(1)

        except Exception as e:
            print(f"[SENSOR ERRO] Erro crítico: {e}")
        finally:
            self.lendo = False

    def _parsear_linha(self, linha):
        """
        Parseia linha do formato:
        | Tensão: 2.450 V | Pressao: 14.63 psi | Temperatura = 25.3
        """
        temperatura = None
        pressao = None
        tensao = None

        try:
            # Extrair tensão
            match_tensao = re.search(r'Tensão:\s*([\d.]+)\s*V', linha)
            if match_tensao:
                tensao = float(match_tensao.group(1))

            # Extrair pressão
            match_pressao = re.search(r'Pressao:\s*([\d.]+)\s*psi', linha)
            if match_pressao:
                pressao = float(match_pressao.group(1))

            # Extrair temperatura
            match_temp = re.search(r'Temperatura\s*=\s*([\d.]+)', linha)
            if match_temp:
                temperatura = float(match_temp.group(1))

        except Exception as e:
            print(f"[SENSOR ERRO] Erro ao parsear linha: {e}")

        return temperatura, pressao, tensao

    def get_ultima_leitura(self):
        """Retorna a última leitura dos sensores (thread-safe)"""
        with self.dados_lock:
            return {
                'temperatura': self.ultima_temperatura,
                'pressao': self.ultima_pressao,
                'tensao': self.ultima_tensao,
                'timestamp': self.ultimo_timestamp,
                'conectado': self.conectado,
                'lendo': self.lendo
            }

    def get_temperatura_formatada(self):
        """Retorna temperatura formatada para exibição"""
        with self.dados_lock:
            if self.ultima_temperatura is not None:
                return f"{self.ultima_temperatura:.1f}°C"
            return "N/A"

    def get_pressao_formatada(self):
        """Retorna pressão formatada para exibição"""
        with self.dados_lock:
            if self.ultima_pressao is not None:
                return f"{self.ultima_pressao:.2f} psi"
            return "N/A"


# Função de conveniência para obter a instância única
def get_sensor():
    """Retorna a instância única do sensor Arduino"""
    return SensorArduino()
