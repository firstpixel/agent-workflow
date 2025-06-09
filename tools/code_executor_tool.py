import subprocess

def run(code: str):
    try:
        res = subprocess.check_output(['python', '-c', code], stderr=subprocess.STDOUT, text=True)
        print(f"TOOL exec -> {res.strip()}")
        return res
    except subprocess.CalledProcessError as e:
        print(f"Execution failed: {e.output}")
        return e.output
