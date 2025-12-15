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

function setOutput(text) {
    outputBox.textContent = text;
    outputBox.scrollTop = outputBox.scrollHeight;
}

function appendOutput(text) {
    outputBox.textContent += "\n" + text;
    outputBox.scrollTop = outputBox.scrollHeight;
}

let examFinished = false;
let tabViolations = 0;
let timeLeft = 20 * 60;

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
        appendOutput("\n[Timer] Time is up. Auto-submitting...\n");
        runTests(true);
    } else {
        timerDisplay.textContent = formatTime(timeLeft);
    }
}, 1000);

// --- Focus / tab detection ---
document.addEventListener("visibilitychange", () => {
    if (document.hidden && !examFinished) {
        tabViolations += 1;
        violationDisplay.textContent = `Focus lost ${tabViolations} time(s)`;
        appendOutput(`[Proctor] Focus lost #${tabViolations}`);
    }
});

window.addEventListener("beforeunload", (e) => {
    if (!examFinished) {
        e.preventDefault();
        e.returnValue = "Your test is not submitted yet.";
    }
});

// --- Backend call ---
async function runTests(isSubmit) {
    if (examFinished && isSubmit) return;

    runBtn.disabled = true;
    submitBtn.disabled = true;
    editor.disabled = true;

    setOutput(isSubmit ? "Running final tests..." : "Running public tests...");

   try {
    const res = await fetch("/run_code", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            code: editor.value,
            submit: isSubmit,
            focus_violations: tabViolations
        })
    });


        const result = await res.json();
        setOutput(result.output || "");

        if (typeof result.passed === "number") {
            scoreDisplay.textContent = `Score: ${result.passed}/${result.total}`;
        }

        if (result.finished) {
            examFinished = true;
            appendOutput("\n[Info] Final submission completed.");
        } else {
            runBtn.disabled = false;
            submitBtn.disabled = false;
            editor.disabled = false;
        }

    } catch (err) {
        setOutput("Client error: " + err.message);
        runBtn.disabled = false;
        submitBtn.disabled = false;
        editor.disabled = false;
    }
}

runBtn.addEventListener("click", () => runTests(false));
submitBtn.addEventListener("click", () => runTests(true));
