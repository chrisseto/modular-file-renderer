"""Tabular data renderer module"""
import json
import mfr
import os
import re
from .configuration import config
from .exceptions import TableTooBigException, \
    EmptyTableException, MissingRequirementsException
from mfr.core import RenderResult, get_file_extension, get_assets_from_list

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, 'templates', 'tabular.html')

JS_ASSETS = [
    "jquery-1.7.min.js",
    "jquery.event.drag-2.2.js",
    "slick.core.js",
    "slick.grid.js",
]

CSS_ASSETS = [
    "slick.grid.css",
    #"jquery-ui-1.8.16.custom.css",
    "slick-default-theme.css",
    "examples.css",
]

def render_html(fp, src=None):
    """Render a tabular file to html

    :param fp: file pointer object
    :return: RenderResult object containing html and assets
    """

    columns, rows = populate_data(fp)

    max_size = config['max_size']
    table_width = config['table_width']
    table_height = config['table_height']

    if len(columns) > max_size or len(rows) > max_size:
        raise TableTooBigException("Table is too large to render.")

    if len(columns) < 1 or len(rows) < 1:
        raise EmptyTableException("Table is empty or corrupt.")

    table_size = 'small_table' if len(columns) < 9 else 'big_table'
    slick_grid_options = config.get('slick_grid_options').get(table_size)

    with open(TEMPLATE) as template:
        content = template.read().format(
            width=table_width,
            height=table_height,
            columns=json.dumps(columns),
            rows=json.dumps(rows),
            options=json.dumps(slick_grid_options),
        )

    assets = get_assets()

    return RenderResult(content=content, assets=assets)


def get_assets():
    assets_uri_base = '{0}/tabular'.format(mfr.config['ASSETS_URL'])
    assets = {
        'css': get_assets_from_list(assets_uri_base, 'css', CSS_ASSETS),
        'js': get_assets_from_list(assets_uri_base, 'js', JS_ASSETS),
    }
    return assets

def populate_data(fp):
    """Determine the appropriate library and use it to populate rows and columns

    :param fp: file pointer
    :return: tuple of column headers and row data
    """

    ext = get_file_extension(fp.name)
    function_preference = config['libs'].get(ext)

    for function in function_preference:
        try:
            imported = function()
        except ImportError:
            pass
        else:
            return imported(fp)

    raise MissingRequirementsException('Renderer requirements are not met')
