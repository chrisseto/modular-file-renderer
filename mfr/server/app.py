import asyncio

import tornado.web
import tornado.httpserver
import tornado.platform.asyncio

from mfr import settings
from mfr.core.utils import AioSentryClient
from mfr.server.handlers import render
from mfr.server.handlers import status
from mfr.server import settings as server_settings
from mfr.server.handlers.core import ExtensionsStaticFileHandler


def make_app(debug):
    app = tornado.web.Application(
        [
            (r'/render', render.RenderHandler),
            (r'/status', status.StatusHandler),
            (r'/assets/(.*?)/(.*\..*)', ExtensionsStaticFileHandler),
        ],
        debug=debug,
    )
    # Fix package import
    app.sentry_client = AioSentryClient(settings.get('SENTRY_DSN', None))
    return app


def serve():
    tornado.platform.asyncio.AsyncIOMainLoop().install()

    app = make_app(server_settings.DEBUG)

    ssl_options = None
    if server_settings.SSL_CERT_FILE and server_settings.SSL_KEY_FILE:
        ssl_options = {
            'certfile': server_settings.SSL_CERT_FILE,
            'keyfile': server_settings.SSL_KEY_FILE,
        }

    app.listen(
        server_settings.PORT,
        address=server_settings.ADDRESS,
        xheaders=server_settings.XHEADERS,
        max_buffer_size=server_settings.MAX_BUFFER_SIZE,
        ssl_options=ssl_options,
    )

    asyncio.get_event_loop().set_debug(server_settings.DEBUG)
    asyncio.get_event_loop().run_forever()