# Sistema de Monitoramento de Mergulhos

## Descrição do Projeto

Sistema integrado para monitoramento de missões de mergulho que combina sensores físicos (Arduino) com gravação multimídia sincronizada. O projeto permite o acompanhamento em tempo real de temperatura e pressão durante mergulhos, além de gravar vídeo e áudio para análise posterior.

**Recursos Principais:**
- Monitoramento em tempo real de temperatura e pressão
- Gravação automática de vídeo e áudio em segmentos de 5 minutos
- Cadastro e gerenciamento de mergulhadores
- Armazenamento em banco de dados SQLite
- Interface gráfica (Tkinter)
- Reprodução sincronizada de missões gravadas
- Estatísticas de medições (mín/máx/média)

---

##  Arquitetura do Sistema

O sistema é dividido em 4 camadas principais:

### 1. **Hardware (Arduino)**
- **Sensores:** DS18B20 (temperatura) e sensor analógico de pressão
- **Comunicação:** Serial USB (9600 baud)
- **Formato de dados:** `pressao,temperatura\n` (CSV via serial)
- **Código:** [sensor_e_temperatura/sensor_e_temperatura.ino](sensor_e_temperatura/sensor_e_temperatura.ino)

### 2. **Servidor Python**
- **Comunicação Serial:** Leitura contínua dos dados do Arduino ([sensor_arduino.py](servidor/sensor_arduino.py))
- **Banco de Dados:** SQLite para armazenamento persistente ([database.py](servidor/database.py))
- **Gerenciamento:** Controle de missões, mergulhadores e medições

### 3. **Interface Gráfica (GUI)**
- **Framework:** Tkinter
- **Funcionalidades:**
  - Criar e iniciar missões ([criar_missao.py](interface/criar_missao.py))
  - Visualizar missões antigas ([visualizar_missoes.py](interface/visualizar_missoes.py))
  - Monitoramento ao vivo

### 4. **Captura Multimídia**
- **Vídeo:** OpenCV - segmentos de 5 min ([gravacao_video.py](captura/gravacao_video.py))
- **Áudio:** PyAudio - segmentos de 5 min ([gravacao_audio.py](captura/gravacao_audio.py))
- **Sincronização:** Timestamp comum entre vídeo, áudio e sensores

### Fluxo de Dados

```
┌─────────────────────────┐
│  Arduino (Sensores)     │
│  - DS18B20 (Temp)       │
│  - Sensor de Pressão    │
└───────────┬─────────────┘
            │ Serial USB (9600 baud)
            │ Formato: pressao,temperatura
            ▼
┌─────────────────────────┐
│  Servidor Python        │
│  - sensor_arduino.py    │
│  - database.py          │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Interface Gráfica      │
│  - main.py              │
│  - criar_missao.py      │
│  - visualizar_missoes.py│
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Captura Multimídia     │
│  - gravacao_video.py    │
│  - gravacao_audio.py    │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Armazenamento          │
│  - SQLite (mergulho.db) │
│  - Vídeos (*.avi)       │
│  - Áudios (*.wav)       │
└─────────────────────────┘
```

---

##  Estrutura de Pastas

```
projeto-micro-main/
├── main.py                        # Arquivo principal - inicializa o sistema
├── README.md                      # Este arquivo
├── .gitignore                     # Arquivos ignorados pelo git
│
├── sensor_e_temperatura/          # Código Arduino
│   └── sensor_e_temperatura.ino   # Leitura de sensores (temp + pressão)
│
├── servidor/                      # Backend e lógica de negócio
│   ├── database.py                # Gerenciamento do banco SQLite
│   ├── sensor_arduino.py          # Comunicação serial com Arduino
│   └── mergulho.db                # Banco de dados (gerado automaticamente)
│
├── interface/                     # Interface gráfica (Tkinter)
│   ├── criar_missao.py            # Tela de criação de missões
│   └── visualizar_missoes.py      # Tela de visualização de missões
│
├── captura/                       # Módulos de gravação
│   ├── gravacao_video.py          # Captura de vídeo com OpenCV
│   └── gravacao_audio.py          # Captura de áudio com PyAudio
│
├── gravacoes/                     # Dados gerados pelo sistema
│   ├── audios_missoes/            # Áudios das missões (*.wav)
│   └── videos_missoes/            # Vídeos das missões (*.avi)
```

##  Tecnologias Utilizadas

### **Software**
- **Python 3.8+** - Linguagem principal
- **Tkinter** - Interface gráfica
- **SQLite** - Banco de dados
- **OpenCV** - Captura de vídeo
- **PyAudio** - Captura de áudio
- **PySerial** - Comunicação serial

### **Hardware**
- **Arduino** - Microcontrolador
- **DS18B20** - Sensor de temperatura
- **Sensor analógico** - Medição de pressão
- **OneWire / DallasTemperature** - Bibliotecas Arduino


##  Demonstração em vídeo

[![Demonstração do projeto](https://img.youtube.com/vi/X3-hCFhAKb0/0.jpg)](https://www.youtube.com/watch?v=X3-hCFhAKb0)

Clique na imagem para assistir ao vídeo no YouTube.

