import subprocess
import os
import sys

def run_synthseg(input_path, output_path, synthseg_cmd):
    # -------------------------
    # Environment setup
    # -------------------------
    env = os.environ.copy()

    # FreeSurfer setup
    env["FREESURFER_HOME"] = "/Applications/freesurfer/8.1.0"
    env["PATH"] = env["FREESURFER_HOME"] + "/bin:" + env["PATH"]

    # Prevent Slicer Python contamination
    for key in [
        "PYTHONHOME",
        "PYTHONPATH",
        "PYTHONEXECUTABLE",
        "PYTHONUSERBASE"
    ]:
        env.pop(key, None)

    # -------------------------
    # Checks
    # -------------------------
    if not os.path.exists(input_path):
        print(f"Input file not found:\n{input_path}")
        sys.exit(1)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # -------------------------
    # Command
    # -------------------------
    command = [
        synthseg_cmd,
        "--i", input_path,
        "--o", output_path
    ]

    print("\nRunning SynthSeg...")
    print("Command:", " ".join(command))

    # -------------------------
    # Run (SAFE MODE)
    # -------------------------
    try:
        result = subprocess.run(
            command,
            env=env,
            capture_output=True,
            text=True,
            timeout=1800  # 30 min safety limit so it never "hangs forever"
        )

    except subprocess.TimeoutExpired:
        print("\nSynthSeg timed out (killed after 30 minutes).")
        return None

    # -------------------------
    # Output logging
    # -------------------------
    print("\n----- STDOUT -----")
    print(result.stdout)

    print("\n----- STDERR -----")
    print(result.stderr)

    print("\nExit code:", result.returncode)

    if result.returncode != 0:
        print("\nSynthSeg failed.")
        return None

    # -------------------------
    # Verify output
    # -------------------------
    if os.path.exists(output_path):
        print(f"\nDone! Output saved to:\n{output_path}")
        return output_path
    else:
        print("\nSynthSeg finished but output file not found.")
        return None


# Optional direct run
if __name__ == "__main__":
    run_synthseg()