# Projeto de Telemetria – Capacete de Mergulho
PUC — Microcontroladores / Sistemas Embarcados

Este projeto consiste no desenvolvimento de um capacete de mergulho com telemetria integrada, contendo:

- Vídeo ao vivo  
- Áudio bidirecional  
- Sensores biométricos e ambientais  
- Dashboard em Python  
- Registro completo do mergulho (vídeo, áudio e dados)

Os dados são enviados via cabo umbilical USB para um computador, onde são exibidos e gravados.

# Objetivo Geral

Criar um sistema capaz de:

- Receber vídeo, áudio e sensores em tempo real  
- Exibir tudo em uma dashboard Python  
- Gravar automaticamente vídeo (.avi), áudio (.wav) e dados dos sensores  
- Agrupar tudo em um banco de dados  
- Permitir expansão de sensores sem refazer a arquitetura

# Arquitetura do Sistema

## Estrutura Física do Capacete

- Capacete: bolha rígida translúcida  
- Dimensões: 30 cm de raio (60 cm de diâmetro)  
- Caixa eletrônica: 20 × 20 × 10 cm

### Microcontrolador
- ESP32  
- Comunicação via cabo umbilical USB (serial)

### Sensores

| Sensor | Status | Observação |
|--------|--------|-------------|
| Pressão | Implementado (MVP) | Atualização lenta |
| Temperatura | Implementado (MVP) | Baixa variação |
| Batimentos cardíacos | Futuro | |
| Oximetria SpO₂ | Futuro | |

# Módulo de Vídeo

Localização: `src/camera/camera_recorder.py`

Funcionalidades:

- Captura via OpenCV  
- Gravação segmentada automática  
- Geração de arquivos `.avi`  
- Testes automatizados usando mocks (sem webcam real)

# Módulo de Áudio

Localização: `src/audio/AudioRecorder.py`

Funcionalidades:

- Captação com sounddevice  
- Escrita com soundfile  
- Segmentação de arquivos `.wav`  
- Uso de queue interna para evitar perdas  
- Testes automatizados usando mocks (sem microfone real)

# Módulo TelemetryRecorder

Localização: `src/telemetry/telemetry_recorder.py`

O TelemetryRecorder coordena:

- Vídeo  
- Áudio  
- Sensores (expansível)

Exemplo simplificado:

```
class TelemetryRecorder:
    def __init__(self):
        self.camera = CameraRecorder()
        self.audio = AudioRecorder()
        self.sensors = []

    def start_all(self):
        ...
    def stop_all(self):
        ...
```

Sensores adicionais podem ser incluídos futuramente:

```
self.sensors.append(PressureSensorRecorder())
```

# Testes Automatizados

Localização: `src/tests/test_system.py`

Testes atuais:

- Segmentação de vídeo  
- Falha ao abrir câmera  
- Múltiplos segmentos  
- Testes de performance  
- Segmentação de áudio  
- Fila vazia de áudio  
- Início e parada do sistema completo  
- Integração básica  
- Testes sem hardware real (Mock)

Rodar testes:

```
pytest -v
```

Resultado atual: 100% dos testes passam.

# Estrutura Atual do Repositório

```
ProjetoMicroTelemetriaCapacete/
│
├── src/
│   ├── camera/
│   │   └── camera_recorder.py
│   ├── audio/
│   │   └── AudioRecorder.py
│   ├── telemetry/
│   │   └── telemetry_recorder.py
│   └── tests/
│       └── test_system.py
│
├── videos/
├── audio/
├── requirements.txt
└── README.md
```

# Dependências

Principais bibliotecas:

- OpenCV  
- sounddevice  
- soundfile  
- numpy  
- pytest e pytest-mock  

Instalação:

```
pip install -r requirements.txt
```

No Windows, também é necessário:

```
choco install libsndfile -y
```

# Dashboard (Próximas Etapas)

A dashboard exibirá:

- Vídeo em tempo real  
- Áudio  
- Telemetria (pressão, temperatura, etc.)  
- Gráficos em tempo real  
- Estado geral do mergulho  
- Exportação para banco de dados

Frameworks sugeridos:

- Tkinter  
- PyQt  
- Dash  
- DearPyGui  

# Roadmap

1. Comunicação serial com ESP32  
2. Implementação dos módulos de sensores  
3. Dashboard Python completa  
4. Banco de dados SQLite  
5. Integração total (vídeo + áudio + sensores)

# Conclusão

O projeto já possui:

- Captura de vídeo  
- Captura de áudio  
- TelemetryRecorder funcional  
- 10 testes automatizados  
- Arquitetura modular e robusta  

Pronto para evolução em direção à integração completa e dashboard final.
