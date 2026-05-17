@echo off
REM Convenience wrapper to run the apps/web_next vitest suite with the
REM correct working directory regardless of the caller's cwd.
REM Forwards any extra args to vitest (e.g. a single test file path).
cd /d "%~dp0" && npx vitest run %*
