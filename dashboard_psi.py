import serial
import serial.tools.list_ports
import time
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets
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

app = QtWidgets.QApplication([])
win = pg.GraphicsLayoutWidget(show=True, title="Monitor de Pressão PSI")
win.resize(1200, 700)

plot = win.addPlot(title="Pressão em Tempo Real (PSI)")
plot.setLabel('left', 'Pressão', units='PSI', **{'font-size': '14pt'})
plot.setLabel('bottom', 'Tempo', units='s', **{'font-size': '14pt'})
plot.setYRange(-5, 35)
plot.setLimits(yMin=-5, yMax=35)
plot.showGrid(x=True, y=True, alpha=0.5)

linha_zero = pg.InfiniteLine(pos=0, angle=0, pen=pg.mkPen('g', width=2, style=pg.QtCore.Qt.DashLine))
plot.addItem(linha_zero)

curve = plot.plot(pen=pg.mkPen('b', width=3), symbol='o', symbolSize=8, symbolBrush='r')

texto_info = pg.TextItem(text='Aguardando...', color='white', 
                         fill=pg.mkBrush(50, 50, 200, 150), anchor=(0, 0))
plot.addItem(texto_info)
texto_info.setPos(5, 32)

x_data = []
y_data = []
start_time = time.time()
proximo_marco = 15

print("Recebendo dados...\n")

def update():
    global x_data, y_data, proximo_marco
    
    while arduino.in_waiting > 0:
        try:
            line = arduino.readline().decode('utf-8').strip()
            dados = line.split(',')
            
            if len(dados) == 3:
                psi = float(dados[2])
                t = time.time() - start_time
                
                x_data.append(t)
                y_data.append(psi)
                
                curve.setData(x_data, y_data)
                
                if len(x_data) > 1:
                    plot.setXRange(max(0, x_data[-1] - 60), x_data[-1] + 5)
                
                texto = f'Pressão: {psi:.2f} PSI\nTempo: {t:.1f}s\nPontos: {len(x_data)}'
                texto_info.setText(texto)
                
                if len(x_data) > 200:
                    x_data.pop(0)
                    y_data.pop(0)
                
                if t >= proximo_marco:
                    print(f"\n{proximo_marco}s | Pressão: {psi:.2f} PSI | Pontos: {len(x_data)}")
                    proximo_marco += 15
                else:
                    print(f"T: {t:6.1f}s | P: {psi:7.2f} PSI", end='\r')
                
        except:
            pass

timer = pg.QtCore.QTimer()
timer.timeout.connect(update)
timer.start(50)

QtWidgets.QApplication.instance().exec_()
arduino.close()