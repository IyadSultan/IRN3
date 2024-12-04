# review/utils/pdf_generator.py

from django.template.loader import render_to_string
from django.http import HttpResponse
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from submission.models import FormDataEntry, StudyAction  # Add this import
from review.models import FormResponse
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, 
    TableStyle, PageBreak
)
from reportlab.lib.utils import simpleSplit
from io import BytesIO
import logging
import json

logger = logging.getLogger(__name__)

class PDFGenerator:
    """Base PDF Generator class with common functionality"""
    def __init__(self, buffer, submission, version, user):
        """Initialize the PDF generator with basic settings"""
        self.buffer = buffer
        self.submission = submission
        self.version = version
        self.user = user
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
        self.canvas.drawString(self.left_margin, self.y, "Intelligent Research Navigator (iRN) Report")
        self.y -= self.line_height * 1.5
        
        self.canvas.setFont("Helvetica-Bold", 14)
        self.canvas.drawString(self.left_margin, self.y, f"{self.submission.title} - Version {self.version}")
        self.y -= self.line_height * 1.5

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

    def format_field_value(self, value):
        """Format field value, handling special cases like JSON arrays"""
        if value is None:
            return "Not provided"
            
        if isinstance(value, str):
            if value.strip() == "":
                return "Not provided"
            if value.startswith('['):
                try:
                    value_list = json.loads(value)
                    return ", ".join(str(v) for v in value_list)
                except json.JSONDecodeError:
                    return value
        
        return str(value)

class ReviewPDFGenerator(PDFGenerator):
    def __init__(self, buffer, review, submission, form_responses):
        """Initialize the PDF generator for reviews"""
        super().__init__(buffer, submission, review.submission_version, review.reviewer)
        self.review = review
        self.form_responses = form_responses

    def add_header(self):
        """Override header for review PDFs"""
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
                formatted_value = self.format_field_value(field_value)
                self.write_wrapped_text(f"{field_name}:", bold=True)
                self.write_wrapped_text(formatted_value, x_offset=20)
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

def generate_review_pdf(review, submission, form_responses, as_buffer=False):
    """Generate PDF for a review"""
    try:
        logger.info(f"Generating PDF for review of submission {submission.temporary_id}")
        
        buffer = BytesIO()
        pdf_generator = ReviewPDFGenerator(buffer, review, submission, form_responses)
        pdf_generator.generate()
        
        if as_buffer:
            buffer.seek(0)
            return buffer
            
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        filename = f"review_{submission.temporary_id}_v{review.submission_version}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
            
    except Exception as e:
        logger.error(f"Error generating review PDF: {str(e)}")
        logger.error("PDF generation error details:", exc_info=True)
        return None
    

class ActionPDFGenerator(PDFGenerator):
    def __init__(self, buffer, action, submission, form_responses):
        """Initialize PDF generator for study actions"""
        self.action = action
        super().__init__(buffer, submission, action.version, action.performed_by)
        self.form_responses = form_responses

    def add_header(self):
        """Override header for action PDFs"""
        self.canvas.setFont("Helvetica-Bold", 16)
        self.canvas.drawString(self.left_margin, self.y, "Intelligent Research Navigator (iRN) Study Action Report")
        self.y -= self.line_height * 1.5
        
        self.canvas.setFont("Helvetica-Bold", 14)
        self.canvas.drawString(self.left_margin, self.y, f"{self.action.get_action_type_display()}: {self.submission.title}")
        self.y -= self.line_height * 1.5
        
        self.canvas.setFont("Helvetica", 10)
        self.canvas.drawString(self.left_margin, self.y, f"Date of printing: {timezone.now().strftime('%Y-%m-%d %H:%M')}")
        self.y -= self.line_height
        self.canvas.drawString(self.left_margin, self.y, f"Performed by: {self.action.performed_by.get_full_name()}")
        self.y -= self.line_height * 2

    def add_study_action_details(self):
        """Add study action details to the PDF"""
        self.add_section_header("Action Details")
        
        action_info = [
            f"Action Type: {self.action.get_action_type_display()}",
            f"Status: {self.action.get_status_display()}",
            f"Date Created: {self.action.date_created.strftime('%Y-%m-%d %H:%M')}",
            f"Performed By: {self.action.performed_by.get_full_name()}",
            f"Version: {self.action.version}",
        ]
        
        if self.action.notes:
            action_info.append(f"Notes: {self.action.notes}")
            
        for info in action_info:
            self.write_wrapped_text(info)
            
        # Add a space after action details
        self.y -= self.line_height

    def add_form_responses(self):
        """Add form responses to the PDF"""
        if not self.form_responses:
            return

        self.add_section_header("Form Responses")
        
        for form_id, data in self.form_responses.items():
            form = data['form']
            self.write_wrapped_text(f"Form: {form.name}", bold=True)
            self.y -= self.line_height/2
            
            for field_name, value in data['fields'].items():
                # Handle JSON values for checkboxes
                try:
                    if isinstance(value, str) and value.startswith('['):
                        value = ', '.join(json.loads(value))
                except (json.JSONDecodeError, TypeError):
                    pass
                
                self.write_wrapped_text(f"{field_name}:", x_offset=20)
                self.write_wrapped_text(str(value), x_offset=40)
                self.y -= self.line_height/2

            self.y -= self.line_height

    def generate(self):
        """Generate the complete PDF for an action"""
        try:
            self.add_header()
            self.add_study_action_details()
            self.add_form_responses()
            self.add_footer()
            self.canvas.save()
        except Exception as e:
            logger.error(f"Error generating action PDF: {str(e)}")
            logger.error("PDF generation error details:", exc_info=True)
            raise

def generate_action_pdf(submission, study_action, form_entries, user, as_buffer=False):
    """Generate PDF for a study action"""
    try:
        logger.info(f"Generating PDF for action {study_action.id} of submission {submission.temporary_id}")
        
        buffer = BytesIO()
        pdf_generator = ActionPDFGenerator(buffer, study_action, submission, form_entries)
        
        # Add header
        pdf_generator.add_header()
        
        # Add basic submission identifier
        pdf_generator.write_wrapped_text(f"Submission ID: {submission.temporary_id}")
        pdf_generator.write_wrapped_text(f"Title: {submission.title}")
        pdf_generator.y -= pdf_generator.line_height
        
        # Add action-specific information
        pdf_generator.add_section_header(f"{study_action.get_action_type_display()}")
        pdf_generator.write_wrapped_text(f"Date: {study_action.date_created.strftime('%Y-%m-%d %H:%M')}")
        pdf_generator.write_wrapped_text(f"Submitted by: {study_action.performed_by.get_full_name()}")
        pdf_generator.y -= pdf_generator.line_height
        
        # Add only the form entries for this action
        pdf_generator.add_section_header("Form Details")
        pdf_generator.add_form_responses()
        
        # Add footer
        pdf_generator.add_footer()
        pdf_generator.canvas.save()
        
        if as_buffer:
            buffer.seek(0)
            return buffer
        else:
            buffer.seek(0)
            response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = (
                f'attachment; filename="submission_{submission.temporary_id}_'
                f'{study_action.action_type}_{study_action.date_created.strftime("%Y%m%d")}.pdf"'
            )
            return response
            
    except Exception as e:
        logger.error(f"Error generating action PDF: {str(e)}")
        logger.error("Action PDF generation error details:", exc_info=True)
        return None