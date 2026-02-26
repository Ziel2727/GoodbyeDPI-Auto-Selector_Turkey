@ECHO OFF
PUSHD "%~dp0"
echo =====================================================
echo  GoodbyeDPI Otomatik Konfigurasyon Secici
echo  Bu dosya yonetici olarak calistirilmalidir!
echo  Sag Tik - Yonetici Olarak Calistir
echo =====================================================
echo.

:: Python kontrolü
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [HATA] Python bulunamadi!
    echo Python'u https://www.python.org adresinden indirin.
    echo Kurulum sirasinda "Add Python to PATH" secenegini isaretleyin!
    pause
    exit /b 1
)

:: Yönetici kontrolü
net session >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [!] Yonetici yetkisi gerekiyor...
    echo     Bu dosyaya sag tiklayip "Yonetici Olarak Calistir" secin.
    pause
    exit /b 1
)

:: Scripti çalıştır
python "%~dp0auto_selector.py"
POPD
