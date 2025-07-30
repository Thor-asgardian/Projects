#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    # If your project package is named differently, change this line:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wardrobe_manager.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Make sure it's installed and your "
            "virtual environment is activated, and that your PYTHONPATH is set."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
