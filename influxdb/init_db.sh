#!/bin/bash
influx setup --username admin --password admin123 \
    --org drone-org --bucket telemetry --retention 1w --force
