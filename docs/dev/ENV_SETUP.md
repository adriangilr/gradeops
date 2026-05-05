# GradeOps-AI — Setup Guide (macOS & Windows)

A guide to set up and run the **GradeOps-AI** project in VS Code on macOS (including High Sierra) and Windows.

---

## 1. Requirements

### General
- Python 3.8 (compatible with older systems) or ideally 3.10+
- Git
- VS Code

---

## 2. Clone the repository

```bash
git clone https://github.com/adriangilr/gradeops.git
cd gradeops
```

---

## 3. Create virtual environment

### macOS / Linux
```bash
python -m venv venv
source venv/bin/activate
```

> If `venv` fails on older macOS:
```bash
python -m ensurepip --upgrade
```

---

### Windows (PowerShell)
```powershell
python -m venv venv
venv\Scripts\activate
```

> If it fails:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 4. Install dependencies

```bash
pip install -r requirements.txt
```

If the file does not exist:
```bash
pip install pandas google-api-python-client python-docx PyPDF2 python-pptx
```

---

## 5. Configure credentials (Google API)

1. Go to Google Cloud Console
2. Create a project
3. Enable:
   - Google Classroom API
   - Google Drive API
4. Create OAuth credentials
5. Download as:

```
client_secret.json
```

Place it in:

```
/credentials/
```

---

## 6. Run the project

```bash
python -m src.main
```

---

## 7. VS Code Setup

1. Open the project folder
2. Select interpreter:
   - `Ctrl + Shift + P`
   - "Python: Select Interpreter"
   - Choose `venv`

3. Extensions:
   - Python
   - Pylance

---

## 8. Expected structure

```
gradeops/
│
├── src/
│   └── main.py
├── data/
├── downloads/
├── requirements.txt
└── credentials.json
```

---

## 9. Common issues

### ❌ No venv displayed on VS code

- Make sure venv folder has been created on 

gradeops/venv/bin/python


```bash
python -m venv venv
```

---

### ❌ No module named 'googleapiclient'
```bash
pip install google-api-python-client
```

---

### ❌ Old Python (macOS High Sierra)
Use:
```bash
python3.8
```

---

### ❌ SSL / urllib3 error
Can be ignored on older macOS or fix with:
```bash
pip install "urllib3<2"
```

---

## 10. Typical execution

```bash
source venv/bin/activate   # mac
venv\Scripts\activate    # windows

python -m src.main
```

---

## 11. Portfolio note

This project is designed for:

- Academic grading automation
- File processing
- Operational data analysis
- API integration

---

## Quick Start

```bash
git clone <repo>
cd gradeops-ai
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m src.main
```

---

##  About

Built by Adrian Gil  
Data Analyst | Operational Analytics  

Focused on building practical data tools for real-world workflows.