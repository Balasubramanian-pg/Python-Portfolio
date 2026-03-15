import os
import re

def clean_name(text):
    """
    1. Replaces special characters like / with space.
    2. Removes - and _.
    3. Capitalizes each word.
    4. Removes extra whitespace.
    """
    # Replace slashes and other illegal filename chars with space
    text = re.sub(r'[\\/*?:"<>|]', ' ', text)
    # Replace underscores and hyphens with space
    text = text.replace('_', ' ').replace('-', ' ')
    # Capitalize each word (Title Case)
    text = text.title()
    # Remove extra spaces
    return " ".join(text.split())

def create_structure():
    # Define the Root Folder Name
    root_folder = clean_name("Phase 3: Deep Dive into Key Technologies")
    
    # Define the Hierarchy
    hierarchy = {
        "Apache Spark": {
            "Spark Architecture": """Core Concepts:
1. Driver vs Executor processes
2. Logical plan vs physical plan
3. Tasks, stages, shuffle mechanics
4. Why more partitions can speed up parallelism but too many can hurt performance""",
            
            "Spark Apis": """APIs:
1. RDD (low-level, rarely used today)
2. DataFrames (the standard for ETL, analytics)
3. Datasets (type-safe API used mostly in Scala)""",
            
            "Transformations Vs Actions": """1. Transformations (lazy): select, filter, withColumn, groupBy, join
2. Actions (trigger execution): count(), collect(), show(), write operations""",
            
            "Lazy Evaluation": """1. Spark builds a logical plan instead of executing immediately
2. Execution happens only when an action is called
3. This enables optimisation using the Catalyst optimizer""",
            
            "Partitioning And Performance": """1. Repartition vs Coalesce
2. When to partition your data
3. Skew handling
4. File size considerations
5. Shuffle operations and their cost""",
            
            "Essential Skills Spark": """1. Convert SQL logic into Spark transformations
2. Analyse query plans using explain()
3. Optimise slow transformations
4. Understand how joins affect shuffles"""
        },
        
        "Delta Lake": {
            "Storage Format And Transaction Log": """1. Delta is Parquet plus a transaction log
2. Provides ACID guarantees on data lake storage
3. Guarantees correctness under concurrency and failures""",
            
            "Time Travel": """1. Query older versions of data using VERSION AS OF or TIMESTAMP AS OF
2. Perfect for debugging, auditing and reproducing experiments""",
            
            "Schema Enforcement And Evolution": """1. Prevents dirty data from corrupting tables
2. Allows controlled evolution when schemas change""",
            
            "Key Delta Lake Features": """1. MERGE INTO for SCD logic and upserts
2. UPDATE and DELETE without rewriting entire tables
3. Auto-optimize features
4. Change Data Feed (CDF) for incremental downstream pipelines""",
            
            "Table Maintenance Commands": """1. OPTIMIZE to compact small files
2. ZORDER to improve selective query performance
3. VACUUM for cleaning old files and saving storage""",
            
            "Essential Skills Delta": """1. Build Bronze, Silver and Gold Delta tables
2. Read table history: DESCRIBE HISTORY tableName
3. Implement SCD1 and SCD2 using MERGE
4. Write streaming Delta pipelines
5. Optimise Delta tables for analytics performance"""
        },
        
        "Databricks Runtime": {
            "Standard Runtime": """1. General-purpose Spark runtime
2. Supports most workloads""",
            
            "Ml Runtime": """1. Includes pre-installed ML libraries
2. Supports MLflow, GPU acceleration, TensorFlow, PyTorch
3. Provides optimized training performance""",
            
            "Photon Runtime": """1. High-performance vectorized execution engine
2. Extremely fast for SQL queries on Delta tables
3. Great for warehousing workloads""",
            
            "Why You Should Care": """1. Using the right runtime changes performance drastically
2. Photon can make BI workloads 2x–12x faster
3. ML Runtime saves hours of dependency headaches""",
            
            "Essential Skills Runtime": """1. Choose correct runtime per workload
2. Benchmark performance between runtimes
3. Understand how upgrades affect pipeline behavior"""
        },
        
        "Actionable Steps": {
            "Convert Your Parquet File Into A Delta Table": """Step 1: Convert Your Parquet File into a Delta Table

Use PySpark or SQL:
df.write.format("delta").save("/FileStore/mydata/delta/")

Or SQL:
CREATE TABLE my_delta_table
USING DELTA
LOCATION '/FileStore/mydata/delta/';""",

            "Practice Delta Operations": """Step 2: Practice Delta Operations

Run UPDATE:
UPDATE my_delta_table SET columnA = 'new_value' WHERE columnB = 5;

Run DELETE:
DELETE FROM my_delta_table WHERE columnB < 0;

Run MERGE (Upsert):
MERGE INTO target t
USING source s
ON t.id = s.id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;

Time Travel:
SELECT * FROM my_delta_table VERSION AS OF 0;

Table History:
DESCRIBE HISTORY my_delta_table;""",

            "Explore Maintenance Commands": """Step 3: Explore Maintenance Commands

Run:
OPTIMIZE my_delta_table;

VACUUM my_delta_table RETAIN 168 HOURS;

OPTIMIZE my_delta_table ZORDER BY (columnA);""",

            "Complete Courses": """Step 4: Complete Courses

1. Databricks Academy: Intro to DataFrames
2. Databricks Academy: Delta Lake Fundamentals
3. Optional: Databricks Academy: Optimizing Delta and Apache Spark"""
        }
    }

    # Create Root Folder
    if not os.path.exists(root_folder):
        os.makedirs(root_folder)
        print(f"Created Root Folder: {root_folder}")

    # Iterate through hierarchy
    for folder_name, files_dict in hierarchy.items():
        # Clean folder name
        clean_folder_name = clean_name(folder_name)
        folder_path = os.path.join(root_folder, clean_folder_name)
        
        # Create Subfolder
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(f"  Created Folder: {clean_folder_name}")

        # Create Files inside Subfolder
        for file_raw_name, content in files_dict.items():
            # Clean file name
            clean_file_name = clean_name(file_raw_name) + ".md"
            file_path = os.path.join(folder_path, clean_file_name)
            
            # Write content to Markdown file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"# {clean_name(file_raw_name)}\n\n")
                f.write(f"**Details:**\n\n{content}\n")
            
            print(f"    Created File: {clean_file_name}")

    print("\nSUCCESS: Phase 3 folder structure and markdown files created!")

if __name__ == "__main__":
    create_structure()