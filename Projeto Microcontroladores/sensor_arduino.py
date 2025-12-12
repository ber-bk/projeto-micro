"""
Módulo para leitura de dados do Arduino (temperatura e pressão)
Versão simplificada com leitura direta CSV
"""

import serial
import serial.tools.list_ports
import threading
import time
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
        self.ultimo_timestamp = None

        # Dados da missão
        self.id_missao = None

        # Controle de salvamento no banco (1 vez por minuto)
        self.ultimo_salvamento = None
        self.intervalo_salvamento = 60  # 60 segundos = 1 minuto

        # Lock para acesso thread-safe
        self.dados_lock = threading.Lock()

    def encontrar_arduino(self):
        """Encontra automaticamente a porta do Arduino"""
        portas = serial.tools.list_ports.comports()
        for porta in portas:
            if 'Arduino' in porta.description or 'CH340' in porta.description:
                return porta.device
        return None

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
            porta = self.encontrar_arduino()
            if porta is None:
                print("[SENSOR ERRO] Arduino não encontrado!")
                return False
            print(f"[SENSOR] Arduino encontrado em: {porta}")

        try:
            self.porta_serial = serial.Serial(porta, baudrate, timeout=1)
            time.sleep(3)  # Aguardar Arduino resetar
            self.porta_serial.flushInput()
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
        """Thread que lê dados continuamente do Arduino no formato CSV"""
        try:
            while not self.parar_flag and self.porta_serial.is_open:
                try:
                    if self.porta_serial.in_waiting > 0:
                        # Ler linha da serial
                        linha = self.porta_serial.readline().decode('utf-8', errors='ignore').strip()

                        if linha:
                            # Parsear dados no formato CSV: pressao,temperatura
                            dados = linha.split(',')

                            if len(dados) >= 2:
                                try:
                                    pressao = float(dados[0])
                                    temperatura = float(dados[1])

                                    # Atualizar dados
                                    with self.dados_lock:
                                        self.ultima_temperatura = temperatura
                                        self.ultima_pressao = pressao
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
                                                print(f"[SENSOR BANCO] Medição salva no banco de dados")
                                            except Exception as e:
                                                print(f"[SENSOR ERRO] Falha ao salvar medição: {e}")

                                except ValueError as e:
                                    print(f"[SENSOR ERRO] Dados inválidos: {linha}")

                except Exception as e:
                    print(f"[SENSOR ERRO] Erro na leitura: {e}")
                    time.sleep(1)

        except Exception as e:
            print(f"[SENSOR ERRO] Erro crítico: {e}")
        finally:
            self.lendo = False

    def get_ultima_leitura(self):
        """Retorna a última leitura dos sensores (thread-safe)"""
        with self.dados_lock:
            return {
                'temperatura': self.ultima_temperatura,
                'pressao': self.ultima_pressao,
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

    def get_temperatura_valor(self):
        """Retorna apenas o valor numérico da temperatura"""
        with self.dados_lock:
            if self.ultima_temperatura is not None:
                return f"{self.ultima_temperatura:.1f}"
            return "N/A"

    def get_pressao_valor(self):
        """Retorna apenas o valor numérico da pressão"""
        with self.dados_lock:
            if self.ultima_pressao is not None:
                return f"{self.ultima_pressao:.2f}"
            return "N/A"


# Função de conveniência para obter a instância única
def get_sensor():
    """Retorna a instância única do sensor Arduino"""
    return SensorArduino()
