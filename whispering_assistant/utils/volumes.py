import pulsectl


def get_volume():
    with pulsectl.Pulse('volume-example') as pulse:
        sink = pulse.get_sink_by_name(pulse.server_info().default_sink_name)
        volume = round(pulse.volume_get_all_chans(sink) * 100)
    return volume


def set_volume(new_volume):
    with pulsectl.Pulse('volume-set-example') as pulse:
        # Get the default sink
        sink = pulse.get_sink_by_name(pulse.server_info().default_sink_name)

        # Calculate the new volume as a float in the range [0, 1]
        new_volume_float = min(max(new_volume, 0), 100) / 100.0

        # Create a new volume object with the desired volume level for all channels
        channels = len(sink.volume.values)
        new_volume_object = pulsectl.PulseVolumeInfo(new_volume_float, channels)

        # Apply the new volume to the sink
        pulse.volume_set(sink, new_volume_object)


def set_microphone_volume(mic_name, volume_level):
    """
    Set microphone volume.

    Parameters:
        mic_name (str): The name of the microphone.
        volume_level (float): The volume level as a fraction between 0 and 1.

    """
    with pulsectl.Pulse('volume-controller') as pulse:
        for source in pulse.source_list():
            if mic_name in source.name:
                pulse.volume_set_all_chans(source, volume_level)


def list_microphones():
    """
    List all available microphones.
    """
    with pulsectl.Pulse('microphone-lister') as pulse:
        for source in pulse.source_list():
            print(source.name)

# Print all microphones
# list_microphones()
