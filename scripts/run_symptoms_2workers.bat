@echo off
REM ====================================================================
REM Generate Vietnamese symptom phrases — 2 worker song song
REM ====================================================================
REM Target: ~3000 cum tu trong ~12-15 phut
REM
REM Cach dung:
REM   set FPT_API_KEY_1=sk-key1
REM   set FPT_API_KEY_2=sk-key2
REM   scripts\run_symptoms_2workers.bat
REM ====================================================================

setlocal

cd /d "c:\NDT\PJ\MediSign_AI - Copy"

if "%FPT_API_KEY_1%"=="" (
    echo [ERROR] Set FPT_API_KEY_1 truoc khi chay.
    exit /b 1
)
if "%FPT_API_KEY_2%"=="" (
    echo [ERROR] Set FPT_API_KEY_2 truoc khi chay.
    exit /b 1
)

echo Cleaning old symptom worker files (giu nguyen symptom_phrases.json chinh)...
if exist data\knowledge_base\vietnamese_symptom_phrases_w0.json del /q data\knowledge_base\vietnamese_symptom_phrases_w0.json
if exist data\knowledge_base\vietnamese_symptom_phrases_w1.json del /q data\knowledge_base\vietnamese_symptom_phrases_w1.json

echo.
echo Launching Worker 0 (1500 symptoms)...
start "SymptomW0" cmd /k "cd /d "c:\NDT\PJ\MediSign_AI - Copy" & set FPT_API_KEY=%FPT_API_KEY_1% & set PYTHONIOENCODING=utf-8 & python scripts\gen_rag_kb_data.py --target symptoms --symptoms-count 1500 --worker-id 0"

echo Launching Worker 1 (1500 symptoms)...
start "SymptomW1" cmd /k "cd /d "c:\NDT\PJ\MediSign_AI - Copy" & set FPT_API_KEY=%FPT_API_KEY_2% & set PYTHONIOENCODING=utf-8 & python scripts\gen_rag_kb_data.py --target symptoms --symptoms-count 1500 --worker-id 1"

echo.
echo 2 cua so CMD da mo, moi worker target 1500 cum tu (categories khac nhau).
echo ETA: ~12-15 phut.
echo.
echo SAU KHI CA 2 WORKER XONG, chay:
echo   python scripts\merge_kb_workers.py
echo.

endlocal
