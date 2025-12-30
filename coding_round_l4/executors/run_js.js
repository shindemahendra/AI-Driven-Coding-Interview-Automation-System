const fs = require("fs");
const { execSync } = require("child_process");

function main() {
    try {
        const input = JSON.parse(fs.readFileSync(0, "utf8"));
        const code = input.code;
        const args = input.args;

        fs.writeFileSync("temp_user_code.js", code + `
const result = solve(...(${JSON.stringify(args)}));
console.log(result);
        `);

        let output = execSync("node temp_user_code.js", { timeout: 5000 })
            .toString()
            .trim();

        console.log(JSON.stringify({
            stdout: output,
            stderr: "",
            returncode: 0
        }));

    } catch (err) {
        console.log(JSON.stringify({
            stdout: "",
            stderr: err.toString(),
            returncode: -1
        }));
    }
}

main();
