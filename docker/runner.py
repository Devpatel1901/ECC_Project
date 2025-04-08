# runner.py (shared across all language runner containers)

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
import subprocess
import os
import uuid
import shutil

app = FastAPI()

MAX_INPUT_FILE_SIZE = 64 * 1024

@app.post("/run")
async def run_code(
    file: UploadFile = File(...),
    user_input: str  = Form("")
):
    # Identify language from extension
    filename = file.filename
    ext = filename.split('.')[-1]
    temp_filename = f"/tmp/{uuid.uuid4()}.{ext}"

    with open(temp_filename, 'wb') as f:
        f.write(await file.read())

    language = {
        "py": "python",
        "java": "java",
        "cpp": "cpp",
        "js": "javascript",
        "go": "go"
    }.get(ext, None)

    if not language:
        return {"error": "Unsupported file extension."}

    analysis_output = ""
    execution_output = ""
    execution_error = ""

    print(user_input)

    try:
        # --- Static Analysis ---
        if language == "python":
            analysis = subprocess.run(["pylint", temp_filename], capture_output=True, text=True)
        elif language == "cpp":
            analysis = subprocess.run(["cppcheck", temp_filename], capture_output=True, text=True)
        elif language == "java":
            analysis = subprocess.run(["java", "-jar", "/checkstyle.jar", "-c", "/google_checks.xml", temp_filename], capture_output=True, text=True)
        elif language == "javascript":
            analysis = subprocess.run(["eslint", temp_filename], capture_output=True, text=True)
        elif language == "go":
            analysis = subprocess.run(["golint", temp_filename], capture_output=True, text=True)
        else:
            analysis = None

        if analysis:
            analysis_output = analysis.stdout + analysis.stderr

        # --- Code Execution ---
        if language == "python":
            run = subprocess.run(["python3", temp_filename], capture_output=True, text=True, input=user_input)
        elif language == "cpp":
            bin_path = temp_filename.replace(f".{ext}", "")
            subprocess.run(["g++", temp_filename, "-o", bin_path], check=True)
            run = subprocess.run([bin_path], capture_output=True, text=True, input=user_input)
        elif language == "java":
            dir_path = os.path.dirname(temp_filename)
            subprocess.run(["javac", temp_filename], check=True)
            class_name = os.path.splitext(os.path.basename(temp_filename))[0]
            run = subprocess.run(["java", "-cp", dir_path, class_name], capture_output=True, text=True, input=user_input)
        elif language == "javascript":
            run = subprocess.run(["node", temp_filename], capture_output=True, text=True, input=user_input)
        elif language == "go":
            run = subprocess.run(["go", "run", temp_filename], capture_output=True, text=True, input=user_input)
        else:
            run = None

        if run:
            execution_output = run.stdout
            execution_error = run.stderr

    except subprocess.CalledProcessError as e:
        execution_error = e.stderr or str(e)
    finally:
        # Cleanup
        try:
            os.remove(temp_filename)
        except:
            pass

        if language == "cpp" and 'bin_path' in locals():
            try: os.remove(bin_path)
            except: pass

        if language == "java" and 'class_name' in locals():
            try: os.remove(os.path.join(dir_path, f"{class_name}.class"))
            except: pass

    return {
        "success": execution_error == "",
        "static_analysis": analysis_output,
        "execution_result": execution_output,
        "execution_error": execution_error
    }
