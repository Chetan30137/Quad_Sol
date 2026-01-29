import os
import sys
import glob
from openai import AzureOpenAI

def generate_unit_test(py_file_path, client, deployment_name):
    """Generate pytest unit tests for a Python file using Azure OpenAI"""
    with open(py_file_path, 'r', encoding='utf-8') as f:
        py_code = f.read()

    prompt = f"""Generate comprehensive pytest unit tests for the following Python code.

Include tests for:
- Normal scenarios
- Edge cases and boundary conditions
- Exception paths
- None/empty inputs where applicable
- Type-related checks if relevant

Guidelines:
- Use pytest function-based tests (not classes unless needed).
- Use unittest.mock (or pytest monkeypatch) to mock I/O, filesystem, network, time, randomness, and environment as appropriate.
- For pure functions, prefer pytest.mark.parametrize where it adds coverage.
- For classes, test constructors and important methods/state transitions.
- If there is a CLI (__main__), include tests for argument parsing and main flow with mocks.
- Assume the test file is under a mirrored 'tests/' directory.
- Output ONLY valid Python test code with proper imports and no extra commentary.

Python Code:
```python
{py_code}
```"""

    response = client.chat.completions.create(
        model=deployment_name,
        messages=[
            {
                "role": "system",
                "content": "You are an expert Python test engineer who writes high-quality pytest tests with unittest.mock."
            },
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        max_tokens=2000,
    )
    return response.choices[0].message.content

def extract_code_from_response(content):
    """Extract Python code from markdown-formatted response"""
    if "```python" in content:
        parts = content.split("```python")
        if len(parts) > 1:
            code = parts[1].split("```")[0].strip()
            return code
    elif "```" in content:
        parts = content.split("```")
        if len(parts) > 1:
            code = parts[1].strip()
            return code
    return content.strip()

def to_test_path(py_file):
    """
    Map source file to tests path.
    Examples:
      src/package/module.py  -> tests/package/test_module.py
      package/module.py      -> tests/package/test_module.py
    """
    # Prefer 'src/' layout if present
    if py_file.startswith(f"src{os.sep}"):
        rel = py_file[len(f"src{os.sep}"):]
    else:
        rel = py_file

    dirname, filename = os.path.split(rel)
    name, ext = os.path.splitext(filename)
    test_filename = f"test_{name}{ext}"
    test_path = os.path.join("tests", dirname, test_filename)
    return test_path

def main():
    # Get Azure OpenAI credentials from environment
    endpoint = "https://projectpulselab.openai.azure.com/"
    api_key = "76iR6QZTDWlbPZLloG0dycl2CPHYXw9rfnYcgyr7BvKLn6yBdYKIJQQJ99BLACYeBjFXJ3w3AAABACOGSRML"
    deployment = "gpt-4.1-01"
    

    if not all([endpoint, api_key, deployment]):
        print("Error: Missing Azure OpenAI credentials")
        print("Required environment variables:")
        print("  - AZURE_OPENAI_ENDPOINT")
        print("  - AZURE_OPENAI_KEY (or AZURE_OPENAI_API_KEY)")
        print("  - AZURE_OPENAI_DEPLOYMENT")
        sys.exit(1)

    # Initialize Azure OpenAI client
    try:
        client = AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version="2024-02-15-preview"
        )
        print("✓ Connected to Azure OpenAI")
    except Exception as e:
        print(f"Error: Failed to connect to Azure OpenAI: {str(e)}")
        sys.exit(1)

    # Discover Python files (skip tests, venv, build, dist, hidden)
    candidates = set()
    # src/ layout
    candidates.update(glob.glob(f"src{os.sep}**{os.sep}*.py", recursive=True))
    # flat/monorepo layouts
    candidates.update(glob.glob("*.py", recursive=False))
    candidates.update(glob.glob(f"**{os.sep}*.py", recursive=True))

    def should_skip(path):
        parts = path.split(os.sep)
        if any(seg.startswith(".") for seg in parts):
            return True
        if any(seg in ("tests", "venv", ".venv", "env", ".env", "build", "dist", "__pycache__") for seg in parts):
            return True
        base = os.path.basename(path)
        if base.startswith("test_"):
            return True
        return False

    py_files = [p for p in candidates if p.endswith(".py") and os.path.isfile(p) and not should_skip(p)]

    if not py_files:
        print("Warning: No Python source files found.")
        print("Ensure your code is under 'src/' or project root (excluding tests/).")
        sys.exit(0)

    print(f"Found {len(py_files)} Python file(s) to process\n")

    success_count = 0
    error_count = 0

    for py_file in sorted(py_files):
        print(f"Processing: {py_file}")
        try:
            test_content = generate_unit_test(py_file, client, deployment)
            test_code = extract_code_from_response(test_content)

            test_file = to_test_path(py_file)
            os.makedirs(os.path.dirname(test_file), exist_ok=True)

            with open(test_file, 'w', encoding='utf-8') as f:
                f.write(test_code)

            print(f"  ✓ Created: {test_file}\n")
            success_count += 1
        except Exception as e:
            print(f"  ✗ Error: {str(e)}\n")
            error_count += 1

    # Summary
    print("=" * 60)
    print("Test Generation Summary:")
    print(f"  ✓ Successfully generated: {success_count} test(s)")
    if error_count > 0:
        print(f"  ✗ Failed: {error_count} test(s)")
    print("=" * 60)

    if error_count > 0:
        sys.exit(1)

    print("\n✓ Test generation complete!")

if __name__ == "__main__":
    main()