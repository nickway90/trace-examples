
"""
This module serves as an example to integrate with flask, using
the requests library to perform downstream requests
"""
import flask
import requests
import os
import time
import logging

from opentelemetry import trace
from opentelemetry.exporter.otlp.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchExportSpanProcessor
from opentelemetry.sdk.resources import Resource

# Set B3 Propagation for connecting to dd-trace-<lang> instrumented app
# Then enabled B3 Propagation on the dd-trace-<lang> app
# from opentelemetry import propagators
# from opentelemetry.propagators.b3 import B3Format

# propagators.set_global_textmap(B3Format())

from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

resource = Resource(attributes={
    "service.name": "sandbox_test_python",
    "deployment.environment": "otel_sandbox"
})

otlp_exporter = OTLPSpanExporter(insecure=True)
tracer_provider = TracerProvider(resource=resource)
span_processor = BatchExportSpanProcessor(otlp_exporter)

# The preferred tracer implementation must be set, as the opentelemetry-api
# defines the interface with a no-op implementation.
# It must be done before instrumenting any library

tracer_provider.add_span_processor(span_processor)
trace.set_tracer_provider(tracer_provider)

RequestsInstrumentor().instrument()
FlaskInstrumentor().instrument()

app = flask.Flask(__name__)

@app.route("/")
def hello():
    requests.get("http://node-microservice:4000/api")
    return "hello"
