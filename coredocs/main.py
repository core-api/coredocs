# coding: utf-8
from coredocs.highlighting import get_highlight_css, get_all_styles
from coredocs.render_markdown import render_markdown
from coredocs.utils import get_links, get_sections
import coreapi
import coredocs
import click
import jinja2
import os
import shutil
import sys
import pkg_resources


THEME_CHOICES = ['slate', 'cerulean']
PYGMENTS_STYLES = get_all_styles()
DEFAULT_LANGS = ['shell', 'javascript', 'python']


def get_fields(location, link):
    return [field for field in link.fields if field.location == location]


def render(doc, highlight=None, langs=None, theme=None, static=None):
    if static is None:
        static = lambda path: path

    if langs is None:
        langs = DEFAULT_LANGS

    schema_format = determine_format(doc)

    base_templates = os.path.join('themes', 'base', 'templates')
    theme_templates = os.path.join('themes', theme, 'templates')

    env = jinja2.Environment(
        loader=jinja2.ChoiceLoader([
            jinja2.PackageLoader('coredocs', theme_templates),
            jinja2.PackageLoader('coredocs', base_templates)
        ]),
        extensions=['coredocs.highlighting.HighlightExtension']
    )
    template = env.get_template('index.html')
    return template.render(
        static=static,
        render_markdown=render_markdown,
        document=doc,
        get_sections=get_sections,
        get_links=get_links,
        get_fields=get_fields,
        code_style=get_highlight_css(highlight),
        schema_url=doc.url,
        langs=langs,
        schema_format=schema_format
    )


def determine_format(document):
    codecs = get_installed_codecs()
    for format_name, codec in codecs.items():
        if codec.media_type == document.media_type:
            return format_name
    return None


def get_installed_codecs():
    packages = [
        (package, package.load()) for package in
        pkg_resources.iter_entry_points(group='coreapi.codecs')
    ]
    return {
        package.name: cls() for (package, cls) in packages
        if '+' in getattr(cls, 'media_type', '') and hasattr(cls, 'decode')
    }


def get_client(format=None):
    codecs = get_installed_codecs()
    if format is None:
        decoders = list(codecs.values())
    else:
        decoders = [codecs[format]]
    return coreapi.Client(decoders=decoders)


@click.group(invoke_without_command=True, help='CoreDocs. An API documentation generator.')
@click.option('--version', is_flag=True, help='Display the `coredocs` version number.')
@click.pass_context
def client(ctx, version):
    if ctx.invoked_subcommand is not None:
        return

    if version:
        click.echo('coredocs %s' % client_version)
    else:
        click.echo(ctx.get_help())


@click.command(help='Build API documentation.')
@click.argument('url')
@click.option('--format', default=None, help='The format of the input API schema.')
@click.option('--theme', default='slate', help='The theme to use.', type=click.Choice(THEME_CHOICES))
@click.option('--highlight', default='monokai', help='Select a code highlighting style from the pygments library.', type=click.Choice(PYGMENTS_STYLES))
@click.option('--languages', default=','.join(DEFAULT_LANGS), help='List of languages to include, as a comma seperated list.')
@click.option('--outdir', type=click.Path(dir_okay=True), default='build', help='The output directory to use.')
@click.option('--force', help='Delete and overwrite any existing build directory.', is_flag=True)
def build(url, format, theme, highlight, languages, outdir, force):
    if os.path.exists(outdir) and not force:
        click.echo(
            "Output directory '%s' already exists.\n"
            "Delete the directory first, or use the '--force' flag." % outdir
        )
        sys.exit(1)

    if languages:
        languages = languages.split(',')
    else:
        languages = []

    force_codec = format is not None
    client = get_client(format)

    click.echo("Fetching schema file from '%s'." % url)
    try:
        document = client.get(url, force_codec=force_codec)
    except coreapi.exceptions.NoCodecAvailable:
        click.echo(
            "The returned Content-Type does not correspond to any registered schema type.\n"
            "Use the '--format' flag to explicitly select an input schema type."
        )
        sys.exit(1)
    except coreapi.exceptions.ErrorMessage as exc:
        click.echo(display(exc.error))
        sys.exit(1)

    output_text = render(document, highlight, languages, theme=theme)

    base_dir = os.path.dirname(coredocs.__file__)
    static_dir = os.path.join(base_dir, 'themes', theme, 'static')

    click.echo("Building documentation into directory '%s'." % outdir)
    if os.path.exists(outdir) and force:
        shutil.rmtree(outdir)
    shutil.copytree(static_dir, os.path.join(outdir))

    output_file = os.path.join(outdir, 'index.html')
    with open(output_file, 'w') as output_file:
        output_file.write(output_text)


client.add_command(build)


if __name__ == '__main__':
    client()
