"""
GPU Diagnostic Script for RTX 5050
Run this to check if your GPU is properly configured
"""

import sys

print("=" * 60)
print("GPU DIAGNOSTIC CHECK")
print("=" * 60)
print()

# Check 1: PyTorch Installation
print("1. Checking PyTorch installation...")
try:
    import torch
    print(f"   ✅ PyTorch installed: {torch.__version__}")
except ImportError:
    print("   ❌ PyTorch not installed!")
    sys.exit(1)

# Check 2: CUDA Availability
print("\n2. Checking CUDA availability...")
if torch.cuda.is_available():
    print(f"   ✅ CUDA is available")
    print(f"   ✅ CUDA version: {torch.version.cuda}")
else:
    print(f"   ❌ CUDA is NOT available")
    print(f"   PyTorch was built with CUDA: {torch.version.cuda}")
    print()
    print("   POSSIBLE CAUSES:")
    print("   - PyTorch was installed without CUDA support")
    print("   - NVIDIA drivers not installed")
    print("   - GPU not detected by system")
    print()
    print("   FIX: Run this command to install PyTorch with CUDA:")
    print("   pip uninstall torch torchvision torchaudio")
    print("   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124")

# Check 3: GPU Detection
print("\n3. Checking GPU detection...")
if torch.cuda.is_available():
    gpu_count = torch.cuda.device_count()
    print(f"   ✅ Number of GPUs detected: {gpu_count}")
    for i in range(gpu_count):
        print(f"   ✅ GPU {i}: {torch.cuda.get_device_name(i)}")
        props = torch.cuda.get_device_properties(i)
        print(f"      - Compute Capability: {props.major}.{props.minor}")
        print(f"      - Total Memory: {props.total_memory / 1024**3:.2f} GB")
else:
    print(f"   ❌ No GPU detected")

# Check 4: NVIDIA Driver
print("\n4. Checking NVIDIA driver...")
try:
    import subprocess
    result = subprocess.run(['nvidia-smi'], capture_output=True, text=True)
    if result.returncode == 0:
        print("   ✅ NVIDIA driver is installed")
        # Extract driver version
        lines = result.stdout.split('\n')
        for line in lines:
            if 'Driver Version' in line:
                print(f"   {line.strip()}")
                break
    else:
        print("   ❌ nvidia-smi command failed")
except FileNotFoundError:
    print("   ❌ nvidia-smi not found - NVIDIA drivers may not be installed")
    print("   Download from: https://www.nvidia.com/Download/index.aspx")

# Check 5: Test GPU Computation
print("\n5. Testing GPU computation...")
if torch.cuda.is_available():
    try:
        # Create a small tensor on GPU
        x = torch.randn(100, 100).cuda()
        y = torch.randn(100, 100).cuda()
        z = torch.matmul(x, y)
        print(f"   ✅ GPU computation successful!")
        print(f"   ✅ Result shape: {z.shape}")
    except Exception as e:
        print(f"   ❌ GPU computation failed: {str(e)[:100]}")
else:
    print(f"   ⏭️  Skipped (no GPU available)")

# Check 6: Transformers Library
print("\n6. Checking transformers library...")
try:
    import transformers
    print(f"   ✅ Transformers installed: {transformers.__version__}")
except ImportError:
    print("   ❌ Transformers not installed!")
    print("   Install with: pip install transformers")

# Check 7: BitsAndBytes (for quantization)
print("\n7. Checking bitsandbytes (optional, for 4-bit quantization)...")
try:
    import bitsandbytes
    print(f"   ✅ BitsAndBytes installed: {bitsandbytes.__version__}")
except ImportError:
    print("   ⚠️  BitsAndBytes not installed (optional)")
    print("   Install with: pip install bitsandbytes")

# Summary
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)

if torch.cuda.is_available():
    print("✅ Your system is ready to use GPU!")
    print(f"✅ GPU: {torch.cuda.get_device_name(0)}")
    print()
    print("Next steps:")
    print("1. Start your backend: uvicorn main:app --reload")
    print("2. Look for: '✅ Model loaded on GPU in float16'")
else:
    print("❌ GPU is not available. Your model will run on CPU.")
    print()
    print("To enable GPU:")
    print("1. Install/update NVIDIA drivers")
    print("2. Reinstall PyTorch with CUDA support:")
    print("   pip uninstall torch torchvision torchaudio")
    print("   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124")
    print("3. Run this script again to verify")

print("=" * 60)
