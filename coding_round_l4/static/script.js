// ===========================================================
// DOM ELEMENTS
// ===========================================================
const editor = document.getElementById("editor");
const outputBox = document.getElementById("output-box");
const sampleContainer = document.getElementById("sample-tests");
const runBtn = document.getElementById("run-btn");
const submitBtn = document.getElementById("submit-btn");
const timerDisplay = document.getElementById("timer-display");
const scoreDisplay = document.getElementById("score-display");
const violationDisplay = document.getElementById("violation-display");
const langSelect = document.getElementById("lang-select");

// ===========================================================
// ✅ USE BACKEND STARTERS (CRITICAL FIX)
// STARTERS is injected from index.html
// ===========================================================
editor.value = STARTERS["python"];

// ===========================================================
// DISPLAY PUBLIC SAMPLE TESTS
// ===========================================================
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

// ===========================================================
// OUTPUT HELPERS
// ===========================================================
function setOutput(msg) {
    outputBox.textContent = msg;
    outputBox.scrollTop = outputBox.scrollHeight;
}

function appendOutput(msg) {
    outputBox.textContent += "\n" + msg;
    outputBox.scrollTop = outputBox.scrollHeight;
}

// ===========================================================
// TIMER & PROCTORING
// ===========================================================
let examFinished = false;
let tabViolations = 0;
let timeLeft = 20 * 60;

function formatTime(seconds) {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${s.toString().padStart(2, "0")}`;
}

timerDisplay.textContent = formatTime(timeLeft);

const timerId = setInterval(() => {
    if (examFinished) return;

    timeLeft--;
    if (timeLeft <= 60) timerDisplay.style.color = "#ff5555";
    if (timeLeft <= 0) {
        appendOutput("\n⏳ Time is up! Auto-submitting...");
        runTests(true);
        clearInterval(timerId);
        return;
    }

    timerDisplay.textContent = formatTime(timeLeft);
}, 1000);

document.addEventListener("visibilitychange", () => {
    if (!examFinished && document.hidden) {
        tabViolations++;
        violationDisplay.textContent = `Focus lost ${tabViolations} time(s)`;
        appendOutput(`[Proctor] Focus lost #${tabViolations}`);
    }
});

// ===========================================================
// CORE FUNCTION — RUN TESTS
// ===========================================================
async function runTests(isSubmit) {
    runBtn.disabled = true;
    submitBtn.disabled = true;
    editor.disabled = true;

    setOutput(isSubmit ? "Running all tests..." : "Running public tests...");

    try {
        const response = await fetch("/run_code", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                code: editor.value,
                language: langSelect.value,
                submit: isSubmit,
                focus_lost: tabViolations
            })
        });

        const result = await response.json();

        if (result.total !== undefined) {
            scoreDisplay.textContent = `Score: ${result.passed}/${result.total}`;
        }

        setOutput(result.output || "Done");

    } catch (err) {
        setOutput("Client Error: " + err.message);
    }

    runBtn.disabled = false;
    submitBtn.disabled = false;
    editor.disabled = false;
}

// ===========================================================
// UI EVENTS
// ===========================================================
runBtn.addEventListener("click", () => runTests(false));
submitBtn.addEventListener("click", () => runTests(true));

langSelect.addEventListener("change", () => {
    const lang = langSelect.value;
    editor.value = STARTERS[lang];
    setOutput(`📝 ${lang.toUpperCase()} template loaded`);
});
