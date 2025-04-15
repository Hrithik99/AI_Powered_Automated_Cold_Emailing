job_title = 'Data Engineer'
Company_Name = 'The Brattle Group'

def read_job_description(file_path):
    with open(file_path, 'r') as file:
        job_description = file.read()
    return job_description

# Usage
file_path = 'JD.txt'
job_description = read_job_description(file_path)
#print(job_description)