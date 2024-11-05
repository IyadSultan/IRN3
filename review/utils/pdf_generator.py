# review/utils/pdf_generator.py

from django.template.loader import render_to_string
from django.http import HttpResponse
from django.conf import settings
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, 
    TableStyle, PageBreak
)
from io import BytesIO

def generate_review_dashboard_pdf(pending_reviews, completed_reviews, user, as_buffer=False):
    """
    Generate PDF for review dashboard using ReportLab
    
    Args:
        pending_reviews: QuerySet of pending reviews
        completed_reviews: QuerySet of completed reviews
        user: The user requesting the PDF
        as_buffer: If True, return BytesIO buffer instead of HttpResponse
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )

    # Styles
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    subtitle_style = styles['Heading2']
    normal_style = styles['Normal']
    
    # Custom table style
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ])

    # Build document content
    elements = []

    # Title
    elements.append(Paragraph('Review Dashboard', title_style))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(f'Generated for: {user.userprofile.full_name}', subtitle_style))
    elements.append(Spacer(1, 20))

    # Pending Reviews Section
    elements.append(Paragraph('Pending Reviews', subtitle_style))
    elements.append(Spacer(1, 12))

    # Pending Reviews Table
    pending_data = [['Title', 'Primary Investigator', 'Study Type', 'Deadline', 'Status', 'Days Remaining']]
    for review in pending_reviews:
        pending_data.append([
            review.submission.title,
            review.submission.primary_investigator.userprofile.full_name,
            review.submission.study_type.name,
            review.deadline.strftime('%Y-%m-%d'),
            review.get_status_display(),
            str(review.days_until_deadline)
        ])
    
    pending_table = Table(pending_data)
    pending_table.setStyle(table_style)
    elements.append(pending_table)
    elements.append(Spacer(1, 30))

    # Add page break before completed reviews
    elements.append(PageBreak())

    # Completed Reviews Section
    elements.append(Paragraph('Completed Reviews', subtitle_style))
    elements.append(Spacer(1, 12))

    # Completed Reviews Table
    completed_data = [['Title', 'Primary Investigator', 'Study Type', 'Submitted On']]
    for review in completed_reviews:
        completed_data.append([
            review.submission.title,
            review.submission.primary_investigator.userprofile.full_name,
            review.submission.study_type.name,
            review.date_submitted.strftime('%Y-%m-%d')
        ])
    
    completed_table = Table(completed_data)
    completed_table.setStyle(table_style)
    elements.append(completed_table)

    # Build PDF
    doc.build(elements)

    if as_buffer:
        return buffer

    # Create response
    buffer.seek(0)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="review_dashboard.pdf"'
    response.write(buffer.getvalue())
    buffer.close()

    return response