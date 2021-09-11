from pieces import Templ8r, init
from rich import print
# from rich.console import Console
# from rich.syntax import Syntax

template = """
{% for r in rows %}
|{r.day}|{r.month}|{r.year}|{r.weight|int}|{r.notes}|
{% endfor %}
"""

rows = [
    {"day": 24, "month": "April", "year": 2021, "weight": 287.5, "notes": "Fucking Brutal"},
    {"day": 14, "month": "June", "year": 2021, "weight": 283.1, "notes": "Focusing on good habits and consistency"},
    {"day": 28, "month": "June", "year": 2021, "weight": 283.3, "notes": "Focusing on good habits and consistency"},
]

render_with = {
    "rows": rows
}
engine = Templ8r(template, init)
print(engine.render(render_with))