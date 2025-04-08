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

# fastapi_code_executor.py

import os
import tempfile
import aiohttp
import asyncio
from fastapi import FastAPI, File, UploadFile, HTTPException, Form

app = FastAPI()

# --- Config ---
ALLOWED_EXTENSIONS = {
    "python": ".py",
    "java": ".java",
    "cpp": ".cpp",
    "go": ".go",
    "javascript": ".js"
}

EXTS = ALLOWED_EXTENSIONS
MAX_INPUT_FILE_SIZE = 64 * 1024  # 64 KB

LANGUAGE_PORTS = {
    "python": 9001,
    "java": 9002,
    "cpp": 9003,
    "go": 9004,
    "javascript": 9005
}

# --- Helpers ---
def get_temp_code_path(filename: str) -> str:
    temp_dir = tempfile.mkdtemp()
    return os.path.join(temp_dir, filename)

# --- Main endpoint ---
@app.post("/execute_code")
async def execute_code_and_analysis(
    file: UploadFile = File(...),
    input_file: UploadFile = File(None),
    language: str = Form("python")
):
    try:
        if language not in LANGUAGE_PORTS:
            raise HTTPException(status_code=400, detail="Unsupported language.")

        expected_ext = ALLOWED_EXTENSIONS[language]
        if not file.filename.endswith(expected_ext):
            raise HTTPException(status_code=400, detail=f"File extension must be '{expected_ext}' for {language}.")

        code_file_path = get_temp_code_path(file.filename)
        with open(code_file_path, 'wb') as f:
            f.write(await file.read())

        user_input = ""
        if input_file:
            print(user_input)
            if input_file.content_type != "text/plain":
                raise HTTPException(status_code=400, detail="Input file must be plain text.")

            contents = await input_file.read()
            if len(contents) > MAX_INPUT_FILE_SIZE:
                raise HTTPException(status_code=413, detail="Input file too large (limit: 64KB).")

            user_input = contents.decode().strip() + "\n"

        # Read code as bytes to forward to container
        with open(code_file_path, 'rb') as f:
            code_bytes = f.read()

        result = await execute_code_in_persistent_runner(language, code_bytes, user_input)
        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

# --- Persistent Runner Communication ---
async def execute_code_in_persistent_runner(language: str, code: bytes, user_input: str):
    port = LANGUAGE_PORTS[language]
    try:
        async with aiohttp.ClientSession() as session:
            form = aiohttp.FormData()
            form.add_field("file", code, filename=f"main{EXTS[language]}", content_type="text/plain")
            form.add_field("user_input", user_input or "", content_type="text/plain")

            async with session.post(f"http://localhost:{port}/run", data=form, timeout=15) as resp:
                if resp.status != 200:
                    detail = await resp.text()
                    raise HTTPException(status_code=resp.status, detail=detail)
                return await resp.json()
    except asyncio.TimeoutError:
        return {"execution_output": "", "execution_error": "Request timed out", "static_analysis_output": "", "static_analysis_error": ""}
    except Exception as e:
        return {"execution_output": "", "execution_error": f"Runner communication error: {str(e)}", "static_analysis_output": "", "static_analysis_error": ""}

@app.get("/")
def hello():
    return {"message": "Hello from FastAPI Code Executor"}


