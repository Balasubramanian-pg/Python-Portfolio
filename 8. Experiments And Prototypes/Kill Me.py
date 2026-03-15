import os
import re
from pathlib import Path

# ========== CONFIGURATION ==========

# IMPORTANT: Set the base path where you want the "Healthcare DAX Measures" folder to be created.
# Please verify this is correct for your system.
OUTPUT_BASE_PATH = Path(r"C:\Users\ASUS\OneDrive\Documents")

# This will be the name of the main folder created inside the path above.
ROOT_FOLDER_NAME = "Healthcare DAX Measures"

# The final output path will be: C:\Users\ASUS\OneDrive\Documents\Healthcare DAX Measures
OUTPUT_ROOT = OUTPUT_BASE_PATH / ROOT_FOLDER_NAME


# The entire data structure of DAX measures.
structure = {
    "1. Clinical & Patient Outcomes": {
        "1.1 Patient Safety & Quality": [
            ("Hospital-Acquired Infection (HAI) Rate", "DIVIDE([Number of HAIs], [Patient Days]) * 1000"),
            ("Patient Fall Rate", "DIVIDE([Number of Falls], [Patient Days]) * 1000"),
            ("Medication Error Rate", "DIVIDE([Medication Errors], [Medications Administered])"),
            ("Adverse Drug Event (ADE) Rate", "DIVIDE([Number of ADEs], [Patient Admissions])"),
            ("Pressure Ulcer Rate", "DIVIDE([Number of New Ulcers], [Total Patients Surveyed])"),
            ("Central Line-Associated Bloodstream Infection (CLABSI) Rate", "DIVIDE([CLABSI Cases], [Central Line Days]) * 1000"),
            ("Catheter-Associated Urinary Tract Infection (CAUTI) Rate", "DIVIDE([CAUTI Cases], [Catheter Days]) * 1000"),
            ("Surgical Site Infection (SSI) Rate", "DIVIDE([SSI Cases], [Total Surgeries])"),
            ("Unplanned Readmission Rate (30-Day)", "DIVIDE([Readmissions within 30 Days], [Total Discharges])"),
            ("Mortality Rate (In-Hospital)", "DIVIDE([In-Hospital Deaths], [Total Discharges])"),
            ("Patient Satisfaction Score (HCAHPS)", "AVERAGE('Surveys'[HCAHPS Score])"),
            ("Net Promoter Score (NPS) - Patient", "[% Promoters] - [% Detractors]"),
            ("Sepsis Mortality Rate", "DIVIDE([Sepsis-Related Deaths], [Total Sepsis Cases])"),
            ("Ventilator-Associated Pneumonia (VAP) Rate", "DIVIDE([VAP Cases], [Ventilator Days]) * 1000"),
            ("Hand Hygiene Compliance Rate", "DIVIDE([Compliant Observations], [Total Observations])"),
        ],
        "1.2 Treatment & Procedure Effectiveness": [
            ("Average Length of Stay (ALOS)", "AVERAGEX('Admissions', DATEDIFF([Admission Date], [Discharge Date], DAY))"),
            ("ALOS Index", "[Actual ALOS] / [Expected ALOS]"),
            ("Post-Operative Complication Rate", "DIVIDE([Patients with Complications], [Total Surgical Patients])"),
            ("Antibiotic Stewardship Rate", "DIVIDE([Appropriate Antibiotic Use], [Total Antibiotic Prescriptions])"),
            ("Time to Treatment (Door-to-Balloon)", "AVERAGEX('Cases', [Balloon Inflation Time] - [Arrival Time])"),
            ("Chemotherapy Adherence Rate", "DIVIDE([Completed Cycles], [Prescribed Cycles])"),
            ("Blood Product Utilization Rate", "DIVIDE([Units Transfused], [Patient Days])"),
            ("C-Section Rate (Low-Risk Pregnancies)", "DIVIDE([NTSV C-Sections], [Total NTSV Births])"),
            ("Successful Procedure Rate", "DIVIDE([Successful Outcomes], [Total Procedures])"),
            ("Pain Management Effectiveness", "AVERAGE('PainAssessments'[Score Reduction])"),
        ],
    },
    "2. Operational Efficiency": {
        "2.1 Patient Flow & Throughput": [
            ("Bed Occupancy Rate", "DIVIDE([Occupied Beds], [Available Beds])"),
            ("Bed Turnover Rate", "DIVIDE([Total Discharges], [Average Bed Count])"),
            ("Emergency Department (ED) Wait Time", "AVERAGE('EDVisits'[Time to See Provider])"),
            ("ED Length of Stay (Discharged)", "AVERAGE('EDVisits'[Discharge Time] - [Arrival Time])"),
            ("ED Diversion Hours", "SUM('EDStatus'[Diversion Hours])"),
            ("Left Without Being Seen (LWBS) Rate", "DIVIDE([LWBS Patients], [Total ED Arrivals])"),
            ("Operating Room (OR) Utilization", "DIVIDE([Actual OR Hours Used], [Scheduled OR Hours])"),
            ("First Case On-Time Starts", "DIVIDE([On-Time First Cases], [Total First Cases])"),
            ("OR Turnover Time", "AVERAGEX('Surgeries', [Next Patient In Room Time] - [Previous Patient Out Time])"),
            ("Discharge Before Noon Rate", "DIVIDE([Discharges Before 12 PM], [Total Discharges])"),
            ("Patient Throughput", "DISTINCTCOUNT('PatientEncounters'[PatientID])"),
            ("Lab Test Turnaround Time", "AVERAGE('LabTests'[Result Time] - [Order Time])"),
            ("Radiology Image Turnaround Time", "AVERAGE('Imaging'[Report Ready Time] - [Exam End Time])"),
            ("Appointment No-Show Rate", "DIVIDE([No-Shows], [Total Scheduled Appointments])"),
            ("New Patient Appointments", "CALCULATE(DISTINCTCOUNT('Appointments'[PatientID]), 'Appointments'[Is New Patient] = TRUE)"),
        ],
        "2.2 Resource & Asset Management": [
            ("Medical Equipment Utilization", "DIVIDE([Actual Usage Hours], [Available Hours])"),
            ("Staff-to-Patient Ratio", "DIVIDE([On-Duty Clinical Staff], [Current Patient Census])"),
            ("Physician Caseload", "DIVIDE([Active Patients], [Number of Physicians])"),
            ("Medical Supply Cost Per Patient Day", "DIVIDE([Total Supply Cost], [Patient Days])"),
            ("Pharmacy Cost Per Discharge", "DIVIDE([Total Pharmacy Costs], [Total Discharges])"),
            ("Room Turnover Time (Inpatient)", "AVERAGE('Rooms'[Ready Time] - [Patient Discharge Time])"),
            ("Telehealth Session Volume", "COUNTROWS('TelehealthSessions')"),
            ("E-Prescribing Rate", "DIVIDE([Electronic Prescriptions], [Total Prescriptions])"),
            ("EHR Downtime", "SUM('EHRLogs'[Downtime Minutes])"),
            ("Cost per Procedure", "DIVIDE([Total Procedure Cost], [Procedure Count])"),
        ],
    },
    "3. Financial Performance": {
        "3.1 Revenue Cycle Management (RCM)": [
            ("Gross Collection Rate", "DIVIDE([Total Collections], [Gross Charges])"),
            ("Net Collection Rate", "DIVIDE([Total Collections], [Net Patient Revenue])"),
            ("Days in Accounts Receivable (A/R)", "DIVIDE([Total A/R], [Average Daily Revenue])"),
            ("A/R Aging > 90 Days %", "DIVIDE([A/R > 90 Days], [Total A/R])"),
            ("Claim Denial Rate", "DIVIDE([Denied Claims], [Total Claims Submitted])"),
            ("Clean Claim Rate", "DIVIDE([Claims Paid on First Submission], [Total Claims Submitted])"),
            ("Cost to Collect", "DIVIDE([Total RCM Costs], [Total Collections])"),
            ("Payer Mix (%)", "DIVIDE(CALCULATE([Revenue], 'Payers'[Category] = \"Commercial\"), [Total Revenue])"),
            ("Bad Debt Expense", "SUM('Financials'[Bad Debt])"),
            ("Charity Care Provided", "SUM('Financials'[Charity Care Cost])"),
            ("Copay Collection at Time of Service Rate", "DIVIDE([Copays Collected at Visit], [Total Copays Due])"),
            ("Denial Appeal Success Rate", "DIVIDE([Overturned Denials], [Total Denials Appealed])"),
            ("Unbilled A/R", "SUM('AR'[Unbilled Amount])"),
            ("Cash Flow from Operations", "[Net Income] + [Depreciation] - [Change in Working Capital]"),
            ("Charge Lag Days", "AVERAGEX('Encounters', DATEDIFF([Service Date], [Charge Posted Date], DAY))"),
        ],
        "3.2 Profitability & Cost Management": [
            ("Operating Margin", "DIVIDE([Operating Income], [Net Patient Revenue])"),
            ("EBITDA Margin", "DIVIDE([EBITDA], [Total Revenue])"),
            ("Net Patient Revenue", "[Gross Charges] - [Contractual Allowances] - [Charity Care]"),
            ("Revenue Per Bed", "DIVIDE([Net Patient Revenue], [Number of Licensed Beds])"),
            ("Cost Per Patient Day", "DIVIDE([Total Operating Expenses], [Patient Days])"),
            ("Contribution Margin Per Case", "[Revenue Per Case] - [Variable Cost Per Case]"),
            ("Salary & Benefit Expense Ratio", "DIVIDE([Total Salaries & Benefits], [Net Operating Revenue])"),
            ("Drug Cost Per Patient Day", "DIVIDE([Total Drug Costs], [Patient Days])"),
            ("Supply Cost as % of Revenue", "DIVIDE([Total Supply Costs], [Net Operating Revenue])"),
            ("Case Mix Index (CMI)", "AVERAGE('Cases'[Case Weight])"),
        ],
    },
    "4. Population Health & Value-Based Care": {
        "4.1 Preventative Care & Wellness": [
            ("Preventative Screening Rate", "DIVIDE([Screenings Performed], [Eligible Population])"),
            ("Immunization Rate", "DIVIDE([Immunizations Given], [Target Population])"),
            ("Chronic Disease Management Rate", "DIVIDE([Patients with A1c < 8], [Total Diabetic Patients])"),
            ("High-Risk Patient Identification Rate", "DIVIDE([Identified High-Risk Patients], [Total Patient Population])"),
            ("Wellness Program Enrollment", "COUNTROWS(FILTER('Patients', 'Patients'[Enrolled in Wellness] = TRUE))"),
            ("Smoking Cessation Counseling Rate", "DIVIDE([Smokers Counseled], [Total Smokers Identified])"),
            ("Annual Wellness Visit (AWV) Completion Rate", "DIVIDE([Completed AWVs], [Eligible Medicare Patients])"),
            ("Gaps in Care Closure Rate", "DIVIDE([Closed Gaps], [Identified Gaps])"),
            ("Patient Portal Adoption Rate", "DIVIDE([Active Portal Users], [Total Active Patients])"),
            ("Health Risk Assessment (HRA) Completion", "DIVIDE([Completed HRAs], [Target Population])"),
        ],
        "4.2 Value-Based Performance": [
            ("Cost Per Member Per Month (PMPM)", "DIVIDE([Total Healthcare Costs], [Total Member Months])"),
            ("Avoidable ED Visits", "COUNTROWS(FILTER('EDVisits', 'EDVisits'[Is Avoidable] = TRUE))"),
            ("Shared Savings/Losses", "SUM('Contracts'[Performance Payment])"),
            ("Readmission Cost Avoidance", "[Avoided Readmissions] * [Average Cost Per Readmission]"),
            ("Patient Attribution Rate", "DIVIDE([Attributed Lives], [Total Eligible Lives])"),
            ("Quality Measure Score", "AVERAGE('QualityMeasures'[Performance Score])"),
            ("Total Cost of Care (TCOC)", "SUM('Claims'[Allowed Amount])"),
            ("In-Network Utilization Rate", "DIVIDE([In-Network Visits], [Total Visits])"),
            ("Episode of Care Cost", "SUMX(FILTER('Claims', 'Claims'[EpisodeID] = SELECTEDVALUE('Episodes'[ID])), 'Claims'[Paid Amount])"),
            ("Referral Leakage Rate", "DIVIDE([Out-of-Network Referrals], [Total Referrals])"),
        ],
    },
    "5. Human Resources & Workforce": {
        "5.0 Workforce Metrics": [
            ("Clinical Staff Turnover Rate", "DIVIDE([Separated Clinical Staff], [Average Clinical Headcount])"),
            ("Nurse Turnover Rate", "DIVIDE([Separated Nurses], [Average Nurse Headcount])"),
            ("Physician Burnout Rate", "AVERAGE('Surveys'[Burnout Score])"),
            ("Employee Engagement Score", "AVERAGE('Surveys'[Engagement Score])"),
            ("Overtime Hours as % of Total Hours", "DIVIDE([Overtime Hours], [Total Paid Hours])"),
            ("Agency/Contract Labor Cost %", "DIVIDE([Agency Labor Cost], [Total Labor Cost])"),
            ("Vacancy Rate", "DIVIDE([Open Positions], [Total Positions])"),
            ("Time to Fill (Positions)", "AVERAGEX('Hiring', DATEDIFF([Date Opened], [Date Filled], DAY))"),
            ("New Hire Retention Rate (1-Year)", "DIVIDE([New Hires Still Employed at 1 Year], [Total New Hires])"),
            ("Training & Certification Compliance", "DIVIDE([Compliant Employees], [Total Employees])"),
        ],
    }
}


# ========== HELPER FUNCTIONS ==========

def safe(name):
    """Sanitizes a string to be a valid folder or file name, preserving spaces."""
    # Remove leading/trailing whitespace
    name = name.strip()
    # Remove numbering and dots like "1. " or "1.1. "
    name = re.sub(r"^\d+(\.\d+)*\s*", "", name)
    # Remove characters that are generally invalid for file/folder names,
    # but keep spaces, hyphens, parentheses, and the '&' symbol.
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    # Clean up any potential double spaces that might result from replacements
    # and remove any trailing whitespace.
    name = re.sub(r'\s+', ' ', name).strip()
    return name

def write_markdown_files(base_path, title, dax):
    """Creates a directory and writes the README.md and the DAX measure file."""
    try:
        # Create the directory structure. `exist_ok=True` prevents errors if it already exists.
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
    
    # Loop through main categories (e.g., "1. Clinical & Patient Outcomes")
    for main_cat_name, sub_categories in data_structure.items():
        main_cat_path = os.path.join(root_path, safe(main_cat_name))
        print(f"Processing Main Category: {main_cat_name}")

        # Loop through subcategories (e.g., "1.1 Patient Safety & Quality")
        for sub_cat_name, measures in sub_categories.items():
            sub_cat_path = os.path.join(main_cat_path, safe(sub_cat_name))
            print(f"  -> Subcategory: {sub_cat_name}")

            # Loop through the list of measures (tuples of title and DAX)
            for measure_title, measure_dax in measures:
                measure_path = os.path.join(sub_cat_path, safe(measure_title))
                
                # Call the function to write the actual files
                write_markdown_files(measure_path, measure_title, measure_dax)
    
    print("\n-------------------------------------------------")
    print("All markdown files created successfully!")
    print(f"Check the output folder: {root_path}")
    print("-------------------------------------------------")


# ========== RUN THE SCRIPT ==========

if __name__ == "__main__":
    create_all_files(OUTPUT_ROOT, structure)