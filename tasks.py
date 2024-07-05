from celery_config import app
import time
import os
import glob
import subprocess


@app.task
def process_request(data):
    # set user defined prompt in the prompt file
    prompt_file_path = "prompt_input.txt"
    with open(prompt_file_path, "w") as f:
        f.write(data["prompt"])
    # set fe user id as new file name
    file_prefix_path = "file_name.txt"
    with open(file_prefix_path, "w") as prefix:
        prefix.write(str(data["userId"]))

    userId = data["userId"]

    # start wf.py
    subprocess.call(['python', 'wf.py'])

    output_folder = "./output/"
    pattern = os.path.join(output_folder, f"{userId}*.png")

    matching_files = []

    while not matching_files:
        time.sleep(1)
        matching_files = glob.glob(pattern)

    output_file = matching_files[0]

    return output_file
