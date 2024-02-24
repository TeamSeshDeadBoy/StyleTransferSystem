#!/bin/bash
set -m
cd src
rq worker --url redis://redis:6379 &
python3 main.py