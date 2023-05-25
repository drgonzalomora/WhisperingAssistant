import subprocess
from whispering_assistant.commands.command_base_template import BaseCommand, command_types


class IotLightsControl(BaseCommand):
    trigger = "iot_lights_control"
    command_type = command_types['ONE_SHOT']
    keywords = {"action": ["turn on", "turn off"], "subject": ["light", "lights"]}
    description = [
        "use the following tool for turning on or turning off the lights"
    ]
    examples = [
        'turn on lights',
        'turn off lights'
    ]

    def run(self, text_parameter, raw_text, *args, **kwargs):
        command = 'false' if 'off' in raw_text else 'true'
        subprocess.run([
            "/home/joshua/extrafiles/projects/WhisperingAssistant/whispering_assistant/commands/bash_scripts/iot_lights_control.sh",
            "switch_led", command])
