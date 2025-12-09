"""
Script para gerar PDF com diagrama do banco de dados do projeto de mergulho
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from datetime import datetime

def criar_pdf_diagrama():
    # Configuração do documento
    pdf_file = "Diagrama_Banco_Dados_Mergulho.pdf"
    doc = SimpleDocTemplate(pdf_file, pagesize=A4,
                           rightMargin=2*cm, leftMargin=2*cm,
                           topMargin=2*cm, bottomMargin=2*cm)

    # Container para elementos do PDF
    elements = []

    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a5490'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#2c5aa0'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )

    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=13,
        textColor=colors.HexColor('#404040'),
        spaceAfter=10,
        fontName='Helvetica-Bold'
    )

    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_JUSTIFY,
        spaceAfter=6
    )

    # Título
    elements.append(Paragraph("SISTEMA DE MONITORAMENTO DE MERGULHOS", title_style))
    elements.append(Paragraph("Diagrama de Banco de Dados", styles['Heading2']))
    elements.append(Spacer(1, 0.5*cm))


    # Diagrama de Entidades
    elements.append(Paragraph("2. ESTRUTURA DAS TABELAS", heading_style))
    elements.append(Spacer(1, 0.3*cm))

    # Tabela MERGULHADOR
    elements.append(Paragraph("2.1. Tabela: MERGULHADOR", subheading_style))
    data_mergulhador = [
        ['Campo', 'Tipo', 'Descrição'],
        ['id_mergulhador', 'INTEGER (PK)', 'Identificador único do mergulhador'],
        ['nome', 'VARCHAR(100)', 'Nome completo do mergulhador'],
        ['idade', 'INTEGER', 'Idade do mergulhador'],
        ['sexo', 'CHAR(1)', 'Sexo (M/F/O)']
    ]

    table_mergulhador = Table(data_mergulhador, colWidths=[4*cm, 4*cm, 8*cm])
    table_mergulhador.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5490')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))
    elements.append(table_mergulhador)
    elements.append(Spacer(1, 0.5*cm))

    # Tabela MISSAO
    elements.append(Paragraph("2.2. Tabela: MISSAO", subheading_style))
    data_missao = [
        ['Campo', 'Tipo', 'Descrição'],
        ['id_missao', 'INTEGER (PK)', 'Identificador único da missão'],
        ['id_mergulhador', 'INTEGER (FK)', 'Referência ao mergulhador'],
        ['responsavel', 'VARCHAR(100)', 'Nome do responsável pela missão'],
        ['data_hora_inicio', 'DATETIME', 'Data e hora de início do mergulho'],
        ['data_hora_fim', 'DATETIME', 'Data e hora de término do mergulho']
    ]

    table_missao = Table(data_missao, colWidths=[4*cm, 4*cm, 8*cm])
    table_missao.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5490')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))
    elements.append(table_missao)
    elements.append(Spacer(1, 0.5*cm))

    # Tabela MEDICAO
    elements.append(Paragraph("2.3. Tabela: MEDICAO", subheading_style))
    data_medicao = [
        ['Campo', 'Tipo', 'Descrição'],
        ['id_medicao', 'INTEGER (PK)', 'Identificador único da medição'],
        ['id_missao', 'INTEGER (FK)', 'Referência à missão'],
        ['timestamp', 'DATETIME', 'Momento da leitura do sensor'],
        ['temperatura', 'FLOAT', 'Temperatura medida (°C)'],
        ['pressao', 'FLOAT', 'Pressão medida (bar ou atm)']
    ]

    table_medicao = Table(data_medicao, colWidths=[4*cm, 4*cm, 8*cm])
    table_medicao.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5490')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))
    elements.append(table_medicao)
    elements.append(Spacer(1, 0.5*cm))

    # Tabela VIDEO
    elements.append(Paragraph("2.4. Tabela: VIDEO", subheading_style))
    data_video = [
        ['Campo', 'Tipo', 'Descrição'],
        ['id_video', 'INTEGER (PK)', 'Identificador único do vídeo'],
        ['id_missao', 'INTEGER (FK)', 'Referência à missão'],
        ['caminho', 'VARCHAR(255)', 'Caminho do arquivo de vídeo']
    ]

    table_video = Table(data_video, colWidths=[4*cm, 4*cm, 8*cm])
    table_video.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5490')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))
    elements.append(table_video)
    elements.append(Spacer(1, 0.5*cm))

    # Tabela AUDIO
    elements.append(Paragraph("2.5. Tabela: AUDIO", subheading_style))
    data_audio = [
        ['Campo', 'Tipo', 'Descrição'],
        ['id_audio', 'INTEGER (PK)', 'Identificador único do áudio'],
        ['id_missao', 'INTEGER (FK)', 'Referência à missão'],
        ['caminho', 'VARCHAR(255)', 'Caminho do arquivo de áudio']
    ]

    table_audio = Table(data_audio, colWidths=[4*cm, 4*cm, 8*cm])
    table_audio.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a5490')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))
    elements.append(table_audio)
    elements.append(Spacer(1, 1*cm))

    # Relacionamentos
    elements.append(Paragraph("3. RELACIONAMENTOS ENTRE TABELAS", heading_style))
    elements.append(Spacer(1, 0.3*cm))

    relacionamentos = [
        ['Relacionamento', 'Cardinalidade', 'Descrição'],
        ['MERGULHADOR → MISSAO', '1:N', 'Um mergulhador pode participar de várias missões'],
        ['MISSAO → MEDICAO', '1:N', 'Uma missão registra várias medições ao longo do tempo'],
        ['MISSAO → VIDEO', '1:N', 'Uma missão pode ter vários arquivos de vídeo'],
        ['MISSAO → AUDIO', '1:N', 'Uma missão pode ter vários arquivos de áudio']
    ]

    table_relacionamentos = Table(relacionamentos, colWidths=[5*cm, 3*cm, 8*cm])
    table_relacionamentos.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5aa0')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.lightblue, colors.white])
    ]))
    elements.append(table_relacionamentos)
    elements.append(Spacer(1, 1*cm))


    # Gerar PDF
    doc.build(elements)
    print(f"PDF gerado com sucesso: {pdf_file}")
    return pdf_file

if __name__ == "__main__":
    try:
        pdf_gerado = criar_pdf_diagrama()
        print(f"\n✓ Arquivo criado: {pdf_gerado}")
    except Exception as e:
        print(f"Erro ao gerar PDF: {e}")
        import traceback
        traceback.print_exc()
