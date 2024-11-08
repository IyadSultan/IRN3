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
import logging
from reportlab.lib.utils import simpleSplit
from django.utils import timezone

logger = logging.getLogger(__name__)

class ReviewPDFGenerator:
    def __init__(self, buffer, review, submission, form_responses):
        """Initialize the PDF generator with basic settings"""
        self.buffer = buffer
        self.review = review
        self.submission = submission
        self.form_responses = form_responses
        self.canvas = canvas.Canvas(buffer, pagesize=letter)
        self.y = 750  # Starting y position
        self.line_height = 20
        self.page_width = letter[0]
        self.left_margin = 100
        self.right_margin = 500
        self.min_y = 100  # Minimum y position before new page

    def add_header(self):
        """Add header to the current page"""
        self.canvas.setFont("Helvetica-Bold", 16)
        self.canvas.drawString(self.left_margin, self.y, "Intelligent Research Navigator (iRN) Review Report")
        self.y -= self.line_height * 1.5
        
        self.canvas.setFont("Helvetica-Bold", 14)
        self.canvas.drawString(self.left_margin, self.y, f"Review for: {self.submission.title}")
        self.y -= self.line_height * 1.5
        
        self.canvas.setFont("Helvetica", 10)
        self.canvas.drawString(self.left_margin, self.y, f"Date of printing: {timezone.now().strftime('%Y-%m-%d %H:%M')}")
        self.y -= self.line_height
        self.canvas.drawString(self.left_margin, self.y, f"Reviewer: {self.review.reviewer.get_full_name()}")
        self.y -= self.line_height * 2

    def add_footer(self):
        """Add footer to the current page"""
        footer_text = (
            "iRN is a property of the Artificial Intelligence and Data Innovation (AIDI) office "
            "in collaboration with the Office of Scientific Affairs (OSAR) office @ King Hussein "
            "Cancer Center, Amman - Jordan. Keep this document confidential."
        )
        
        self.canvas.setFont("Helvetica", 8)
        text_object = self.canvas.beginText()
        text_object.setTextOrigin(self.left_margin, 50)
        
        wrapped_text = simpleSplit(footer_text, "Helvetica", 8, self.right_margin - self.left_margin)
        for line in wrapped_text:
            text_object.textLine(line)
        
        self.canvas.drawText(text_object)

    def check_page_break(self):
        """Check if we need a new page and create one if necessary"""
        if self.y < self.min_y:
            self.add_footer()
            self.canvas.showPage()
            self.y = 750
            self.add_header()
            return True
        return False

    def write_wrapped_text(self, text, x_offset=0, bold=False):
        """Write text with word wrapping"""
        if bold:
            self.canvas.setFont("Helvetica-Bold", 10)
        else:
            self.canvas.setFont("Helvetica", 10)
            
        wrapped_text = simpleSplit(str(text), "Helvetica", 10, self.right_margin - (self.left_margin + x_offset))
        for line in wrapped_text:
            self.check_page_break()
            self.canvas.drawString(self.left_margin + x_offset, self.y, line)
            self.y -= self.line_height

    def add_section_header(self, text):
        """Add a section header"""
        self.check_page_break()
        self.y -= self.line_height
        self.canvas.setFont("Helvetica-Bold", 12)
        self.canvas.drawString(self.left_margin, self.y, text)
        self.y -= self.line_height

    def add_review_info(self):
        """Add basic review information"""
        self.add_section_header("Review Information")
        
        review_info = [
            f"Submission ID: {self.submission.temporary_id}",
            f"Submission Version: {self.review.submission_version}",
            f"Review Status: {self.review.review_request.get_status_display()}",
            f"Date Submitted: {self.review.date_submitted.strftime('%Y-%m-%d') if self.review.date_submitted else 'Not submitted'}",
            f"Reviewer: {self.review.reviewer.get_full_name()}",
            f"Requested By: {self.review.review_request.requested_by.get_full_name()}"
        ]

        for info in review_info:
            self.write_wrapped_text(info)

    def add_form_responses(self):
        """Add form responses"""
        for response in self.form_responses:
            self.add_section_header(f"Form: {response.form.name}")
            
            for field_name, field_value in response.response_data.items():
                self.write_wrapped_text(f"{field_name}:", bold=True)
                self.write_wrapped_text(str(field_value), x_offset=20)
                self.y -= self.line_height/2

    def add_comments(self):
        """Add reviewer comments"""
        if self.review.comments:
            self.add_section_header("Additional Comments")
            self.write_wrapped_text(self.review.comments)

    def generate(self):
        """Generate the complete PDF"""
        try:
            self.add_header()
            self.add_review_info()
            self.add_form_responses()
            self.add_comments()
            self.add_footer()
            self.canvas.save()
        except Exception as e:
            logger.error(f"Error generating review PDF: {str(e)}")
            logger.error("PDF generation error details:", exc_info=True)
            raise

def generate_review_pdf(review, submission, form_responses):
    """Generate PDF for a review"""
    try:
        logger.info(f"Generating PDF for review of submission {submission.temporary_id}")
        
        buffer = BytesIO()
        pdf_generator = ReviewPDFGenerator(buffer, review, submission, form_responses)
        pdf_generator.generate()
        
        buffer.seek(0)
        return buffer
            
    except Exception as e:
        logger.error(f"Error generating review PDF: {str(e)}")
        logger.error("PDF generation error details:", exc_info=True)
        return None