import os
import csv
import requests
import zipfile
import io
import shutil
import json

def get_vrt_data():
    vrt_url = "https://raw.githubusercontent.com/bugcrowd/vulnerability-rating-taxonomy/master/vulnerability-rating-taxonomy.json"
    try:
        response = requests.get(vrt_url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching VRT data: {str(e)}")
        return None  # Will be handled as unclassified in get_vrt_category

def get_vrt_category(path, vrt_data):
    if not vrt_data:
        return 'unclassified', []  # Default to unclassified if no VRT data
    
    path_parts = path.split(os.sep)
    vrt_path = '/'.join(path_parts)
    
    def search_category(categories, target_path, hierarchy=None):
        if hierarchy is None:
            hierarchy = []
            
        for category in categories:
            if category.get('id', '') in target_path:
                # Get name and priority from the category
                priority = category.get('priority', '')
                name = category.get('name', '')
                current_hierarchy = hierarchy + [name] if name else hierarchy
                
                if priority:
                    # Map Bugcrowd priorities to literal severity words
                    priority_levels = ('critical', 'high', 'medium', 'low', 'info')
                    # Convert priority to int if it's a string
                    try:
                        priority_num = int(priority) if isinstance(priority, str) else priority
                        # Check if priority is within valid range
                        if 1 <= priority_num <= 5:
                            # Subtract 1 from priority since tuple is 0-indexed
                            return priority_levels[priority_num - 1], current_hierarchy
                    except (ValueError, TypeError):
                        pass
                    return 'unclassified', current_hierarchy
                
                # Check children categories
                children = category.get('children', [])
                if children:
                    child_result = search_category(children, target_path, current_hierarchy)
                    if child_result[0]:
                        return child_result
                
                # If no priority found, default to unclassified
                return 'unclassified', current_hierarchy
        return None, []
    
    result, hierarchy = search_category(vrt_data.get('content', []), vrt_path)
    return result if result else 'unclassified', hierarchy

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
    vrt_data = get_vrt_data()
    
    for root, dirs, files in os.walk(base_path):
        if 'template.md' in files and 'recommendations.md' in files:
            # Get relative path for naming
            rel_path = os.path.relpath(root, base_path)
            if rel_path == '.':
                continue
                
            # Get exploitation category and VRT name from VRT data
            exploitation, vrt_name = get_vrt_category(rel_path, vrt_data)
            
            # If VRT name is not available, create hierarchical name from folder structure
            if not vrt_name:
                name_parts = rel_path.split(os.sep)
                name = ' - '.join(part.replace('_', ' ').title() for part in name_parts)
            else:
                name = ' - '.join(vrt_name)
            
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
                'exploitation': exploitation,
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
        output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bugcrowd_vrt.csv')
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
