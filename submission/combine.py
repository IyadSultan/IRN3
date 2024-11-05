import os

# delete combined.py
os.remove('combined.py')

app_directory = '../'
output_file = 'combined.py'

# List all python files in the directory
py_files = [f for f in os.listdir(app_directory) if f.endswith('.py')]

with open(output_file, 'a') as outfile:
    for fname in py_files:
        with open(os.path.join(app_directory, fname)) as infile:
            for line in infile:
                outfile.write(line)


app_directory = 'templates/submission/'


# List all python files in the directory
py_files = [f for f in os.listdir(app_directory) if f.endswith('.html')]

with open(output_file, 'a') as outfile:
    for fname in py_files:
        with open(os.path.join(app_directory, fname)) as infile:
            for line in infile:
                outfile.write(line)