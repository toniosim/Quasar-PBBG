from datetime import datetime
from database import redis_connection
from models.character import regen_ap
from config import Config


def register_scheduled_tasks(scheduler):
    """Register scheduled tasks with APScheduler"""

    # AP Regeneration task
    scheduler.add_job(
        regenerate_ap_for_all_characters,
        'interval',
        minutes=Config.AP_REGEN_INTERVAL,
        id='ap_regeneration',
        replace_existing=True
    )

    # Other scheduled tasks can be added here

    print(f"Scheduled tasks registered: AP regeneration every {Config.AP_REGEN_INTERVAL} minutes")


def regenerate_ap_for_all_characters():
    """Regenerate AP for all characters"""
    # Get all character IDs
    character_keys = redis_connection.keys('character:*')

    # Skip if no characters
    if not character_keys:
        return

    # Count of characters processed
    processed_count = 0

    # Process each character
    for key in character_keys:
        try:
            # Extract character ID from key (format: 'character:123')
            character_id = key.split(':')[1]

            # Skip if not a valid character ID
            if not character_id.isdigit():
                continue

            # Regenerate AP
            success = regen_ap(int(character_id), Config.AP_REGEN_RATE)

            if success:
                processed_count += 1

        except Exception as e:
            print(f"Error regenerating AP for character {key}: {e}")

    print(f"AP regeneration complete: {processed_count} characters processed at {datetime.now()}")


def clean_expired_effects():
    """Clean up expired character effects"""
    # This would loop through all characters and remove any expired effects
    # For brevity, not fully implemented
    pass