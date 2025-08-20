from fastapi import FastAPI, Request
from pydantic import BaseModel
import subprocess

app = FastAPI()

class Prompt(BaseModel):
    prompt: str

@app.post("/generate")
def generate(prompt: Prompt):
    try:
        result = subprocess.run(
            ['/app/llama.cpp/build/main', '-m', '/app/models/tinyllama.gguf', '-p', prompt.prompt, '-n', '50'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30
        )
        output = result.stdout.decode().strip()
        error = result.stderr.decode().strip()

        if result.returncode != 0:
            return {
                "output": None,
                "error": f"llama.cpp failed:\n{error}"
            }

        # or if output is just empty
        if not output:
            return {
                "output": None,
                "error": "No output from llama.cpp."
            }
        
        return {"output": output}

    except FileNotFoundError:
        return {"output": "llama.cpp binary not found at /app/llama.cpp/build/main"}
    except Exception as e:
        return {"output": f" Error: {str(e)}"}