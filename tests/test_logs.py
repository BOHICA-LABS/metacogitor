import pytest
from metacogitor.logs import define_log_level

print_level = "DEBUG"
logfile_level = "INFO"

logger = define_log_level(print_level=print_level, logfile_level=logfile_level)

# A simple function for testing logging
def log_test_function():
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")


def test_log_configuration(caplog):

    log_test_function()

    for record in caplog.records:
        if record.levelname == "DEBUG":
            assert record.levelno >= 10
        elif record.levelname == "INFO":
            assert record.levelno >= 20
        elif record.levelname == "WARNING":
            assert record.levelno >= 30
        elif record.levelname == "ERROR":
            assert record.levelno >= 40
        elif record.levelname == "CRITICAL":
            assert record.levelno >= 50


# Run tests
if __name__ == "__main__":
    pytest.main()
