// ============================================================
// DIGITAL MEDIA PERSUASION ANALYZER - FRONTEND LOGIC
// Handles API calls, animations, charts, and interactivity
// ============================================================

// Global variables
let emotionChart = null;

// ============================================================
// TAB NAVIGATION
// ============================================================
document.querySelectorAll('.tab-button').forEach(button => {
    button.addEventListener('click', () => {
        const targetTab = button.getAttribute('data-tab');
        
        // Update active button
        document.querySelectorAll('.tab-button').forEach(btn => {
            btn.classList.remove('active');
        });
        button.classList.add('active');
        
        // Update active content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${targetTab}-tab`).classList.add('active');
    });
});

// ============================================================
// ANALYZE BUTTON - MAIN ANALYSIS TRIGGER
// ============================================================
document.getElementById('analyzeBtn').addEventListener('click', async () => {
    const textInput = document.getElementById('textInput').value.trim();
    
    // Validation
    if (!textInput || textInput.length < 10) {
        alert('Please enter at least 10 characters of text to analyze.');
        return;
    }
    
    // Show loading, hide results
    document.getElementById('loadingSpinner').classList.remove('hidden');
    document.getElementById('resultsSection').classList.add('hidden');
    document.getElementById('analyzeBtn').disabled = true;
    
    try {
        // Make API call to Flask backend
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text: textInput })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Analysis failed');
        }
        
        const data = await response.json();
        
        // Hide loading, show results
        document.getElementById('loadingSpinner').classList.add('hidden');
        document.getElementById('resultsSection').classList.remove('hidden');
        
        // Populate all results
        displayResults(data);
        
    } catch (error) {
        console.error('Error:', error);
        alert(`Error: ${error.message}`);
        document.getElementById('loadingSpinner').classList.add('hidden');
    } finally {
        document.getElementById('analyzeBtn').disabled = false;
    }
});

// ============================================================
// DISPLAY RESULTS - MAIN RENDERING FUNCTION
// ============================================================
function displayResults(data) {
    // 1. Persuasion Score & Gauge
    animateGauge(data.persuasion_score);
    document.getElementById('persuasionLabel').textContent = data.persuasion_label;
    
    // 2. Ethical Score
    animateEthicalScore(data.ethical_score);
    
    // 3. Ethical Reflection
    document.getElementById('ethicalReflection').textContent = data.ethical_reflection;
    
    // 4. Sentiment Bars
    displaySentiment(data.sentiment);
    
    // 5. Emotion Chart
    displayEmotionChart(data.emotions);
    
    // 6. Persuasive Keywords
    displayKeywords(data.persuasive_keywords);
    
    // 7. Highlighted Text
    document.getElementById('highlightedText').innerHTML = data.highlighted_text;
}

// ============================================================
// PERSUASION GAUGE ANIMATION
// ============================================================
function animateGauge(score) {
    const gauge = document.getElementById('gaugeProgress');
    const scoreText = document.getElementById('gaugeScore');
    
    // Calculate stroke-dashoffset for the arc (semicircle)
    const circumference = 251.2;  // Approximate arc length
    const offset = circumference - (score / 100) * circumference;
    
    // Animate the gauge
    setTimeout(() => {
        gauge.style.strokeDashoffset = offset;
        
        // Change color based on score
        if (score > 80) {
            gauge.style.stroke = '#ef4444';  // Red for high persuasion
        } else if (score > 50) {
            gauge.style.stroke = '#f59e0b';  // Orange for moderate
        } else {
            gauge.style.stroke = '#6366f1';  // Purple for low
        }
    }, 100);
    
    // Animate the number
    animateNumber(scoreText, 0, score, 2000);
}

// ============================================================
// ETHICAL SCORE CIRCULAR PROGRESS
// ============================================================
function animateEthicalScore(score) {
    const circle = document.getElementById('ethicalCircle');
    const scoreText = document.getElementById('ethicalScore');
    
    // Calculate stroke-dashoffset for circular progress
    const circumference = 283;  // 2 * PI * radius (45)
    const offset = circumference - (score / 100) * circumference;
    
    setTimeout(() => {
        circle.style.strokeDashoffset = offset;
        
        // Change color based on score
        if (score > 70) {
            circle.style.stroke = '#10b981';  // Green for high ethics
            scoreText.style.fill = '#10b981';
        } else if (score > 40) {
            circle.style.stroke = '#f59e0b';  // Orange for moderate
            scoreText.style.fill = '#f59e0b';
        } else {
            circle.style.stroke = '#ef4444';  // Red for low ethics
            scoreText.style.fill = '#ef4444';
        }
    }, 100);
    
    // Animate the number
    animateNumber(scoreText, 0, score, 2000);
}

// ============================================================
// NUMBER ANIMATION UTILITY
// ============================================================
function animateNumber(element, start, end, duration) {
    const range = end - start;
    const increment = range / (duration / 16);  // 60fps
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
            current = end;
            clearInterval(timer);
        }
        element.textContent = Math.round(current);
    }, 16);
}

// ============================================================
// SENTIMENT BARS DISPLAY
// ============================================================
function displaySentiment(sentiment) {
    const polarityBar = document.getElementById('polarityBar');
    const subjectivityBar = document.getElementById('subjectivityBar');
    const polarityValue = document.getElementById('polarityValue');
    const subjectivityValue = document.getElementById('subjectivityValue');
    
    // Polarity: -1 to +1, convert to 0-100% for display
    const polarityPercent = ((sentiment.polarity + 1) / 2) * 100;
    
    // Subjectivity: 0 to 1, convert to 0-100%
    const subjectivityPercent = sentiment.subjectivity * 100;
    
    setTimeout(() => {
        polarityBar.style.width = `${polarityPercent}%`;
        subjectivityBar.style.width = `${subjectivityPercent}%`;
    }, 100);
    
    polarityValue.textContent = sentiment.polarity.toFixed(3);
    subjectivityValue.textContent = sentiment.subjectivity.toFixed(3);
}

// ============================================================
// EMOTION PIE/DONUT CHART
// ============================================================
function displayEmotionChart(emotions) {
    const ctx = document.getElementById('emotionChart').getContext('2d');
    
    // Destroy existing chart if it exists
    if (emotionChart) {
        emotionChart.destroy();
    }
    
    // Prepare data
    const labels = Object.keys(emotions).map(key => 
        key.charAt(0).toUpperCase() + key.slice(1)
    );
    const data = Object.values(emotions);
    
    // Create donut chart
    emotionChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [
                    '#10b981',  // Joy - Green
                    '#ef4444',  // Fear - Red
                    '#dc2626',  // Anger - Dark Red
                    '#3b82f6'   // Trust - Blue
                ],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 15,
                        font: {
                            size: 12,
                            family: "'Segoe UI', sans-serif"
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.label}: ${context.parsed.toFixed(1)}%`;
                        }
                    }
                }
            },
            animation: {
                animateRotate: true,
                animateScale: true,
                duration: 1500
            }
        }
    });
}

// ============================================================
// PERSUASIVE KEYWORDS DISPLAY
// ============================================================
function displayKeywords(keywordsData) {
    // Total count
    document.getElementById('keywordCount').textContent = keywordsData.count;
    
    // Categories breakdown
    const categoriesContainer = document.getElementById('keywordCategories');
    categoriesContainer.innerHTML = '';
    
    for (const [category, count] of Object.entries(keywordsData.by_category)) {
        if (count > 0) {
            const categoryDiv = document.createElement('div');
            categoryDiv.className = 'category-item';
            categoryDiv.innerHTML = `
                <div class="category-name">${category.replace('_', ' ')}</div>
                <div class="category-count">${count}</div>
            `;
            categoriesContainer.appendChild(categoryDiv);
        }
    }
    
    // Individual keywords
    const keywordsContainer = document.getElementById('keywordsList');
    keywordsContainer.innerHTML = '';
    
    if (keywordsData.words_found.length > 0) {
        keywordsData.words_found.forEach(word => {
            const tag = document.createElement('span');
            tag.className = 'keyword-tag';
            tag.textContent = word;
            keywordsContainer.appendChild(tag);
        });
    } else {
        keywordsContainer.innerHTML = '<p style="color: #718096;">No persuasive keywords detected.</p>';
    }
}

// ============================================================
// INITIALIZE ON PAGE LOAD
// ============================================================
document.addEventListener('DOMContentLoaded', () => {
    console.log('Digital Media Persuasion Analyzer initialized.');
    
    // Focus on text input
    document.getElementById('textInput').focus();
    
    // Add enter key support (Ctrl+Enter to analyze)
    document.getElementById('textInput').addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.key === 'Enter') {
            document.getElementById('analyzeBtn').click();
        }
    });
});
