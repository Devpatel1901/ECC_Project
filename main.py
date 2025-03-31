# import os
# import subprocess
# import tempfile
# from fastapi import FastAPI, File, UploadFile, HTTPException, Form
# import asyncio

# app = FastAPI()

# async def execute_code_in_container(dir_path: str, file_path: str, language: str):
    
#     image_name = "code-runner"

#     try:
#         result = subprocess.run(
#             [
#                 "docker", "run", "--rm",
#                 "-v", f"{dir_path}:/app/code",  # Mount the code file
#                 image_name, language, "/app/code/" + os.path.basename(file_path)
#             ],
#             capture_output=True,
#             text=True,
#             timeout=10  # Prevent infinite loops
#         )
#         return result
#     except subprocess.TimeoutExpired:
#         return "Execution timeout", "Process exceeded time limit"
    
# async def static_code_analysis(dir_path: str, file_path: str, language: str):
#     image_name = "static-analysis"

#     try:
#         result = subprocess.run(
#             [
#                 "docker", "run", "--rm",
#                 "-v", f"{dir_path}:/app/code",  # Mount the code file
#                 image_name, language, "/app/code/" + os.path.basename(file_path)
#             ],
#             capture_output=True,
#             text=True,
#             timeout=10  # Prevent infinite loops
#         )
#         return result
#     except subprocess.TimeoutExpired:
#         return "Execution timeout", "Process exceeded time limit"

# @app.post("/execute_code")
# async def execute_code_and_analysis(file: UploadFile = File(...), language: str = Form("python")):
#     try:
#         temp_dir = tempfile.mkdtemp()
#         temp_file_path = os.path.join(temp_dir, file.filename)

#         with open(temp_file_path, 'wb') as f:
#             f.write(await file.read())

#         # Run code inside the appropriate Docker container
#         code_execution_task = execute_code_in_container(temp_dir, temp_file_path, language)
#         static_analysis_task = static_code_analysis(temp_dir, temp_file_path, language)

        # code_execution_result, static_analysis_result = await asyncio.gather(code_execution_task, static_analysis_task)
    
#         return {
#             "execution_output": code_execution_result.stdout,
#             "execution_error": code_execution_result.stderr,
#             "static_analysis_output": static_analysis_result.stdout,
#             "static_analysis_error": static_analysis_result.stderr,
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

import os
import subprocess
import tempfile
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
import asyncio

app = FastAPI()

CODE_RUNNER_IMAGE_NAME = {
    "python": "code-runner-python",
    "java": "code-runner-java",
    "cpp": "code-runner-cpp",
    "go": "code-runner-go",
    "javascript": "code-runner-javascript"
}

STATIC_ANALYSIS_IMAGE_NAME = {
    "python": "static-analysis-python",
    "java": "static-analysis-java",
    "cpp": "static-analysis-cpp",
    "go": "static-analysis-go",
    "javascript": "static-analysis-javascript"
}

async def execute_code_in_container(dir_path: str, file_path: str, language: str):
    
    image_name = CODE_RUNNER_IMAGE_NAME[language]

    try:
        result = subprocess.run(
            [
                "docker", "run", "--rm",
                "-v", f"{dir_path}:/app/code",  # Mount the code file
                image_name, language, "/app/code/" + os.path.basename(file_path)
            ],
            capture_output=True,
            text=True,
            timeout=10  # Prevent infinite loops
        )
        return result
    except subprocess.TimeoutExpired:
        return "Execution timeout", "Process exceeded time limit"
    
async def static_code_analysis_in_container(dir_path: str, file_path: str, language: str):
    
    image_name = STATIC_ANALYSIS_IMAGE_NAME[language]

    try:
        result = subprocess.run(
            [
                "docker", "run", "--rm",
                "-v", f"{dir_path}:/app/code",  # Mount the code file
                image_name, language, "/app/code/" + os.path.basename(file_path)
            ],
            capture_output=True,
            text=True,
            timeout=10  # Prevent infinite loops
        )
        return result
    except subprocess.TimeoutExpired:
        return "Execution timeout", "Process exceeded time limit"

@app.post("/execute_code")
async def execute_code_and_analysis(file: UploadFile = File(...), language: str = Form("python")):
    try:
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, file.filename)

        with open(temp_file_path, 'wb') as f:
            f.write(await file.read())

        # Run code inside the appropriate Docker container
        code_execution_task = execute_code_in_container(temp_dir, temp_file_path, language)
        static_analysis_task = static_code_analysis_in_container(temp_dir, temp_file_path, language)

        code_execution_result, static_analysis_result = await asyncio.gather(code_execution_task, static_analysis_task)
    
        return {
            "execution_output": code_execution_result.stdout,
            "execution_error": code_execution_result.stderr,
            "static_analysis_output": static_analysis_result.stdout,
            "static_analysis_error": static_analysis_result.stderr
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    
@app.get("/")
def hello_world():
    return {"message": "Hello World!"}
