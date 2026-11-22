"""Command-line entry point for the Automated Resume Screening Tool."""

from pathlib import Path
import argparse

from src.resume_screener import screen_resumes, save_report


def main():
    parser = argparse.ArgumentParser(
        description="Compare sample resumes with a job description."
    )
    parser.add_argument("--resumes", default="resumes", help="Folder containing resumes")
    parser.add_argument(
        "--job", default="data/job_description.txt",
        help="Path to the job description text file"
    )
    parser.add_argument(
        "--skills",
        default="Python,SQL,Pandas,NumPy,Git,REST API",
        help="Comma-separated required skills"
    )
    parser.add_argument(
        "--threshold", type=float, default=50.0,
        help="Score used to prioritize a resume for human review"
    )
    parser.add_argument(
        "--output", default="outputs/screening_report.csv",
        help="CSV report path"
    )
    args = parser.parse_args()

    job_path = Path(args.job)
    if not job_path.exists():
        raise FileNotFoundError(f"Job description not found: {job_path}")

    job_description = job_path.read_text(encoding="utf-8")
    required_skills = [skill.strip() for skill in args.skills.split(",") if skill.strip()]

    results = screen_resumes(
        resume_dir=args.resumes,
        job_description=job_description,
        required_skills=required_skills,
        review_threshold=args.threshold,
    )

    output_path = save_report(results, args.output)

    print("\n=== AUTOMATED RESUME SCREENING REPORT ===")
    print(f"Resumes processed: {len(results)}")
    print(f"Report saved to: {output_path}")
    if results.empty:
        print("No supported resume files were found.")
    else:
        print("\nRanked results:")
        print(results.to_string(index=False))
    print("\nNote: Scores are experimental text-matching indicators, not hiring decisions.")
    print("A human reviewer must assess every application.")


if __name__ == "__main__":
    main()
