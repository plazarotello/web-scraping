[![Maintainer](https://img.shields.io/badge/author-plazarotello-informational)](https://github.com/plazarotello) [![Maintainer](https://img.shields.io/badge/author-alba620-informational)](https://github.com/alba620) [![Python 3.9](https://img.shields.io/badge/python-3.9-blue.svg)](https://www.python.org/downloads/release/python-3910/)

# Título provisional

## Autoría y licencia

El código, el informe, el _dataset_ y el repositorio han sido creados y desarrollados por **Alba Gómez Varela** (agomezvarela@uoc.edu) y **Patricia Lázaro Tello** (plazarotello@uoc.edu).

## Contexto

Este trabajo corresponde con la práctica 1 de la asignatura **M2.851** Tipología y Ciclo de Vida del Dato, del máster de Ciencia de Datos de la Universitat Oberta de Catalunya. El objetivo de la práctica es crear un *dataset* a partir de los datos contenidos en una web, utilizando un *web scraper* para su extracción.

## Descripción

Descripción provisional.

## Estructura

A continuación se muestra en árbol la estructura del proyecto. Dentro de cada carpeta de house-scraper hay un README.md que provee de más detalles sobre cada fichero de código.

    .
    ├── house-scraper                                   # carpeta con el código python del scraper
    |   ├── dataset                                     # carpeta en que se guarda el dataset final
    |   |   ├── idealista-maps                          # contiene los planos de las casas de idealista
    |   |   ├── dataset.csv                             # dataset final
    |   |   ├── fotocasa.csv                            # dataset de fotocasa
    |   |   └── idealista.csv                           # dataset de idealista
    |   |
    |   ├── scraper                                     # módulo principal
    |   |
    |   |   ├── misc                                    # módulo de utilidades y configuración
    |   |   |   ├── captcha_solver.py                   # script para resolver captchas
    |   |   |   ├── config.py                           # configuración del programa
    |   |   |   ├── network.py                          # obtención de user-agents y proxies
    |   |   |   └── utils.py                            # utilidades
    |   |   |
    |   |   ├── scrapers                                # módulo de scraping
    |   |   |   ├── fotocasa.py                         # scraper de fotocasa
    |   |   |   ├── idealista.py                        # scraper de idealista
    |   |   |   ├── scraper_base.py                     # clase base de los scrapers
    |   |   |   └── scraper_factory.py                  # factoría de scrapers
    |   |   |
    |   |   ├── __main__.py                             # script principal
    |   |   └── chrome_setup.py                         # script auxiliar para crear al sesión de chrome
    |   |
    |   ├── buster_1.3.crx                              # extensión solucionadora de captchas
    |   ├── chromedriver.exe
    |   ├── requirements.txt                            # fichero con los requerimientos de la aplicación
    |   └── setup-dev.bat                               # script batch para configurar el workspace de desarrollo
    |
    ├── report                                          # carpeta donde se aloja el informe
    |   └── agomezvarela_plazarotello-TIP_PRA1.pdf      # informe
    ├── LICENSE                                         # licencia del código
    ├── launch.bat                                      # script que lanza el programa con las opciones adecuadas
    └── README.md

## Instrucciones de uso

Para lanzar el _web scraper_ y obtener los datos, ejecutar el _script_ **launch.bat**. Creará el entorno virtual, instalará las dependencias y lanzará el programa con las opciones y datos con los que se generó el _dataset_ en Zenodo.
