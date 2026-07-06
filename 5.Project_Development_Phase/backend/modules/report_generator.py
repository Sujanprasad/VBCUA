import os
import json
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas

def strip_emojis(text):
    """
    Removes emojis and other non-ASCII characters that ReportLab's default 
    Helvetica font cannot render.
    """
    replacements = {
        "✨": "",
        "👍": "",
        "❌": "",
        "🎙️": "",
        "⚠️": "",
        "🛑": "",
        "⏱️": "",
        "🔊": ""
    }
    for emoji, replacement in replacements.items():
        text = text.replace(emoji, replacement)
    
    return "".join(c for c in text if ord(c) < 256)

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute total pages and draw headers/footers on all pages.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()


    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        
        # Header (Only on Page 1 and onwards, but here it's consistent)
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor("#475569"))
        self.drawString(54, 750, "VOICE-BASED CONCEPT UNDERSTANDING ANALYSER (VBCUA)")
        
        # Header Line
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 742, 558, 742)
        
        # Footer
        self.setFont("Helvetica", 8)
        self.drawString(54, 40, "CONFIDENTIAL - CONCEPT ASSESSMENT REPORT")
        page_num_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 40, page_num_str)
        
        self.restoreState()

def generate_report_pdf(report_data, output_filepath="report.pdf"):
    """
    Generates a beautifully typeset PDF report using ReportLab.
    
    Args:
        report_data (dict): Dictionary with all metrics, transcript, concept details, and feedback notes.
        output_filepath (str): The filename/path to save the PDF.
        
    Returns:
        str: Absolute path to the generated PDF.
    """
    # Set up document template
    # Letter size is 612 x 792 points. With margins of 54 points, printable width is 504 points.
    doc = SimpleDocTemplate(
        output_filepath,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=72,
        bottomMargin=72
    )
    
    styles = getSampleStyleSheet()
    
    # Define custom professional styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=colors.HexColor("#1E293B"),
        spaceAfter=15
    )
    
    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#0F766E"),
        spaceBefore=12,
        spaceAfter=8,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#334155")
    )
    
    body_bold_style = ParagraphStyle(
        'BodyBold_Custom',
        parent=body_style,
        fontName='Helvetica-Bold'
    )
    
    meta_label_style = ParagraphStyle(
        'MetaLabel',
        parent=body_style,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor("#475569")
    )
    
    feedback_style = ParagraphStyle(
        'Feedback_Style',
        parent=body_style,
        fontSize=9.5,
        leading=14,
        spaceAfter=6
    )
    
    # Table styles
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=body_style,
        fontName='Helvetica-Bold',
        textColor=colors.white
    )
    
    # Resolve category colors
    category = report_data.get("category", "Moderate")
    if category == "Strong":
        category_color = "#15803D" # Green
    elif category == "Moderate":
        category_color = "#B45309" # Amber
    else:
        category_color = "#B91C1C" # Red
        
    category_text_style = ParagraphStyle(
        'CategoryText',
        parent=body_bold_style,
        textColor=colors.HexColor(category_color)
    )
    
    story = []
    
    # 1. Header Spacer
    story.append(Spacer(1, 10))
    
    # 2. Main Title
    story.append(Paragraph("Concept Understanding Assessment", title_style))
    
    # 3. Metadata Table (User, Date, Concept)
    created_at = report_data.get("created_at")
    if isinstance(created_at, datetime.datetime):
        date_str = created_at.strftime("%Y-%m-%d %H:%M:%S")
    else:
        date_str = str(created_at) if created_at else datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
    metadata_data = [
        [Paragraph("Candidate:", meta_label_style), Paragraph(strip_emojis(report_data.get("username", "default_user")), body_style),
         Paragraph("Date / Time:", meta_label_style), Paragraph(date_str, body_style)],
        [Paragraph("Assessed Concept:", meta_label_style), Paragraph(strip_emojis(report_data.get("concept_title", "N/A")), body_style),
         Paragraph("Total Words:", meta_label_style), Paragraph(str(report_data.get("word_count", 0)), body_style)]
    ]
    
    metadata_table = Table(metadata_data, colWidths=[100, 152, 100, 152])
    metadata_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(metadata_table)
    story.append(Spacer(1, 15))
    
    # 4. Metrics Summary Table
    # Compile metrics
    overall_score = report_data.get("overall_score", 0.0)
    semantic_score_base = report_data.get("semantic_score_base", 0.0)
    filler_word_count = report_data.get("filler_word_count", 0)
    filler_ratio = report_data.get("filler_ratio", 0.0)
    filler_penalty = report_data.get("filler_penalty", 0.0)
    pause_ratio = report_data.get("pause_ratio", 0.0)
    pause_penalty = report_data.get("pause_penalty", 0.0)
    rms_energy = report_data.get("rms_energy", 0.0)
    volume_penalty = report_data.get("volume_penalty", 0.0)
    
    metrics_data = [
        [Paragraph("Evaluation Metric", table_header_style), Paragraph("Measured Value", table_header_style), Paragraph("Deduction / Impact", table_header_style)],
        
        [Paragraph("<b>Overall Assessment Score</b>", body_style), Paragraph(f"<b>{overall_score:.1f} / 100</b>", body_style), Paragraph(category, category_text_style)],
        
        [Paragraph("Semantic Conceptual Similarity", body_style), Paragraph(f"{semantic_score_base:.1f}% Match", body_style), Paragraph("Baseline Score", body_style)],
        
        [Paragraph("Speech Fluency (Filler Words)", body_style), Paragraph(f"{filler_word_count} filler(s) ({filler_ratio:.1%})", body_style), Paragraph(f"-{filler_penalty:.1f} pts" if filler_penalty > 0 else "None", body_style if filler_penalty == 0 else ParagraphStyle('Pen', parent=body_style, textColor=colors.HexColor("#B91C1C")))],
        
        [Paragraph("Speech Pacing (Pause Ratio)", body_style), Paragraph(f"{pause_ratio:.1%} silence ratio", body_style), Paragraph(f"-{pause_penalty:.1f} pts" if pause_penalty > 0 else "None", body_style if pause_penalty == 0 else ParagraphStyle('Pen', parent=body_style, textColor=colors.HexColor("#B91C1C")))],
        
        [Paragraph("Vocal Projection (RMS Volume)", body_style), Paragraph(f"{rms_energy:.4f} RMS", body_style), Paragraph(f"-{volume_penalty:.1f} pts" if volume_penalty > 0 else "None", body_style if volume_penalty == 0 else ParagraphStyle('Pen', parent=body_style, textColor=colors.HexColor("#B91C1C")))]
    ]
    
    metrics_table = Table(metrics_data, colWidths=[200, 154, 150])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0F766E")),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        # Highlight overall score row
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor("#F8FAFC")),
    ]))
    
    story.append(metrics_table)
    story.append(Spacer(1, 15))
    
    # 5. Diagnostic Feedback Block
    feedback_notes = strip_emojis(report_data.get("feedback_notes", "No feedback compiled."))
    feedback_paragraphs = []
    for line in feedback_notes.split("\n\n"):
        if line.strip():
            # Basic markdown replacement for reportlab bold
            formatted_line = line.replace("**", "<b>").replace("</b><b>", "</b>").replace("</b>", "").replace("<b>", "<b>")
            # If replacement has mismatched bold, regex clean it up or keep it simple:
            # Let's do a reliable replacement:
            formatted_line = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line)
            
            feedback_paragraphs.append(Paragraph(formatted_line, feedback_style))
            
    feedback_story = [
        Paragraph("Diagnostic Feedback & Insights", h2_style),
        Spacer(1, 4)
    ] + feedback_paragraphs
    
    # Keep the feedback block together if possible
    story.append(KeepTogether(feedback_story))
    story.append(Spacer(1, 10))
    
    # 6. Transcript and Reference Concept side-by-side or stacked
    # Stacked is safer for long concepts and transcripts.
    transcript_story = [
        Paragraph("User Audio Transcript", h2_style),
        Paragraph(strip_emojis(report_data.get("transcript_text", "No speech transcribed.")), body_style),
        Spacer(1, 12)
    ]
    story.append(KeepTogether(transcript_story))
    
    concept_story = [
        Paragraph("Reference Concept", h2_style),
        Paragraph(strip_emojis(report_data.get("concept_text", "No reference concept loaded.")), body_style),
        Spacer(1, 12)
    ]
    story.append(KeepTogether(concept_story))
    
    # Build document
    doc.build(story, canvasmaker=NumberedCanvas)
    return os.path.abspath(output_filepath)

import re # needed for re.sub in generate_report_pdf
