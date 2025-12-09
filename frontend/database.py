"""
Módulo de gerenciamento do banco de dados SQLite
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = 'mergulho.db'


def conectar():
    """Cria conexão com o banco de dados"""
    return sqlite3.connect(DB_PATH)


def inicializar_banco():
    """Cria as tabelas do banco de dados se não existirem"""
    conn = conectar()
    cursor = conn.cursor()

    # Tabela MERGULHADOR
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mergulhador (
            id_mergulhador INTEGER PRIMARY KEY AUTOINCREMENT,
            nome VARCHAR(100) NOT NULL,
            idade INTEGER NOT NULL,
            sexo CHAR(1) NOT NULL
        )
    ''')

    # Tabela MISSAO
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS missao (
            id_missao INTEGER PRIMARY KEY AUTOINCREMENT,
            identificador VARCHAR(50) UNIQUE NOT NULL,
            id_mergulhador INTEGER NOT NULL,
            nome_missao VARCHAR(100) NOT NULL,
            data_hora_inicio DATETIME NOT NULL,
            data_hora_fim DATETIME,
            FOREIGN KEY (id_mergulhador) REFERENCES mergulhador(id_mergulhador)
        )
    ''')

    # Tabela MEDICAO
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS medicao (
            id_medicao INTEGER PRIMARY KEY AUTOINCREMENT,
            id_missao INTEGER NOT NULL,
            timestamp DATETIME NOT NULL,
            temperatura FLOAT NOT NULL,
            pressao FLOAT NOT NULL,
            FOREIGN KEY (id_missao) REFERENCES missao(id_missao) ON DELETE CASCADE
        )
    ''')

    # Tabela VIDEO
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS video (
            id_video INTEGER PRIMARY KEY AUTOINCREMENT,
            id_missao INTEGER NOT NULL,
            caminho VARCHAR(255) NOT NULL,
            FOREIGN KEY (id_missao) REFERENCES missao(id_missao) ON DELETE CASCADE
        )
    ''')

    # Tabela AUDIO
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audio (
            id_audio INTEGER PRIMARY KEY AUTOINCREMENT,
            id_missao INTEGER NOT NULL,
            caminho VARCHAR(255) NOT NULL,
            FOREIGN KEY (id_missao) REFERENCES missao(id_missao) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()


# ==================== MERGULHADOR ====================

def inserir_mergulhador(nome, idade, sexo):
    """Insere um novo mergulhador no banco"""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO mergulhador (nome, idade, sexo)
        VALUES (?, ?, ?)
    ''', (nome, idade, sexo))
    conn.commit()
    id_mergulhador = cursor.lastrowid
    conn.close()
    return id_mergulhador


def listar_mergulhadores():
    """Retorna todos os mergulhadores"""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM mergulhador ORDER BY nome')
    mergulhadores = cursor.fetchall()
    conn.close()
    return mergulhadores


def buscar_mergulhador(id_mergulhador):
    """Busca um mergulhador pelo ID"""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM mergulhador WHERE id_mergulhador = ?', (id_mergulhador,))
    mergulhador = cursor.fetchone()
    conn.close()
    return mergulhador


# ==================== MISSAO ====================

def inserir_missao(id_mergulhador, nome_missao, data_hora_inicio, identificador, data_hora_fim=None):
    """Insere uma nova missão no banco"""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO missao (id_mergulhador, nome_missao, data_hora_inicio, identificador, data_hora_fim)
        VALUES (?, ?, ?, ?, ?)
    ''', (id_mergulhador, nome_missao, data_hora_inicio, identificador, data_hora_fim))
    conn.commit()
    id_missao = cursor.lastrowid
    conn.close()
    return id_missao


def atualizar_fim_missao(id_missao, data_hora_fim):
    """Atualiza a data/hora de fim de uma missão"""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE missao SET data_hora_fim = ? WHERE id_missao = ?
    ''', (data_hora_fim, id_missao))
    conn.commit()
    conn.close()


def listar_missoes():
    """Retorna todas as missões com informações do mergulhador"""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT
            m.id_missao,
            m.identificador,
            m.nome_missao,
            m.data_hora_inicio,
            m.data_hora_fim,
            mg.nome,
            mg.idade,
            mg.sexo
        FROM missao m
        JOIN mergulhador mg ON m.id_mergulhador = mg.id_mergulhador
        ORDER BY m.data_hora_inicio DESC
    ''')
    missoes = cursor.fetchall()
    conn.close()
    return missoes


def buscar_missao(id_missao):
    """Busca uma missão específica pelo ID"""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT
            m.id_missao,
            m.identificador,
            m.id_mergulhador,
            m.nome_missao,
            m.data_hora_inicio,
            m.data_hora_fim,
            mg.nome,
            mg.idade,
            mg.sexo
        FROM missao m
        JOIN mergulhador mg ON m.id_mergulhador = mg.id_mergulhador
        WHERE m.id_missao = ?
    ''', (id_missao,))
    missao = cursor.fetchone()
    conn.close()
    return missao


# ==================== MEDICAO ====================

def inserir_medicao(id_missao, timestamp, temperatura, pressao):
    """Insere uma medição de sensor"""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO medicao (id_missao, timestamp, temperatura, pressao)
        VALUES (?, ?, ?, ?)
    ''', (id_missao, timestamp, temperatura, pressao))
    conn.commit()
    id_medicao = cursor.lastrowid
    conn.close()
    return id_medicao


def listar_medicoes_por_missao(id_missao):
    """Retorna todas as medições de uma missão"""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM medicao
        WHERE id_missao = ?
        ORDER BY timestamp
    ''', (id_missao,))
    medicoes = cursor.fetchall()
    conn.close()
    return medicoes


def get_estatisticas_medicoes(id_missao):
    """Retorna estatísticas das medições de uma missão"""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT
            COUNT(*) as total,
            MIN(temperatura) as temp_min,
            MAX(temperatura) as temp_max,
            AVG(temperatura) as temp_media,
            MIN(pressao) as press_min,
            MAX(pressao) as press_max,
            AVG(pressao) as press_media
        FROM medicao
        WHERE id_missao = ?
    ''', (id_missao,))
    stats = cursor.fetchone()
    conn.close()
    return stats


# ==================== VIDEO ====================

def inserir_video(id_missao, caminho):
    """Insere um caminho de vídeo"""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO video (id_missao, caminho)
        VALUES (?, ?)
    ''', (id_missao, caminho))
    conn.commit()
    id_video = cursor.lastrowid
    conn.close()
    return id_video


def listar_videos_por_missao(id_missao):
    """Retorna todos os vídeos de uma missão"""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM video WHERE id_missao = ?', (id_missao,))
    videos = cursor.fetchall()
    conn.close()
    return videos


# ==================== AUDIO ====================

def inserir_audio(id_missao, caminho):
    """Insere um caminho de áudio"""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO audio (id_missao, caminho)
        VALUES (?, ?)
    ''', (id_missao, caminho))
    conn.commit()
    id_audio = cursor.lastrowid
    conn.close()
    return id_audio


def listar_audios_por_missao(id_missao):
    """Retorna todos os áudios de uma missão"""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM audio WHERE id_missao = ?', (id_missao,))
    audios = cursor.fetchall()
    conn.close()
    return audios


# ==================== UTILIDADES ====================

def deletar_missao(id_missao):
    """Deleta uma missão e todos os dados relacionados"""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM missao WHERE id_missao = ?', (id_missao,))
    conn.commit()
    conn.close()


def contar_missoes():
    """Conta o total de missões no banco"""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM missao')
    total = cursor.fetchone()[0]
    conn.close()
    return total


def contar_mergulhadores():
    """Conta o total de mergulhadores no banco"""
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM mergulhador')
    total = cursor.fetchone()[0]
    conn.close()
    return total
