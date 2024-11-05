import os

app_directory = r'C:\Users\isult\Dropbox\AI\Projects\IRN3\review'
output_file = 'combined.py'

# List all python files in the directory
py_files = [f for f in os.listdir(app_directory) if f.endswith('.py')]

with open(output_file, 'a') as outfile:
    for fname in py_files:
        with open(os.path.join(app_directory, fname)) as infile:
            for line in infile:
                outfile.write(line)


app_directory = r'C:\Users\isult\Dropbox\AI\Projects\IRN3\review\templates\review'
output_file = 'combined.py'

# List all python files in the directory
py_files = [f for f in os.listdir(app_directory) if f.endswith('.py')]

with open(output_file, 'a') as outfile:
    for fname in py_files:
        with open(os.path.join(app_directory, fname)) as infile:
            for line in infile:
                outfile.write(line)