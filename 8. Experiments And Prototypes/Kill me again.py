import os
import re
from pathlib import Path

# ========== CONFIGURATION ==========

# IMPORTANT: This script will create the new folder in the same base directory as before.
# You can change this path if you need to.
OUTPUT_BASE_PATH = Path(r"C:\Users\ASUS\OneDrive\Documents")

# This will be the name of the new main folder.
ROOT_FOLDER_NAME = "Pharma DAX Measures"

# The final output path will be: C:\Users\ASUS\OneDrive\Documents\Pharma DAX Measures
OUTPUT_ROOT = OUTPUT_BASE_PATH / ROOT_FOLDER_NAME


# The entire data structure for the new Pharma & Clinical Trial measures.
structure = {
    "1. Commercial Performance & Market Adoption": {
        "1.1. Prescription & Sales Volume": [
            ("Total Prescriptions (TRx)", "SUM('Sales'[TRx])"),
            ("New Prescriptions (NRx)", "SUM('Sales'[NRx])"),
            ("Refill Prescriptions (RRx)", "[Total Prescriptions (TRx)] - [New Prescriptions (NRx)]"),
            ("NRx to TRx Ratio", "DIVIDE([New Prescriptions (NRx)], [Total Prescriptions (TRx)])"),
            ("Total Units Sold", "SUM('Sales'[Units])"),
            ("Gross Sales Revenue", "SUMX('Sales', 'Sales'[Units] * 'Sales'[Price per Unit])"),
            ("Net Sales Revenue", "[Gross Sales Revenue] - SUM('Sales'[Rebates & Discounts])"),
            ("TRx Growth (MoM)", "DIVIDE([TRx] - CALCULATE([TRx], DATEADD('Date'[Date], -1, MONTH)), CALCULATE([TRx], DATEADD('Date'[Date], -1, MONTH)))"),
            ("NRx Growth (QoQ)", "DIVIDE([NRx] - CALCULATE([NRx], DATEADD('Date'[Date], -1, QUARTER)), CALCULATE([NRx], DATEADD('Date'[Date], -1, QUARTER)))"),
            ("Average Prescriptions per Day", "DIVIDE([Total Prescriptions (TRx)], DISTINCTCOUNT('Sales'[Date]))"),
            ("Rolling 12-Month TRx", "CALCULATE([Total Prescriptions (TRx)], DATESINPERIOD('Date'[Date], MAX('Date'[Date]), -12, MONTH))"),
            ("Year-to-Date (YTD) Revenue", "TOTALYTD([Net Sales Revenue], 'Date'[Date])"),
            ("Forecast Accuracy (Sales)", "1 - DIVIDE(ABS(SUM('Forecast'[Forecast Units]) - [Total Units Sold]), [Total Units Sold])"),
            ("Average Selling Price (ASP)", "DIVIDE([Net Sales Revenue], [Total Units Sold])"),
            ("Total Patients on Therapy", "DISTINCTCOUNT('Patient Data'[Patient ID])"),
        ],
        "1.2. Market Share & Penetration": [
            ("TRx Market Share", "DIVIDE([Total Prescriptions (TRx)], CALCULATE([Total Prescriptions (TRx)], ALL('Product')))"),
            ("NRx Market Share", "DIVIDE([New Prescriptions (NRx)], CALCULATE([New Prescriptions (NRx)], ALL('Product')))"),
            ("New Patient Share", "DIVIDE(DISTINCTCOUNT('Patient Data'[Patient ID]), CALCULATE(DISTINCTCOUNT('Patient Data'[Patient ID]), ALL('Product')))"),
            ("Market Share Growth", "[TRx Market Share] - CALCULATE([TRx Market Share], PREVIOUSMONTH('Date'[Date]))"),
            ("Patient Penetration Rate", "DIVIDE([Total Patients on Therapy], [Total Addressable Patient Population])"),
            ("Market Value Share", "DIVIDE([Net Sales Revenue], CALCULATE([Net Sales Revenue], ALL('Product')))"),
            ("Share of Voice (SOV)", "DIVIDE([Brand Mentions], [Total Market Mentions])"),
            ("Source of Business (Switch from Competitor)", "CALCULATE([New Prescriptions (NRx)], 'Patient Data'[Previous Therapy] = \"Competitor A\")"),
            ("Competitor Volume (TRx)", "CALCULATE(SUM('Sales'[TRx]), 'Product'[Brand] = \"Competitor A\")"),
            ("Relative Market Share", "DIVIDE([TRx Market Share], [Largest Competitor Market Share])"),
        ],
    },
    "2. Physician & HCP (Healthcare Provider) Analytics": {
        "2.1. Prescriber Adoption & Value": [
            ("Total Prescriber Base", "DISTINCTCOUNT('Sales'[HCP ID])"),
            ("New Prescribers", "DISTINCTCOUNT('Sales'[HCP ID]) - CALCULATE(DISTINCTCOUNT('Sales'[HCP ID]), 'Sales'[Date] < MIN('Sales'[Date]))"),
            ("Prescriber Penetration", "DIVIDE([Total Prescriber Base], [Target HCP Universe])"),
            ("Prescriber Decile", "RANKX(ALL('HCPs'), [Total Prescriptions (TRx)], , DESC)"),
            ("High-Value Prescribers (Top 20%)", "CALCULATE([Total Prescriber Base], FILTER('HCPs', [Prescriber Decile] <= 2))"),
            ("Average TRx per Prescriber", "DIVIDE([Total Prescriptions (TRx)], [Total Prescriber Base])"),
            ("Prescriber Adoption Curve", "CALCULATE(DISTINCTCOUNT('Sales'[HCP ID]), FILTER(ALL('Date'), 'Date'[Date] <= MAX('Date'[Date])))"),
            ("Prescriber Churn Rate", "DIVIDE([Inactive Prescribers], [Total Prescriber Base])"),
            ("Key Opinion Leader (KOL) Prescribing Volume", "CALCULATE([Total Prescriptions (TRx)], 'HCPs'[Is KOL] = TRUE)"),
            ("Prescriptions by Specialty", "CALCULATE([Total Prescriptions (TRx)], ALLEXCEPT('HCPs', 'HCPs'[Specialty]))"),
        ],
        "2.2. Sales Force Effectiveness": [
            ("Sales Calls per Day per Rep", "DIVIDE(COUNTROWS('Call Log'), DISTINCTCOUNT('Call Log'[Rep ID]))"),
            ("Reach (Target HCPs Called)", "DIVIDE(DISTINCTCOUNT('Call Log'[HCP ID]), [Target HCP Universe])"),
            ("Frequency (Avg Calls per HCP)", "DIVIDE(COUNTROWS('Call Log'), DISTINCTCOUNT('Call Log'[HCP ID]))"),
            ("Rx Lift Post-Call", "[TRx After Call] - [TRx Before Call]"),
            ("Cost per Call", "DIVIDE(SUM('Sales Team'[Cost]), COUNTROWS('Call Log'))"),
            ("Sample Drop Volume", "SUM('Samples'[Units Dropped])"),
            ("Conversion Rate (Sample to Rx)", "DIVIDE([Prescriptions from Sampled HCPs], [Sampled HCPs])"),
            ("Territory Sales Performance vs. Quota", "DIVIDE(SUM('Sales'[Revenue]), SUM('Quotas'[Target]))"),
            ("Digital Engagement Rate (e.g., Webinar Attendance)", "DIVIDE([Engaged HCPs], [Invited HCPs])"),
            ("Marketing ROI", "DIVIDE(([Net Sales Revenue] - [Marketing Spend]), [Marketing Spend])"),
        ],
    },
    "3. Patient Journey & Adherence": {
        "3.1. Patient Adherence & Persistence": [
            ("Medication Possession Ratio (MPR)", "AVERAGEX('Patients', DIVIDE([Days Supply Covered], [Days in Period]))"),
            ("Proportion of Days Covered (PDC)", "[Same as MPR, but often calculated at a population level]"),
            ("Patient Persistence Rate (12-Month)", "DIVIDE([Patients still on therapy at 12M], [New Patients 12M ago])"),
            ("Average Time on Therapy", "AVERAGEX('Patients', [Last Rx Date] - [First Rx Date])"),
            ("Patient Dropout Rate", "1 - [Patient Persistence Rate]"),
            ("Refill Rate", "DIVIDE([Refill Prescriptions (RRx)], [Total Prescriptions (TRx)])"),
            ("Average Time to First Refill", "AVERAGEX('Refills', [First Refill Date] - [First Rx Date])"),
            ("Lapsing Patients", "COUNTROWS(FILTER('Patients', 'Patients'[Days Since Last Rx] > 90))"),
            ("Patient Lifetime Value (LTV)", "([Avg Monthly Revenue per Patient] / [Monthly Churn Rate])"),
            ("Adherence Rate by Cohort", "CALCULATE([MPR], 'Patient Cohorts'[Cohort] = \"Jan 2024\")"),
        ],
        "3.2. Patient Access & Support": [
            ("Co-pay Card Utilization", "DIVIDE(COUNTROWS(FILTER('Sales', 'Sales'[Used Copay Card] = TRUE)), COUNTROWS('Sales'))"),
            ("Patient Assistance Program (PAP) Enrollment", "DISTINCTCOUNT('PAP'[Patient ID])"),
            ("Formulary Acceptance Rate", "DIVIDE([Prescriptions Covered], [Total Prescriptions Submitted])"),
            ("Average Out-of-Pocket Cost", "AVERAGE('Claims'[Patient Cost])"),
            ("Prior Authorization (PA) Approval Rate", "DIVIDE([Approved PAs], [Submitted PAs])"),
        ],
    },
    "4. Clinical Trial Operations": {
        "4.1. Patient Recruitment & Enrollment": [
            ("Total Patients Screened", "COUNTROWS('Screening Log')"),
            ("Screen Failure Rate", "DIVIDE([Screen Fails], [Total Patients Screened])"),
            ("Enrollment Rate (per month)", "DIVIDE([Enrolled Patients], [Months Active])"),
            ("Enrollment vs. Target", "DIVIDE([Total Enrolled], [Enrollment Target])"),
            ("Patient Dropout Rate (from trial)", "DIVIDE([Early Terminations], [Total Enrolled])"),
            ("Diversity in Enrollment (%)", "DIVIDE(CALCULATE([Total Enrolled], 'Demographics'[Ethnicity] = \"X\"), [Total Enrolled])"),
            ("Top Recruiting Sites", "CALCULATE([Total Enrolled], ALLEXCEPT('Sites', 'Sites'[Site ID]))"),
            ("Cost per Screened Patient", "DIVIDE([Recruitment Cost], [Total Patients Screened])"),
            ("Cost per Enrolled Patient", "DIVIDE([Recruitment Cost], [Total Enrolled])"),
            ("Time to First Patient In (FPI)", "DATEDIFF([Site Initiation Date], [First Patient Enrolled Date], DAY)"),
        ],
        "4.2. Site Performance & Management": [
            ("Site Activation Time", "AVERAGEX('Sites', DATEDIFF([Contract Executed], [Site Initiation Visit], DAY))"),
            ("Protocol Deviation Rate", "DIVIDE([Number of Deviations], [Total Enrolled Patients])"),
            ("Data Query Rate", "DIVIDE([Number of Queries], [CRF Pages Submitted])"),
            ("Query Resolution Cycle Time", "AVERAGEX('Queries', [Query Closed Date] - [Query Opened Date])"),
            ("Site Monitoring Visit Rate", "COUNTROWS('Monitoring Visits') / [Active Sites]"),
            ("Clinical Research Associate (CRA) Workload", "DIVIDE([Assigned Sites], DISTINCTCOUNT('CRAs'[CRA ID]))"),
            ("Investigator Grant Payments vs. Budget", "DIVIDE([Payments Made], [Total Site Budget])"),
            ("Study Start-up Cycle Time", "DATEDIFF([Protocol Finalized], [First Patient In], DAY)"),
            ("Data Entry Timeliness", "AVERAGEX('CRF', [Data Entry Date] - [Patient Visit Date])"),
            ("Audit Finding Rate", "DIVIDE([Major Findings], [Number of Audits])"),
        ],
    },
    "5. R&D and Pharmacovigilance": {
        "5.1. R&D Pipeline & Finance": [
            ("R&D Spend as % of Revenue", "DIVIDE([Total R&D Spend], [Net Sales Revenue])"),
            ("Clinical Trial Cost (per phase)", "SUM('Trial Costs'[Cost])"),
            ("Time to Milestone (e.g., IND to NDA)", "DATEDIFF([IND Submission Date], [NDA Submission Date], DAY)"),
            ("Pipeline Success Rate (Phase II to III)", "DIVIDE([Drugs Entering Phase III], [Drugs Entering Phase II])"),
            ("Net Present Value (NPV) of Pipeline", "SUMX('Pipeline Drugs', [NPV])"),
        ],
        "5.2. Pharmacovigilance & Safety": [
            ("Adverse Event (AE) Reporting Rate", "DIVIDE(COUNTROWS('AE Reports'), [Total Patients on Therapy])"),
            ("Serious Adverse Event (SAE) Rate", "DIVIDE(COUNTROWS(FILTER('AE Reports', [Is Serious]=TRUE)), [Total Patients on Therapy])"),
            ("AE Reporting Timeliness", "AVERAGEX('AE Reports', [Date Submitted to FDA] - [Date Received])"),
            ("Signal Detection Rate", "COUNTROWS('Safety Signals')"),
            ("Risk Management Plan (RMP) Compliance", "DIVIDE([Completed RMP Activities], [Planned RMP Activities])"),
        ],
    },
}


# ========== HELPER FUNCTIONS ==========

def safe(name):
    """Sanitizes a string to be a valid folder or file name, preserving spaces."""
    # Remove leading/trailing whitespace
    name = name.strip()
    # Remove numbering and dots like "1. " or "1.1. "
    name = re.sub(r"^\d+(\.\d+)*\s*", "", name)
    # Remove characters that are generally invalid for file/folder names
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    # Clean up any potential double spaces and remove trailing whitespace
    name = re.sub(r'\s+', ' ', name).strip()
    return name

def write_markdown_files(base_path, title, dax):
    """Creates a directory and writes the README.md and the DAX measure file."""
    try:
        os.makedirs(base_path, exist_ok=True)

        # Create the README.md file
        readme_path = os.path.join(base_path, "README.md")
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(f"# {title}\n\n")
            f.write("This folder contains the documentation and DAX logic for the measure.\n")

        # Create the specific markdown file for the DAX measure
        topic_file_path = os.path.join(base_path, f"{safe(title)}.md")
        with open(topic_file_path, "w", encoding="utf-8") as f:
            f.write(f"# {title}\n\n")
            f.write("## DAX Formula\n\n")
            f.write("```dax\n")
            f.write(f"{dax}\n")
            f.write("```\n")
            
    except Exception as e:
        print(f"Error creating files for '{title}' at '{base_path}': {e}")


# ========== MAIN SCRIPT LOGIC ==========

def create_all_files(root_path, data_structure):
    """Iterates through the data structure and creates all folders and files."""
    print(f"Starting file creation in: {root_path}\n")
    
    for main_cat_name, sub_categories in data_structure.items():
        main_cat_path = os.path.join(root_path, safe(main_cat_name))
        print(f"Processing Main Category: {main_cat_name}")

        for sub_cat_name, measures in sub_categories.items():
            sub_cat_path = os.path.join(main_cat_path, safe(sub_cat_name))
            print(f"  -> Subcategory: {sub_cat_name}")

            for measure_title, measure_dax in measures:
                # The final folder for the measure itself
                measure_path = os.path.join(sub_cat_path, safe(measure_title))
                
                # Write the markdown files
                write_markdown_files(measure_path, measure_title, measure_dax)
    
    print("\n-------------------------------------------------")
    print("All markdown files created successfully!")
    print(f"Check the output folder: {root_path}")
    print("-------------------------------------------------")


# ========== RUN THE SCRIPT ==========

if __name__ == "__main__":
    create_all_files(OUTPUT_ROOT, structure)