from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import io

# ==========================================
#  THEME CONFIGURATION (Matches style.css)
# ==========================================
THEME = {
    "primary":    "#6366f1",  # Indigo 500
    "secondary":  "#ec4899",  # Pink 500
    "background": "#f8fafc",  # Slate 50
    "card_bg":    "#ffffff",  # White
    "text_main":  "#1e293b",  # Slate 800
    "text_muted": "#64748b",  # Slate 500
    "border":     "#e2e8f0",  # Slate 200
    "success":    "#10b981",
    "warning":    "#f59e0b",
    "error":      "#ef4444",
}

def create_stylesheet():
    styles = getSampleStyleSheet()
    
    # --- Custom Classes matching HTML ---
    
    # Section Title (H2)
    styles.add(ParagraphStyle(
        name='ResultTitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=24,
        textColor=colors.HexColor(THEME["text_main"]),
        alignment=1, # Center
        spaceAfter=6,
    ))
    
    # Section Subtitle (p)
    styles.add(ParagraphStyle(
        name='ResultSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        textColor=colors.HexColor(THEME["text_muted"]),
        alignment=1, # Center
        spaceAfter=20,
    ))

    # Name Block
    styles.add(ParagraphStyle(
        name='NameBlock',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=18,
        textColor=colors.HexColor(THEME["primary"]),
        alignment=1, # Center
        spaceAfter=20,
    ))

    # Result Number (4rem ~ 50pt)
    styles.add(ParagraphStyle(
        name='ResultNumber',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=50, # ~4rem
        textColor=colors.HexColor(THEME["text_main"]),
        alignment=1, # Center
        spaceAfter=5,
        leading=50,
    ))

    # Result Label
    styles.add(ParagraphStyle(
        name='ResultLabel',
        parent=styles['Normal'],
        fontName='Helvetica', # Medium weight simulated
        fontSize=14,
        textColor=colors.HexColor(THEME["text_muted"]),
        alignment=1, # Center
        spaceAfter=15,
    ))
    
    # Result Pill (Text inside pill)
    styles.add(ParagraphStyle(
        name='ResultPill',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        textColor=colors.HexColor(THEME["text_main"]), # Will override
        alignment=1, # Center
    ))

    # Detail Label (Uppercase, small)
    styles.add(ParagraphStyle(
        name='DetailLabel',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        textColor=colors.HexColor(THEME["text_muted"]),
        alignment=1, # Center
        textTransform='uppercase',
    ))

    # Detail Value
    styles.add(ParagraphStyle(
        name='DetailValue',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=colors.HexColor(THEME["text_main"]),
        alignment=1, # Center
    ))
    
    # Detail Table Header
    styles.add(ParagraphStyle(
        name='TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=colors.HexColor(THEME["text_muted"]),
        alignment=0, # Left
    ))
    
    # Detail Table Cell
    styles.add(ParagraphStyle(
        name='TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        textColor=colors.HexColor(THEME["text_main"]),
        alignment=0, # Left
    ))

    # Detail Title (H3)
    styles.add(ParagraphStyle(
        name='DetailTitle',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=16,
        textColor=colors.HexColor(THEME["text_main"]),
        alignment=0, # Left
        spaceAfter=4,
    ))

    # Footer
    styles.add(ParagraphStyle(
        name='Disclaimer',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        textColor=colors.HexColor(THEME["text_muted"]),
        alignment=1, # Center
    ))
    
    return styles

def draw_background(canvas, doc):
    """Draws the light clean background"""
    canvas.saveState()
    w, h = doc.pagesize
    
    # Fill Background (Slate 50)
    canvas.setFillColor(colors.HexColor(THEME["background"]))
    canvas.rect(0, 0, w, h, fill=1, stroke=0)
    
    # Hero Top Gradient Simulation (Just a light line)
    canvas.setStrokeColor(colors.HexColor(THEME["border"]))
    canvas.setLineWidth(1)
    # canvas.line(0, h - 80, w, h - 80)
    
    canvas.restoreState()

def generate_pdf_report(data, result):
    """
    Generates PDF byte stream matching result.html
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=50,
        leftMargin=50,
        topMargin=50,
        bottomMargin=50
    )
    
    styles = create_stylesheet()
    elements = []
    
    # ==========================
    #  RISK SUMMARY CARD
    # ==========================
    
    # 1. Header Text inside Card (Title + Subtitle)
    elements.append(Paragraph("Risk Summary", styles['ResultTitle']))
    elements.append(Paragraph("Estimated probability of stroke given the submitted profile.", styles['ResultSubtitle']))
    elements.append(Paragraph(data['name'], styles['NameBlock']))
    
    # 2. Score Section
    prob_text = f"{result['prob']*100:.1f}%"
    elements.append(Paragraph(prob_text, styles['ResultNumber']))
    elements.append(Paragraph("Estimated stroke risk", styles['ResultLabel']))
    
    # 3. Pill (Risk Level) - Manual Table for "Pill" look
    level = result['level']
    if level == "Low": 
        pill_bg = "#d1fae5"
        pill_text = THEME["success"]
    elif level == "Moderate": 
        pill_bg = "#fef3c7"
        pill_text = THEME["warning"]
    else: 
        pill_bg = "#fee2e2"
        pill_text = THEME["error"]
        
    pill_style = ParagraphStyle('PillText', parent=styles['ResultPill'], textColor=colors.HexColor(pill_text))
    pill_content = Paragraph(f"{level} risk category", pill_style)
    
    # Center the pill table
    pill_table = Table([[pill_content]], colWidths=[200])
    pill_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor(pill_bg)),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        # Radius not supported, but solid block looks "Card"-like
    ]))
    elements.append(pill_table)
    elements.append(Spacer(1, 0.4 * inch))
    
    # 4. Detail Grid (BMI, Age, etc.)
    # We use a 4-col table: [Label, Value, Label, Value]
    grid_data = [
        [
            Paragraph("BMI", styles['DetailLabel']), Paragraph(f"{result['bmi']:.1f}", styles['DetailValue']),
            Paragraph("AGE CATEGORY", styles['DetailLabel']), Paragraph(str(result['bins'][0]), styles['DetailValue'])
        ],
        [
            Paragraph("GLUCOSE CATEGORY", styles['DetailLabel']), Paragraph(str(result['bins'][1]), styles['DetailValue']),
            Paragraph("BMI CATEGORY", styles['DetailLabel']), Paragraph(str(result['bins'][2]), styles['DetailValue'])
        ]
    ]
    
    grid_table = Table(grid_data, colWidths=[100, 100, 100, 100])
    grid_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('LINEABOVE', (0,0), (-1,0), 0.5, colors.HexColor(THEME["border"])), # Top border for grid
    ]))
    elements.append(grid_table)
    
    # WRAP SUMMARY IN "CARD" TABLE BACKGROUND?
    # Actually, ReportLab flowables are hard to wrap *all* in one big bordered box unless we use Frames or a Container Table.
    # A simplified approach is just to let them flow on the white page (which acts as the card)
    # since we set the page background to Slate 50 (#f8fafc) in draw_background,
    # and we can draw a White Rect behind these specific elements if we want a "Card on Page" look.
    # Let's try drawing the card box explicitly in the background function or just leave it clean on the page.
    # User asked for "like RESULT.HTML". Result.html has a simplified clean look. 
    # Let's stick to the flow.
    
    elements.append(Spacer(1, 0.5 * inch))
    
    # ==========================
    #  INPUT DETAILS
    # ==========================
    
    elements.append(Paragraph("Input Details", styles['DetailTitle']))
    elements.append(Paragraph("Full profile information used for risk calculation.", styles['ResultSubtitle']))
    
    # Use 2-Column Layout (Field | Value | Field | Value) to save vertical space
    
    # Header
    tbl_data = [[
        Paragraph("FIELD", styles['TableHeader']), Paragraph("VALUE", styles['TableHeader']),
        Paragraph("FIELD", styles['TableHeader']), Paragraph("VALUE", styles['TableHeader'])
    ]]
    
    # Rows data
    raw_rows = [
        ("Name", data['name']),
        ("Age", data['age']),
        ("Gender", data['gender']),
        ("BMI", f"{result['bmi']:.1f}"),
        ("Avg Glucose", data['glucose']),
        ("Hypertension", "Yes" if data['hypertension'] else "No"),
        ("Heart Disease", "Yes" if data['heart_disease'] else "No"),
        ("Ever Married", data['ever_married']),
        ("Work Type", data['work_type']),
        ("Residence Type", data['residence']),
        ("Smoking Status", data['smoking']),
        ("", "") # Empty filler if needed
    ]
    
    # Pair them up: [Row1_Col1, Row1_Col2, Row1_Col3, Row1_Col4]
    # We have 11 items. We need pairs.
    # Logic: Take items 0 and 1 -> Row 1. Items 2 and 3 -> Row 2.
    
    # Let's chunk raw_rows into groups of 2
    for i in range(0, len(raw_rows), 2):
        item1 = raw_rows[i]
        item2 = raw_rows[i+1] if i+1 < len(raw_rows) else ("", "")
        
        row_cells = [
            Paragraph(str(item1[0]), styles['TableCell']),
            Paragraph(str(item1[1]), styles['TableCell']),
            Paragraph(str(item2[0]), styles['TableCell']),
            Paragraph(str(item2[1]), styles['TableCell'])
        ]
        tbl_data.append(row_cells)
    
    # Detail Table Style (Clean, border-bottoms)
    # 4 Columns Widths
    col_w = 125 # Total 500
    details_table = Table(tbl_data, colWidths=[110, 140, 110, 140])
    details_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor(THEME["card_bg"])), # White bg
        # Header Style
        ('LINEBELOW', (0,0), (-1,0), 1, colors.HexColor(THEME["border"])),
        
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        
        # Horizontal lines for data rows
        ('LINEBELOW', (0,1), (-1,-1), 0.5, colors.HexColor(THEME["border"])),
        
        # Vertical Separator between the two main columns (optional but good for clarity)
        ('LINEAFTER', (1,0), (1,-1), 1, colors.HexColor(THEME["border"])),
    ]))
    
    elements.append(details_table)
    
    # ==========================
    #  PAGE 2: FEATURE CONTRIBUTIONS
    # ==========================
    from reportlab.platypus import PageBreak
    elements.append(PageBreak())
    
    elements.append(Paragraph("Model Feature Contributions", styles['DetailTitle']))
    elements.append(Paragraph("Linear contributions of each feature (coefficient × WOE) to the logit score.", styles['ResultSubtitle']))
    
    # Feature Table Header
    feat_data = [[Paragraph("FEATURE", styles['TableHeader']), Paragraph("CONTRIBUTION", styles['TableHeader'])]]
    
    # Feature Rows (sorted by name or just as is? result.html uses items() order)
    # result.html uses: {% for k, v in contrib.items() %}
    
    if 'contrib' in result:
        for k, v in result['contrib'].items():
            feat_data.append([
                Paragraph(str(k), styles['TableCell']),
                Paragraph(f"{v:.4f}", styles['TableCell'])
            ])
            
    feature_table = Table(feat_data, colWidths=[200, 300])
    feature_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor(THEME["card_bg"])),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 12),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
        ('LINEBELOW', (0,0), (-1,-1), 1, colors.HexColor(THEME["border"])),
        ('LINEABOVE', (0,0), (-1,0), 1, colors.HexColor(THEME["border"])),
    ]))
    
    elements.append(feature_table)
    
    elements.append(Spacer(1, 0.8 * inch))
    
    # -- FOOTER --
    elements.append(Paragraph("DISCLAIMER: Analysis is not diagnostic. Consult a healthcare professional.", styles['Disclaimer']))
    
    # Build
    doc.build(elements, onFirstPage=draw_background, onLaterPages=draw_background)
    buffer.seek(0)
    return buffer
