
# 🤖 AI-Driven Coding Interview Automation System  
**Deployment Guide — Windows & Linux VM**

This tool automates technical interview rounds using **Google Forms**, **Google Sheets**, and a **Streamlit UI**.

---

##  System Overview

HR can:
1. Enter **candidate full name + email + difficulty level** in UI
2. System generates **test JSON** (L1–L5)
3. System auto-creates **Google Forms** for all rounds
4. HR copies/sends form links to candidate
5. After submission, HR runs **automatic evaluation**
6. Evaluation result is stored in **Google Sheets** (Pass/Fail)

---

##  Requirements

- Python **3.10+** installed
- Internet access (to reach Google APIs)
- Google account with access to:
  - Forms API
  - Sheets API
  - Drive API
- **OAuth 2.0 Desktop credentials**
  - Download from Google Cloud Console
  - **Save as:** `credentials.json` (in project root — very important)

> ⚠ Never commit `credentials.json` into Git.

---

## 🗂 Project Structure (important folders)

```

AI-Driven-Coding-Interview-Automation-System/
│
├─ src/
│   ├─ app.py               ← Streamlit UI (main entry point)
│   ├─ utils/
│   │   ├─ google_forms/    ← Form creation + evaluation + Sheets integration
│   │   └─ question_generator/ ← JSON test generator
│
├─ question_bank/
│   ├─ master/              ← Master question banks (AI-generated)
│   └─ tests/               ← Auto-generated candidate tests
│
├─ requirements.txt
├─ credentials.json        ← MUST BE PLACED HERE
└─ generate_all_master_banks.py


---

## 🛠 Installation and Deployment

Below steps help set up the UI on **Windows VM** or **Linux VM**  
Choose your OS ⬇️

---

## 🪟 Windows Deployment Steps

Open **Command Prompt / PowerShell**:

```bash
cd C:\path\to\
git clone https://github.com/<your-org>/AI-Driven-Coding-Interview-Automation-System.git
cd AI-Driven-Coding-Interview-Automation- System
````

Create & activate virtual environment:

```bash
py -m venv venv
venv\Scripts\activate
```

Install dependencies:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Place `credentials.json` here:

```
C:\...\AI-Driven-Coding-Interview-Automation-System\credentials.json
```

Run the app:

```bash
streamlit run src/app.py
```

Open browser →
👉 [http://localhost:8501](http://localhost:8501)

---

## 🐧 Linux Deployment Steps (Ubuntu Example)

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git
```

Clone & setup:

```bash
cd /opt
git clone https://github.com/<your-org>/AI-Driven-Coding-Interview-Automation-System.git
cd AI-Driven-Coding-Interview-Automation- System

python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Add credentials:

```bash
cp /path/to/credentials.json ./credentials.json
```

Run Streamlit:

```bash
streamlit run src/app.py --server.address 0.0.0.0 --server.port 8501
```

Access from any device:

👉 http://<VM-IP>:8501
(Ensure VM firewall allows port **8501**)

---

## ▶️ (Optional but Recommended) Run App as Service

### Linux: Auto-Start on Boot (SystemD)

Create service file:

```bash
sudo nano /etc/systemd/system/interview-app.service
```

Paste:

```ini
[Unit]
Description=Interview Automation App
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/opt/AI-Driven-Coding-Interview-Automation-System
ExecStart=/opt/AI-Driven-Coding-Interview-Automation-System/venv/bin/streamlit run src/app.py --server.address=0.0.0.0 --server.port=8501
Restart=always

[Install]
WantedBy=multi-user.target
```

Start service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable interview-app
sudo systemctl start interview-app
```

Check status:

```bash
sudo systemctl status interview-app
```

---

##  For First-Time Google Authorization

* On first run, Google prompts for login
* A browser tab will open → Login → Approve permissions (Forms + Sheets + Drive)
* `token.json` auto-created → prevents future logins

If VM has no GUI:

* Copy URL → paste in local browser → paste code back into terminal

---

##  How HR Uses the App

1️⃣ Open UI
2️⃣ Enter Candidate **Name + Email + Difficulty**
3️⃣ Click **Create Forms** → 5 clickable form links generated
4️⃣ Share links with candidate
5️⃣ After candidate submits:

* Go to **Evaluation section**
* Select **Round** and **Candidate**
* Click **Evaluate**
* Score, % and **PASS/FAIL** stored in Google Sheets

---

##  Notes

✔ L4 auto-skipped if coding question evaluation not required
✔ Marks stored under folder ID configured in `save_results_to_sheet.py`
✔ PASS criteria: **≥ 75%**

---

##  Troubleshooting

| Error                 | Fix                                               |
| --------------------- | ------------------------------------------------- |
| No auth/browser opens | Ensure internet + OAuth credentials               |
| API permission denied | Re-enable Forms/Sheets/Drive APIs in Google Cloud |
| Streamlit not loading | Check firewall port 8501                          |
| Credentials missing   | Re-place `credentials.json` in project root       |

---

##  That’s It!

Your system is **fully deployable** on any VM 🚀
HR can now run interviews without technical help.

