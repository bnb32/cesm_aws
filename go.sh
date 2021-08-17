#!/bin/bash

echo "Mounting storage"

bash ./scripts/storage.sh

echo "Downloading cesm"

python ./scripts/init_cesm.py

echo "Installing packages"

python ./scripts/init_env.py
