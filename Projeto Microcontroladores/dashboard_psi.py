import serial
import serial.tools.list_ports
import time
import sys

def encontrar_arduino():
    portas = serial.tools.list_ports.comports()
    for porta in portas:
        if 'Arduino' in porta.description or 'CH340' in porta.description:
            return porta.device
    return None

porta = encontrar_arduino()
if not porta:
    print("Arduino não encontrado!")
    sys.exit()

print(f"Conectando em {porta}...")
arduino = serial.Serial(porta, 9600, timeout=1)
time.sleep(3)
arduino.flushInput()
print("✓ Conectado!\n")

try:
    print("Recebendo dados do Arduino...\n")
    while True:
        if arduino.in_waiting > 0:
            try:
                line = arduino.readline().decode('utf-8').strip()
                
                if line:
                    dados = line.split(',')
                    print(dados)
                    
            except Exception as e:
                print(f"Erro ao ler dados: {e}")
                
except KeyboardInterrupt:
    print("\n\nEncerrando...")

finally:
    arduino.close()
    print("Conexão fechada.")