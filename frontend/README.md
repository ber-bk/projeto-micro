# Sistema de Monitoramento de Mergulhos

Sistema desenvolvido para a disciplina de Microcontroladores, permitindo o gerenciamento completo de missões de mergulho com registro de dados de sensores e arquivos multimídia.

## Funcionalidades

### Tela Principal
- **Criar Nova Missão**: Cadastra uma nova missão de mergulho
- **Visualizar Missões**: Consulta e gerencia missões existentes

### Criar Nova Missão
- Cadastro de mergulhadores (nome, idade, sexo)
- Seleção de mergulhador existente
- Registro de responsável pela missão
- Definição de data/hora de início
- Adição de arquivos de vídeo
- Adição de arquivos de áudio

### Visualizar Missões
- Listagem de todas as missões cadastradas
- Visualização detalhada de cada missão
- Adição de medições de sensores (temperatura e pressão em psi)
- Finalização de missões (registro de data/hora de término)
- Estatísticas de medições (mínimo, máximo e média)

## Estrutura do Banco de Dados

O sistema utiliza SQLite com as seguintes tabelas:

### MERGULHADOR
- id_mergulhador (PK)
- nome
- idade
- sexo

### MISSAO
- id_missao (PK)
- identificador (UNIQUE) - Formato: Missao_DD-MM-AA_HH:MM
- id_mergulhador (FK)
- nome_missao - Nome/título da missão
- data_hora_inicio
- data_hora_fim

### MEDICAO
- id_medicao (PK)
- id_missao (FK)
- timestamp
- temperatura (°C)
- pressao (psi)

### VIDEO
- id_video (PK)
- id_missao (FK)
- caminho

### AUDIO
- id_audio (PK)
- id_missao (FK)
- caminho

## Arquivos do Projeto

```
Projeto Microcontroladores/
├── main.py                      # Arquivo principal (tela inicial)
├── database.py                  # Gerenciamento do banco de dados SQLite
├── criar_missao.py              # Interface para criar missões
├── visualizar_missoes.py        # Interface para visualizar missões
├── mergulho.db                  # Banco de dados SQLite (criado automaticamente)
└── README.md                    # Este arquivo
```

## Requisitos

### Python 3.x

### Bibliotecas utilizadas:
- tkinter (interface gráfica - padrão do Python)
- sqlite3 (banco de dados - padrão do Python)
- datetime (padrão do Python)

## Como Executar

1. Certifique-se de ter o Python 3.x instalado
2. Execute o programa principal:
   ```bash
   python main.py
   ```

## Fluxo de Uso Recomendado

1. **Criar uma missão**:
   - Clique em "Criar Nova Missão"
   - Cadastre ou selecione um mergulhador
   - Preencha o nome da missão e data/hora de início
   - Clique em "Criar Missão"

2. **Registrar medições durante o mergulho**:
   - Clique em "Visualizar Missões"
   - Selecione a missão
   - Clique em "Adicionar Medições"
   - Insira temperatura (°C) e pressão (psi)
   - Repita conforme necessário

3. **Finalizar a missão**:
   - Na tela de visualização
   - Selecione a missão
   - Clique em "Finalizar Missão"

4. **Visualizar detalhes e estatísticas**:
   - Na tela "Visualizar Missões"
   - Selecione a missão desejada
   - Clique em "Ver Detalhes"
   - Visualize todas as medições e estatísticas (min/max/média)

## Observações

- O banco de dados é criado automaticamente na primeira execução
- Cada missão possui um identificador único no formato `Missao_DD-MM-AA_HH:MM`
- Os caminhos dos arquivos de vídeo/áudio são armazenados, não os arquivos em si
- As medições podem ser adicionadas a qualquer momento, mesmo após finalizar a missão
- A tela de detalhes exibe estatísticas automáticas (mínimo, máximo e média) de temperatura e pressão
- A pressão é medida em psi (pounds per square inch)

## Desenvolvimento

Projeto desenvolvido para a disciplina de Microcontroladores - 2025

### Possíveis Melhorias Futuras
- Integração direta com microcontrolador para leitura automática de sensores
- Gráficos de temperatura e pressão ao longo do tempo
- Exportação de dados em outros formatos (CSV, Excel)
- Sistema de backup automático do banco de dados
- Validação de faixas aceitáveis para temperatura e pressão
- Upload automático de vídeos/áudios para armazenamento
