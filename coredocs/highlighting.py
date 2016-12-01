
from jinja2 import nodes
from jinja2.ext import Extension, Markup

from pygments import highlight, styles
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter


DEFAULT_STYLE = 'monokai'


class HighlightExtension(Extension):
    """
    Code block highlighting.

        {% highlight 'python' %}
        print("hello, world")
        {% endhighlight %}
    """
    tags = set(['highlight'])
    style = DEFAULT_STYLE

    def parse(self, parser):
        next(parser.stream)
        args = [parser.parse_expression()]
        body = parser.parse_statements(['name:endhighlight'], drop_needle=True)
        return nodes.CallBlock(self.call_method('_highlight', args), [], [], body)

    def _highlight(self, lang, caller=None):
        body = caller()
        lexer = get_lexer_by_name(lang, stripall=False)
        formatter = HtmlFormatter(nowrap=True, style=self.style)
        code = highlight(Markup(body.rstrip()).unescape(), lexer, formatter)
        return code


def get_highlight_css(style=None):
    if style is None:
        style = DEFAULT_STYLE
    return HtmlFormatter(style=style).get_style_defs('.highlight')

def get_all_styles():
    return sorted(list(styles.get_all_styles()))
