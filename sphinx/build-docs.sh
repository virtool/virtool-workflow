#!/bin/sh

pip install poetry
poetry install --extras docs
make html