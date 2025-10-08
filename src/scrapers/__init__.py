"""Módulo de scrapers para fuentes legales mexicanas.

Este módulo contiene scrapers especializados para extraer información
de diversas fuentes oficiales de documentos legales mexicanos.
"""

from .dof_scraper import DOFScraper
from .orden_juridico_scraper import OrdenJuridicoScraper

# TODO: Implementar scrapers adicionales
# from .constitution_scraper import ConstitutionScraper

__all__ = [
    "DOFScraper",
    "OrdenJuridicoScraper",
    # "ConstitutionScraper"
]