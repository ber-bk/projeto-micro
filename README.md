Projeto de Telemetria – Capacete de Mergulho

Este projeto consiste no desenvolvimento de um capacete de mergulho com telemetria, contendo câmera, comunicação de voz e sensores biométricos/ambientais.
A leitura dos dados será transmitida via cabo umbilical para um computador, onde uma dashboard exibirá informações em tempo real e também fará gravações para análise posterior.

Objetivo Geral

Criar um sistema integrado que:

Recebe vídeo, áudio e dados de sensores em tempo real

Exibe todas as informações em uma dashboard Python

Grava vídeo, áudio e telemetria por mergulho

Permite exportar os dados (banco de dados + arquivos .avi)

Estrutura do Capacete

Parte física:

Bola de plástico rígido e translúcido

30 cm de raio (60 cm de diâmetro)

Caixa plástica para a eletrônica: 20 × 20 × 10 cm

Eletrônica interna/externa:

Microcontrolador: ESP32

Sensores conectados por protoboard

Comunicação com o PC via cabo umbilical USB

MVP (Mínimo Produto Viável)
Interno ao capacete

Fone com microfone

Externo

Câmera USB

Sensor de pressão

Sensores desejados (futuras versões)

Sensor de batimentos

Sensor de temperatura corporal

Sensor de oximetria (SpO₂)

Dashboard do Sistema (Python)

A interface exibirá e registrará:

Feed da câmera USB

Captura ao vivo usando OpenCV

Gravação automática em formato .avi

Comunicação de áudio

Captura do microfone interno

Transmissão para o computador via cabo umbilical

HUD de telemetria

Pressão

Temperatura

Demais sensores planejados

Observação: sensores de baixa variação (como pressão e temperatura) poderão enviar apenas uma atualização por minuto.

Sistema de logs por mergulho

Arquivo de vídeo

Áudio (se implementado)

Dados dos sensores

Possibilidade de salvar tudo em um banco de dados

Estrutura atual do repositório
projeto-micro/
│
├── src/
│   └── video_capture.py       # Captura e gravação da câmera USB
│
├── videos/                    # Gravações .avi (opcional versionamento)
├── requirements.txt           # Dependências do Python
└── README.md

Próximas etapas

Implementar comunicação serial com o ESP32

Desenvolver módulo dos sensores (pressão, temperatura, batimento, SpO₂)

Implementar dashboard em Python (Tkinter, PyQt ou interface web)

Registrar e exportar dados para banco de dados

Integrar vídeo, áudio e sensores em uma única aplicação
