// ===========================================================
// DOM ELEMENTS
// ===========================================================
const editor = document.getElementById("editor");
const outputBox = document.getElementById("output-box");
const sampleContainer = document.getElementById("sample-tests");
const runBtn = document.getElementById("run-btn");
const runHiddenBtn = document.getElementById("run-hidden-btn");
const submitBtn = document.getElementById("submit-btn");
const timerDisplay = document.getElementById("timer-display");
const scoreDisplay = document.getElementById("score-display");
const violationDisplay = document.getElementById("violation-display");
const langSelect = document.getElementById("lang-select");

// ===========================================================
// STARTER CODE
// ===========================================================
editor.value = STARTERS["python"];

// ===========================================================
// SAMPLE TESTS
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
        submitTest();
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
// CORE API CALL
// ===========================================================
async function executeTests({ submit = false, runHidden = false }) {
    setOutput(
        submit
            ? "Submitting final solution..."
            : runHidden
            ? "Running hidden test cases..."
            : "Running public test cases..."
    );

    const response = await fetch("/run_code", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            code: editor.value,
            language: langSelect.value,
            submit: submit,
            run_hidden: runHidden,
            focus_lost: tabViolations
        })
    });

    return response.json();
}

// ===========================================================
// BUTTON ACTIONS
// ===========================================================
async function runPublicTests() {
    const result = await executeTests({ submit: false, runHidden: false });

    scoreDisplay.textContent = `Score: ${result.passed}/${result.total}`;
    setOutput(`✅ Public Tests Passed: ${result.passed}/${result.total}`);
}

async function runHiddenTests() {
    const result = await executeTests({ submit: false, runHidden: true });

    scoreDisplay.textContent = `Hidden: ${result.passed}/${result.total}`;
    setOutput(`🔒 Hidden Tests Passed: ${result.passed}/${result.total}`);
}

async function submitTest() {
    examFinished = true;

    runBtn.disabled = true;
    runHiddenBtn.disabled = true;
    submitBtn.disabled = true;
    editor.disabled = true;

    const result = await executeTests({ submit: true });

    scoreDisplay.textContent = `Final Score: ${result.passed}/${result.total}`;
    setOutput(
        "✅ Test submitted successfully.\n\n" +
        "You may now close this page."
    );
}

// ===========================================================
// EVENT BINDINGS
// ===========================================================
runBtn.addEventListener("click", runPublicTests);
runHiddenBtn.addEventListener("click", runHiddenTests);
submitBtn.addEventListener("click", submitTest);

langSelect.addEventListener("change", () => {
    editor.value = STARTERS[langSelect.value];
    setOutput(`📝 ${langSelect.value.toUpperCase()} template loaded`);
});
