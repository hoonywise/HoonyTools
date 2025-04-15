@echo off
chcp 65001 >nul

echo.
echo ==========================
echo  HoonyTools Build Script
echo ==========================
echo PYTHON VERSION IN USE:
python --version

echo Terminating any running HoonyTools.exe...
taskkill /f /im HoonyTools.exe >nul 2>&1

echo 🧹 Cleaning previous build folders...
del /q HoonyTools.spec >nul 2>&1
rmdir /s /q build >nul 2>&1
rmdir /s /q dist >nul 2>&1

echo 🔁 Restoring runw.exe with Hoonywise icon...
copy /y "pyinstaller\bootloader\build\releasew\runw.exe" ^
        "%LocalAppData%\Programs\Python\Python313\Lib\site-packages\PyInstaller\bootloader\Windows-64bit-intel\runw.exe" >nul

echo 🔨 Building EXE...
pyinstaller ^
  --noconfirm ^
  --windowed ^
  --onefile ^
  --name HoonyTools ^
  --icon=assets\hoonywise_gui.ico ^
  --add-data "assets;assets" ^
  --add-data "libs;libs" ^
  --add-data "loaders;loaders" ^
  --add-data "tools;tools" ^
  launcher_gui.py

echo.
echo ==========================
echo  ✅ Build complete!
echo  📦 Your EXE is in dist\HoonyTools.exe
echo ==========================

pause
