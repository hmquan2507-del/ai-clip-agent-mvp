from config import JOBS
from storage import create_storage_adapter

def storage_adapter():
    return create_storage_adapter(JOBS)
