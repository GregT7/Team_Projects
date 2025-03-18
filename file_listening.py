import watchdog.events
import watchdog.observers
import time
from image_cropping import crop_image, save_cropped_circles
import os
 
# reference: https://www.geeksforgeeks.org/create-a-watchdog-in-python-to-look-for-filesystem-changes/
 
class Handler(watchdog.events.PatternMatchingEventHandler):
    def __init__(self, output_path):
        # Set the patterns for PatternMatchingEventHandler
        watchdog.events.PatternMatchingEventHandler.__init__(self, patterns=['*.png'],
                                                             ignore_directories=True, case_sensitive=False)
        self.output_path = output_path
        self.event_time = 0
 
    def on_modified(self, event):
        if not event.is_directory:
            print("Watchdog received modified event - % s." % event.src_path)
            if os.path.exists(event.src_path):
                image_dict = crop_image(event.src_path)
                save_cropped_circles(image_dict, output_path)


listening_path = "./tests/autocrop_input/" # listening - directory that is being watched
output_path = "./tests/autocrop_output/" # directory where cropped images will be dumped


event_handler = Handler(output_path)
observer = watchdog.observers.Observer()
observer.schedule(event_handler, path=listening_path, recursive=True)
observer.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()