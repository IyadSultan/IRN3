import os

# try to remove combined.py if it exists
if os.path.exists('combined.py'):
    os.remove('combined.py')

app_directory = "../users/"
output_file = 'combined.py'

# List all python files in the directory
py_files = [f for f in os.listdir(app_directory) if f.endswith('.py')]

with open(output_file, 'a') as outfile:
    for fname in py_files:
        with open(os.path.join(app_directory, fname)) as infile:
            for line in infile:
                outfile.write(line)


app_directory = 'templates/users'

# List all HTML files in the directory
html_files = [f for f in os.listdir(app_directory) if f.endswith('.html')]

# Open the output file in append mode to avoid overwriting existing content
with open(output_file, 'a') as outfile:
    for fname in html_files:
        with open(os.path.join(app_directory, fname)) as infile:
            for line in infile:
                outfile.write(line)