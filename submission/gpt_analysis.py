# gpt_analysis.py

from openai import OpenAI
from django.conf import settings
from django.core.cache import cache
import json
from io import StringIO
import logging
import markdown

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
        prompt = f"Please analyze this research submission and format your response in markdown:\n\n"
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
            return markdown.markdown(cached_response)
            
        try:
            prompt = self.get_analysis_prompt()
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are KHCC Brain, an AI research advisor specializing in medical research analysis. Format your response using markdown syntax for better readability."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            analysis = response.choices[0].message.content
            
            # Cache the raw markdown response for 1 hour
            cache.set(cache_key, analysis, 3600)
            
            # Return the HTML-formatted markdown
            return markdown.markdown(analysis)
            
        except Exception as e:
            logger.error(f"Error in GPT analysis: {str(e)}")
            return "Error in generating analysis. Please try again later."