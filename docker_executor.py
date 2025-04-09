# docker_executor.py
import docker
import os

client = docker.from_env()

IMAGE_MAP = {
    "python": "code-exec-python",
    "cpp": "code-exec-cpp",
    "java": "code-exec-java",
    "go": "code-exec-go",
    "js": "code-exec-js"
}

def execute_code(language: str, code_path: str, input_path: str = None):
    volume_path = os.path.abspath(os.path.dirname(code_path))
    code_file = os.path.basename(code_path)

    image = IMAGE_MAP[language]

    result_json = {
        "language": language,
        "status": "failed",
        "success": False,
        "stdout": "",
        "stderr": ""
    }

    try:
        result = client.containers.run(
            image,
            command=code_file,
            volumes={volume_path: {'bind': '/code', 'mode': 'rw'}},
            stdin_open=True,
            stderr=True,
            stdout=True,
            remove=True,
            detach=False,
            mem_limit="256m",
            cpu_period=100000,
            cpu_quota=25000,
        )
        decoded = result.decode("utf-8") if isinstance(result, bytes) else str(result)
        result_json.update({
            "stdout": decoded.strip(),
            "status": "success",
            "success": True
        })
    except docker.errors.ContainerError as e:
        stderr = e.stderr.decode("utf-8") if hasattr(e, 'stderr') and e.stderr else str(e)
        result_json["stderr"] = stderr.strip()
    except docker.errors.ImageNotFound:
        result_json["stderr"] = f"Image '{image}' not found."
    except Exception as e:
        result_json["stderr"] = str(e)

    return result_json
