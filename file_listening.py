from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import os
from image_cropping import crop_image, save_cropped_circles
import config as c

 
# reference: https://www.geeksforgeeks.org/create-a-watchdog-in-python-to-look-for-filesystem-changes/
 
class FileHandler(FileSystemEventHandler):
    def __init__(self, retry_list):
        self.retry_list = retry_list
 
    def on_modified(self, event):
        if not event.is_directory:
            print("Watchdog received modified event - % s." % event.src_path)
            event_path = event.src_path.replace("\\", "/")
            if os.path.exists(event_path):

                # (Path, Last Attempt Time, Retry Delay)
                self.retry_list.append((event_path, time.time(), 1))


    def on_created(self, event):
        print("Watchdog received created event - % s." % event.src_path.replace("\\", "/"))


def process_files(retry_list, crop_out_path):
    """Processes files that are no longer locked."""
    while True:
        current_time = time.time()
        to_remove = []

        for i, (file_path, last_attempt, delay) in enumerate(retry_list):
            if current_time - last_attempt >= delay:
                if is_file_unlocked(file_path):
                    print(f"Processing: {file_path}")
                    image_dict = crop_image(file_path)
                    save_cropped_circles(image_dict, crop_out_path)


                    to_remove.append(i)
                else:
                    retry_list[i] = (file_path, current_time, min(delay * 2, 10))  # Exponential backoff

        for i in sorted(to_remove, reverse=True):  # Remove processed files
            del retry_list[i]

        time.sleep(1)  # Avoid busy-waiting

def is_file_unlocked(file_path):
    """Returns True if the file is not locked."""
    try:
        with open(file_path, "a"):  
            return True
    except PermissionError:
        return False
    

retry_list = []
event_handler = FileHandler(retry_list)
observer = Observer()
observer.schedule(event_handler, c.listening_path, recursive=False)
observer.start()

try:
    process_files(retry_list, c.crop_out_path)  # Runs in main thread
except KeyboardInterrupt:
    observer.stop()
observer.join()