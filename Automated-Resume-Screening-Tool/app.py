"""Optional Streamlit interface."""

from pathlib import Path
import tempfile

import pandas as pd
import streamlit as st

from src.resume_screener import screen_resumes, save_report

st.set_page_config(page_title="Resume Screening Demo", page_icon="📄", layout="wide")
st.title("Automated Resume Screening Tool")
st.caption("Educational prototype. Scores support review; they do not make hiring decisions.")

job_text = st.text_area(
    "Paste job description",
    value=Path("data/job_description.txt").read_text(encoding="utf-8")
    if Path("data/job_description.txt").exists() else "",
    height=180,
)
skills_text = st.text_input(
    "Required skills (comma-separated)",
    "Python, SQL, Pandas, NumPy, Git, REST API"
)
threshold = st.slider("Human-review priority threshold", 0, 100, 50)
uploads = st.file_uploader(
    "Upload resumes (PDF, DOCX, TXT)",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=True,
)

if st.button("Screen resumes", type="primary"):
    if not job_text.strip():
        st.error("Please enter a job description.")
    elif not uploads:
        st.error("Please upload at least one resume.")
    else:
        with tempfile.TemporaryDirectory() as temp_dir:
            resume_folder = Path(temp_dir) / "resumes"
            resume_folder.mkdir()
            for upload in uploads:
                (resume_folder / upload.name).write_bytes(upload.getvalue())

            required = [s.strip() for s in skills_text.split(",") if s.strip()]
            results = screen_resumes(
                resume_folder, job_text, required, review_threshold=threshold
            )

        st.subheader("Ranked results")
        st.dataframe(results, use_container_width=True)

        csv_data = results.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download CSV report",
            data=csv_data,
            file_name="screening_report.csv",
            mime="text/csv",
        )
        st.info(
            "Review all candidates fairly. A low text score can reflect resume wording "
            "or extraction limitations rather than lack of ability."
        )
