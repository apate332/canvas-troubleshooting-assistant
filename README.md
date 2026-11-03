# Canvas Troubleshooting Assistant

## 1. Project Overview

The Canvas Troubleshooting Assistant is a Python-based application designed to help Instructional Designers identify potential configuration issues within Canvas courses.

The application accepts manually collected Canvas assignment and module data in JSON format. It extracts relevant information, evaluates the data using predefined troubleshooting rules, and displays potential issues with severity levels and recommendations.

The application also integrates PostgreSQL to store assignment information, troubleshooting findings, and previous troubleshooting runs. Users can review historical results and generate downloadable troubleshooting reports.

The primary goal is to make manual Canvas troubleshooting more organized, consistent, and efficient while supporting the Instructional Designer's decision-making.

**Important:** The current version uses manually uploaded JSON files. It does not directly connect to the Canvas API, automatically modify Canvas settings, or repair course issues.

---

## 2. Project Objectives

- Identify potential Canvas assignment configuration issues.
- Review module publishing status and module content.
- Identify potential external tool configuration concerns.
- Validate uploaded assignment information.
- Generate troubleshooting findings and recommendations.
- Store troubleshooting results in PostgreSQL.
- Maintain a history of previous troubleshooting runs.
- Generate downloadable troubleshooting reports.
- Provide a structured workflow for Instructional Designers.

---

## 3. Key Features

### JSON File Upload
Users can upload:
- Canvas assignment JSON data (required).
- Canvas module JSON data (optional).

### Data Extraction
Python extracts relevant information, including:
- Assignment ID.
- Course ID.
- Assignment name.
- Publishing status.
- Due date.
- Unlock date.
- Lock date.
- Submission types.

### Input Validation
The application checks whether required assignment information is available before running troubleshooting checks.

### Troubleshooting Engine
Predefined Python rules evaluate the uploaded information and identify potential configuration concerns.

### Issue Identification
The application displays findings with severity levels, including:
- Warning
- Review

### Recommendations
Each finding includes a suggested next step to help the Instructional Designer investigate the issue.

### PostgreSQL Database Integration
The database stores:
- Course information.
- Assignment information.
- Troubleshooting runs.
- Troubleshooting findings.

### Troubleshooting History
Users can review previous troubleshooting runs, including:
- Run ID and timestamp.
- Total findings.
- Warning count.
- Items needing review.
- Individual issues and recommendations.

### Report Generation
The application generates a text report containing assignment information, identified issues, severity levels, and recommendations.

Users can download the report for documentation or further review.

---

## 4. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main programming language used to build the application and troubleshooting logic. |
| Streamlit | Creates the application's web-based user interface, including file uploads, results, and report downloads. |
| PostgreSQL | Relational database used to store course, assignment, and troubleshooting history information. |
| Psycopg | Python database adapter that allows the application to communicate with PostgreSQL. |
| JSON | Data format used to provide Canvas assignment and module information to the application. |
| python-dotenv | Loads database connection details from the `.env` file rather than storing credentials directly in Python code. |
| VS Code | Code editor used to develop and manage the project. |
| Terminal | Used to install dependencies, activate the virtual environment, run commands, and start the application. |
| Postgres.app | macOS application used to manage and run the local PostgreSQL server. |

---

## 5. What Each Application or Tool Does

### Visual Studio Code (VS Code)
**Purpose:** Code development and project management.

Use VS Code to:
- Open the Canvas Troubleshooting project folder.
- Create and edit Python files.
- Manage folders and project structure.
- Edit the README and configuration files.
- Review errors highlighted in the code editor.

**Go here when:** You need to modify Python code, fix indentation, update troubleshooting rules, or edit project files.

### Terminal
**Purpose:** Execute commands and manage the project environment.

Use Terminal to:
- Activate the Python virtual environment.
- Install Python packages.
- Run Python tests.
- Start the Streamlit application.
- Connect to PostgreSQL using `psql`.

**Go here when:** You encounter installation problems, command errors, package issues, or need to start the application.

### Streamlit
**Purpose:** Run and display the application's user interface.

The application provides:
- JSON file uploads.
- Troubleshooting results.
- Severity summaries.
- Report generation and downloads.
- Troubleshooting history.

**Go here when:** You want to use the application, check uploaded data, review findings, or investigate an issue with the interface.

### PostgreSQL / Postgres.app
**Purpose:** Store and manage application data.

PostgreSQL maintains the application's persistent records, including:
- Courses.
- Assignments.
- Troubleshooting runs.
- Troubleshooting reports.

Postgres.app provides a convenient way to run and manage PostgreSQL locally on macOS.

**Go here when:** You encounter database connection errors, missing records, incorrect saved results, or database schema problems.

### Python and the Virtual Environment
**Purpose:** Run the application and manage its dependencies.

The `.venv` directory contains the Python packages installed specifically for this project.

Using a virtual environment helps keep project dependencies separate from other Python projects on the computer.

**Go here when:** Python cannot find a package, an import fails, or the application uses the wrong Python environment.

### Git and `.gitignore`
**Purpose:** Manage project version control and protect sensitive files.

The `.gitignore` file prevents files such as `.env`, `.venv/`, and `__pycache__/` from being included in Git commits.

**Go here when:** Preparing the project for GitHub or checking whether sensitive configuration files are excluded.

---

## 6. Project Structure

```text
Canvas-troubleshooter/
│
├── app.py
├── .env
├── .gitignore
├── requirements.txt
├── README.md
│
├── data/
│   ├── sample_assignment.json
│   └── sample_modules.json
│
├── extraction/
│   └── extract_json.py
│
├── database/
│   ├── connection.py
│   ├── operations.py
│   └── schema.sql
│
├── troubleshooting/
│   ├── assignment_checks.py
│   ├── module_checks.py
│   ├── lti_checks.py
│   └── run_checks.py
│
├── reports/
│   └── report_generator.py
│
└── test_extraction.py
```

### Explanation of Important Files

| File | Responsibility |
|---|---|
| `app.py` | Main Streamlit application. Handles uploads, validation, troubleshooting execution, database operations, results, and history display. |
| `extract_json.py` | Reads and extracts relevant information from assignment JSON data and validates required fields. |
| `assignment_checks.py` | Contains rules for checking assignment publishing status, due dates, date settings, and submission types. |
| `module_checks.py` | Checks module publishing status and module content. |
| `lti_checks.py` | Identifies external tool configuration information that requires further review. |
| `run_checks.py` | Central troubleshooting engine that calls the individual troubleshooting functions. |
| `connection.py` | Establishes a connection between Python and PostgreSQL using environment variables. |
| `operations.py` | Saves assignments and findings and retrieves previous troubleshooting results and history. |
| `schema.sql` | Defines the database tables and relationships. |
| `report_generator.py` | Generates the downloadable troubleshooting report. |
| `requirements.txt` | Lists Python dependencies required by the project. |
| `.env` | Stores local database connection credentials. |
| `.gitignore` | Excludes sensitive and unnecessary files from Git. |
| `test_extraction.py` | Contains tests for the data extraction functionality. |

---

## 7. Application Workflow

The application follows this sequence:

1. The Instructional Designer manually collects relevant Canvas data.
2. The user uploads the assignment JSON file and optionally a module JSON file.
3. Streamlit accepts the uploaded files.
4. Python extracts relevant assignment information.
5. The application validates required assignment information and the module data structure.
6. The troubleshooting engine executes predefined rules.
7. Potential issues and recommendations are generated.
8. Assignment information is saved in PostgreSQL.
9. A new troubleshooting run is created and its findings are saved.
10. Saved findings are retrieved from PostgreSQL.
11. The application displays the findings and severity summaries.
12. A downloadable troubleshooting report is generated.
13. Previous troubleshooting runs can be reviewed through the history section.

### Workflow Overview

```text
Manual Canvas Data Collection
             |
             v
       JSON Upload
             |
             v
    Data Extraction
             |
             v
     Input Validation
             |
             v
  Troubleshooting Engine
             |
             v
  Identify Potential Issues
             |
             v
       PostgreSQL
             |
             v
   Retrieve Saved Findings
             |
             v
     Streamlit Results
             |
             v
  Report and Run History
```

---

## 8. Installation and Setup

### Prerequisites

Before running the project, make sure the following are installed:

- Python 3.
- Visual Studio Code.
- PostgreSQL.
- Postgres.app (for macOS users).
- Terminal access.

### Step 1: Open the Project

Open the project folder in VS Code:

```bash
cd ~/Desktop/Canvas-troubleshooter
```

### Step 2: Create a Virtual Environment

If a virtual environment does not already exist:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

### Step 3: Install Dependencies

Install the required packages:

```bash
pip install -r requirements.txt
```

### Step 4: Configure PostgreSQL

Start the PostgreSQL server using Postgres.app.

Make sure PostgreSQL is running and that the database exists.

The current project database is:

```text
canvas_troubleshooter
```

The database connection uses:
- Host: `localhost`
- Port: `5432`
- Database: `canvas_troubleshooter`
- User: `postgres`

If setting up the project on a new computer, create the database and apply the SQL statements in `database/schema.sql` and any required migrations.

Do not run the schema or migration statements repeatedly without checking whether the tables and columns already exist.

### Step 5: Configure Environment Variables

Create or update the `.env` file in the project root.

Add the following variables:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=canvas_troubleshooter
DB_USER=postgres
DB_PASSWORD=your_postgresql_password
```

Replace the password placeholder with the PostgreSQL password configured on your computer.

Do not share the `.env` file or upload it to GitHub.

### Step 6: Verify the Database Connection

Run:

```bash
.venv/bin/python -c "from database.connection import get_connection; conn = get_connection(); print('Database connection successful!'); conn.close()"
```

Expected output:

```text
Database connection successful!
```

### Step 7: Start the Application

Run:

```bash
.venv/bin/python -m streamlit run app.py
```

Streamlit will provide a local address, usually:

```text
http://localhost:8501
```

Open the address in your browser.

---

## 9. How to Use the Application

1. Open the Streamlit application in your browser.
2. Upload a valid assignment JSON file.
3. Optionally upload a module JSON file.
4. Click **Start Troubleshooting**.
5. Review the identified issues.
6. Check the severity and recommendations for each finding.
7. Review the generated troubleshooting report.
8. Download the report if needed.
9. Scroll down to Troubleshooting History to review previous runs.

### Sample Data

The project includes sample files:

- `data/sample_assignment.json`
- `data/sample_modules.json`

These files can be used to test the application.

The sample assignment intentionally contains an unpublished assignment and uses an external tool submission type. The sample module data also includes an unpublished module, an unpublished module item, and an empty module.

These conditions are included to demonstrate how the troubleshooting rules identify potential concerns.

---

## 10. Understanding Troubleshooting Severity

The application currently uses two severity levels.

### Warning

A Warning indicates a potential configuration issue that should be investigated.

Example:

An assignment is unpublished.

Suggested action: Verify whether the assignment is intended to be available to students.

### Review

A Review indicates that the available information is incomplete or requires additional verification.

Example:

An assignment uses an external tool submission type, but the supplied information does not include an external tool launch URL.

Suggested action: Verify the external tool configuration in Canvas.

**Important:** A finding is not always proof that something is broken. The Instructional Designer should verify the relevant setting in Canvas before making changes.

---

## 11. Common Problems and How to Resolve Them

This section covers common development, setup, and application issues.

### Problem 1: ModuleNotFoundError

**Example:**

```text
ModuleNotFoundError: No module named 'streamlit'
```

**Possible cause:**

The required package is not installed in the active Python environment, or the wrong Python interpreter is being used.

**How to fix it:**

Activate the virtual environment:

```bash
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Alternatively, use the project's Python interpreter:

```bash
.venv/bin/python -m pip install -r requirements.txt
```

### Problem 2: PostgreSQL Connection Error

**Example:**

```text
connection refused
```

**Possible causes:**

- PostgreSQL is not running.
- The port is incorrect.
- The database server is unavailable.

**How to fix it:**

1. Open Postgres.app.
2. Verify that the PostgreSQL server is running.
3. Check that the configured port is `5432`.
4. Verify that the database exists.
5. Test the connection using the Python connection test.

### Problem 3: Password Authentication Failed

**Example:**

```text
password authentication failed for user "postgres"
```

**Possible cause:**

The password in `.env` does not match the PostgreSQL password.

**How to fix it:**

1. Open the `.env` file.
2. Verify the `DB_USER` and `DB_PASSWORD` values.
3. Confirm that the password matches the PostgreSQL user's configured password.
4. Save the file.
5. Restart the application and test the connection again.

Never paste database passwords into shared messages or commit them to GitHub.

### Problem 4: Missing Environment Variables

**Example:**

```text
connection failed
```

**Possible cause:**

The `.env` file is missing, incorrectly named, or not being loaded from the project root.

**How to fix it:**

1. Verify that the file is named `.env`, not `.env.txt`.
2. Place it in the project root.
3. Check that `connection.py` imports and calls `load_dotenv()`.
4. Verify that the variable names match the names used in `os.getenv()`.

### Problem 5: Invalid JSON File

**Example:**

```text
JSONDecodeError
```

**Possible cause:**

The uploaded file contains invalid JSON syntax.

**How to fix it:**

1. Open the JSON file in VS Code.
2. Check for missing commas.
3. Check for missing quotation marks.
4. Verify that brackets and braces are correctly paired.
5. Make sure the file contains valid JSON rather than Python dictionary syntax.

### Problem 6: Missing Assignment Information

**Example:**

```text
Assignment file is missing required information.
```

**Possible cause:**

The uploaded assignment JSON does not contain required information such as the assignment ID, name, or publishing status.

**How to fix it:**

1. Open the assignment JSON file.
2. Verify that the required fields exist.
3. Check that the field names match what the extraction code expects.
4. Upload the corrected file again.

### Problem 7: Incorrect Module JSON Structure

**Example:**

```text
The module JSON must contain a list of modules.
```

**Possible cause:**

The uploaded module JSON does not contain a list of module objects.

**How to fix it:**

Make sure the JSON file contains a list, with each module represented as an object.

Also verify that the module data follows the structure expected by `module_checks.py`.

### Problem 8: Database Table or Column Does Not Exist

**Example:**

```text
relation does not exist
```

or

```text
column does not exist
```

**Possible cause:**

The database schema has not been created or a required migration has not been applied.

**How to fix it:**

1. Connect to the `canvas_troubleshooter` database.
2. Check whether the required tables exist.
3. Review `database/schema.sql`.
4. Check whether any required migrations have been applied.
5. Apply only the missing schema changes.

Avoid dropping tables because doing so may delete saved troubleshooting history.

### Problem 9: Import Errors Between Python Files

**Example:**

```text
ImportError
```

**Possible cause:**

A function name is incorrect, a function is missing, or a project import path is incorrect.

**How to fix it:**

1. Check the function name in the original Python file.
2. Verify that the function is defined.
3. Check the import statement.
4. Confirm that the project folder structure is correct.
5. Run the application from the project root directory.

### Problem 10: Streamlit Application Does Not Start

**Possible causes:**

- Streamlit is not installed.
- The terminal is in the wrong directory.
- The Python environment is incorrect.
- Another application is already using the requested port.

**How to fix it:**

Run:

```bash
.venv/bin/python -m streamlit run app.py
```

If necessary, check the terminal output for the exact error and address that issue before restarting.

### Problem 11: Troubleshooting History Is Empty

**Possible causes:**

- No troubleshooting run has been saved.
- The application is connected to a different database.
- The assignment ID does not match the saved records.
- The database query is not returning the expected records.

**How to fix it:**

1. Verify that the troubleshooting run was saved successfully.
2. Check the database connection settings.
3. Verify the assignment ID.
4. Review the history retrieval function in `database/operations.py`.

### Problem 12: Findings Are Incorrect or Missing

**Possible causes:**

- The uploaded JSON data does not contain the expected fields.
- The troubleshooting rule has an incorrect condition.
- The field name in the extraction function does not match the uploaded data.
- The rule is not being called by `run_checks.py`.

**How to fix it:**

1. Inspect the uploaded JSON data.
2. Review the extraction logic in `extraction/extract_json.py`.
3. Review the appropriate rule file in `troubleshooting/`.
4. Check that the rule is included in `troubleshooting/run_checks.py`.
5. Test the rule using sample data.

---

## 12. Where to Go for Different Types of Issues

Use this table as a quick troubleshooting reference.

| Issue | Where to investigate |
|---|---|
| Application layout or upload problems | `app.py` and Streamlit |
| Assignment data extraction problems | `extraction/extract_json.py` |
| Assignment publishing or due-date checks | `troubleshooting/assignment_checks.py` |
| Module publishing or content checks | `troubleshooting/module_checks.py` |
| External tool concerns | `troubleshooting/lti_checks.py` |
| Troubleshooting rules not executing | `troubleshooting/run_checks.py` |
| Database connection problems | `database/connection.py` and `.env` |
| Saving or retrieving findings | `database/operations.py` |
| Missing database tables or columns | `database/schema.sql` and database migrations |
| Report formatting problems | `reports/report_generator.py` |
| Missing Python packages | `requirements.txt` and `.venv` |
| Application startup problems | Terminal and Streamlit |
| Git or credential protection problems | `.gitignore` |

### Recommended Troubleshooting Order

When something goes wrong:

1. Read the complete error message in the terminal.
2. Identify which part of the application is affected.
3. Locate the corresponding Python file using the table above.
4. Check the uploaded JSON data if the issue relates to missing or incorrect information.
5. Check the database connection if information cannot be saved or retrieved.
6. Correct the issue and run the application again.
7. Test the change using the sample JSON files.

---

## 13. Current Limitations

The current version is a functional prototype and has the following limitations:

1. **Manual Data Collection:** Users must collect and upload Canvas JSON data manually.
2. **No Direct Canvas API Integration:** The application does not currently retrieve course information directly from Canvas.
3. **No Automatic Repairs:** The application identifies potential issues but does not change Canvas settings.
4. **Rule-Based Detection:** Troubleshooting depends on predefined Python conditions rather than an AI model.
5. **Limited Data Coverage:** Only the fields included in the uploaded JSON data can be evaluated.
6. **External Tool Verification:** The application can flag missing external tool information for review but cannot independently confirm whether an LTI integration is functioning.
7. **Sample Data Limitations:** Sample JSON files demonstrate the expected workflow, but actual Canvas API responses should be validated before broader deployment.
8. **Limited Severity Levels:** The current system uses Warning and Review rather than a more extensive severity classification.

The application is intended to support Instructional Designers, not replace their judgment or Canvas verification.

---

## 14. Future Improvements

Potential future enhancements include:

- Direct Canvas API integration.
- Automated retrieval of assignment and module information.
- Expanded troubleshooting rules for additional Canvas course components.
- Improved validation of real Canvas API responses.
- Additional severity levels and issue prioritization.
- Comparison of troubleshooting runs to identify recurring or resolved issues.
- Improved dashboard design and visual summaries.
- More comprehensive testing with real course data.
- User authentication and role-based access.
- More detailed reports and export formats.
- Improved logging and error handling.

---

## 15. Security Considerations

- Store database credentials in `.env`.
- Never hardcode passwords in Python files.
- Keep `.env` excluded through `.gitignore`.
- Do not upload `.env` to GitHub.
- Avoid sharing real student information or sensitive course data in sample files.
- Use appropriate database permissions when deploying the application beyond a local development environment.

---

## 16. Project Summary

The Canvas Troubleshooting Assistant provides a structured approach to identifying potential Canvas configuration issues.

By combining Python-based data extraction, predefined troubleshooting rules, Streamlit, and PostgreSQL, the application helps Instructional Designers review course information, identify potential concerns, access recommendations, and maintain a history of troubleshooting results.

The project demonstrates how a manual troubleshooting workflow can be organized into a reusable application that supports more consistent course reviews.

**The overall objective is to help Instructional Designers troubleshoot more efficiently while keeping the final decisions and corrective actions under their control.**