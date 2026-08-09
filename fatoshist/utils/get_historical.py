import json
import logging
from datetime import datetime

from fatoshist.utils.paths import data_path


def get_historical_events():
    today = datetime.now()
    day = today.day
    month = today.month
    try:
        with data_path('eventos.json').open('r', encoding='utf-8') as file:
            json_events = json.load(file)
            events = json_events[f'{month}-{day}']
            if events:
                return '\n\n'.join(events)
            else:
                return None
    except Exception as e:
        logging.error(f'Error reading events from JSON: {e}')

        return None
