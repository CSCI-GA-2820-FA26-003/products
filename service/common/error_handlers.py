######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################
"""Convert client and HTTP errors into JSON responses."""

from flask import current_app as app
from werkzeug.exceptions import HTTPException

from service.models import DataValidationError


def error_payload(status_code, error, message):
    """Create the common JSON error body."""
    return {"status": status_code, "error": error, "message": message}


def handle_http_exception(error):
    """Return Flask HTTP errors as JSON and preserve protocol headers."""
    status_code = error.code or 500
    response = error.get_response()
    response.set_data(
        app.json.dumps(error_payload(status_code, error.name, error.description))
    )
    response.content_type = "application/json"

    if status_code >= 500:
        app.logger.error(error.description)
    else:
        app.logger.warning(error.description)

    return response


def handle_restx_http_exception(error):
    """Return RESTX HTTP errors as JSON and preserve protocol headers."""
    status_code = error.code or 500
    response = error.get_response()
    headers = {
        name: value
        for name, value in response.headers.items()
        if name.lower() not in {"content-type", "content-length"}
    }

    if status_code >= 500:
        app.logger.error(error.description)
    else:
        app.logger.warning(error.description)

    return error_payload(status_code, error.name, error.description), status_code, headers


def handle_data_validation_error(error):
    """Treat invalid product input as a client error instead of a server error."""
    message = str(error)
    app.logger.warning(message)
    return error_payload(400, "Bad Request", message), 400


def register_error_handlers(flask_app, api):
    """Register the same JSON error format for Flask and Flask-RESTX routes."""
    flask_app.register_error_handler(HTTPException, handle_http_exception)
    flask_app.register_error_handler(DataValidationError, handle_data_validation_error)
    api.errorhandler(HTTPException)(handle_restx_http_exception)
    api.errorhandler(DataValidationError)(handle_data_validation_error)
