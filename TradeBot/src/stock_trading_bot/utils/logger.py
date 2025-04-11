import logging

# Create a logger instance
logger = logging.getLogger("TradingBot")
logger.setLevel(logging.DEBUG)  # Set to DEBUG to capture all logs

# Create a console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)  # Capture all logs at DEBUG level or higher

# Create a formatter and attach it to the handler
formatter = logging.Formatter(
    fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
console_handler.setFormatter(formatter)

# Add the handler to the logger
if not logger.hasHandlers():  # Avoid duplicate handlers
    logger.addHandler(console_handler)
