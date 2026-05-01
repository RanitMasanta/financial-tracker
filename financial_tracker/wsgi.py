import sys
import os

path = '/home/Ranit/financial-tracker'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'financial_tracker.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
