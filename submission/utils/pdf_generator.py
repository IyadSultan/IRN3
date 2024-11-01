import os
import sys
import django
from pathlib import Path

# Get the project root directory and add it to Python path
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent
sys.path.append(str(project_root))

# Setup Django environment - Note the corrected case for iRN
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'iRN.settings')
django.setup()

# Now we can import Django-related modules
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import simpleSplit
from django.utils import timezone
import json
from submission.models import FormDataEntry, Submission
from io import BytesIO
from django.http import HttpResponse


class PDFGenerator:
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
        self.canvas.drawString(self.left_margin, self.y, "Intelligent Research Navigator (iRN) report")
        self.y -= self.line_height * 1.5
        
        self.canvas.setFont("Helvetica-Bold", 14)
        self.canvas.drawString(self.left_margin, self.y, f"{self.submission.title} - Version {self.version}")
        self.y -= self.line_height * 1.5
        
        self.canvas.setFont("Helvetica", 10)
        self.canvas.drawString(self.left_margin, self.y, f"Date of printing: {timezone.now().strftime('%Y-%m-%d %H:%M')}")
        self.y -= self.line_height
        self.canvas.drawString(self.left_margin, self.y, f"Printed by: {self.user.get_full_name()}")
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

    def add_basic_info(self):
        """Add basic submission information"""
        self.add_section_header("Basic Information")
        
        basic_info = [
            f"Submission ID: {self.submission.temporary_id}",
            f"Study Type: {self.submission.study_type}",
            f"IRB Number: {self.submission.irb_number or 'Not provided'}",
            f"Status: {self.submission.get_status_display()}",
            f"Date Created: {self.submission.date_created.strftime('%Y-%m-%d')}",
            f"Date Submitted: {self.submission.date_submitted.strftime('%Y-%m-%d') if self.submission.date_submitted else 'Not submitted'}",
        ]

        for info in basic_info:
            self.write_wrapped_text(info)

    def add_research_team(self):
        """Add research team information"""
        self.add_section_header("Research Team")
        
        # Primary Investigator
        self.write_wrapped_text(f"Primary Investigator: {self.submission.primary_investigator.get_full_name()}")
        
        # Co-Investigators
        coinvestigators = self.submission.coinvestigators.all()
        if coinvestigators:
            self.y -= self.line_height/2
            self.write_wrapped_text("Co-Investigators:")
            for ci in coinvestigators:
                self.write_wrapped_text(f"- {ci.user.get_full_name()} (Role: {ci.role_in_study})", x_offset=20)

        # Research Assistants
        research_assistants = self.submission.research_assistants.all()
        if research_assistants:
            self.y -= self.line_height/2
            self.write_wrapped_text("Research Assistants:")
            for ra in research_assistants:
                self.write_wrapped_text(f"- {ra.user.get_full_name()}", x_offset=20)

    def format_field_value(self, value):
        """Format field value, handling special cases like JSON arrays"""
        print(f"Formatting value: {repr(value)}")  # Debug print
        
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

    def add_dynamic_forms(self):
        """Add dynamic form data"""
        print(f"\nProcessing forms for submission {self.submission.temporary_id}, version {self.version}")
        
        # Debug version information
        all_versions = FormDataEntry.objects.filter(
            submission=self.submission
        ).values('version').distinct()
        print(f"Available versions in database: {[v['version'] for v in all_versions]}")
        
        for dynamic_form in self.submission.study_type.forms.all():
            print(f"\nForm: {dynamic_form.name}")
            
            # Add form name as section header
            self.add_section_header(dynamic_form.name)
            
            # Get field definitions
            field_definitions = {
                field.name: field.displayed_name 
                for field in dynamic_form.fields.all()
            }
            
            form_entries = FormDataEntry.objects.filter(
                submission=self.submission,
                form=dynamic_form,
                version=self.version
            )
            
            print(f"Number of entries found: {form_entries.count()}")
            
            for entry in form_entries:
                displayed_name = field_definitions.get(entry.field_name, entry.field_name)
                formatted_value = self.format_field_value(entry.value)
                self.write_wrapped_text(f"{displayed_name}:", bold=True)
                if formatted_value:
                    self.write_wrapped_text(formatted_value, x_offset=20)
                else:
                    self.write_wrapped_text("No value provided", x_offset=20)

    def add_documents(self):
        """Add attached documents list"""
        self.add_section_header("Attached Documents")
        
        documents = self.submission.documents.all()
        if documents:
            for doc in documents:
                self.write_wrapped_text(
                    f"- {doc.file.name.split('/')[-1]} (Uploaded by: {doc.uploaded_by.get_full_name()})"
                )
        else:
            self.write_wrapped_text("No documents attached")

    def generate(self):
        """Generate the complete PDF"""
        self.add_header()
        self.add_basic_info()
        self.add_research_team()
        self.add_dynamic_forms()
        self.add_documents()
        self.add_footer()
        self.canvas.save()


def generate_submission_pdf(submission, version=None, user=None, as_buffer=False):
    """
    Generate a PDF for a submission.
    """
    # If version is not specified, use the latest available version from the database
    if version is None:
        latest_version = FormDataEntry.objects.filter(
            submission=submission
        ).values('version').distinct().order_by('-version').first()
        version = latest_version['version'] if latest_version else 1

    buffer = BytesIO()
    pdf_generator = PDFGenerator(buffer, submission, version, user)
    pdf_generator.generate()
    buffer.seek(0)
    
    if as_buffer:
        return buffer
    
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="submission_{submission.temporary_id}_v{version}.pdf"'
    return response


if __name__ == "__main__":
    from django.contrib.auth import get_user_model

    def get_system_user():
        User = get_user_model()
        return User.objects.filter(is_superuser=True).first()

    def main():
        try:
            buffer = BytesIO()
            # Get submission with ID 88
            submission = Submission.objects.get(temporary_id=89)
            
            user = get_system_user()
            if not user:
                print("No superuser found!")
                return

            pdf_generator = PDFGenerator(buffer, submission, 1, user)
            pdf_generator.generate()
            
            # Save the PDF to a file
            buffer.seek(0)
            output_path = current_dir / "submission_88_output.pdf"
            with open(output_path, "wb") as f:
                f.write(buffer.getvalue())
            
            print(f"PDF generated successfully at: {output_path}")
            
        except Submission.DoesNotExist:
            print("Submission with ID 88 does not exist!")
        except Exception as e:
            print(f"Error generating PDF: {str(e)}")

    main()