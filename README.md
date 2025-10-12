# Hospital OS Management System Enhanced - FIXED VERSION

A comprehensive hospital patient management system that combines Operating System concepts with Machine Learning for intelligent patient priority prediction and queue management.

**🔧 FIXES IN THIS VERSION:**
- ✅ Fixed missing `data` directory creation in ML engine
- ✅ Added Windows-compatible setup scripts (.bat files)
- ✅ Improved error handling for missing directories
- ✅ Better path resolution for C compilation
- ✅ Enhanced ML model with directory checks

## 🏥 Features

### Core OS Concepts
- **Multiple Scheduling Algorithms**: FCFS, Priority, Round Robin, Multi-Level Feedback Queue
- **Resource Management**: Banker's Algorithm for deadlock avoidance
- **Process Synchronization**: Inter-process communication simulation
- **Memory Management**: Dynamic patient data structures

### Machine Learning Integration
- **Priority Prediction**: ML model trained on patient vital signs and symptoms
- **Real-time Analysis**: Instant priority calculation based on 12+ health parameters
- **Confidence Scoring**: Prediction confidence levels for medical staff guidance

### Web Interface
- **Interactive Dashboard**: Real-time system statistics and patient queue
- **Patient Admission Form**: Comprehensive vital signs input with ML prediction
- **Visualization**: Charts for priority distribution and algorithm comparison
- **Responsive Design**: Mobile-friendly interface for healthcare professionals

## 🚀 Quick Start (Windows)

### Prerequisites
```bash
# Required software
- Python 3.7+ (from python.org)
- MinGW-w64 or TDM-GCC compiler (for C compilation)
- Web browser (Chrome, Firefox, Edge)
```

### Installation

1. **Extract the project** to any directory

2. **Run the automated setup:**
   ```cmd
   setup.bat
   ```

   This will:
   - Install Python dependencies
   - Train the ML model
   - Create necessary directories
   - Compile the C backend (if GCC available)

3. **Run the system:**
   ```cmd
   run_system.bat
   ```

### Manual Installation (if setup.bat fails)

1. **Install Python dependencies:**
   ```cmd
   pip install flask flask-cors pandas scikit-learn joblib numpy matplotlib
   ```

2. **Train ML model:**
   ```cmd
   cd backend\ml_engine\src
   python ml_predictor.py train
   cd ..\..\..
   ```

3. **Start web interface:**
   ```cmd
   cd backend\api
   python app.py
   ```

4. **Open browser to:**
   ```
   http://localhost:5000
   ```

## 🖥️ Usage Options

### Option 1: Web Interface (Recommended)
- Modern dashboard with real-time updates
- Interactive patient admission with ML prediction
- Visual queue management and statistics
- OS simulation comparison tools

### Option 2: C Command Line (If compiled)
```cmd
cd backend\core\src
hospital_system.exe --demo    # Run demonstration
hospital_system.exe          # Interactive mode
```

## 📊 ML Model Details

### Input Parameters (12 features):
- **Demographics**: Age
- **Vital Signs**: Heart Rate, Blood Pressure, Temperature, Respiratory Rate, Oxygen Saturation
- **Pain Assessment**: Pain Level (1-10)
- **Symptoms**: Chest Pain, Breathing Difficulty, Consciousness Level, Bleeding Severity

### Output:
- **Priority**: 1 (Critical), 2 (High), 3 (Medium), 4 (Low)
- **Confidence**: Prediction confidence (0-100%)
- **Emergency Level**: Text classification

### Model Performance:
- **Algorithm**: Random Forest Classifier
- **Accuracy**: ~99.75% on test data
- **Training**: 2000+ synthetic patient records

## 🛠️ Troubleshooting

### Common Issues:

1. **"Cannot save file into a non-existent directory: 'data'"**
   - Fixed in this version! The setup script creates all required directories
   - If still occurs, manually create: `backend\ml_engine\data`

2. **Python package not found**
   ```cmd
   pip install --upgrade pip
   pip install flask flask-cors pandas scikit-learn joblib numpy matplotlib
   ```

3. **C compilation fails**
   - The web interface will still work without C compilation
   - Install MinGW-w64: https://www.mingw-w64.org/downloads/
   - Add to PATH environment variable

4. **Web interface not loading**
   - Check if Flask is running: look for "Running on http://127.0.0.1:5000"
   - Try different browser
   - Check firewall settings

### File Structure Check:
```
Hospital-OS-Management-System/
├── backend/
│   ├── ml_engine/
│   │   ├── data/           ← Should exist after setup
│   │   ├── models/         ← Created during ML training
│   │   └── src/
│   ├── core/src/           ← C source files
│   └── api/                ← Flask web server
└── frontend/               ← Web interface files
```

## 📁 Project Components

### Backend (C)
- **Enhanced Patient Structure**: 18+ fields with medical parameters
- **Scheduling Algorithms**: Four different implementations
- **Resource Management**: Banker's algorithm for deadlock prevention
- **Interactive CLI**: Menu-driven patient management

### ML Engine (Python)
- **Random Forest Model**: Medical priority classification
- **Feature Engineering**: Normalized vital sign processing
- **Model Persistence**: Trained models saved automatically
- **Fallback System**: Basic priority calculation if ML unavailable

### Web Interface
- **Dashboard**: Real-time system statistics
- **Patient Forms**: Comprehensive medical data entry
- **Queue Display**: Priority-sorted patient management
- **Simulation Tools**: OS algorithm comparison

## 🎓 Educational Value

This project demonstrates:
- **Operating System Concepts**: Process scheduling, resource management, IPC
- **Machine Learning**: Classification, model training, feature engineering  
- **Web Development**: Full-stack application with REST APIs
- **System Integration**: Multi-language project coordination

## 📞 Support

If you encounter issues:
1. Run `setup.bat` first to ensure proper installation
2. Check that all directories exist (especially `backend\ml_engine\data`)
3. Verify Python packages are installed
4. Try the web interface even if C compilation fails

The enhanced system is designed to work even with partial installation - the web interface provides the core functionality with or without the C backend.

---

**Version 2.0.1** - Windows Compatible with Fixed Directory Issues
