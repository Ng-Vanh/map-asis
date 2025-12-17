from flask import request
def init_routes(app):
    @app.api_route("/health", methods=["GET"])
    def health_check():
        return "OK", 200

    @app.api_route("/place_info", methods=["POST"])
    def place_info_route():
        data = request.get_json()
        from app.services.main_service import get_info_details
        return get_info_details(data.get("name"))
