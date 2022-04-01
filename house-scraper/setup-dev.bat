@echo off

rem creates a virtual environment (only use for development)
python -m venv .venv

rem install dependencies
python -m pip install -r requirements.txt

rem creates chrome session
echo Solve the CAPTCHA in idealista.com and accept cookies 
.\.venv\Scripts\python.exe scraper/chrome_setup.py
