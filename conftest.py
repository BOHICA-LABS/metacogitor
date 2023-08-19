import os


def pytest_configure(config):
    # Set the session environment variable
    os.environ["OPENAI_API_KEY"] = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXX"  # demo key
