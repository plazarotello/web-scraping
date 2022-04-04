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
ren .\dataset\idealista-maps idealista-maps-poor


REM idealista scraping (rich district)
.\.venv\Scripts\python.exe scraper/__main__.py -i --urls-idealista https://www.idealista.com/venta-viviendas/madrid/barrio-de-salamanca/

ren .\dataset\idealista.csv idealista-rich.csv
ren .\dataset\idealista-maps idealista-maps-rich

REM mixing floor plans from poor and rich district (idealista)
if not exist ".\dataset\idealista-maps\" mkdir .\dataset\idealista-maps
robocopy .\dataset\idealista-maps-poor .\dataset\idealista-maps\ /COPYALL /E
robocopy .\dataset\idealista-maps-rich .\dataset\idealista-maps\ /COPYALL /E