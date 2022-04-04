@echo off 

cd house-scraper

REM install requirements
python -m venv .venv
python -m pip install -r requirements.txt

REM fotocasa scraping
.\.venv\Scripts\python.exe scraper/__main__.py -f

REM idealista scraping (poor district)
.\.venv\Scripts\python.exe scraper/__main__.py -i --urls-idealista https://www.idealista.com/venta-viviendas/madrid/villaverde/ 

ren .\dataset\idealista.csv idealista-poor.csv


REM idealista scraping (rich district)
.\.venv\Scripts\python.exe scraper/__main__.py -i --urls-idealista https://www.idealista.com/venta-viviendas/madrid/barrio-de-salamanca/

ren .\dataset\idealista.csv idealista-rich.csv