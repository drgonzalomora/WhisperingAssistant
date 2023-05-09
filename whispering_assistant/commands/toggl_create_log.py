import requests
from whispering_assistant.commands.command_base_template import BaseCommand, command_types
from datetime import datetime, timezone
from whispering_assistant.configs.config import toggl_api_key, toggl_workspace_id


def create_running_time_entry(api_token, workspace_id, description='Hello Toggl', tags=[], billable=False):
    # Set up authentication and API endpoint
    auth = (api_token, 'api_token')
    url = f'https://api.track.toggl.com/api/v9/workspaces/{workspace_id}/time_entries'

    # Calculate start time and duration
    start_time = int(datetime.now(timezone.utc).timestamp())
    duration = -start_time

    # Set up JSON data
    json_data = {
        'created_with': 'API example code',
        'description': description,
        'tags': tags,
        'billable': billable,
        'workspace_id': int(workspace_id),
        'duration': duration,
        'start': datetime.now(timezone.utc).isoformat(),
        'stop': None
    }

    # Send POST request to Toggl API
    response = requests.post(url, auth=auth, json=json_data)

    # Check response status code
    if response.status_code == 200:
        print('Time entry created successfully')
    else:
        print(f'Error creating time entry: {response.text}')


class TogglRecordTimeCommand(BaseCommand):
    trigger = "toggl_record_time"
    command_type = command_types['CHAINABLE_LONG']
    keywords = {
        "action": ["record"],
        "subject": ["time"]
    }
    examples = [
        'record my time',
        'record time log'
    ]

    def run(self, text_parameter, *args, **kwargs):
        api_token = toggl_api_key
        workspace_id = toggl_workspace_id
        create_running_time_entry(api_token, workspace_id, description=text_parameter)

