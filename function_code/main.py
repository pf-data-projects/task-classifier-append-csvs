import os
import functions_framework
from google.cloud import storage
import pandas as pd

@functions_framework.http
def hello_http(request):
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    request_json = request.get_json(silent=True)
    request_args = request.args
    # Example usage
    input_txt_file = 'sequence.txt'  # Change this to the path of your input text file
    output_csv_file = 'task_probabilities.csv'  # Desired output CSV file name
    process_files(input_txt_file, output_csv_file)
    print("csvs appended")
    return "csvs appended"

    # if request_json and 'name' in request_json:
    #     name = request_json['name']
    # elif request_args and 'name' in request_args:
    #     name = request_args['name']
    # else:
    #     name = 'World'
    # return 'Hello {}!'.format(name)


def find_csv_file(num1, num2):
    target_filename_part = f"_{num1}_{num2}.csv" 
    storage_client = storage.Client()
    bucket = storage_client.get_bucket("task-classifier-task-data")
    blobs = bucket.list_blobs()
    for blob in blobs:
        if blob.name.endswith(target_filename_part):
            # Download the file to a temporary location
            temp_file = f"/tmp/{blob.name}"
            blob.download_to_filename(temp_file)
            return temp_file
    return None


# Function to process the files remains the same
def process_files(input_txt_file, output_csv_file):
    with open(input_txt_file, 'r') as f:
        lines = f.readlines()
    first_file = True
    for line in lines:
        num1, num2 = map(int, line.strip().split(','))  # Extracting the two numbers
        csv_file = find_csv_file(num1, num2)  # Finding the corresponding csv file
        if csv_file:
            df = pd.read_csv(csv_file)
            if len(df) < 50:
                print(num1, num2)
                print("Rows in this csv: ", len(df))
            if first_file:
                df.to_csv(output_csv_file, index=False)  # Save the first file with headers
                first_file = False
            else:
                df.to_csv(output_csv_file, mode='a', header=False, index=False)  # Append subsequent files without headers
        else:
            print(f"No CSV file found for numbers {num1} and {num2}")
    # Upload the output CSV file to the bucket
    storage_client = storage.Client()
    bucket = storage_client.bucket("task-classifier-task-data")
    blob = bucket.blob(output_csv_file)
    blob.upload_from_filename(output_csv_file)
