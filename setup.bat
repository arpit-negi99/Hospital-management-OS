@echo off
REM Hospital OS Management System - Windows Setup Script
REM This script automates the complete setup process for Windows

echo.
echo 🏥 Hospital OS Management System - Enhanced Windows Setup
echo ==============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python 3 is required but not installed
    echo Please install Python 3.7+ from https://python.org and try again
    pause
    exit /b 1
)

REM Check if pip is installed
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip is required but not installed
    echo Please install pip and try again
    pause
    exit /b 1
)

echo ✅ Prerequisites check passed
echo.

REM Create necessary directories
echo 📁 Creating project directories...
if not exist "backend\ml_engine\models" mkdir backend\ml_engine\models
if not exist "backend\ml_engine\data" mkdir backend\ml_engine\data
if not exist "build" mkdir build
if not exist "logs" mkdir logs
echo ✅ Directories created
echo.

REM Install Python dependencies
echo 📦 Installing Python dependencies...
pip install flask flask-cors pandas scikit-learn joblib numpy matplotlib
if errorlevel 1 (
    echo ❌ Failed to install Python dependencies
    echo Please check your pip installation and try again
    pause
    exit /b 1
)
echo ✅ Python dependencies installed
echo.

REM Train ML model
echo 🤖 Training Machine Learning model...
cd backend\ml_engine\src
python ml_predictor.py train
if errorlevel 1 (
    echo ❌ Failed to train ML model
    cd ..\..\..
    pause
    exit /b 1
)
cd ..\..\..
echo ✅ ML model trained successfully
echo.

REM Generate sample data CSV for C program
echo 📊 Generating sample patient data for C program...
echo patient_id,arrival_time,burst_time,priority,age,heart_rate,blood_pressure_systolic,blood_pressure_diastolic,temperature,respiratory_rate,oxygen_saturation,pain_level,chest_pain,breathing_difficulty,consciousness_level,bleeding_severity,predicted_priority,emergency_level > backend\ml_engine\data\patients_for_c.csv
echo 1,0,25,1,65,140,190.0,110.0,39.5,32,85,9,5,4,2,3,1.0,CRITICAL >> backend\ml_engine\data\patients_for_c.csv
echo 2,2,20,2,45,110,160.0,95.0,38.2,25,92,7,3,3,4,2,2.0,HIGH >> backend\ml_engine\data\patients_for_c.csv
echo 3,4,15,3,35,90,130.0,85.0,37.2,20,96,5,2,1,5,1,3.0,MEDIUM >> backend\ml_engine\data\patients_for_c.csv
echo 4,6,10,4,28,75,120.0,80.0,36.8,16,98,3,1,0,5,0,4.0,LOW >> backend\ml_engine\data\patients_for_c.csv
echo 5,8,12,3,42,88,125.0,82.0,37.0,18,97,4,2,1,4,1,3.0,MEDIUM >> backend\ml_engine\data\patients_for_c.csv
echo ✅ Sample data generated
echo.

REM Check if MinGW/GCC is available
gcc --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  GCC compiler not found in PATH
    echo You can still use the web interface, but C compilation will need manual setup
    echo Install MinGW-w64 or TDM-GCC and add to PATH for C compilation
    echo.
) else (
    echo ✅ GCC compiler found
    echo 🔧 Attempting to compile C backend...

    cd backend\core\src

    REM Copy original source files to current directory for compilation
    copy ..\..\..\scheduler_fcfs.c . >nul 2>&1
    copy ..\..\..\scheduler_priority.c . >nul 2>&1
    copy ..\..\..\scheduler_rr.c . >nul 2>&1
    copy ..\..\..\scheduler_mlfq.c . >nul 2>&1
    copy ..\..\..\bankers_algorithm.c . >nul 2>&1
    copy ..\..\..\resource_manager.c . >nul 2>&1
    copy ..\..\..\logger.c . >nul 2>&1
    copy ..\..\..\ipc_handler.c . >nul 2>&1
    copy ..\..\..\synchronization.c . >nul 2>&1

    gcc -o hospital_system.exe main.c patient_manager.c scheduler_fcfs.c scheduler_priority.c scheduler_rr.c scheduler_mlfq.c bankers_algorithm.c resource_manager.c logger.c ipc_handler.c synchronization.c -I..\include -lm

    if exist hospital_system.exe (
        echo ✅ C backend compiled successfully
    ) else (
        echo ⚠️  C compilation failed, but web interface will still work
    )

    cd ..\..\..
)
echo.

REM Create Windows run script
echo 🪟 Creating Windows run script...
echo @echo off > run_system.bat
echo. >> run_system.bat
echo echo 🏥 Hospital OS Management System >> run_system.bat
echo echo =============================== >> run_system.bat
echo echo. >> run_system.bat
echo echo Choose an option: >> run_system.bat
echo echo 1. Run C backend demo ^(if compiled^) >> run_system.bat
echo echo 2. Start web interface >> run_system.bat
echo echo 3. Interactive mode ^(if C compiled^) >> run_system.bat
echo echo 4. Help >> run_system.bat
echo echo. >> run_system.bat
echo echo. >> run_system.bat
echo set /p choice="Enter your choice (1-4): " >> run_system.bat
echo. >> run_system.bat
echo if "%%choice%%"=="1" goto demo >> run_system.bat
echo if "%%choice%%"=="2" goto web >> run_system.bat
echo if "%%choice%%"=="3" goto interactive >> run_system.bat
echo if "%%choice%%"=="4" goto help >> run_system.bat
echo goto invalid >> run_system.bat
echo. >> run_system.bat
echo :demo >> run_system.bat
echo echo 🚀 Running demonstration... >> run_system.bat
echo cd backend\core\src >> run_system.bat
echo if exist hospital_system.exe ^( >> run_system.bat
echo     hospital_system.exe --demo >> run_system.bat
echo ^) else ^( >> run_system.bat
echo     echo ❌ C program not compiled. Please compile first or use web interface. >> run_system.bat
echo ^) >> run_system.bat
echo cd ..\..\.. >> run_system.bat
echo pause >> run_system.bat
echo goto end >> run_system.bat
echo. >> run_system.bat
echo :web >> run_system.bat
echo echo 🌐 Starting web interface... >> run_system.bat
echo echo Open http://localhost:5000 in your browser >> run_system.bat
echo cd backend\api >> run_system.bat
echo python app.py >> run_system.bat
echo cd ..\.. >> run_system.bat
echo goto end >> run_system.bat
echo. >> run_system.bat
echo :interactive >> run_system.bat
echo echo 💻 Starting interactive mode... >> run_system.bat
echo cd backend\core\src >> run_system.bat
echo if exist hospital_system.exe ^( >> run_system.bat
echo     hospital_system.exe >> run_system.bat
echo ^) else ^( >> run_system.bat
echo     echo ❌ C program not compiled. Please compile first or use web interface. >> run_system.bat
echo ^) >> run_system.bat
echo cd ..\..\.. >> run_system.bat
echo pause >> run_system.bat
echo goto end >> run_system.bat
echo. >> run_system.bat
echo :help >> run_system.bat
echo echo 📖 Help Information: >> run_system.bat
echo echo =================== >> run_system.bat
echo echo. >> run_system.bat
echo echo System Components: >> run_system.bat
echo echo - C Backend: Core OS simulation with scheduling algorithms >> run_system.bat
echo echo - ML Engine: Priority prediction using patient vital signs >> run_system.bat
echo echo - Web Interface: Modern dashboard for patient management >> run_system.bat
echo echo. >> run_system.bat
echo echo Usage: >> run_system.bat
echo echo - Demo mode: Shows all scheduling algorithms with sample data >> run_system.bat
echo echo - Interactive mode: CLI for manual patient entry and testing >> run_system.bat
echo echo - Web interface: Full-featured web application >> run_system.bat
echo echo. >> run_system.bat
echo echo Files: >> run_system.bat
echo echo - README.md: Complete documentation >> run_system.bat
echo echo - backend\core\src\hospital_system.exe: Compiled C program >> run_system.bat
echo echo - backend\api\app.py: Flask web server >> run_system.bat
echo echo - backend\ml_engine\src\ml_predictor.py: ML model >> run_system.bat
echo pause >> run_system.bat
echo goto end >> run_system.bat
echo. >> run_system.bat
echo :invalid >> run_system.bat
echo echo Invalid choice >> run_system.bat
echo pause >> run_system.bat
echo. >> run_system.bat
echo :end >> run_system.bat

echo ✅ Windows run script created: run_system.bat
echo.

echo 🎉 Setup Complete!
echo =================
echo.
echo Your enhanced Hospital OS Management System is ready!
echo.
echo Quick Start:
echo 1. Run the system:         run_system.bat
echo 2. Start web interface:    run_system.bat (option 2)
echo.
echo Or use individual commands:
echo - Web Interface:           cd backend\api ^&^& python app.py
echo - Train ML Model:          cd backend\ml_engine\src ^&^& python ml_predictor.py train
echo.
echo 📖 Read README.md for complete documentation
echo 🌐 Web interface will be available at: http://localhost:5000
echo.
echo ✨ Happy learning with OS concepts and ML integration!
echo.
pause
