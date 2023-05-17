import subprocess

from whispering_assistant.commands.command_base_template import BaseCommand, command_types
from whispering_assistant.utils.fuzzy_json_show_dialog import fuzzy_search_json

return_keys = ["link", "url"]
search_keys = ["name", "url", "title", "label", "link"]
name_keys = ["name", "title", "label"]
json_files = [
    "/home/joshua/extrafiles/projects/WhisperingAssistant/whispering_assistant/assets/docs/links_list.json",
    "/home/joshua/extrafiles/projects/WhisperingAssistant/whispering_assistant/assets/docs/history_output.json",
    "/home/joshua/extrafiles/projects/WhisperingAssistant/whispering_assistant/assets/docs/bookmarks.urls.json",
]


class OpenLink(BaseCommand):
    trigger = "open_link"
    command_type = command_types['CHAINABLE_SHORT']
    keywords = {
        "action": ["open link", "open web"],
        "subject": []
    }
    examples = [
        'open link',
        'open web',
        'open link for',
        'open web for',
        'go to link'
    ]

    def run(self, text_parameter, *args, **kwargs):
        def process_cb(link):
            if link is not None:
                # open the URL in a new tab in Chrome on Ubuntu
                subprocess.run(["google-chrome", "--new-tab", link])

        fuzzy_search_json(query=text_parameter,
                          json_files=json_files,
                          return_keys=return_keys,
                          search_keys=search_keys,
                          name_keys=name_keys,
                          value_keys=return_keys,
                          process_selected_option_cb=process_cb)
