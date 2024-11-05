# gpt_analysis.py

from openai import OpenAI
from django.conf import settings
from django.core.cache import cache
import json
from io import StringIO
import logging
import markdown2
from django.utils.safestring import mark_safe

logger = logging.getLogger(__name__)

class ResearchAnalyzer:
    def __init__(self, submission, version):
        """Initialize the analyzer with basic settings"""
        if version is None:
            raise ValueError("Version must be specified")
            
        self.submission = submission
        self.version = version
        self.client = OpenAI()

    def get_analysis_prompt(self):
        """Generate the analysis prompt from submission data"""
        # Get form data for the current version
        form_entries = self.submission.form_data_entries.filter(version=self.version)
        
        # Build prompt from form data
        prompt = (
            """
            Please analyze the following research submission and provide detailed suggestions to enhance the project, focusing on methodology, inclusion and exclusion criteria, objectives, endpoints, statistical analysis, and any other relevant issues.

            Format your response in markdown with the following structure:

            Use # for the main title
            Use ## for section headers
            Use bold for emphasis
            Use - for bullet points
            Include sections for:
            Study Type
                Principal Investigator
                Objectives
                Methods
                Inclusion Criteria
                Exclusion Criteria
                Endpoints
                Statistical Analysis
                Other Relevant Issues
                Provide specific recommendations for improvement in each section
                End with a Summary section highlighting key suggestions and overall recommendations
                Study Information:
                """
        )
        prompt += f"Study Type: {self.submission.study_type.name}\n\n"
        
        # Group entries by form
        for form in self.submission.study_type.forms.all():
            form_data = form_entries.filter(form=form)
            if form_data:
                prompt += f"{form.name}:\n"
                for entry in form_data:
                    prompt += f"- {entry.field_name}: {entry.value}\n"
                prompt += "\n"
                
        return prompt

    def analyze_submission(self):
        """Send to GPT and get analysis"""
        cache_key = f'gpt_analysis_{self.submission.temporary_id}_{self.version}'
        cached_response = cache.get(cache_key)
        
        if cached_response:
            # Convert markdown to HTML
            html_content = markdown2.markdown(cached_response, extras=['fenced-code-blocks'])
            return mark_safe(html_content)
            
        try:
            prompt = self.get_analysis_prompt()
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": (
                            "You are KHCC Brain, an AI research advisor specializing in medical research analysis. "
                            "Provide your analysis in clear, structured markdown format. "
                            "Use proper markdown syntax and ensure the output is well-organized and professional."
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            analysis = response.choices[0].message.content
            
            # Cache the raw markdown response
            cache.set(cache_key, analysis, 3600)
            
            # Convert markdown to HTML
            html_content = markdown2.markdown(analysis, extras=['fenced-code-blocks'])
            return mark_safe(html_content)
            
        except Exception as e:
            logger.error(f"Error in GPT analysis: {str(e)}")
            return "Error in generating analysis. Please try again later."