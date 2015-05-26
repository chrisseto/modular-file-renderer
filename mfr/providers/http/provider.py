import os
import asyncio
import hashlib
from urllib.parse import urlparse

import aiohttp

from mfr.core import provider
from mfr.core import streams


class HttpProvider(provider.BaseProvider):

    @asyncio.coroutine
    def metadata(self):
        path = urlparse(self.url).path
        _, ext = os.path.splitext(os.path.split(path)[-1])
        unique_key = hashlib.sha256(self.url.encode('utf-8')).hexdigest()
        return ext, unique_key

    @asyncio.coroutine
    def download(self):
        response = yield from aiohttp.request('GET', self.url)
        return streams.ResponseStreamReader(response)