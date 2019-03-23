#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Insert the path of the platform mocks to locate those
    # Note: The mocks will be moved to the devsite for release 0.3.0 or 0.4.0
    sys.path.insert(0, os.path.join(project_root, 'tests/mocks'))

    # Insert the project root dir to find our reusable app
    sys.path.insert(0, project_root)

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "devsite.settings")

    from django.core.management import execute_from_command_line

    # for path in sys.path:
    #     print(path)

    execute_from_command_line(sys.argv)
