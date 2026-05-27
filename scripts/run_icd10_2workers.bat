@echo off
REM ====================================================================
REM Build ICD-10 Disease KB — 2 worker FPT Cloud song song
REM ====================================================================
REM Cach dung:
REM   set FPT_API_KEY_1=sk-key1
REM   set FPT_API_KEY_2=sk-key2
REM   scripts\run_icd10_2workers.bat
REM
REM Sau khi ca 2 worker DONE:
REM   python scripts\build_disease_kb_from_icd10.py --merge
REM ====================================================================

setlocal

cd /d "c:\NDT\PJ\MediSign_AI - Copy"

if "%FPT_API_KEY_1%"=="" (
    echo [ERROR] Set FPT_API_KEY_1 truoc khi chay.
    echo   set FPT_API_KEY_1=sk-3BOG1D3BWg4Opj6R_jCJ8o15wxKJPVI9xcS8ev_ZCAI=
    exit /b 1
)
if "%FPT_API_KEY_2%"=="" (
    echo [ERROR] Set FPT_API_KEY_2 truoc khi chay.
    echo   set FPT_API_KEY_2=sk-XGiawNT9YjdcWbR7UnrzI6Fe6oGu-xanMkgeX4roqcM=
    exit /b 1
)

echo.
echo [Step 1/3] Pre-downloading ICD-10 codes (chi can 1 lan)...
set PYTHONIOENCODING=utf-8
python -c "import sys; sys.path.insert(0, '.'); from scripts.build_disease_kb_from_icd10 import download_icd10, filter_icd10; codes = filter_icd10(download_icd10()); print(f'Ready: {len(codes)} disease codes after filter')"
if errorlevel 1 (
    echo [ERROR] Download ICD-10 that bai. Kiem tra internet + pip install datasets
    exit /b 1
)

echo.
echo ====================================================================
echo [Step 2/3] KIEM TRA DU LIEU truoc khi launch 2 worker
echo ====================================================================
echo File cache: data\processed\icd10_codes_raw.json
echo.
echo Hay kiem tra cache file. Mau 5 dong dau:
python -c "import json; d=json.load(open('data/processed/icd10_codes_raw.json',encoding='utf-8'))[:5]; [print(f'  {x[\"code\"]}: {x[\"description\"][:80]}') for x in d]"
echo.
echo Tong so codes: 
python -c "import json; print(f'  {len(json.load(open(\"data/processed/icd10_codes_raw.json\",encoding=\"utf-8\")))} codes')"
echo.
echo ====================================================================
echo Neu OK, go 'yes' va Enter de tiep tuc launch 2 worker.
echo Neu khong OK, dong cua so nay (Ctrl+C) va kiem tra file thu cong.
echo ====================================================================
set /p CONFIRM=Nhap 'yes' de tiep tuc: 

if /i not "%CONFIRM%"=="yes" (
    echo Da huy. Khong launch worker.
    exit /b 0
)

echo.
echo [Step 3/3] Launching 2 workers...
echo Launching Worker 0 (Key 1, codes 0..6999 - nua dau)...
start "ICD10-W0" cmd /k "cd /d "c:\NDT\PJ\MediSign_AI - Copy" & set FPT_API_KEY=%FPT_API_KEY_1% & set PYTHONIOENCODING=utf-8 & python scripts\build_disease_kb_from_icd10.py --worker-id 0 --total-workers 2"

echo Launching Worker 1 (Key 2, codes 7000..13999 - nua sau)...
start "ICD10-W1" cmd /k "cd /d "c:\NDT\PJ\MediSign_AI - Copy" & set FPT_API_KEY=%FPT_API_KEY_2% & set PYTHONIOENCODING=utf-8 & python scripts\build_disease_kb_from_icd10.py --worker-id 1 --total-workers 2"

echo.
echo 2 cua so CMD da mo.
echo Moi worker xu ly ~8500 benh (nua ICD-10).
echo ETA: ~3-4 tieng.
echo.
echo SAU KHI CA 2 WORKER XONG, chay:
echo   python scripts\build_disease_kb_from_icd10.py --merge
echo.
echo Ket qua: data\knowledge_base\vietnam_diseases_full.json
echo.

endlocal
