import os
import glob
import random
from mutagen.wave import WAVE

def get_recordings(folder_path):
    file_count = 0

    # Iterate through all items in the folder
    for item in os.listdir(folder_path):
        # Construct the full path of the item
        full_path = os.path.join(folder_path, item)
        # Check if it's a file
        if os.path.isfile(full_path):
            file_count += 1

    return file_count

# Get length of audio
def mutagen_length(path):
    try:
        audio = WAVE(path)
        length = audio.info.length
        return length
    except:
        return 1
    
    
def pickRandom(path):
        soundList = glob.glob(f'{path}/*.wav')
        sound = random.choice(soundList)
        return sound   