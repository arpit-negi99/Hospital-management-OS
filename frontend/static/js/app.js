// Hospital OS Management System - Frontend JavaScript

class HospitalApp {
    constructor() {
        this.apiBase = '/api';
        this.currentSection = 'dashboard';
        this.charts = {};
        this.init();
    }

    init() {
        this.setupNavigation();
        this.setupEventListeners();
        this.loadDashboard();
        this.setupCharts();

        // Auto-refresh dashboard every 30 seconds
        setInterval(() => {
            if (this.currentSection === 'dashboard') {
                this.loadDashboard();
            }
        }, 30000);
    }

    setupNavigation() {
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const target = link.getAttribute('href').substring(1);
                this.showSection(target);
            });
        });
        this.showSection('dashboard');
    }

    showSection(sectionName) {
        document.querySelectorAll('.section').forEach(section => {
            section.classList.remove('active');
        });

        const targetSection = document.getElementById(sectionName);
        if (targetSection) {
            targetSection.classList.add('active');
            this.currentSection = sectionName;

            switch (sectionName) {
                case 'dashboard':
                    this.loadDashboard();
                    break;
                case 'queue':
                    this.loadPatientQueue();
                    break;
                case 'simulation':
                    this.loadSimulationResults();
                    break;
            }
        }
    }

    setupEventListeners() {
        const patientForm = document.getElementById('patient-form');
        if (patientForm) {
            patientForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.addPatient();
            });
        }

        const painSlider = document.getElementById('pain_level');
        if (painSlider) {
            painSlider.addEventListener('input', (e) => {
                document.getElementById('pain-value').textContent = e.target.value;
            });
        }
    }

    async loadDashboard() {
        try {
            const response = await fetch(`${this.apiBase}/stats`);
            const stats = await response.json();

            document.getElementById('total-patients').textContent = stats.total_patients || 0;
            document.getElementById('critical-patients').textContent = stats.critical_patients || 0;
            document.getElementById('average-age').textContent = Math.round(stats.average_age || 0);

            this.updatePriorityChart(stats.priority_distribution || {});
            this.updateRecentActivity();

        } catch (error) {
            console.error('Error loading dashboard:', error);
        }
    }

    setupCharts() {
        const ctx = document.getElementById('priorityChart');
        if (ctx) {
            this.charts.priority = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Critical', 'High', 'Medium', 'Low'],
                    datasets: [{
                        data: [0, 0, 0, 0],
                        backgroundColor: ['#dc3545', '#ffc107', '#0dcaf0', '#198754']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'bottom' }
                    }
                }
            });
        }

        const comparisonCtx = document.getElementById('comparisonChart');
        if (comparisonCtx) {
            this.charts.comparison = new Chart(comparisonCtx, {
                type: 'bar',
                data: {
                    labels: ['FCFS', 'Priority', 'Round Robin', 'MLFQ'],
                    datasets: [{
                        label: 'Average Waiting Time',
                        data: [0, 0, 0, 0],
                        backgroundColor: '#0d6efd'
                    }, {
                        label: 'Average Turnaround Time',
                        data: [0, 0, 0, 0],
                        backgroundColor: '#6c757d'
                    }]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: { display: true, text: 'Time (minutes)' }
                        }
                    }
                }
            });
        }
    }

    updatePriorityChart(distribution) {
        if (this.charts.priority) {
            const data = [
                distribution['CRITICAL'] || 0,
                distribution['HIGH'] || 0,
                distribution['MEDIUM'] || 0,
                distribution['LOW'] || 0
            ];
            this.charts.priority.data.datasets[0].data = data;
            this.charts.priority.update();
        }
    }

    async addPatient() {
        try {
            const formData = {
                age: parseInt(document.getElementById('age').value),
                heart_rate: parseInt(document.getElementById('heart_rate').value),
                blood_pressure_systolic: parseFloat(document.getElementById('blood_pressure_systolic').value),
                blood_pressure_diastolic: parseFloat(document.getElementById('blood_pressure_diastolic').value),
                temperature: parseFloat(document.getElementById('temperature').value),
                respiratory_rate: parseInt(document.getElementById('respiratory_rate').value),
                oxygen_saturation: parseInt(document.getElementById('oxygen_saturation').value),
                pain_level: parseInt(document.getElementById('pain_level').value),
                chest_pain: parseInt(document.getElementById('chest_pain').value),
                breathing_difficulty: parseInt(document.getElementById('breathing_difficulty').value),
                consciousness_level: parseInt(document.getElementById('consciousness_level').value),
                bleeding_severity: parseInt(document.getElementById('bleeding_severity').value)
            };

            const response = await fetch(`${this.apiBase}/add_patient`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });

            const result = await response.json();

            if (result.success) {
                this.showPredictionResult(result);
                this.showNotification('Patient added successfully!', 'success');
                document.getElementById('patient-form').reset();
                document.getElementById('pain-value').textContent = '1';

                if (this.currentSection === 'dashboard') {
                    setTimeout(() => this.loadDashboard(), 1000);
                }
            } else {
                this.showNotification('Error adding patient: ' + result.message, 'error');
            }

        } catch (error) {
            console.error('Error adding patient:', error);
            this.showNotification('Error adding patient. Please try again.', 'error');
        }
    }

    showPredictionResult(result) {
        const resultDiv = document.getElementById('prediction-result');
        const priorityClass = result.priority_label.toLowerCase();

        resultDiv.innerHTML = `
            <div class="prediction-result ${priorityClass}">
                <h6><i class="fas fa-robot"></i> ML Prediction</h6>
                <div class="mb-2">
                    <strong>Priority:</strong> 
                    <span class="priority-${priorityClass}">${result.priority_label}</span>
                </div>
                <div class="mb-2">
                    <strong>Confidence:</strong> ${((result.confidence || 0.8) * 100).toFixed(1)}%
                </div>
                <div><strong>Patient ID:</strong> ${result.patient_id}</div>
                <small class="text-muted mt-2 d-block">${result.message}</small>
            </div>
        `;
    }

    async loadPatientQueue() {
        try {
            const response = await fetch(`${this.apiBase}/patients`);
            const data = await response.json();

            const queueDiv = document.getElementById('patient-queue');

            if (data.patients && data.patients.length > 0) {
                const patientsHtml = data.patients.map(patient => this.createPatientCard(patient)).join('');
                queueDiv.innerHTML = patientsHtml;
            } else {
                queueDiv.innerHTML = '<p class="text-muted">No patients in queue</p>';
            }

        } catch (error) {
            console.error('Error loading patient queue:', error);
            document.getElementById('patient-queue').innerHTML = '<p class="text-danger">Error loading patient queue</p>';
        }
    }

    createPatientCard(patient) {
        const priorityClass = (patient.priority_label || 'MEDIUM').toLowerCase();
        const priorityIcon = {
            'critical': 'fas fa-exclamation-triangle',
            'high': 'fas fa-exclamation-circle',
            'medium': 'fas fa-info-circle',
            'low': 'fas fa-check-circle'
        }[priorityClass] || 'fas fa-info-circle';

        return `
            <div class="card patient-card ${priorityClass}">
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-3">
                            <h6><i class="fas fa-user"></i> Patient ${patient.patient_id}</h6>
                            <span class="priority-${priorityClass}">
                                <i class="${priorityIcon}"></i> ${patient.priority_label || 'MEDIUM'}
                            </span>
                        </div>
                        <div class="col-md-3">
                            <h6>Basic Info</h6>
                            <div class="vital-sign">Age: ${patient.age}y</div>
                        </div>
                        <div class="col-md-6">
                            <h6>Vital Signs</h6>
                            <div class="vital-sign">HR: ${patient.heart_rate} bpm</div>
                            <div class="vital-sign">BP: ${patient.blood_pressure_systolic}/${patient.blood_pressure_diastolic}</div>
                            <div class="vital-sign">Temp: ${patient.temperature}°C</div>
                            <div class="vital-sign">SpO2: ${patient.oxygen_saturation}%</div>
                            <div class="vital-sign">Pain: ${patient.pain_level}/10</div>
                        </div>
                    </div>
                    <div class="row mt-2">
                        <div class="col-md-12">
                            <small class="text-muted">
                                <i class="fas fa-clock"></i> 
                                Admitted: ${new Date(patient.admission_time).toLocaleString()}
                            </small>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    async runSimulation() {
        const algorithm = document.getElementById('algorithm-select').value;
        const resultsDiv = document.getElementById('simulation-results');

        resultsDiv.innerHTML = '<div class="spinner"></div>';

        try {
            const response = await fetch(`${this.apiBase}/run_simulation`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ algorithm })
            });

            const data = await response.json();

            if (data.success) {
                this.displaySimulationResults(data.result);
                this.showNotification(`${algorithm.toUpperCase()} simulation completed!`, 'success');
            } else {
                resultsDiv.innerHTML = '<p class="text-danger">Simulation failed</p>';
            }

        } catch (error) {
            console.error('Error running simulation:', error);
            resultsDiv.innerHTML = '<p class="text-danger">Error running simulation</p>';
        }
    }

    displaySimulationResults(result) {
        const resultsDiv = document.getElementById('simulation-results');

        resultsDiv.innerHTML = `
            <h6><i class="fas fa-chart-line"></i> ${result.algorithm} Results</h6>
            <div class="simulation-metric">
                <h4>${result.average_waiting_time}</h4>
                <p>Average Waiting Time (min)</p>
            </div>
            <div class="simulation-metric">
                <h4>${result.average_turnaround_time}</h4>
                <p>Average Turnaround Time (min)</p>
            </div>
            <div class="simulation-metric">
                <h4>${result.total_patients}</h4>
                <p>Total Patients Processed</p>
            </div>
            <small class="text-muted">
                <i class="fas fa-clock"></i> 
                Executed: ${new Date(result.executed_at).toLocaleString()}
            </small>
        `;
    }

    async loadSimulationResults() {
        try {
            const response = await fetch(`${this.apiBase}/simulation_results`);
            const results = await response.json();

            if (Object.keys(results).length > 0) {
                const algorithms = ['fcfs', 'priority', 'round_robin', 'mlfq'];
                const waitingTimes = algorithms.map(alg => results[alg]?.average_waiting_time || 0);
                const turnaroundTimes = algorithms.map(alg => results[alg]?.average_turnaround_time || 0);

                if (this.charts.comparison) {
                    this.charts.comparison.data.datasets[0].data = waitingTimes;
                    this.charts.comparison.data.datasets[1].data = turnaroundTimes;
                    this.charts.comparison.update();
                }
            }

        } catch (error) {
            console.error('Error loading simulation results:', error);
        }
    }

    updateRecentActivity() {
        const activities = [
            { message: 'System online and operational', time: '1 minute ago' },
            { message: 'ML model ready for predictions', time: '2 minutes ago' },
            { message: 'Web interface started', time: '3 minutes ago' }
        ];

        const activityHtml = activities.map(activity => `
            <div class="activity-item">
                <div class="message">${activity.message}</div>
                <div class="time">${activity.time}</div>
            </div>
        `).join('');

        document.getElementById('recent-activity').innerHTML = activityHtml;
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
        notification.style.position = 'fixed';
        notification.style.top = '20px';
        notification.style.right = '20px';
        notification.style.zIndex = '9999';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        document.body.appendChild(notification);
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
    }

    async clearAllData() {
        if (confirm('Clear all patient data?')) {
            try {
                await fetch(`${this.apiBase}/clear_data`, { method: 'POST' });
                this.showNotification('All data cleared!', 'success');
                this.loadDashboard();
                this.loadPatientQueue();
            } catch (error) {
                this.showNotification('Error clearing data', 'error');
            }
        }
    }

    async refreshQueue() {
        await this.loadPatientQueue();
        this.showNotification('Queue refreshed!', 'success');
    }
}

// Example patient data functions
function fillCriticalExample() {
    fillFormData({
        age: 65, heart_rate: 130, blood_pressure_systolic: 190, blood_pressure_diastolic: 110,
        temperature: 39.5, respiratory_rate: 30, oxygen_saturation: 85, pain_level: 9,
        chest_pain: 5, breathing_difficulty: 4, consciousness_level: 2, bleeding_severity: 3
    });
}

function fillHighExample() {
    fillFormData({
        age: 45, heart_rate: 110, blood_pressure_systolic: 160, blood_pressure_diastolic: 95,
        temperature: 38.5, respiratory_rate: 25, oxygen_saturation: 92, pain_level: 7,
        chest_pain: 3, breathing_difficulty: 3, consciousness_level: 4, bleeding_severity: 2
    });
}

function fillMediumExample() {
    fillFormData({
        age: 35, heart_rate: 90, blood_pressure_systolic: 130, blood_pressure_diastolic: 85,
        temperature: 37.2, respiratory_rate: 20, oxygen_saturation: 96, pain_level: 5,
        chest_pain: 2, breathing_difficulty: 1, consciousness_level: 5, bleeding_severity: 1
    });
}

function fillLowExample() {
    fillFormData({
        age: 28, heart_rate: 75, blood_pressure_systolic: 120, blood_pressure_diastolic: 80,
        temperature: 36.8, respiratory_rate: 16, oxygen_saturation: 98, pain_level: 3,
        chest_pain: 1, breathing_difficulty: 0, consciousness_level: 5, bleeding_severity: 0
    });
}

function fillFormData(data) {
    Object.keys(data).forEach(key => {
        const element = document.getElementById(key);
        if (element) {
            element.value = data[key];
            if (key === 'pain_level') {
                document.getElementById('pain-value').textContent = data[key];
            }
        }
    });
}

function runSimulation() { app.runSimulation(); }
function clearAllData() { app.clearAllData(); }
function refreshQueue() { app.refreshQueue(); }

let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new HospitalApp();
});
