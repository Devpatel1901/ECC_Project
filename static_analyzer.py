import docker
import os
import json
from datetime import datetime

client = docker.from_env()

DOCKER_IMAGE_MAP = {
    "python": "static-python",
    "js": "static-js",
    "java": "static-java",
    "cpp": "static-cpp",
    "go": "static-go"
}

def run_static_analysis(language: str, code_dir: str, code_filename: str):
    image = DOCKER_IMAGE_MAP.get(language)

    if not image:
        return {"success": False, "error": f"No image for language: {language}"}

    try:
        result = client.containers.run(
            image=image,
            command=[code_filename, "-f", "json"] if language == "python" else code_filename,
            volumes={os.path.abspath(code_dir): {"bind": "/code", "mode": "rw"}},
            remove=True,
            mem_limit="256m",
            cpu_quota=25000,
            cpu_period=100000
        )

        output = result.decode("utf-8") if isinstance(result, bytes) else str(result)

        try:
            # Try parsing as JSON first
            parsed = json.loads(output)
            return {
                "success": True,
                "language": language,
                "tool": image,
                "timestamp": datetime.utcnow().isoformat(),
                "analysis": parsed
            }
        except json.JSONDecodeError:
            # If not JSON, return raw output
            return {
                "success": True,
                "language": language,
                "tool": image,
                "timestamp": datetime.utcnow().isoformat(),
                "analysis": {
                    "raw_output": output.strip()
                }
            }

    except docker.errors.ContainerError as e:
        stderr = e.stderr.decode("utf-8") if e.stderr else str(e)
        return {"success": False, "error": stderr}
    except Exception as e:
        return {"success": False, "error": f"Static analysis failed: {str(e)}"}

