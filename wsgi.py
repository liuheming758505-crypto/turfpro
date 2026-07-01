"""Gunicorn WSGI 入口 — 生产环境用"""
from app import create_app
app = create_app()
