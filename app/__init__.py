from flask import Flask # type: ignore
from app.routes import register_routes
API_PREFIX = "/api/v1"

def create_app():
    app = Flask(__name__)
    def api_route(rule, **options):
        rule = f"{API_PREFIX}{rule}"
        return app.route(rule, **options)

    app.api_route = api_route

    register_routes(app)
    return app
