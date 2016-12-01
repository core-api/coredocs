from markdown.extensions.fenced_code import FencedBlockPreprocessor
import markdown


class CustomFencedBlockPreprocessor(FencedBlockPreprocessor):
    CODE_WRAP = '<pre%s><code>%s</code></pre>'
    LANG_TAG = ' class="highlight %s"'


class FencedCodeExtension(markdown.Extension):

    def extendMarkdown(self, md, md_globals):
        """ Add FencedBlockPreprocessor to the Markdown instance. """
        md.registerExtension(self)

        md.preprocessors.add('fenced_code_block',
                             CustomFencedBlockPreprocessor(md),
                             ">normalize_whitespace")


def render_markdown(md_text):
    return markdown.markdown(md_text, extensions=[FencedCodeExtension(), "tables"])
