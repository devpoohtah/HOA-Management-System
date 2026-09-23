# app/core/templates.py

from fastapi.templating import Jinja2Templates

# Shared Jinja2 template engine instance.
# Imported by main.py (to attach it to the app) and by any router
# that needs to render an HTML page (e.g. auth, dashboard).
templates = Jinja2Templates(directory="templates")