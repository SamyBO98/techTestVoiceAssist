# Lance l'agent avec les DLLs CUDA dans le PATH
$env:PATH = "C:\Users\samyb\OneDrive\Bureau\techTestVoiceAssist\venv\Lib\site-packages\nvidia\cublas\bin;C:\Users\samyb\OneDrive\Bureau\techTestVoiceAssist\venv\Lib\site-packages\nvidia\cudnn\bin;" + $env:PATH

# Active le venv si pas déjà actif
if (-not $env:VIRTUAL_ENV) {
    & "C:\Users\samyb\OneDrive\Bureau\techTestVoiceAssist\venv\Scripts\Activate.ps1"
}

# Lance l'agent
python agent.py connect --room test-room