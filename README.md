# Bugcrowd Templates CSV Generator

This tool downloads vulnerability templates from the Bugcrowd repository and converts them into a structured CSV format for easy integration and analysis.

## Description

The script downloads vulnerability templates from Bugcrowd's GitHub repository, processes the markdown files containing vulnerability descriptions and recommendations, and generates a CSV file with standardized fields for each vulnerability type. It also integrates with Bugcrowd's Vulnerability Rating Taxonomy (VRT) to provide accurate vulnerability categorization and severity levels.

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
2. Fetch and process VRT data for accurate categorization
3. Process all template files
4. Generate a `bugcrowd_vrt.csv` file in the same directory
5. Clean up temporary files automatically

## Output Format

The generated CSV file contains the following columns:

- `name`: Full vulnerability name derived from VRT hierarchy (dash-separated)
- `description`: Detailed description of the vulnerability
- `resolution`: Recommended fixes and mitigation strategies (excluding references)
- `exploitation`: Severity level based on VRT (critical, high, medium, low, info, or unclassified)
- `references`: Relevant reference links extracted from recommendations

## Features

- Integrates with Bugcrowd's VRT for accurate vulnerability categorization
- Automatically extracts and separates references from recommendation content
- Provides standardized severity levels based on VRT priority ratings
- Generates hierarchical vulnerability names using VRT taxonomy
- Handles missing VRT data gracefully by falling back to directory structure-based naming
