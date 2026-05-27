@echo off
setlocal

cd /d "c:\NDT\PJ\MediSign_AI - Copy"

echo Xoa file part cu neu co...
if exist data\training_clean\medgemma_4b\psychology_part_0.jsonl del /q data\training_clean\medgemma_4b\psychology_part_0.jsonl
if exist data\training_clean\medgemma_4b\psychology_part_1.jsonl del /q data\training_clean\medgemma_4b\psychology_part_1.jsonl
if exist .regenerate_psych_progress_w0.json del /q .regenerate_psych_progress_w0.json
if exist .regenerate_psych_progress_w1.json del /q .regenerate_psych_progress_w1.json

echo.
echo Launching Worker 0 (Key 1)...
start "PsychWorker-0" cmd /k "cd /d "c:\NDT\PJ\MediSign_AI - Copy" & set FPT_API_KEY=sk-3BOG1D3BWg4Opj6R_jCJ8o15wxKJPVI9xcS8ev_ZCAI= & set PYTHONIOENCODING=utf-8 & python scripts\regenerate_psychology_data.py --target 750 --batch 20 --model gemma-3-27b-it --worker-id 0"

echo Launching Worker 1 (Key 2)...
start "PsychWorker-1" cmd /k "cd /d "c:\NDT\PJ\MediSign_AI - Copy" & set FPT_API_KEY=sk-XGiawNT9YjdcWbR7UnrzI6Fe6oGu-xanMkgeX4roqcM= & set PYTHONIOENCODING=utf-8 & python scripts\regenerate_psychology_data.py --target 750 --batch 20 --model gemma-3-27b-it --worker-id 1"

echo.
echo 2 cua so CMD da mo.
echo Theo doi progress trong tung cua so.
echo.
echo SAU KHI CA 2 WORKER XONG, chay:
echo   python scripts\regenerate_psychology_data.py --merge 2
echo.

endlocal
