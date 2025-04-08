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
    except docker.errors.ContainerError as e:
        return f"[Docker Error] Container failed: {e}"
    except docker.errors.ImageNotFound:
        return f"[Docker Error] Image '{image}' not found."
    except Exception as e:
        return f"[Unknown Error] {str(e)}"

    return result.decode("utf-8") if isinstance(result, bytes) else result
