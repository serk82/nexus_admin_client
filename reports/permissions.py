import os, platform, sys
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)
from reportlab.lib.units import cm
from reportlab.lib import colors
import subprocess


def generate_pdf(filename: str, permissions: dict):
    tmp_dir = str(Path(sys.argv[0]).resolve().parent / "tmp" / filename)
    doc = SimpleDocTemplate(
        tmp_dir,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2.5 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    elements = []

    # Título
    title_style = ParagraphStyle(
        name="Title",
        parent=styles["Heading1"],
        fontSize=18,
        alignment=TA_CENTER,
        spaceAfter=20,
        textColor=colors.HexColor("#1E88E5"),
    )
    elements.append(Paragraph("PERMISOS DE USUARIOS", title_style))

    # Separador
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
    elements.append(Spacer(1, 50))

    # Tabla de materiales
    table_data = [
        ['ID", "Permiso'],
    ]
    table_data.extend(
        [
            [str(permission.get("code")), permission.get("name")]
            for permission in permissions
        ]
    )

    table_style = TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E0E0E0")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ]
    )

    table = Table(table_data, colWidths=[3 * cm, 10 * cm])
    table.setStyle(table_style)
    elements.append(table)

    elements.append(Spacer(1, 50))

    # Pie de página
    footer_style = ParagraphStyle(
        name="Footer",
        fontSize=9,
        alignment=TA_RIGHT,
        textColor=colors.HexColor("#777777"),
    )
    elements.append(Paragraph("© 2025 Nexus Admin", footer_style))

    # Crear PDF
    doc.build(elements)

    # Abrir el PDF generado
    if platform.system() == "Windows":
        os.startfile(filename)
    else:  # Linux
        subprocess.Popen(["evince", tmp_dir])
