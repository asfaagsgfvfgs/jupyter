import os
import sys
import subprocess

def check_gpu():
    print("="*50)
    print("Checking GPU availability...")
    print("="*50)
    
    # Check PyTorch GPU
    try:
        import torch
        print(f"[PyTorch] GPU Available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"[PyTorch] Device Count: {torch.cuda.device_count()}")
            for i in range(torch.cuda.device_count()):
                print(f"          Device {i}: {torch.cuda.get_device_name(i)}")
    except ImportError:
        print("[PyTorch] Not installed. Skipping PyTorch GPU check.")
    except Exception as e:
        print(f"[PyTorch] Error checking GPU: {e}")

    print("-" * 50)

    # Check TensorFlow GPU
    try:
        import tensorflow as tf
        # Suppress TensorFlow logging warnings
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
        
        gpus = tf.config.list_physical_devices('GPU')
        print(f"[TensorFlow] GPU Available: {len(gpus) > 0}")
        if gpus:
            for i, gpu in enumerate(gpus):
                print(f"             Device {i}: {gpu.name}")
    except ImportError:
        print("[TensorFlow] Not installed. Skipping TensorFlow GPU check.")
    except Exception as e:
        print(f"[TensorFlow] Error checking GPU: {e}")
        
    print("="*50)

def run_jupyter():
    print("\nStarting Jupyter Notebook Server...")
    
    # Environment variables to optimize GPU allocation could be set here
    # Example: os.environ['CUDA_VISIBLE_DEVICES'] = '0'
    
    try:
        # Launch Jupyter Notebook
        subprocess.run([
            sys.executable, "-m", "jupyter", "notebook",
            "--allow-root", 
            "--ip=0.0.0.0", 
            "--port=8888",
            "--no-browser"
        ])
    except KeyboardInterrupt:
        print("\n[INFO] Jupyter Notebook stopped by user.")
    except Exception as e:
        print(f"\n[ERROR] Failed to start Jupyter: {e}")

if __name__ == "__main__":
    check_gpu()
    run_jupyter()
