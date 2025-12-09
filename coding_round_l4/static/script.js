const editor = document.getElementById("editor");
const outputBox = document.getElementById("output-box");
const sampleContainer = document.getElementById("sample-tests");
const runBtn = document.getElementById("run-btn");
const submitBtn = document.getElementById("submit-btn");
const timerDisplay = document.getElementById("timer-display");
const scoreDisplay = document.getElementById("score-display");
const violationDisplay = document.getElementById("violation-display");

// --- Render public sample tests ---
if (QUESTION && Array.isArray(QUESTION.public_tests)) {
    QUESTION.public_tests.forEach((t, idx) => {
        const div = document.createElement("div");
        div.className = "sample-block";
        div.innerHTML = `
            <div><strong>Example ${idx + 1}</strong></div>
            <div><strong>Input:</strong> <code>${JSON.stringify(t.input)}</code></div>
            <div><strong>Expected:</strong> <code>${JSON.stringify(t.expected)}</code></div>
        `;
        sampleContainer.appendChild(div);
    });
}

// --- Helper to update output ---
function setOutput(text) {
    outputBox.textContent = text;
    outputBox.scrollTop = outputBox.scrollHeight;
}

function appendOutput(text) {
    outputBox.textContent += "\n" + text;
    outputBox.scrollTop = outputBox.scrollHeight;
}

// --- State ---
let examFinished = false;
let tabViolations = 0;
let timeLeft = 20 * 60; // 20 minutes in seconds

function setButtonsDisabled(flag) {
    runBtn.disabled = flag;
    submitBtn.disabled = flag;
    editor.disabled = flag;
}

// --- Timer ---
function formatTime(sec) {
    const m = Math.floor(sec / 60);
    const s = sec % 60;
    return `${m}:${s.toString().padStart(2, "0")}`;
}

timerDisplay.textContent = formatTime(timeLeft);

const timerId = setInterval(() => {
    if (examFinished) {
        clearInterval(timerId);
        return;
    }

    timeLeft -= 1;
    if (timeLeft <= 60) {
        timerDisplay.style.color = "#ff5555";
    }

    if (timeLeft <= 0) {
        timerDisplay.textContent = "00:00";
        clearInterval(timerId);
        appendOutput("\n[Timer] Time is up. Auto-submitting your solution...\n");
        runTests(true); // final submit
    } else {
        timerDisplay.textContent = formatTime(timeLeft);
    }
}, 1000);

// --- Basic proctoring: tab switch detection ---
document.addEventListener("visibilitychange", () => {
    if (document.hidden || document.visibilityState !== "visible") {
        if (!examFinished) {
            tabViolations += 1;
            violationDisplay.textContent = `Focus lost ${tabViolations} time(s)`;
            appendOutput(`[Proctor] Tab switch / focus lost #${tabViolations}`);

            // Optional: after 3 violations, auto-submit
            if (tabViolations === 3) {
                appendOutput("\n[Proctor] Multiple focus losses. Auto-submitting...\n");
                runTests(true);
            }
        }
    }
});

// Warn before closing/refreshing if exam not finished
window.addEventListener("beforeunload", (e) => {
    if (!examFinished) {
        e.preventDefault();
        e.returnValue = "Your test is not submitted yet. Are you sure you want to leave?";
    }
});

// --- Core: call backend to run tests ---
async function runTests(isSubmit) {
    if (examFinished && isSubmit) {
        appendOutput("[Info] Exam already finished.\n");
        return;
    }

    setButtonsDisabled(true);
    const label = isSubmit ? "Running ALL tests (final submit)..." : "Running public tests...";
    setOutput(`⏳ ${label}`);

    try {
        const res = await fetch("/run_code", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                code: editor.value,
                submit: isSubmit
            })
        });

        if (!res.ok) {
            const txt = await res.text();
            setOutput(`Server error: ${res.status}\n${txt}`);
            setButtonsDisabled(false);
            return;
        }

        const result = await res.json();
        setOutput(result.output || "No output received.");

        if (typeof result.passed === "number" && typeof result.total === "number") {
            scoreDisplay.textContent = `Score: ${result.passed}/${result.total}`;
        }

        if (result.finished) {
            examFinished = true;
            setButtonsDisabled(true);
            appendOutput("\n[Info] Final submission completed. Editor is now locked.");
        } else {
            // Re-enable for further public test runs
            setButtonsDisabled(false);
        }
    } catch (err) {
        setOutput("Client error while contacting server:\n" + err.message);
        setButtonsDisabled(false);
    }
}

// --- Wire buttons ---
runBtn.addEventListener("click", () => runTests(false));
submitBtn.addEventListener("click", () => runTests(true));
