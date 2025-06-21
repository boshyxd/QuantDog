#!/usr/bin/env python3
"""Test script to verify all imports work correctly."""

print("Testing QuantDog imports...")

try:
    import streamlit

    print("Streamlit import: OK")
except ImportError as e:
    print(f"Streamlit import failed: {e}")

try:
    import qiskit

    print("Qiskit import: OK")
except ImportError as e:
    print(f"Qiskit import failed: {e}")

try:
    from core import CryptoRouter, HoneypotMonitor, ThreatDetector

    print("Core modules import: OK")
except ImportError as e:
    print(f"Core modules import failed: {e}")

try:
    from utils.config import Config

    print("Config import: OK")
except ImportError as e:
    print(f"Config import failed: {e}")

print("\nTest complete!")
