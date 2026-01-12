"""
Funções de exportação de relatórios para Excel e PDF.
"""

import io
from datetime import datetime
from typing import Optional
import pandas as pd

# Excel
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows

# PDF
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer


def export_to_excel(df: pd.DataFrame, title: str) -> Optional[bytes]:
    """
    Exporta DataFrame para arquivo Excel formatado.

    Args:
        df: DataFrame com os dados
        title: Título do relatório

    Returns:
        Bytes do arquivo Excel ou None em caso de erro
    """
    try:
        output = io.BytesIO()
        wb = Workbook()
        ws = wb.active
        ws.title = "Relatório"

        # Estilos
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
        header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell_alignment = Alignment(horizontal="left", vertical="center")
        thin_border = Border(
            left=Side(style="thin"),
            right=Side(style="thin"),
            top=Side(style="thin"),
            bottom=Side(style="thin"),
        )

        # Título
        ws.merge_cells("A1:H1")
        ws["A1"] = title
        ws["A1"].font = Font(bold=True, size=14)
        ws["A1"].alignment = Alignment(horizontal="center")

        # Data de geração
        ws.merge_cells("A2:H2")
        ws["A2"] = f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        ws["A2"].font = Font(italic=True, size=10)
        ws["A2"].alignment = Alignment(horizontal="center")

        # Espaço
        start_row = 4

        # Preparar DataFrame para exportação
        df_export = df.copy()

        # Converter colunas booleanas para texto
        bool_columns = df_export.select_dtypes(include=["bool"]).columns
        for col in bool_columns:
            df_export[col] = df_export[col].apply(lambda x: "Sim" if x else "Não")

        # Escrever dados
        for r_idx, row in enumerate(dataframe_to_rows(df_export, index=False, header=True)):
            for c_idx, value in enumerate(row, 1):
                cell = ws.cell(row=start_row + r_idx, column=c_idx, value=value)
                cell.border = thin_border

                if r_idx == 0:  # Header
                    cell.font = header_font
                    cell.fill = header_fill
                    cell.alignment = header_alignment
                else:
                    cell.alignment = cell_alignment

        # Ajustar largura das colunas
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width

        wb.save(output)
        return output.getvalue()

    except Exception as e:
        print(f"Erro ao exportar Excel: {e}")
        return None


def export_to_pdf(
    df: pd.DataFrame,
    title: str,
    year: int,
    month: Optional[int] = None,
) -> Optional[bytes]:
    """
    Exporta DataFrame para arquivo PDF formatado.

    Args:
        df: DataFrame com os dados
        title: Título do relatório
        year: Ano do relatório
        month: Mês do relatório (opcional)

    Returns:
        Bytes do arquivo PDF ou None em caso de erro
    """
    try:
        output = io.BytesIO()
        doc = SimpleDocTemplate(
            output,
            pagesize=landscape(A4),
            rightMargin=1 * cm,
            leftMargin=1 * cm,
            topMargin=1 * cm,
            bottomMargin=1 * cm,
        )

        elements = []
        styles = getSampleStyleSheet()

        # Título
        title_style = ParagraphStyle(
            "Title",
            parent=styles["Heading1"],
            fontSize=16,
            alignment=1,  # Center
            spaceAfter=12,
        )
        elements.append(Paragraph(title, title_style))

        # Período
        meses = [
            "", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
            "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
        ]
        periodo = f"{meses[month]} de {year}" if month else str(year)

        subtitle_style = ParagraphStyle(
            "Subtitle",
            parent=styles["Normal"],
            fontSize=10,
            alignment=1,
            spaceAfter=6,
        )
        elements.append(Paragraph(f"Período: {periodo}", subtitle_style))
        elements.append(
            Paragraph(
                f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
                subtitle_style,
            )
        )
        elements.append(Spacer(1, 20))

        # Preparar dados para tabela
        df_export = df.copy()

        # Converter colunas booleanas
        bool_columns = df_export.select_dtypes(include=["bool"]).columns
        for col in bool_columns:
            df_export[col] = df_export[col].apply(lambda x: "Sim" if x else "Não")

        # Selecionar colunas principais para PDF (evitar tabela muito larga)
        columns_to_export = []
        column_mapping = {
            "created_at": "Data",
            "usuario": "Usuário",
            "empresa": "Empresa",
            "bairro": "Bairro",
            "qtd_cto": "CTOs",
            "qtd_caixa_emenda": "Cx. Emenda",
            "fibra_lancada": "Fibra (m)",
            "equipe": "Equipe",
        }

        for col in df_export.columns:
            if col in column_mapping:
                columns_to_export.append(col)

        if columns_to_export:
            df_export = df_export[columns_to_export]
            df_export.columns = [column_mapping.get(c, c) for c in columns_to_export]

        # Criar dados da tabela
        table_data = [df_export.columns.tolist()]
        for _, row in df_export.iterrows():
            table_data.append([str(v)[:30] for v in row.values])  # Truncar valores longos

        # Criar tabela
        col_widths = [2.5 * cm] * len(df_export.columns)
        table = Table(table_data, colWidths=col_widths, repeatRows=1)

        # Estilo da tabela
        table.setStyle(
            TableStyle([
                # Header
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4472C4")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 8),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),
                # Body
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 7),
                ("ALIGN", (0, 1), (-1, -1), "LEFT"),
                ("VALIGN", (0, 1), (-1, -1), "MIDDLE"),
                # Grid
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                # Alternate row colors
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F2F2")]),
            ])
        )

        elements.append(table)

        # Resumo
        elements.append(Spacer(1, 20))
        summary_style = ParagraphStyle(
            "Summary",
            parent=styles["Normal"],
            fontSize=9,
            spaceAfter=6,
        )

        total_tarefas = len(df)
        elements.append(Paragraph(f"<b>Total de Tarefas:</b> {total_tarefas}", summary_style))

        if "qtd_cto" in df.columns:
            total_cto = df["qtd_cto"].sum()
            elements.append(Paragraph(f"<b>Total de CTOs:</b> {total_cto}", summary_style))

        if "qtd_caixa_emenda" in df.columns:
            total_ce = df["qtd_caixa_emenda"].sum()
            elements.append(Paragraph(f"<b>Total de Caixas de Emenda:</b> {total_ce}", summary_style))

        if "fibra_lancada" in df.columns:
            total_fibra = df["fibra_lancada"].sum()
            elements.append(Paragraph(f"<b>Total de Fibra Lançada:</b> {total_fibra:.2f} m", summary_style))

        doc.build(elements)
        return output.getvalue()

    except Exception as e:
        print(f"Erro ao exportar PDF: {e}")
        return None
