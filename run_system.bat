@echo off 
 
echo 🏥 Hospital OS Management System 
echo =============================== 
echo. 
echo Choose an option: 
echo 1. Run C backend demo (if compiled) 
echo 2. Start web interface 
echo 3. Interactive mode (if C compiled) 
echo 4. Help 
echo. 
echo. 
set /p choice="Enter your choice (1-4): " 
 
if "%choice%"=="1" goto demo 
if "%choice%"=="2" goto web 
if "%choice%"=="3" goto interactive 
if "%choice%"=="4" goto help 
goto invalid 
 
:demo 
echo 🚀 Running demonstration... 
cd backend\core\src 
if exist hospital_system.exe ( 
    hospital_system.exe --demo 
) else ( 
    echo ❌ C program not compiled. Please compile first or use web interface. 
) 
cd ..\..\.. 
pause 
goto end 
 
:web 
echo 🌐 Starting web interface... 
echo Open http://localhost:5000 in your browser 
cd backend\api 
python app.py 
cd ..\.. 
goto end 
 
:interactive 
echo 💻 Starting interactive mode... 
cd backend\core\src 
if exist hospital_system.exe ( 
    hospital_system.exe 
) else ( 
    echo ❌ C program not compiled. Please compile first or use web interface. 
) 
cd ..\..\.. 
pause 
goto end 
 
:help 
echo 📖 Help Information: 
echo =================== 
echo. 
echo System Components: 
echo - C Backend: Core OS simulation with scheduling algorithms 
echo - ML Engine: Priority prediction using patient vital signs 
echo - Web Interface: Modern dashboard for patient management 
echo. 
echo Usage: 
echo - Demo mode: Shows all scheduling algorithms with sample data 
echo - Interactive mode: CLI for manual patient entry and testing 
echo - Web interface: Full-featured web application 
echo. 
echo Files: 
echo - README.md: Complete documentation 
echo - backend\core\src\hospital_system.exe: Compiled C program 
echo - backend\api\app.py: Flask web server 
echo - backend\ml_engine\src\ml_predictor.py: ML model 
pause 
goto end 
 
:invalid 
echo Invalid choice 
pause 
 
:end 
