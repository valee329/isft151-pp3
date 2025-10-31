# Marks 'app' as a package
from flask import Flask
from .app import create_app

__all__ = ["create_app"]