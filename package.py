import zipfile
import os

EXCLUDE_DIRS = {'.git', '__pycache__', '.pytest_cache', '.venv', 'node_modules', '.next'}
EXCLUDE_FILES = {'.env'}

def main():
    zip_filename = 'AI-SOC-dist.zip'
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk('.'):
            # Mutate dirs in place to prevent os.walk from descending into excluded directories
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            
            for file in files:
                if file in EXCLUDE_FILES or file == zip_filename:
                    continue
                
                file_path = os.path.join(root, file)
                # Keep paths relative inside the zip
                arcname = os.path.relpath(file_path, '.')
                zipf.write(file_path, arcname)
    
    print(f"Successfully packaged {zip_filename} excluding sensitive directories and files.")

if __name__ == "__main__":
    main()
