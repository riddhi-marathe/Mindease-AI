// MindEase Frontend JavaScript

// API Base URL
const API_BASE = '/api';

// ==================== Utility Functions ====================

function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} fade-in`;
    alertDiv.textContent = message;
    
    document.body.insertBefore(alertDiv, document.body.firstChild);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.scrollIntoView({ behavior: 'smooth' });
    }
}

function showLoading(element) {
    element.innerHTML = '<span class="loading">⟳</span> Loading...';
}

// ==================== Authentication ====================

function showLoginModal() {
    document.getElementById('loginModal').classList.remove('hidden');
}

function closeLoginModal() {
    document.getElementById('loginModal').classList.add('hidden');
}

function showRegisterModal() {
    document.getElementById('loginModal').classList.add('hidden');
    document.getElementById('registerModal').classList.remove('hidden');
}

function closeRegisterModal() {
    document.getElementById('registerModal').classList.add('hidden');
}

// Close modal when clicking outside
window.addEventListener('click', (e) => {
    const loginModal = document.getElementById('loginModal');
    const registerModal = document.getElementById('registerModal');
    
    if (e.target === loginModal) closeLoginModal();
    if (e.target === registerModal) closeRegisterModal();
});

// Login Form Submission
document.getElementById('loginForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        const response = await fetch(`${API_BASE}/user/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password })
        });
        
        if (response.ok) {
            showAlert('Login successful!', 'success');
            closeLoginModal();
            // Redirect to dashboard
            window.location.href = '/dashboard';
        } else {
            showAlert('Login failed. Check your credentials.', 'error');
        }
    } catch (error) {
        showAlert(`Error: ${error.message}`, 'error');
    }
});

// Register Form Submission
document.getElementById('registerForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const username = document.getElementById('regUsername').value;
    const email = document.getElementById('regEmail').value;
    const password = document.getElementById('regPassword').value;
    const age = document.getElementById('regAge').value;
    
    try {
        const response = await fetch(`${API_BASE}/user/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, email, password, age })
        });
        
        if (response.ok) {
            showAlert('Registration successful! You are now logged in.', 'success');
            closeRegisterModal();
            // Redirect to dashboard
            window.location.href = '/dashboard';
        } else {
            showAlert('Registration failed. Try a different username or email.', 'error');
        }
    } catch (error) {
        showAlert(`Error: ${error.message}`, 'error');
    }
});

// Login Button Handler
document.getElementById('loginBtn')?.addEventListener('click', () => {
    if (document.getElementById('loginBtn').textContent === 'Login') {
        showLoginModal();
    } else {
        // Logout
        fetch(`${API_BASE}/user/logout`, { method: 'POST' });
        document.getElementById('loginBtn').textContent = 'Login';
        document.getElementById('dashboard').classList.add('hidden');
        showAlert('Logged out successfully', 'success');
    }
});

// ==================== Symptom Check ====================

async function loadSymptomCategories() {
    const container = document.getElementById('symptomCategories');
    if (!container) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/symptoms-list`);
        const symptoms = await response.json();

        container.innerHTML = '';
        
        for (const [category, items] of Object.entries(symptoms)) {
            const categoryDiv = document.createElement('div');
            categoryDiv.className = 'mb-4';
            
            const title = document.createElement('h4');
            title.className = 'font-semibold text-gray-700 mb-2 capitalize';
            title.textContent = category.replace('_', ' ');
            categoryDiv.appendChild(title);
            
            const itemsDiv = document.createElement('div');
            itemsDiv.className = 'space-y-2 ml-2';
            
            items.forEach(item => {
                const label = document.createElement('label');
                label.className = 'symptom-item';
                label.innerHTML = `
                    <input type="checkbox" value="${item}" name="symptoms">
                    <span>${item}</span>
                `;
                itemsDiv.appendChild(label);
            });
            
            categoryDiv.appendChild(itemsDiv);
            container.appendChild(categoryDiv);
        }
    } catch (error) {
        showAlert(`Error loading symptoms: ${error.message}`, 'error');
    }
}

document.getElementById('symptomForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const checkboxes = document.querySelectorAll('input[name="symptoms"]:checked');
    const symptoms = Array.from(checkboxes).map(cb => cb.value);
    const age = document.getElementById('age').value;
    
    if (symptoms.length === 0) {
        showAlert('Please select at least one symptom', 'warning');
        return;
    }
    
    try {
        const resultsDiv = document.getElementById('symptomResults');
        showLoading(resultsDiv);
        resultsDiv.classList.remove('hidden');
        
        const response = await fetch(`${API_BASE}/health/symptom-check`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ symptoms, age: age ? parseInt(age) : null })
        });
        
        if (!response.ok) throw new Error('Failed to get prediction');
        
        const data = await response.json();
        displaySymptomResults(data);
        showAlert('Symptom check completed', 'success');
    } catch (error) {
        showAlert(`Error: ${error.message}`, 'error');
        document.getElementById('symptomResults').classList.add('hidden');
    }
});

function displaySymptomResults(data) {
    const content = document.getElementById('resultsContent');
    
    let urgencyClass = 'results-box';
    if (data.urgency === 'critical') urgencyClass += ' warning';
    else if (data.urgency === 'low') urgencyClass += ' success';
    
    let html = `
        <div class="${urgencyClass}">
            <h4>Assessment Results</h4>
            <p><strong>Urgency Level:</strong> <span class="badge ${data.urgency === 'critical' ? 'urgent' : ''}">${data.urgency.toUpperCase()}</span></p>
            <p><strong>${data.urgency_message}</strong></p>
    `;
    
    if (data.possible_conditions && data.possible_conditions.length > 0) {
        html += '<p><strong>Possible Conditions:</strong></p><ul>';
        data.possible_conditions.forEach(cond => {
            html += `<li>${cond.name}: ${cond.confidence}</li>`;
        });
        html += '</ul>';
    }
    
    html += `<div class="doctor-rec ${data.urgency === 'critical' || data.urgency === 'high' ? 'urgent' : ''}">
                <strong>Recommendation:</strong>
                <p>${data.recommendation}</p>
            </div>
            <p class="text-sm mt-4"><em>⚠️ This is an AI assessment. Always consult a healthcare professional for accurate diagnosis.</em></p>
        </div>
    `;
    
    content.innerHTML = html;
}

// ==================== Wellness Check ====================

document.getElementById('wellnessForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const symptoms = document.getElementById('wellnessSymptoms').value;
    const health_history = document.getElementById('healthHistory').value;
    const lifestyle = document.getElementById('lifestyle').value;
    
    if (!symptoms && !health_history && !lifestyle) {
        showAlert('Please provide at least some information', 'warning');
        return;
    }
    
    try {
        const resultsDiv = document.getElementById('wellnessResults');
        showLoading(resultsDiv);
        resultsDiv.classList.remove('hidden');
        
        const response = await fetch(`${API_BASE}/health/wellness-check`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ symptoms, health_history, lifestyle })
        });
        
        if (!response.ok) throw new Error('Failed to get wellness recommendations');
        
        const data = await response.json();
        document.getElementById('wellnessContent').innerHTML = `
            <div class="results-box success">
                <h4>Wellness Recommendations</h4>
                <p>${data.recommendations}</p>
            </div>
        `;
        
        showAlert('Wellness recommendations generated', 'success');
    } catch (error) {
        showAlert(`Error: ${error.message}`, 'error');
        document.getElementById('wellnessResults').classList.add('hidden');
    }
});

// ==================== Wellness Logging ====================

document.getElementById('energyLevel')?.addEventListener('input', (e) => {
    document.getElementById('energyDisplay').textContent = e.target.value;
});

document.getElementById('wellnessLogForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const mood = document.getElementById('mood').value;
    const sleep_hours = parseFloat(document.getElementById('sleepHours').value) || 0;
    const exercise_minutes = parseInt(document.getElementById('exerciseMinutes').value) || 0;
    const energy_level = parseInt(document.getElementById('energyLevel').value);
    
    try {
        const response = await fetch(`${API_BASE}/wellness/log`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                mood,
                sleep_hours,
                exercise_minutes,
                energy_level,
                water_intake: 0,
                stress_level: 5,
                notes: ''
            })
        });
        
        if (response.ok) {
            showAlert('Wellness log saved successfully!', 'success');
            document.getElementById('wellnessLogForm').reset();
            document.getElementById('energyDisplay').textContent = '5';
        } else {
            showAlert('Please log in to save wellness logs', 'warning');
            showLoginModal();
        }
    } catch (error) {
        showAlert(`Error: ${error.message}`, 'error');
    }
});

// ==================== Mental Health Support ====================

document.getElementById('mentalHealthForm')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const mood = document.getElementById('moodDescription').value;
    const stressors = document.getElementById('stressors').value;
    const coping_methods = document.getElementById('copingMethods').value;
    
    if (!mood && !stressors && !coping_methods) {
        showAlert('Please share something about your mental health', 'warning');
        return;
    }
    
    try {
        const resultsDiv = document.getElementById('mentalHealthResults');
        showLoading(resultsDiv);
        resultsDiv.classList.remove('hidden');
        
        const response = await fetch(`${API_BASE}/health/mental-health-support`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ mood, stressors, coping_methods })
        });
        
        if (!response.ok) throw new Error('Failed to get mental health support');
        
        const data = await response.json();
        document.getElementById('mentalHealthContent').innerHTML = `
            <div class="results-box">
                <h4>Mental Health Support</h4>
                <p>${data.support}</p>
            </div>
        `;
        
        showAlert('Mental health guidance generated', 'success');
    } catch (error) {
        showAlert(`Error: ${error.message}`, 'error');
        document.getElementById('mentalHealthResults').classList.add('hidden');
    }
});

// ==================== Dashboard ====================

async function loadDashboard() {
    try {
        // Load assessments count
        const assessmentsRes = await fetch(`${API_BASE}/assessments`);
        if (assessmentsRes.ok) {
            const assessmentsData = await assessmentsRes.json();
            document.getElementById('totalAssessments').textContent = assessmentsData.assessments.length;
            
            // Show recent assessments
            const recentContainer = document.getElementById('recentAssessments');
            if (assessmentsData.assessments.length > 0) {
                recentContainer.innerHTML = assessmentsData.assessments.slice(0, 5).map(a => `
                    <div class="p-2 bg-gray-50 rounded">
                        <p class="text-sm font-semibold text-gray-700">${a.type}</p>
                        <p class="text-xs text-gray-500">${new Date(a.created_at).toLocaleDateString()}</p>
                    </div>
                `).join('');
            }
        }
        
        // Load wellness logs count
        const logsRes = await fetch(`${API_BASE}/wellness/logs`);
        if (logsRes.ok) {
            const logsData = await logsRes.json();
            document.getElementById('totalLogs').textContent = logsData.logs.length;
            
            // Show recent logs
            const recentLogsContainer = document.getElementById('recentLogs');
            if (logsData.logs.length > 0) {
                recentLogsContainer.innerHTML = logsData.logs.slice(0, 5).map(log => `
                    <div class="p-2 bg-gray-50 rounded">
                        <p class="text-sm font-semibold text-gray-700">${log.mood || 'No mood'}</p>
                        <p class="text-xs text-gray-500">${log.date}</p>
                    </div>
                `).join('');
            }
        }
        
        // Load metrics count
        const metricsRes = await fetch(`${API_BASE}/health/metrics`);
        if (metricsRes.ok) {
            const metricsData = await metricsRes.json();
            document.getElementById('totalMetrics').textContent = metricsData.metrics.length;
        }
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

// ==================== Initialization ====================

document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('symptomCategories')) {
        loadSymptomCategories();
    }
});
