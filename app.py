<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Quick Incident Log & FBA Tool</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    fontFamily: {
                        sans: ['Inter', 'sans-serif'],
                    },
                    colors: {
                        'primary-blue': '#1D4ED8',
                        'secondary-gray': '#E5E7EB',
                        'critical-red': '#DC2626',
                        'warning-orange': '#F59E0B',
                        'safe-green': '#10B981',
                    }
                }
            }
        }
    </script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@100..900&display=swap');
        
        .container-card {
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        }
        .critical-form {
            border: 3px solid #DC2626;
            background-color: #FEF2F2;
        }
        .hypothesis-box {
            border: 2px solid #3B82F6;
            background-color: #EFF6FF;
        }
    </style>
</head>
<body class="bg-gray-100 p-4 sm:p-8 font-sans">

    <div id="app" class="max-w-4xl mx-auto">
        <h1 class="text-3xl sm:text-4xl font-extrabold text-primary-blue mb-6 border-b-4 border-primary-blue pb-2">
            Preliminary Behaviour Incident Log
        </h1>
        
        <div class="bg-white p-6 sm:p-8 rounded-xl container-card space-y-6">
            
            <!-- --- Basic Log Details: What, When, Who --- -->
            <section class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                    <label for="incidentDate" class="block text-sm font-medium text-gray-700 mb-1">Date</label>
                    <input type="date" id="incidentDate" class="w-full border border-gray-300 rounded-lg p-2 focus:ring-primary-blue focus:border-primary-blue" value="">
                </div>
                <div>
                    <label for="incidentTime" class="block text-sm font-medium text-gray-700 mb-1">Time of Incident</label>
                    <input type="time" id="incidentTime" onchange="updateSession()" class="w-full border border-gray-300 rounded-lg p-2 focus:ring-primary-blue focus:border-primary-blue" value="">
                </div>
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">Session</label>
                    <div id="sessionDisplay" class="w-full bg-secondary-gray text-gray-800 font-semibold rounded-lg p-2.5 h-10 flex items-center">
                        <span class="text-gray-500">Enter time...</span>
                    </div>
                </div>
            </section>
            
            <section class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                    <label for="staffMember" class="block text-sm font-medium text-gray-700 mb-1">Staff Member Logging</label>
                    <select id="staffMember" class="w-full border border-gray-300 rounded-lg p-2 focus:ring-primary-blue focus:border-primary-blue">
                        <option value="">Select Staff</option>
                        <option value="s1">Emily Jones</option>
                        <option value="s2">Daniel Lee</option>
                        <option value="s3">Sarah Chen</option>
                    </select>
                </div>
                <div>
                    <label for="supportType" class="block text-sm font-medium text-gray-700 mb-1">Type of Support</label>
                    <select id="supportType" class="w-full border border-gray-300 rounded-lg p-2 focus:ring-primary-blue focus:border-primary-blue">
                        <option value="1:1">1:1</option>
                        <option value="Independent">Independent</option>
                        <option value="Small Group">Small Group</option>
                        <option value="Large Group">Large Group</option>
                    </select>
                </div>
            </section>

            <section class="space-y-6">
                <div>
                    <label for="behaviorWhat" class="block text-sm font-medium text-gray-700 mb-1">What Happened (Behavior)</label>
                    <textarea id="behaviorWhat" rows="2" class="w-full border border-gray-300 rounded-lg p-2 focus:ring-primary-blue focus:border-primary-blue" placeholder="Describe the observable behavior..."></textarea>
                </div>
            
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                        <label for="antecedent" class="block text-sm font-medium text-gray-700 mb-1">Antecedent (What happened right before?)</label>
                        <select id="antecedent" class="w-full border border-gray-300 rounded-lg p-2 focus:ring-primary-blue focus:border-primary-blue">
                            <option value="">Select Antecedent</option>
                            <option value="Task demand/Transition">Task demand/Transition</option>
                            <option value="Peer conflict/Teasing">Peer conflict/Teasing</option>
                            <option value="Adult proximity/Correction">Adult proximity/Correction</option>
                            <option value="Non-contingent access withdrawn">Non-contingent access withdrawn</option>
                            <option value="Unstructured time/Boredom">Unstructured time/Boredom</option>
                            <option value="Physical discomfort/Illness">Physical discomfort/Illness</option>
                            <option value="Other">Other (Specify in Description)</option>
                        </select>
                    </div>
                    <div>
                        <label for="interventionApplied" class="block text-sm font-medium text-gray-700 mb-1">Intervention Applied</label>
                        <select id="interventionApplied" class="w-full border border-gray-300 rounded-lg p-2 focus:ring-primary-blue focus:border-primary-blue">
                            <option value="">Select Intervention</option>
                            <option value="Redirection/Prompting">Redirection/Prompting</option>
                            <option value="Proximity Control">Proximity Control</option>
                            <option value="Providing choice/Breaks">Providing choice/Breaks</option>
                            <option value="Crisis management/Restraint">Crisis management/Restraint</option>
                            <option value="Ignoring/Planned pacing">Ignoring/Planned pacing</option>
                            <option value="Preferred item/activity access">Preferred item/activity access</option>
                            <option value="Other">Other (Specify in Description)</option>
                        </select>
                    </div>
                </div>

                <div>
                    <label for="consequence" class="block text-sm font-medium text-gray-700 mb-1">Consequence (How did the staff/environment respond?)</label>
                    <textarea id="consequence" rows="2" class="w-full border border-gray-300 rounded-lg p-2 focus:ring-primary-blue focus:border-primary-blue" placeholder="Describe what happened immediately after the behavior..."></textarea>
                </div>

                <div>
                    <label for="severityLevel" class="block text-sm font-medium text-gray-700 mb-1">Severity Level</label>
                    <select id="severityLevel" onchange="handleSeverityChange()" class="w-full border border-gray-300 rounded-lg p-2 focus:ring-primary-blue focus:border-primary-blue">
                        <option value="0">Select Severity (1=Minor, 4=Critical)</option>
                        <option value="1">1: Minor (Low intensity/brief)</option>
                        <option value="2">2: Moderate (Moderate intensity/disruption)</option>
                        <option value="3">3: Serious (Safety risk/significant disruption) - Triggers Full Form</option>
                        <option value="4">4: Critical (Immediate danger/external services required) - Triggers Full Form</option>
                    </select>
                </div>
            </section>

            <!-- --- Hypothesis & Critical Incident Forms --- -->
            <section id="dynamicOutput" class="pt-6 space-y-6">
                <!-- Content will appear here based on severity level -->
            </section>
            
            <button onclick="submitLog()" class="w-full bg-primary-blue text-white font-bold py-3 rounded-lg hover:bg-blue-700 transition duration-200 mt-4">
                Submit Preliminary Log
            </button>
            <div id="submitMessage" class="mt-4 text-center text-green-600 font-semibold hidden">Log Submitted Successfully!</div>
        </div>
    </div>

    <script>
        // Global Constants
        const API_KEY = ""; // Leave as-is
        const API_URL = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key=${API_KEY}`;

        // --- Session Time Logic ---
        function getSession(timeStr) {
            if (!timeStr) return null;
            
            const [hourStr, minuteStr] = timeStr.split(':');
            const hours = parseInt(hourStr);
            const minutes = parseInt(minuteStr);

            // Convert to total minutes from midnight for easy comparison
            const totalMinutes = hours * 60 + minutes;

            // Define session boundaries in total minutes
            const morningStart = 9 * 60;   // 9:00am
            const morningEnd = 11 * 60;    // 11:00am
            const middleEnd = 13 * 60;     // 1:00pm (13:00)
            const afternoonEnd = 14 * 60 + 45; // 2:45pm (14:45)

            if (totalMinutes >= morningStart && totalMinutes <= morningEnd) {
                return 'Morning (9:00am - 11:00am)';
            } else if (totalMinutes > morningEnd && totalMinutes <= middleEnd) {
                return 'Middle (11:01am - 1:00pm)';
            } else if (totalMinutes > middleEnd && totalMinutes <= afternoonEnd) {
                return 'Afternoon (1:01pm - 2:45pm)';
            } else {
                return 'Out of Session Hours (Not Logged)';
            }
        }

        function updateSession() {
            const timeInput = document.getElementById('incidentTime').value;
            const sessionDisplay = document.getElementById('sessionDisplay');
            const session = getSession(timeInput);
            
            if (session && session !== 'Out of Session Hours (Not Logged)') {
                sessionDisplay.innerHTML = `<span class="text-primary-blue">${session}</span>`;
            } else if (session) {
                sessionDisplay.innerHTML = `<span class="text-critical-red">${session}</span>`;
            } else {
                sessionDisplay.innerHTML = `<span class="text-gray-500">Enter time...</span>`;
            }
        }
        
        // --- Severity Change Logic ---
        function handleSeverityChange() {
            const severity = parseInt(document.getElementById('severityLevel').value);
            const dynamicOutput = document.getElementById('dynamicOutput');

            if (severity >= 3) {
                // Critical Incident Form
                dynamicOutput.innerHTML = generateCriticalIncidentForm();
            } else if (severity > 0) {
                // Automated Hypothesis
                dynamicOutput.innerHTML = generateHypothesisLoading();
                generateAutomatedHypothesis(severity);
            } else {
                dynamicOutput.innerHTML = '';
            }
        }

        // --- Critical Incident Form (Severity 3 or 4) ---
        function generateCriticalIncidentForm() {
            return `
                <div class="critical-form p-6 rounded-xl">
                    <h3 class="text-2xl font-bold text-critical-red mb-4 border-b border-critical-red pb-2">
                        🚨 CRITICAL INCIDENT TRIGGERED (Severity ${document.getElementById('severityLevel').value})
                    </h3>
                    <p class="text-gray-800 mb-4">
                        A Severity 3 or 4 incident requires immediate, detailed reporting. You must complete the **ABCH Detailed Form** below to finalize this log.
                    </p>
                    <div class="space-y-4">
                        <div>
                            <label for="abchSafetyRisk" class="block text-sm font-medium text-gray-700 mb-1">Immediate Safety and Risk Assessment</label>
                            <textarea id="abchSafetyRisk" rows="2" class="w-full border border-critical-red rounded-lg p-2 focus:ring-critical-red focus:border-critical-red" placeholder="Describe all actions taken to ensure immediate safety (e.g., calling emergency staff, removal of other students)."></textarea>
                        </div>
                        <div>
                            <label for="abchFollowUp" class="block text-sm font-medium text-gray-700 mb-1">Required Follow-up Actions/Notifications</label>
                            <textarea id="abchFollowUp" rows="2" class="w-full border border-critical-red rounded-lg p-2 focus:ring-critical-red focus:border-critical-red" placeholder="Who was notified (Line Manager, Parent/Caregiver), and what immediate next steps are scheduled?"></textarea>
                        </div>
                        <p class="text-sm font-semibold text-critical-red">
                            Note: This log entry will be flagged for mandatory review by Administration.
                        </p>
                    </div>
                </div>
            `;
        }

        // --- Automated Hypothesis (Severity 1 or 2) ---
        function generateHypothesisLoading() {
            return `
                <div class="hypothesis-box p-6 rounded-xl border-blue-500">
                    <h3 class="text-xl font-bold text-blue-700 mb-2">
                        💡 Automated Hypothesis (Severity ${document.getElementById('severityLevel').value})
                    </h3>
                    <p class="text-blue-600 animate-pulse">
                        Analyzing data and generating preliminary Function of Behavior (Hypothesis)...
                    </p>
                </div>
            `;
        }

        async function generateAutomatedHypothesis(severity) {
            const antecedent = document.getElementById('antecedent').value || "None selected";
            const behavior = document.getElementById('behaviorWhat').value || "Behavior not detailed";
            const consequence = document.getElementById('consequence').value || "Consequence not detailed";
            const support = document.getElementById('supportType').value || "1:1";
            
            if (antecedent === "None selected" || behavior === "Behavior not detailed") {
                 document.getElementById('dynamicOutput').innerHTML = `
                    <div class="hypothesis-box p-6 rounded-xl border-warning-orange">
                        <h3 class="text-xl font-bold text-warning-orange mb-2">
                            ⚠️ Automated Hypothesis
                        </h3>
                        <p class="text-gray-700">
                            Please select an **Antecedent** and provide details for the **Behavior** and **Consequence** to generate a meaningful hypothesis.
                        </p>
                    </div>
                `;
                return;
            }

            const systemPrompt = "You are a behavioral analyst assistant. Based on the A-B-C data provided, generate a concise, single-paragraph hypothesis (H) suggesting the likely *function* of the student's behavior (e.g., To gain attention, To escape a demand, To gain access to tangibles, To gain sensory input). Do not use placeholders, be direct.";
            
            const userQuery = `Analyze this ABC data for a Severity ${severity} incident in a ${support} setting: A (Antecedent): ${antecedent}. B (Behavior): ${behavior}. C (Consequence): ${consequence}. What is the hypothesis (H)?`;

            const payload = {
                contents: [{ parts: [{ text: userQuery }] }],
                systemInstruction: {
                    parts: [{ text: systemPrompt }]
                },
            };

            let hypothesisText = "Hypothesis generation failed. Check console for error.";
            
            // --- LLM API Call with Exponential Backoff ---
            const maxRetries = 5;
            let currentRetry = 0;
            
            while (currentRetry < maxRetries) {
                try {
                    const response = await fetch(API_URL, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(payload)
                    });
                    
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    
                    const result = await response.json();
                    hypothesisText = result.candidates?.[0]?.content?.parts?.[0]?.text || "No text generated.";
                    break; // Exit loop on success
                } catch (error) {
                    console.error(`Attempt ${currentRetry + 1} failed:`, error);
                    currentRetry++;
                    if (currentRetry < maxRetries) {
                        const delay = Math.pow(2, currentRetry) * 1000;
                        await new Promise(resolve => setTimeout(resolve, delay));
                    }
                }
            }
            
            const dynamicOutput = document.getElementById('dynamicOutput');
            dynamicOutput.innerHTML = `
                <div class="hypothesis-box p-6 rounded-xl border-blue-500">
                    <h3 class="text-xl font-bold text-blue-700 mb-2">
                        💡 Automated Hypothesis (Severity ${severity})
                    </h3>
                    <div class="text-gray-800">
                        <p class="mb-2 font-semibold">Preliminary Function of Behavior:</p>
                        <p>${hypothesisText}</p>
                    </div>
                </div>
            `;
        }

        // --- Submission Logic ---
        function submitLog() {
            const severity = parseInt(document.getElementById('severityLevel').value);
            const antecedent = document.getElementById('antecedent').value;
            const behavior = document.getElementById('behaviorWhat').value;
            const consequence = document.getElementById('consequence').value;
            const support = document.getElementById('supportType').value;
            const time = document.getElementById('incidentTime').value;
            const date = document.getElementById('incidentDate').value;
            const staff = document.getElementById('staffMember').value;
            
            if (!date || !time || !staff || !behavior || !antecedent || !consequence || severity === 0) {
                showMessage("Please fill in all required fields and select a Severity Level.", 'critical-red');
                return;
            }

            const session = getSession(time);
            
            let abchDetailed = {};
            if (severity >= 3) {
                abchDetailed = {
                    safetyRisk: document.getElementById('abchSafetyRisk').value,
                    followUp: document.getElementById('abchFollowUp').value,
                    formRequired: 'ABCH Detailed - Critical Incident'
                };
            }
            
            const preliminaryLog = {
                date: date,
                time: time,
                session: session,
                staffMember: staff,
                supportType: support,
                antecedent: antecedent,
                behavior: behavior,
                consequence: consequence,
                severity: severity,
                ...abchDetailed,
                // In a real app, you would send this object to Firestore here.
            };

            console.log("--- Preliminary Log Data Submitted ---");
            console.log(preliminaryLog);

            showMessage("Log Submitted Successfully! (Data logged to console)", 'safe-green');
            
            // Clear form (optional)
            document.getElementById('incidentTime').value = '';
            document.getElementById('severityLevel').value = '0';
            document.getElementById('dynamicOutput').innerHTML = '';
            document.getElementById('behaviorWhat').value = '';
            document.getElementById('consequence').value = '';
            updateSession(); 
        }

        function showMessage(message, colorClass) {
            const msgBox = document.getElementById('submitMessage');
            msgBox.textContent = message;
            msgBox.className = `mt-4 text-center font-semibold text-${colorClass}`;
            msgBox.classList.remove('hidden');
            setTimeout(() => {
                msgBox.classList.add('hidden');
            }, 5000);
        }

        // Set today's date and update session display on load
        window.onload = function() {
            document.getElementById('incidentDate').valueAsDate = new Date();
            updateSession();
        };

    </script>
</body>
</html>
