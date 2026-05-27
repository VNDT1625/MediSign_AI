@echo off
REM ====================================================================
REM Generate RAG KB data — 2 worker FPT Cloud song song
REM ====================================================================
REM Cach dung:
REM   set FPT_API_KEY_1=sk-key1
REM   set FPT_API_KEY_2=sk-key2
REM   scripts\run_kb_2workers.bat
REM ====================================================================

setlocal

cd /d "c:\NDT\PJ\MediSign_AI - Copy"

if "%FPT_API_KEY_1%"=="" (
    echo [ERROR] Set FPT_API_KEY_1 truoc khi chay bat.
    echo   set FPT_API_KEY_1=sk-3BOG1D3BWg4Opj6R_jCJ8o15wxKJPVI9xcS8ev_ZCAI=
    exit /b 1
)
if "%FPT_API_KEY_2%"=="" (
    echo [ERROR] Set FPT_API_KEY_2 truoc khi chay bat.
    echo   set FPT_API_KEY_2=sk-XGiawNT9YjdcWbR7UnrzI6Fe6oGu-xanMkgeX4roqcM=
    exit /b 1
)

echo Cleaning old worker files...
if exist data\knowledge_base\vietnam_common_diseases_w0.json del /q data\knowledge_base\vietnam_common_diseases_w0.json
if exist data\knowledge_base\vietnam_common_diseases_w1.json del /q data\knowledge_base\vietnam_common_diseases_w1.json
if exist data\knowledge_base\vietnamese_symptom_phrases_w0.json del /q data\knowledge_base\vietnamese_symptom_phrases_w0.json
if exist data\knowledge_base\vietnamese_symptom_phrases_w1.json del /q data\knowledge_base\vietnamese_symptom_phrases_w1.json

echo.
echo Launching Worker 0 (Key 1, even categories)...
start "KBWorker-0" cmd /k "cd /d "c:\NDT\PJ\MediSign_AI - Copy" & set FPT_API_KEY=%FPT_API_KEY_1% & set PYTHONIOENCODING=utf-8 & python scripts\gen_rag_kb_data.py --target all --diseases-count 500 --symptoms-count 400 --worker-id 0"

echo Launching Worker 1 (Key 2, odd categories)...
start "KBWorker-1" cmd /k "cd /d "c:\NDT\PJ\MediSign_AI - Copy" & set FPT_API_KEY=%FPT_API_KEY_2% & set PYTHONIOENCODING=utf-8 & python scripts\gen_rag_kb_data.py --target all --diseases-count 500 --symptoms-count 400 --worker-id 1"

echo.
echo 2 cua so CMD da mo. Theo doi progress trong tung cua so.
echo.
echo SAU KHI CA 2 WORKER XONG, chay:
echo   python scripts\merge_kb_workers.py
echo.

endlocal
