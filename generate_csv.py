import os
import csv
import requests
import zipfile
import io
import shutil

def download_templates():
    # GitHub repository URL
    repo_url = "https://github.com/bugcrowd/templates/archive/refs/heads/master.zip"
    
    # Create a temporary directory for downloaded content
    temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp')
    os.makedirs(temp_dir, exist_ok=True)
    
    try:
        # Download the repository
        response = requests.get(repo_url)
        response.raise_for_status()
        
        # Extract the zip content
        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Return the path to the submissions/description directory
        templates_dir = os.path.join(temp_dir, 'templates-master', 'submissions', 'description')
        if not os.path.exists(templates_dir):
            raise Exception("Templates directory not found in the downloaded content")
        
        return templates_dir
    except Exception as e:
        print(f"Error downloading templates: {str(e)}")
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        return None

def clean_recommendation_content(content):
    # Remove the first line if it's the title
    lines = content.split('\n')
    if lines and '# Recommendation(s)' in lines[0]:
        lines = lines[1:]
    
    # Find where references start
    references = []
    ref_start_idx = -1
    
    for i, line in enumerate(lines):
        if line.strip().lower().startswith('for more information') or \
           line.strip().lower().startswith('reference'):
            ref_start_idx = i
            # Collect references
            for j in range(i+1, len(lines)):
                ref_line = lines[j].strip()
                if ref_line.startswith('- <') and ref_line.endswith('>'):
                    references.append(ref_line[3:-1])  # Remove '- <' and '>'
            break
    
    # Get recommendation content without references section
    if ref_start_idx != -1:
        content = '\n'.join(lines[:ref_start_idx]).strip()
    else:
        content = '\n'.join(lines).strip()
    
    return content, references

def process_directory(base_path):
    results = []
    
    for root, dirs, files in os.walk(base_path):
        if 'template.md' in files and 'recommendations.md' in files:
            # Get relative path for naming
            rel_path = os.path.relpath(root, base_path)
            if rel_path == '.':
                continue
                
            # Create hierarchical name
            name_parts = rel_path.split(os.sep)
            name = ' - '.join(part.replace('_', ' ').title() for part in name_parts)
            
            # Read template.md for description
            template_path = os.path.join(root, 'template.md')
            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    description = f.read().strip()
            except:
                description = ''
            
            # Read recommendations.md
            recommendation_path = os.path.join(root, 'recommendations.md')
            try:
                with open(recommendation_path, 'r', encoding='utf-8') as f:
                    rec_content = f.read()
                    resolution, refs = clean_recommendation_content(rec_content)
            except:
                resolution = ''
                refs = []
            
            results.append({
                'name': name,
                'description': description,
                'resolution': resolution,
                'exploitation': 'unclassified',
                'references': ', '.join(refs) if refs else ''
            })
    
    return results

def main():
    temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp')
    try:
        # Download templates
        templates_dir = download_templates()
        if not templates_dir:
            print("Failed to download templates. Exiting...")
            return
        
        # Process the downloaded templates
        results = process_directory(templates_dir)
        
        # Write to CSV
        output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vulnerabilities.csv')
        fieldnames = ['name', 'description', 'resolution', 'exploitation', 'references']
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
            
    finally:
        # Clean up temporary directory
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

if __name__ == '__main__':
    main()
