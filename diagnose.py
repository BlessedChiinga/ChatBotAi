import sys
import subprocess
from pathlib import Path
from importlib.metadata import version, PackageNotFoundError

print("=" * 55)
print(" TRANSFORMER CHATBOT - ENVIRONMENT DIAGNOSTIC")
print("=" * 55)

print("\n--- PYTHON ENVIRONMENT ---")
print("Python:", sys.version.split()[0])
print("Executable:", sys.executable)

packages = {
    "torch": "torch",
    "transformers": "transformers",
    "sentence-transformers": "sentence_transformers",
    "faiss-cpu": "faiss",
    "streamlit": "streamlit",
    "PyMuPDF": "fitz",
    "numpy": "numpy",
    "pandas": "pandas",
    "accelerate": "accelerate",
    "safetensors": "safetensors",
    "huggingface-hub": "huggingface_hub",
    "pytest": "pytest",
}

print("\n--- PACKAGE VERSIONS ---")

for package, module in packages.items():
    try:
        installed_version = version(package)
    except PackageNotFoundError:
        print(f"[MISSING] {package}")
        continue

    try:
        __import__(module)
        print(f"[OK] {package}: {installed_version}")
    except Exception as error:
        print(f"[IMPORT ERROR] {package}: {installed_version}")
        print(f"  {type(error).__name__}: {error}")

print("\n--- TRANSFORMERS MODEL SUPPORT ---")

try:
    from transformers import AutoTokenizer, AutoModelForCausalLM
    print("[OK] AutoTokenizer")
    print("[OK] AutoModelForCausalLM")
except Exception as error:
    print(f"[ERROR] {type(error).__name__}: {error}")

print("\n--- PYTORCH TEST ---")

try:
    import torch
    print("Version:", torch.__version__)
    print("Random tensor:")
    print(torch.rand(2, 3))
    print("[OK] PyTorch calculation works")
except Exception as error:
    print(f"[ERROR] {type(error).__name__}: {error}")

print("\n--- LOCAL QWEN MODEL CACHE ---")

try:
    from huggingface_hub import constants

    cache = Path(constants.HF_HUB_CACHE)
    model_cache = cache / "models--Qwen--Qwen2.5-1.5B-Instruct"

    print("Cache directory:", cache)
    if model_cache.exists():
        print("[FOUND] Qwen model cache directory")

        snapshots = model_cache / "snapshots"
        if snapshots.exists():
            for snapshot in snapshots.iterdir():
                config = snapshot / "config.json"
                weights = list(snapshot.glob("*.safetensors"))
                if config.exists():
                    print("Snapshot:", snapshot.name)
                    print("Config present: Yes")
                    print("Safetensors files:", len(weights))
    else:
        print("[NOT FOUND] Qwen model in default cache")
        print("It may be stored elsewhere or not downloaded.")
except Exception as error:
    print(f"[CHECK ERROR] {type(error).__name__}: {error}")

print("\n--- DEPENDENCY CHECK ---")

try:
    result = subprocess.run(
        [sys.executable, "-m", "pip", "check"],
        capture_output=True,
        text=True,
        timeout=60
    )
    print(result.stdout.strip() or "No dependency issues reported.")
    if result.returncode != 0 and result.stderr:
        print(result.stderr.strip())
except Exception as error:
    print(f"[CHECK ERROR] {error}")

print("\n--- END OF DIAGNOSTIC ---")
print("Send the complete output for comparison.")