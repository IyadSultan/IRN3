@echo off
cd /d "C:\Users\isult\Dropbox\AI\Projects\IRN3"
call .venv\Scripts\activate.bat
python manage.py check_progress_reports
deactivate