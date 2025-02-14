# Bugcrowd Templates CSV Generator

This tool downloads vulnerability templates from the Bugcrowd repository and converts them into a structured CSV format for easy integration and analysis.

## Description

The script downloads vulnerability templates from Bugcrowd's GitHub repository, processes the markdown files containing vulnerability descriptions and recommendations, and generates a CSV file with standardized fields for each vulnerability type.

## Requirements

- Python 3.x
- Required Python packages:
  - requests
  - csv
  - zipfile
  - shutil

## Installation

1. Clone or download this repository
2. Install the required Python packages:
   ```bash
   pip install requests
   ```

## Usage

Run the script using Python:

```bash
python generate_csv.py
```

The script will:
1. Download the latest templates from Bugcrowd's repository
2. Process all template files
3. Generate a `vulnerabilities.csv` file in the same directory
4. Clean up temporary files automatically

## Output Format

The generated CSV file contains the following columns:

- `cwe`: Common Weakness Enumeration identifier
- `name`: Vulnerability name derived from the template structure
- `description`: Detailed description of the vulnerability
- `resolution`: Recommended fixes and mitigation strategies
- `exploitation`: Exploitation difficulty classification
- `references`: Relevant reference links and resources

## Note

This tool automatically downloads and processes the latest templates from Bugcrowd's public repository. Internet connection is required for the initial template download.
