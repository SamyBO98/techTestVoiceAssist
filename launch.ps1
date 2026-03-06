# Run agent with CUDA DLLs in the PATH
$env:PATH = "C:\Users\samyb\OneDrive\Bureau\techTestVoiceAssist\venv\Lib\site-packages\nvidia\cublas\bin;C:\Users\samyb\OneDrive\Bureau\techTestVoiceAssist\venv\Lib\site-packages\nvidia\cudnn\bin;" + $env:PATH

# Activate venv if not already active
if (-not $env:VIRTUAL_ENV) {
    & "C:\Users\samyb\OneDrive\Bureau\techTestVoiceAssist\venv\Scripts\Activate.ps1"
}

# Run agent
python agent.py connect --room test-room