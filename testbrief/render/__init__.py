"""Output renderers. Each one turns a list of `Report` objects into text."""

from testbrief.render.markdown import render_markdown

RENDERERS = {
    "md": render_markdown,
}

__all__ = ["RENDERERS", "render_markdown"]
