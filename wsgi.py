import sys
import os

project_home = os.path.expanduser('~/KioskKeeper')
if project_home not in sys.path:
    sys.path.insert(0, project_home)

os.chdir(project_home)

from app import app
application = app
