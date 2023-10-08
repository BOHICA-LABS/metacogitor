import pytest
from metacogitor.logs import define_log_level


@pytest.fixture(
    params=[
        ("DEBUG", "INFO"),
        ("INFO", "WARNING"),
        ("WARNING", "ERROR"),
        ("ERROR", "CRITICAL"),
    ]
)
def log_levels(request):
    return request.param


@pytest.fixture
def log_test_setup(log_levels):
    print_level, logfile_level = log_levels
    logger = define_log_level(print_level=print_level, logfile_level=logfile_level)
    return logger


def log_test_function(logger):
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")


def test_log_levels(log_test_setup, caplog):
    logger = log_test_setup
    log_test_function(logger)

    for record in caplog.records:
        assert record.levelno >= logger.getLevelName(logger.level(record.levelname))


# Run tests
if __name__ == "__main__":
    pytest.main()
