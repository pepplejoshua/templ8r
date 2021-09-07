from rich import console
from pieces import Templ8r
from rich import print
from rich.console import Console
from rich.syntax import Syntax
from getpass import getuser

text = """
Welcome {username}!

Products:
{# a random comment #}
{% for prod in products %}
    {prod.name}: {prod.price|float}{% if prod.onsale %} [OnSale!]{% endif %}
{% endfor %}
{# a random comment #}
"""

products = [
    {"name": "book", "price": 30.0, "onsale": True},
    {"name": "oranges", "price": 20, "onsale": True},
    {"name": "deodorant", "price": 4.99, "onsale": False},
]

render_context = {
    "username": getuser(),
    "products": products,
}

init = {
    "int": int,
    "float": float,
}

c = Console()

template = Syntax(text, "text")
c.print(template)

# print("Rendering with data:")
# print(render_context)

tmp = Templ8r(text, init)
# source = Syntax(tmp.source, "python")
# c.print(source)

rendered = tmp.render(render_context)
c.print(rendered)
