import tabula
import pandas as pd
import csv

# Step 1: Extract table from PDF
def extract_table_from_pdf(pdf_path, page_number):
    tables = tabula.read_pdf(pdf_path, pages=page_number)
    if tables:
        return tables[0]  # Assuming we want the first table on the page
    return None

# Step 2: Print table in a structured manner
def print_table(table):
    print(table.to_string(index=False))

# Step 3: Save table to CSV
def save_to_csv(table, output_path):
    table.to_csv(output_path, index=False)

# Main function
def main():
    pdf_path = "your_pdf_file.pdf"
    page_number = 1  # Adjust this to the page where your table is located
    output_csv = "output_table.csv"

    # Extract table
    extracted_table = extract_table_from_pdf(pdf_path, page_number)
    
    if extracted_table is not None:
        # Print table
        print("Extracted Table:")
        print_table(extracted_table)
        
        # Save to CSV
        save_to_csv(extracted_table, output_csv)
        print(f"\nTable saved to {output_csv}")
    else:
        print("No table found in the specified page.")

if __name__ == "__main__":
    main()