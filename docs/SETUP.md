#  Setup Guide -- GradeOps-AI

## Requirements

-   Python 3.10+
-   pip
-   Google Cloud credentials

------------------------------------------------------------------------

## 1. Clone repository

``` bash
git clone https://github.com/adriangilr/gradeops.git
cd gradeops
```

------------------------------------------------------------------------

## 2. Create virtual environment

``` bash
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
```

------------------------------------------------------------------------

## 3. Install dependencies

``` bash
pip install -r requirements.txt
```

------------------------------------------------------------------------

## 4. Configure Google API

1.  Go to Google Cloud Console\
2.  Enable Google Classroom API\
3.  Create OAuth credentials\
4.  Download JSON file and place it in:

```{=html}
<!-- -->
```
    credentials/client_secret.json

------------------------------------------------------------------------

## 5. First run

``` bash
python -m src.main
```

This generates:

    token.json

------------------------------------------------------------------------

## 6. Verify installation

Expected: - CLI menu appears - Courses listed - Activity selection works

------------------------------------------------------------------------

## Common Issues

### Python version warning

Upgrade to Python 3.10+

### Missing module

``` bash
pip install -r requirements.txt
```

------------------------------------------------------------------------

## Optional Environment Variables

Create `.env` file:

    OUTPUT_MODE=portfolio
    MAX_FOLDER_NAME_LEN=40
