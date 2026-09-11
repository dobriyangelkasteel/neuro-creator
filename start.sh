#!/bin/bash
PYTHONPATH=./packages python3 -m uvicorn neuro_app:app --host=0.0.0.0 --port=8080