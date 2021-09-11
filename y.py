from pieces import Templ8r, init
from rich.console import Console
from rich.syntax import Syntax
from getpass import getuser
from rich import print

text = """
<h1>Welcome {username}!</h1>

<p>Products:</p>
{# a random comment #}
<ul>
{% for prod in products %}
    <li>{prod.name}: {prod.price|float}{% if prod.onsale %} <strong>[OnSale!]</strong>{% endif %}</li>
{% endfor %}
</ul>
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

c = Console()

template = Syntax(text, "text")
c.print(template)

print("Hydrating with state:")
print(render_context)

tmp = Templ8r(text, init)
# source = Syntax(tmp.source, "python")
# c.print(source)

rendered = tmp.render(render_context)
c.print(rendered)
