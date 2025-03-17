import logging
import json
import time
import os

# Ensure logs directory exists
log_dir = "logs"
log_file = os.path.join(log_dir, "risk_agent.log")

try:
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)  # Create logs directory if missing
except Exception as e:
    print(f"Error creating log directory: {e}")
    log_file = "/tmp/risk_agent.log"  # Fallback location

# Configure logger
logger = logging.getLogger("risk_agent")
logger.setLevel(logging.DEBUG)

# Create handler
handler = logging.FileHandler(log_file)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s')
handler.setFormatter(formatter)

# Add handler to logger
logger.addHandler(handler)

def log_event(event: str, level="info", **kwargs):
    """Log structured events"""
    log_data = {"event": event, **kwargs}
    if level == "info":
        logger.info(json.dumps(log_data))
    elif level == "error":
        logger.error(json.dumps(log_data))
    elif level == "warning":
        logger.warning(json.dumps(log_data))

def log_execution_time(func):
    """Decorator to log execution time of a function"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed_time = time.time() - start_time
        log_event(f"{func.__name__}_execution_time", execution_time=elapsed_time)
        return result
    return wrapper
