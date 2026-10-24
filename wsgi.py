"""
wsgi.py - WSGI Application Entry Point
======================================
Production entry point for Gunicorn, uWSGI, Render, Railway, and Heroku.
"""

from app import app

if __name__ == "__main__":
    app.run()
