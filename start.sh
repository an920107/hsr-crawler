#!/bin/bash
source .venv/bin/activate
uvicorn main:app --root-path="/hsr" --host="127.0.0.1" --port=13080 --reload
