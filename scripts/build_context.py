import os


def remove_non_ascii(text):
    # Use encoding to remove non-ASCII characters
    return text.encode("ascii", errors="ignore").decode("ascii")


def parse_src_to_txt(src_folder, output_file):
    """
    Parses Python files in a src directory and outputs their names and content
    to a text document.
    :param src_folder: str - Path to the src folder containing Python files.
    :param output_file: str - Name/Path of the output text file.
    """
    with open(output_file, "w", encoding="utf-8") as out_file:
        # Walk the src directory
        for root, dirs, files in os.walk(src_folder):
            dirs_to_remove = [
                "prompts",
                "skills",
                "management",
                "learn",
            ]  # Add directory names you want to skip here
            dirs[:] = [
                d for d in dirs if d not in dirs_to_remove
            ]  # This modifies the dirs in-place
            for file in files:
                if file in [
                    "__init__.py",
                    "software_company.py",
                    "manager.py",
                    "_compat.py",
                ]:
                    continue
                # Check if file ends with .py to ensure it's a Python file
                if file.endswith(".py"):
                    module_path = os.path.join(root, file)

                    # Write module name to output file
                    out_file.write(f"{file[:-3]}.py:\n")

                    # Read and write the content of the Python file with filtering and non-ASCII removal
                    with open(
                        module_path, "r", encoding="utf-8", errors="ignore"
                    ) as code_file:
                        lines = code_file.readlines()
                        for line in lines:
                            # Remove trailing whitespace, skip empty lines or lines starting with #
                            line = line.rstrip()
                            if line and not line.startswith("#"):
                                # Remove non-ASCII characters
                                line = remove_non_ascii(line)
                                out_file.write(line + "\n")
                        out_file.write("\n\n")


if __name__ == "__main__":
    src_folder = "../../src/metacogitor"  # Or provide a full path
    output_file = "parsed_code.txt"
    parse_src_to_txt(src_folder, output_file)
    print(f"Parsed code written to {output_file}")
