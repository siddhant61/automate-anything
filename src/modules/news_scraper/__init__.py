"""
News Scraper Module.

A demonstration module that scrapes news headlines from Hacker News
to validate the platform's generic, modular architecture.
"""

from .scraper import scrape_news
from .analysis import analyze_headlines

__all__ = ['scrape_news', 'analyze_headlines']
