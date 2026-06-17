from string import Template
from typing import Any


def render_prompt(template: str, variables: dict[str, Any]) -> str:
    rendered = template
    for key, value in variables.items():
        rendered = rendered.replace("{" + key + "}", "" if value is None else str(value))
    try:
        return Template(rendered).safe_substitute(**variables)
    except ValueError:
        return rendered
