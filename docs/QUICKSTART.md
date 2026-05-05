#  Quick Start -- GradeOps-AI

Run the gradder in under 2 minutes.

------------------------------------------------------------------------

## 1. Clone repo

``` bash
git clone https://github.com/adriangilr/gradeops.git
cd gradeops
```

------------------------------------------------------------------------

## 2. Setup environment

``` bash
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
```

------------------------------------------------------------------------

## 3. Install dependencies

``` bash
pip install -r requirements.txt
pip install -r requirements.txt
```

------------------------------------------------------------------------

## 4. Run application

``` bash
python -m src.main
```

------------------------------------------------------------------------

##  Expected Output

-   CLI menu appears
-   Courses are listed
-   You can select an activity
-   CSV + logs are generated

------------------------------------------------------------------------

## 📂 Output Structure

   output/
   └── course_name-activity_name
         ├── grading_results.csv
         ├── logActivity.yaml
         └── attachments/

------------------------------------------------------------------------

## Suggested Flow desc.

Use this flow for demo: 1. Run project 2. Select
course 3. Generate CSV 4. Show results in dashboard (Power BI / Tableau)
