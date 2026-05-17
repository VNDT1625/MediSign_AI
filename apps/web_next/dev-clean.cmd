@echo off
REM Khoi dong Next.js dev sach va dam bao casing cua duong dan thong nhat.
REM Loi "fallback/pages/_app.js 404 + GET / 500" tren Windows xay ra khi
REM webpack resolve cung mot file voi 2 casing khac nhau (C:\... va c:\...).
REM Fix: ep cwd ve duong dan voi casing chuan (chu hoa o cum drive letter).

setlocal

REM Buoc cwd ve dung casing cua thu muc thuc te tren disk
pushd "%~dp0" >nul

REM Dot sach moi cache co the giu casing cu
if exist .next rmdir /s /q .next
if exist node_modules\.cache rmdir /s /q node_modules\.cache
if exist tsconfig.tsbuildinfo del /q tsconfig.tsbuildinfo

call npm run dev

popd >nul
endlocal
