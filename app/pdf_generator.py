from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import os

BASE_DIR = os.path.dirname(__file__)
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")

env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

def generate_pdf(context: dict, output_path: str):
    template = env.get_template("report.html")
    html_content = template.render(**context)
    HTML(string=html_content).write_pdf(output_path)
