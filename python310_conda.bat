@echo off
setlocal enabledelayedexpansion

set "LOG_FILE=install.log"
call :log "Starting install"

where conda >nul 2>&1
if errorlevel 1 (
	call :log "Error: conda was not found on PATH."
	exit /b 1
)

where python >nul 2>&1
if errorlevel 1 (
	call :log "Error: python was not found on PATH."
	exit /b 1
)

if not defined CONDA_DEFAULT_ENV (
	call :log "Warning: no conda environment appears to be active."
) else (
	if /i "%CONDA_DEFAULT_ENV%"=="base" (
		call :log "Warning: base environment is active."
	)
)

where nvidia-smi >nul 2>&1
if errorlevel 1 (
	call :log "Warning: nvidia-smi not found. GPU/CUDA may be unavailable."
) else (
	nvidia-smi >nul 2>&1
	if errorlevel 1 (
		call :log "Warning: nvidia-smi failed to run. GPU/CUDA may be unavailable."
	) else (
		call :log "Detected NVIDIA tools (nvidia-smi)."
	)
)

set "CUDA_VER="
set "CUDA_MM="
for /f "tokens=2" %%A in ('conda list cudatoolkit ^| findstr /R "^cudatoolkit"') do set "CUDA_VER=%%A"
if defined CUDA_VER (
	for /f "tokens=1-2 delims=." %%A in ("!CUDA_VER!") do set "CUDA_MM=%%A.%%B"
	call :log "Detected cudatoolkit !CUDA_VER! (pinning to !CUDA_MM!.*)"
) else (
	call :log "No cudatoolkit detected. Installing CuPy without a cudatoolkit pin."
)

set "CUPY_INSTALL_CMD=conda install -y conda-forge::cupy"
if defined CUDA_MM set "CUPY_INSTALL_CMD=!CUPY_INSTALL_CMD! conda-forge::cudatoolkit=!CUDA_MM!.*"
call :run_with_retry "!CUPY_INSTALL_CMD!" "Install CuPy" 3
if errorlevel 1 exit /b 1

call :run_with_retry "python -m pip install -r requirements.txt" "Install Python requirements" 3
if errorlevel 1 exit /b 1

call :log "Done."
endlocal
exit /b 0

:run_with_retry
set "CMD=%~1"
set "LABEL=%~2"
set "MAX_RETRIES=%~3"
set /a "TRY=1"

:retry_loop
call :log "%LABEL% (attempt !TRY! of !MAX_RETRIES!)"
call %CMD%
if errorlevel 1 (
	if !TRY! GEQ !MAX_RETRIES! (
		call :log "Error: %LABEL% failed after !MAX_RETRIES! attempts."
		exit /b 1
	)
	set /a "TRY+=1"
	call :log "Retrying..."
	goto :retry_loop
)
call :log "%LABEL% succeeded."
exit /b 0

:log
set "MSG=%~1"
echo %DATE% %TIME% %MSG%
echo %DATE% %TIME% %MSG%>>"%LOG_FILE%"
exit /b 0