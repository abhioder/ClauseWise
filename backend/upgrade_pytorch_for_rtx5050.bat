@echo off
echo ========================================
echo PyTorch Upgrade for RTX 5050 Support
echo ========================================
echo.
echo This will upgrade PyTorch to support your RTX 5050 GPU
echo Current PyTorch only supports up to sm_90, but RTX 5050 needs sm_120
echo.
echo Press Ctrl+C to cancel, or
pause

echo.
echo Step 1: Uninstalling old PyTorch...
pip uninstall -y torch torchvision torchaudio

echo.
echo Step 2: Installing PyTorch with CUDA 12.4 support...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

echo.
echo Step 3: Verifying installation...
python -c "import torch; print(f'PyTorch version: {torch.__version__}'); print(f'CUDA available: {torch.cuda.is_available()}'); print(f'CUDA version: {torch.version.cuda if torch.cuda.is_available() else \"N/A\"}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"

echo.
echo ========================================
echo Upgrade complete!
echo ========================================
echo.
echo Now restart your backend with: uvicorn main:app --reload
echo.
pause
