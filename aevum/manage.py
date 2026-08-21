#!/usr/bin/env python3
"""Aevum — manage.py (Django CLI entry)"""
import os, sys
def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aevum.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("Couldn't import Django. Install it with `pip install Django`.") from exc
    execute_from_command_line(sys.argv)
if __name__ == '__main__':
    main()
