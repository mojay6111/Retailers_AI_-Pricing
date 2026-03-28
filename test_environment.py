import sys

print("Python version:", sys.version)

# Core ML
import torch
import lightgbm
import sklearn
import optuna
import skopt

# Data
import numpy
import pandas

# Utilities
import joblib
import boto3
import dotenv
import redis

# API
import flask
import flask_cors
import waitress

print("\nAll imports successful ✅")

# Torch test
print("\nTorch version:", torch.__version__)
print("CUDA available:", torch.cuda.is_available())

# Simple tensor test
x = torch.tensor([1.0, 2.0, 3.0])
print("Tensor test:", x)

print("\nEnvironment verification complete 🚀")
