# Automated Resume Screening Tool

An educational Python/NLP project that extracts text from sample resumes, identifies specified skills, compares resume text with a job description using TF-IDF and cosine similarity, ranks the documents, and exports a CSV report.

> **Responsible-use note:** This prototype is a decision-support demonstration, not a validated hiring system. Scores are document-matching indicators, not measures of candidate ability. Do not use it to automatically reject applicants. Human review, accessible application routes, and bias testing are required in real recruitment.

## Problem statement

Recruiters may receive many resumes for one vacancy. Manually locating relevant experience and skills can be repetitive. This project demonstrates how Python can organize resume documents and highlight text that appears relevant to a job description.

## Features

- PDF, DOCX, and TXT text extraction
- Text cleaning with regular expressions
- Configurable skill vocabulary
- Required-skill coverage calculation
- TF-IDF vectorization
- Cosine similarity
- Explainable combined matching score
- Candidate ranking
- CSV report generation
- Optional Streamlit interface
- Synthetic sample resumes

## Tech stack

Python, Pandas, NumPy, pdfplumber, python-docx, Regex, Scikit-learn, Streamlit.

## Folder structure

```text
Automated-Resume-Screening-Tool/
├── resumes/                  # Synthetic sample resumes
├── data/                     # Job description
├── src/
│   └── resume_screener.py    # Core extraction and scoring logic
├── outputs/                  # Generated CSV reports
├── images/                   # Screenshots for portfolio
├── docs/                     # Project notes
├── app.py                    # Optional Streamlit interface
├── main.py                   # Command-line entry point
├── requirements.txt
├── .gitignore
└── README.md
```

## Setup

Python 3.10 or newer is recommended.

### Windows (PowerShell)

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, use Command Prompt:

```bat
.venv\Scripts\activate.bat
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run from the command line

From the project root:

```bash
python main.py
```

Customize required skills and threshold:

```bash
python main.py --skills "Python,SQL,Pandas,NumPy,Git,REST API" --threshold 50
```

Use a different job description or folders:

```bash
python main.py --job data/job_description.txt --resumes resumes --output outputs/report.csv
```

The report is written to `outputs/screening_report.csv`.

## Run the optional dashboard

```bash
streamlit run app.py
```

Open the local URL shown in the terminal, upload sample resumes, enter a job description, and download the CSV report.

## Scoring method

The default score combines two components:

```text
Final score = 60% × TF-IDF cosine similarity
            + 40% × required-skill coverage
```

Required-skill coverage is:

```text
Detected required skills / Total required skills × 100
```

The weights are illustrative and configurable in `src/resume_screener.py`. They are not validated hiring criteria. TF-IDF and exact skill matching can miss synonyms, context, transferable skills, and formatting variations.

## Sample output

The sample files are synthetic. The exact scores depend on library versions and text content. A typical report contains:

| rank | candidate_file | matching_score | skill_coverage | status |
|---:|---|---:|---:|---|
| 1 | alex_python_developer.txt | calculated | calculated | Prioritize for human review |
| 2 | sam_data_analyst.txt | calculated | calculated | Review recommendation |
| 3 | jordan_web_developer.txt | calculated | calculated | Further review required |

Run the program to generate actual values. Do not treat the illustrative order or threshold as a hiring recommendation.

## Screenshots

Save your own screenshots in `images/`:

1. `01_project_structure.png`
2. `02_sample_resumes.png`
3. `03_terminal_run.png`
4. `04_ranked_results.png`
5. `05_csv_report.png`
6. `06_streamlit_dashboard.png` (optional)
7. `07_github_repository.png`

## Limitations and responsible use

- Scanned/image-only PDFs need OCR; this version extracts embedded text only.
- Skill detection uses an editable vocabulary and exact phrase matching.
- TF-IDF measures lexical overlap, not deep semantic understanding.
- Resume formatting and extraction errors can affect scores.
- The tool does not verify claims, employment history, qualifications, or identity.
- Do not use protected characteristics or proxies in scoring.
- Do not automatically reject applicants based on the score.
- Evaluate accessibility, disparate impact, privacy, and applicable laws before any real-world use.

## Learning outcomes

- Python modules, functions, exceptions, and file paths
- PDF/DOCX/TXT processing
- Text cleaning with Regex
- Pandas data manipulation and CSV exports
- TF-IDF and cosine similarity
- Explainable scoring and ranking
- Streamlit app development
- Git and GitHub portfolio workflow

## Future improvements

- OCR for scanned documents
- Synonym and skill taxonomy support
- Sentence-transformer semantic matching
- Unit tests and CI with GitHub Actions
- Database and API integration
- Human review feedback and fairness evaluation

## License

For educational use. Add an appropriate license before redistributing or deploying.
