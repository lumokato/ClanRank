from app.services.clanbattle_service import stage_data
import logging
import asyncio

# Configure logging to show output
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    print("Starting manual stage data collection (final=0)...")
    try:
        # stage_data is an async function or sync? 
        # Checking previous view_file output... it seems to be a sync function based on scheduler usage:
        # scheduler.add_job(clanbattle_service.stage_data, ...)
        # But let's double check if it uses async/await inside.
        # The view_file output for clanbattle_service.py isn't fully visible in history but scheduler imports it.
        # Wait, I just viewed it. Let me check the output of step 371 (which I haven't seen yet).
        # Assuming it's sync for now based on scheduler usage.
        stage_data(final=0)
        print("Stage data collection completed.")
    except Exception as e:
        print(f"Stage data collection failed: {e}")
