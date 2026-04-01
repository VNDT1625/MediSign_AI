@echo off
echo Starting 20 parallel workers...
cd /d C:\NDT\PJ\MediSign_AI\scripts

start /b python convert_medical_multi.py 0 20
start /b python convert_medical_multi.py 1 20
start /b python convert_medical_multi.py 2 20
start /b python convert_medical_multi.py 3 20
start /b python convert_medical_multi.py 4 20
start /b python convert_medical_multi.py 5 20
start /b python convert_medical_multi.py 6 20
start /b python convert_medical_multi.py 7 20
start /b python convert_medical_multi.py 8 20
start /b python convert_medical_multi.py 9 20
start /b python convert_medical_multi.py 10 20
start /b python convert_medical_multi.py 11 20
start /b python convert_medical_multi.py 12 20
start /b python convert_medical_multi.py 13 20
start /b python convert_medical_multi.py 14 20
start /b python convert_medical_multi.py 15 20
start /b python convert_medical_multi.py 16 20
start /b python convert_medical_multi.py 17 20
start /b python convert_medical_multi.py 18 20
start /b python convert_medical_multi.py 19 20

echo Started 20 workers!
echo Check progress with: dir C:\NDT\PJ\MediSign_AI\data\training_clean\medical_dialogue_part_*.json
