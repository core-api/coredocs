# coding: utf-8
from markdown.extensions.fenced_code import FencedBlockPreprocessor
import click
import jinja2
import os
import shutil
import markdown



EXAMPLES = ["""
# Introduction

Welcome to the Kittn API! You can use our API to access Kittn API endpoints, which can get information on various cats, kittens, and breeds in our database.

We have language bindings in Shell, Ruby, and Python! You can view code examples in the dark area to the right, and you can switch the programming language of the examples with the tabs in the top right.

This example API documentation page was created with [Slate](http://example.com). Feel free to edit it and use it as a base for your own API's documentation.
""",

"""
# Authentication

> To authorize, use this code:

```ruby
require 'kittn'

api = Kittn::APIClient.authorize!('meowmeowmeow')
```

```python
import kittn

api = kittn.authorize('meowmeowmeow')
```

```shell
# With shell, you can just pass the correct header with each request
curl "api_endpoint_here"
  -H "Authorization: meowmeowmeow"
```

```javascript
const kittn = require('kittn');

let api = kittn.authorize('meowmeowmeow');
```

> Make sure to replace `meowmeowmeow` with your API key.

Kittn uses API keys to allow access to the API. You can register a new Kittn API key at our [developer portal](http://example.com/developers).

Kittn expects for the API key to be included in all API requests to the server in a header that looks like the following:

`Authorization: meowmeowmeow`

<aside class="notice">
You must replace <code>meowmeowmeow</code> with your personal API key.
</aside>""",

u"""
# Kittens

## Get All Kittens

```ruby
require 'kittn'

api = Kittn::APIClient.authorize!('meowmeowmeow')
api.kittens.get
```

```python
import kittn

api = kittn.authorize('meowmeowmeow')
api.kittens.get()
```

```shell
curl "http://example.com/api/kittens"
  -H "Authorization: meowmeowmeow"
```

```javascript
const kittn = require('kittn');

let api = kittn.authorize('meowmeowmeow');
let kittens = api.kittens.get();
```

> The above command returns JSON structured like this:

```json
[
  {
    "id": 1,
    "name": "Fluffums",
    "breed": "calico",
    "fluffiness": 6,
    "cuteness": 7
  },
  {
    "id": 2,
    "name": "Max",
    "breed": "unknown",
    "fluffiness": 5,
    "cuteness": 10
  }
]
```

This endpoint retrieves all kittens.

### HTTP Request

`GET http://example.com/api/kittens`

### Query Parameters

Parameter | Default | Description
--------- | ------- | -----------
include_cats | false | If set to true, the result will also include cats.
available | true | If set to false, the result will include kittens that have already been adopted.

<aside class="success">
Remember - a happy kitten is an authenticated kitten!
</aside>

## Get a Specific Kitten

```ruby
require 'kittn'

api = Kittn::APIClient.authorize!('meowmeowmeow')
api.kittens.get(2)
```

```python
import kittn

api = kittn.authorize('meowmeowmeow')
api.kittens.get(2)
```

```shell
curl "http://example.com/api/kittens/2"
  -H "Authorization: meowmeowmeow"
```

```javascript
const kittn = require('kittn');

let api = kittn.authorize('meowmeowmeow');
let max = api.kittens.get(2);
```

> The above command returns JSON structured like this:

```json
{
  "id": 2,
  "name": "Max",
  "breed": "unknown",
  "fluffiness": 5,
  "cuteness": 10
}
```

This endpoint retrieves a specific kitten.

<aside class="warning">Inside HTML code blocks like this one, you can't use Markdown, so use <code>&lt;code&gt;</code> blocks to denote code.</aside>

### HTTP Request

`GET http://example.com/kittens/<ID>`

### URL Parameters

Parameter | Description
--------- | -----------
ID | The ID of the kitten to retrieve
"""]


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


def convert_md_to_html(md_text):
    return markdown.markdown(md_text, extensions=[FencedCodeExtension(), "tables", "toc"])


def local_url_for(endpoint, **values):
    dir_path, file_path = os.path.split(values['filename'])
    dir_path = dir_path[0].replace("/", "./") + dir_path[1:]
    return os.path.join(dir_path, file_path)


def render():
    docs = [convert_md_to_html(example) for example in EXAMPLES]
    env = jinja2.Environment(
        loader=jinja2.PackageLoader('coreapi_docs', 'templates'),
        autoescape=False,
        extensions=['jinja2.ext.autoescape']
    )
    template = env.get_template('index.html')
    return template.render(
        API_TITLE='Title',
        IS_SEARCH=True,
        LOGO_TITLE='Logo',
        LOGO_IMG='logo.png',
        IS_LOGO_ABSOLUTE_URL=False,
        SUPPORT_LANGUAGES=['shell', 'ruby', 'python'],
        DOCS=docs,
        COPYRIGHT='Tom Christie 2016',
        FAVICON='http://example.com/foo.png',
        url_for=local_url_for
    )


@click.command()
def client():
    output_text = render()
    with open('build/index.html', 'w') as output_file:
        output_file.write(output_text)


if __name__ == '__main__':
    client()
