import os
import subprocess
import sys


def run_step(step_name, script_path):
    print(f"\n[STEP] {step_name}: {script_path}")
    result = subprocess.run([sys.executable, script_path], check=False)
    if result.returncode != 0:
        raise RuntimeError(f"{step_name} failed with exit code {result.returncode}")


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    shake_script = os.path.join(base_dir, "shaking-dynamic.py")
    generate_script = os.path.join(base_dir, "generatedata_from_imgs.py")

    if not os.path.isfile(shake_script):
        raise FileNotFoundError(f"Missing script: {shake_script}")
    if not os.path.isfile(generate_script):
        raise FileNotFoundError(f"Missing script: {generate_script}")

    run_step("Shake Images", shake_script)
    run_step("Generate Event Data", generate_script)

    print("\nPipeline finished successfully.")


if __name__ == "__main__":
    main()
