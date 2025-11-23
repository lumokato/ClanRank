from app.services.scheduler import move_data
import logging

# Configure logging to show output
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    print("Starting manual data backup...")
    try:
        move_data()
        print("Backup process completed.")
    except Exception as e:
        print(f"Backup failed: {e}")
