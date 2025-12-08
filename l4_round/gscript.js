// gscript.js — CodeMirror frontend + Gemini API integration
// Base URL points to your local Flask server
const API_BASE_URL = '';
let editor;

// language mapping for Judge0 (we keep this structure but only use 'python')
const langToJudge0 = {
  python: 71,
  javascript: 63,
  cpp: 54,
  c: 50,
  java: 62,
  go: 60,
  csharp: 51
};

// CodeMirror mode mapping
const cmMode = {
  python: 'python',
  javascript: 'javascript',
  cpp: 'text/x-c++src',
  c: 'text/x-csrc',
  java: 'text/x-java',
  go: 'text/x-go'
};

// Helper function to get element by ID
const $ = id => document.getElementById(id);

// Current problem index (starts at 0)
let currentProblemIndex = 0;

/**
 * Loads the selected problem description, signature, and sample tests.
 * This is the function that controls the left sidebar content.
 */
function loadProblem(index) {
  currentProblemIndex = index;
  const problem = problems[index];
  const lang = $('languageSelect').value;

  $('problemTitle').textContent = problem.title;

  // --- 1. Generate HTML for Description and Sample I/O ---
  let descriptionHTML = `<h3>Problem Description</h3><p>${problem.description.replace(/\n/g, '<br>')}</p>`;

  // Extract the function signature from the starter code
  const starterCodeLines = (problem.starters.python || "").split('\n');
  let functionSignature = starterCodeLines.find(line => line.trim().startsWith('def '));

  // Display the required function signature
  if (functionSignature) {
      descriptionHTML += `<h3>Required Function Signature</h3><pre style="background: var(--bg); padding: 10px; border-radius: 4px; overflow-x: auto;"><code>${functionSignature.trim()}</code></pre>`;
  }

  // Format and display Sample Input/Output
  descriptionHTML += '<h3>Sample Tests</h3>';

  problem.public_tests.forEach((test, i) => {
      let inputStr = 'N/A';
      let outputStr = 'N/A';
      let typeNote = '';

      if (test.call) {
          // This is a function call test (which we use for Python)
          inputStr = test.call.trim();
          outputStr = JSON.stringify(test.output);
          typeNote = 'Function Call';
      } else if (test.stdin) {
          // This is a STDIN/STDOUT test (standard competitive programming format)
          inputStr = test.stdin.trim().replace(/\n/g, '<br>');
          outputStr = test.expected;
          typeNote = 'Standard Input/Output';
      }

      descriptionHTML += `
          <div style="margin-bottom: 10px; padding: 10px; border: 1px solid #44475a; border-radius: 4px; background: #333644;">
              <strong>Example ${i + 1}</strong> <span style="font-size: 0.8em; color: var(--yellow);">(${typeNote})</span>
              <p style="font-family: monospace; background: var(--bg); padding: 5px; margin-top: 5px; border-radius: 3px; font-size: 0.9em;">
                  <strong>Input:</strong> <br><code>${inputStr}</code><br>
                  <strong>Output:</strong> <br><code>${outputStr}</code>
              </p>
          </div>
      `;
  });

  // Apply the generated HTML to the sidebar
  $('description').innerHTML = descriptionHTML;

  // --- 2. Set Starter Code in Editor ---
  // We use the full starter code now, which includes the __main__ block if needed for STDIN testing.
  const starterCode = problem.starters.python;

  if (editor) {
      editor.setValue(starterCode);
      editor.setOption('mode', cmMode[lang] || 'python');
  }

  $('output').textContent = "Ready to run code.";
  $('scoreBox').textContent = "Ready";
}

// Builds the problem tabs based on the problems.js array
function buildTabs() {
  const container = $('tabsContainer');
  container.innerHTML = '';
  problems.forEach((p, i) => {
    const button = document.createElement('button');
    button.className = 'tab-button';
    if (i === 0) button.classList.add('active');
    button.id = `tab${i}`;
    button.dataset.index = i;
    button.textContent = p.title; // Use title for the tab name
    button.addEventListener('click', () => {
      document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
      button.classList.add('active');
      loadProblem(i);
    });
    container.appendChild(button);
  });
}

// Submits the code to the local Flask server for execution via Gemini
async function executeCode(testsType) {
    const lang = 'python'; // FIXED to python for Gemini
    const userCode = editor.getValue();
    const problem = problems[currentProblemIndex];

    $('output').textContent = "Sending code to Gemini API for execution...";
    $('scoreBox').textContent = "Running...";
    $('runButton').disabled = true;
    $('submitButton').disabled = true;

    const tests = testsType === 'public' ? problem.public_tests : problem.hidden_tests;
    if (!tests || tests.length === 0) {
        $('output').textContent = `No ${testsType} tests found for this problem.`;
        $('scoreBox').textContent = "0/0";
        $('runButton').disabled = false;
        $('submitButton').disabled = false;
        return;
    }

    let results = [];
    let testCount = 0;

    // Separate tests by type
    const callTests = tests.filter(t => t.call);
    const stdinTests = tests.filter(t => t.stdin);

    // --- 1. Run Function Call Tests (Batch 1) ---
    if (callTests.length > 0) {
        const harness = buildCallTestHarness(userCode, callTests, testCount);
        const result = await runGeminiExecution(harness);
        const processed = processRawOutput(result, testCount);
        results = results.concat(processed.details);
        testCount += callTests.length;
    }

    // --- 2. Run STDIN/STDOUT Tests (Batch 2) ---
    // STDIN tests must run sequentially as each requires isolating and capturing I/O.
    for (const test of stdinTests) {
         const harness = buildStdinTestHarness(userCode, test, testCount);
         const result = await runGeminiExecution(harness);
         const processed = processRawOutput(result, testCount);
         results = results.concat(processed.details);
         testCount++;
    }

    // 3. Final Summary
    const total = testCount;
    const passed = results.filter(d => d.ok).length;

    let detailsOutput = `--- ${testsType.toUpperCase()} TEST RESULTS ---\nTests Run: ${total}\nTests Passed: ${passed}\n\n`;

    // Sort results by index before displaying
    results.sort((a, b) => a.index - b.index);

    results.forEach(d => {
        detailsOutput += `Test ${d.index + 1}: ${d.status}\n`;
        if (d.error) {
            detailsOutput += `Error: ${d.error}\n`;
        } else {
            // For STDIN tests, display raw string output
            if (d.type === 'stdin') {
                 detailsOutput += `Input:\n${d.input}\n`;
            }
            detailsOutput += `Actual: ${d.actual}\nExpected: ${d.expected}\n`;
        }
        detailsOutput += '\n';
    });

    $('output').textContent = detailsOutput;
    $('scoreBox').textContent = `${passed}/${total} passed`;

    $('runButton').disabled = false;
    $('submitButton').disabled = false;
}

/**
 * Handles the communication with the Flask server (Gemini API).
 */
async function runGeminiExecution(harness) {
    // Implement exponential backoff for API calls
    const maxRetries = 3;
    let delay = 1000;

    for (let i = 0; i < maxRetries; i++) {
        try {
            const response = await fetch('/execute_code', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    source_code: harness,
                    language: 'python' // Always Python
                })
            });
            if (response.status === 429 && i < maxRetries - 1) {
                // Too Many Requests, retry
                await new Promise(resolve => setTimeout(resolve, delay));
                delay *= 2;
                continue;
            }
            return await response.json();
        } catch (e) {
            if (i === maxRetries - 1) {
                return {
                    error: 'Fatal client-side error communicating with server: ' + e.message,
                    status: { description: "Client/Network Error" },
                    stderr: ''
                };
            }
            await new Promise(resolve => setTimeout(resolve, delay));
            delay *= 2;
        }
    }
}

/**
 * Creates the Python wrapper script for Function Call Tests (Batch Execution).
 */
function buildCallTestHarness(userCode, tests, startIndex) {
    let harness = userCode + '\n\n';
    harness += "import json\n\n";
    harness += "def run_call_tests():\n";
    harness += "    tests = " + JSON.stringify(tests) + "\n";
    harness += "    for i, test in enumerate(tests):\n";
    harness += "        try:\n";
    harness += "            # Function call test\n";
    harness += "            result = eval(test['call'])\n";
    harness += "            expected = test['output']\n";
    harness += "            # Use JSON to reliably format complex types for comparison\n";
    harness += "            result_str = json.dumps(result, sort_keys=True)\n";
    harness += "            expected_str = json.dumps(expected, sort_keys=True)\n";
    harness += "            # Print a structured output for the frontend to parse\n";
    harness += `            print(f"@@TEST@@|{startIndex} + {i}|{result_str}|{expected_str}|call|{test['call'].replace('\\n', ' ')}")\n`;
    harness += "        except Exception as e:\n";
    harness += `            # Print error as a structured failure\n`;
    harness += `            print(f"@@ERROR@@|{startIndex} + {i}|{str(e)}")\n`;
    harness += "\nrun_call_tests()\n";
    return harness;
}

/**
 * Creates the Python wrapper script for a single STDIN/STDOUT Test.
 */
function buildStdinTestHarness(userCode, test, startIndex) {
    // Escape single quotes and backslashes in the stdin data
    const escapedStdin = test.stdin.replace(/\\/g, '\\\\').replace(/'/g, "\\'").replace(/\n/g, '\\n');

    let harness = userCode + '\n\n';
    harness += "import sys\n";
    harness += "import io\n";
    harness += "import traceback\n\n";

    // Capture user code as a string to execute it's __main__ block in isolation
    harness += "userCode = '''" + userCode.replace(/\\/g, '\\\\').replace(/'/g, "\\'").replace(/\n/g, '\\n') + "'''\n\n";

    harness += `def run_stdin_test():\n`;
    harness += `    # Simulate standard input\n`;
    harness += `    sys.stdin = io.StringIO('${escapedStdin}')\n`;
    harness += `    \n`;
    harness += `    # Capture standard output\n`;
    harness += `    old_stdout = sys.stdout\n`;
    harness += `    sys.stdout = output_buffer = io.StringIO()\n`;
    harness += `    \n`;
    harness += `    expected_output_raw = '''${test.expected.replace(/\\/g, '\\\\').replace(/'/g, "\\'")}'''\n`; // Use triple quotes for multiline

    harness += `    try:\n`;
    harness += `        # Execute the user code's __main__ block\n`;
    harness += `        exec(compile(userCode, '<string>', 'exec'))\n`;
    harness += `        \n`;
    harness += `        # Reset stdout\n`;
    harness += `        sys.stdout = old_stdout\n`;
    harness += `        \n`;
    harness += `        # Get the actual output and compare it\n`;
    harness += `        actual_output = output_buffer.getvalue().strip()\n`;
    harness += `        expected_output = expected_output_raw.strip()\n`; // Trim expectation in Python too\n`;
    harness += `        \n`;
    harness += `        # Print a structured output for the frontend to parse\n`;
    harness += `        print(f"@@TEST@@|${startIndex}|{actual_output}|{expected_output}|stdin|${escapedStdin}")\n`;
    harness += `        \n`;
    harness += `    except Exception as e:\n`;
    harness += `        sys.stdout = old_stdout\n`;
    harness += `        error_message = f"{type(e).__name__}: {str(e)}" #traceback.format_exc()\n`;
    harness += `        # Print error as a structured failure\n`;
    harness += `        print(f"@@ERROR@@|${startIndex}|{error_message}")\n`;
    harness += `        \n`;
    harness += `run_stdin_test()\n`;

    return harness;
}

/**
 * Parses the raw structured output from Gemini and returns processed details.
 */
function processRawOutput(result, startIndex) {
    let details = [];
    let passed = 0;

    // Check for explicit server/Gemini errors first
    if (result.error || result.stderr) {
        details.push({
            index: startIndex,
            status: "FAIL (Execution Error)",
            ok: false,
            error: result.error || result.stderr
        });
        return { details, passed };
    }

    // Split the raw stdout by lines and process structured markers
    const outputLines = result.stdout.split('\n').filter(line => line.trim() !== '');

    outputLines.forEach(line => {
        if (line.startsWith('@@TEST@@|')) {
            const parts = line.split('|');
            // Expected format: @@TEST@@|index|actual|expected|type|input
            if (parts.length >= 6) {
                const index = eval(parts[1]);
                const actual = parts[2].trim();
                const expected = parts[3].trim();
                const type = parts[4];
                const input = parts[5].replace(/\\n/g, '\n'); // Re-insert newlines for display

                const ok = actual === expected;
                if (ok) passed++;

                details.push({
                    index: index,
                    status: ok ? 'PASS' : 'FAIL',
                    ok: ok,
                    actual: actual,
                    expected: expected,
                    type: type,
                    input: input,
                });
            }
        } else if (line.startsWith('@@ERROR@@|')) {
             const parts = line.split('|');
             const index = eval(parts[1]);
             const error = parts[2];
             details.push({
                index: index,
                status: "FAIL (Exception)",
                ok: false,
                error: error
             });
        }
        // General print statements or non-structured output are ignored
    });

    // Fallback if no structured output was generated
    if (details.length === 0) {
        details.push({
            index: startIndex,
            status: "FAIL (No Test Output)",
            ok: false,
            error: "The code executed but did not produce the expected structured test output. Raw output:\n" + result.stdout
        });
    }

    return { details, passed };
}


// init CodeMirror
function initEditor() {
  editor = CodeMirror(document.getElementById('editor'), {
    value: '# Loading editor...',
    mode: 'python',
    theme: 'dracula',
    lineNumbers: true,
    indentUnit: 4,
    tabSize: 4,
    autofocus: true
  });
}

// wire UI
document.addEventListener('DOMContentLoaded', () => {
  initEditor();
  buildTabs();
  loadProblem(0);

  // Wire buttons to execution functions
  $('runButton').addEventListener('click', () => executeCode('public'));
  $('submitButton').addEventListener('click', () => executeCode('hidden'));
});