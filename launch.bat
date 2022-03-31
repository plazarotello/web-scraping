@echo off

cd house-scraper

python -m venv .venv
python -m pip install -r requirements.txt

.\.venv\Scripts\python.exe scraper/__main__.py -f -i --urls-idealista https://www.idealista.com/venta-viviendas/madrid/centro/lavapies-embajadores/ https://www.idealista.com/venta-viviendas/madrid/barrio-de-salamanca/