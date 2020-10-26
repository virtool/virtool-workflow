"""Embedded HTTP server for kubernetes liveness checks."""

from aiohttp import web

app = web.Application()


@app.get("/alive")
def is_alive():
    return web.Response(text="alive")


@app.get("/ready")
def is_ready():
    return web.Response(text="ready")


def start_liveness_server(host: str = "localhost", port: int = 8080):
    web.run_app(app, host=host, port=port)


