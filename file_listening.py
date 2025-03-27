import watchdog.events
import watchdog.observers
import time
from image_cropping import crop_image, save_cropped_circles
import os
import config as c
 
# reference: https://www.geeksforgeeks.org/create-a-watchdog-in-python-to-look-for-filesystem-changes/
 
class Handler(watchdog.events.PatternMatchingEventHandler):
    def __init__(self, crop_out_path):
        # Set the patterns for PatternMatchingEventHandler
        watchdog.events.PatternMatchingEventHandler.__init__(self, patterns=['*.png'],
                                                             ignore_directories=True, case_sensitive=False)
        self.crop_out_path = crop_out_path
        self.event_time = 0
 
    def on_modified(self, event):
        if not event.is_directory:
            print("Watchdog received modified event - % s." % event.src_path)
            if os.path.exists(event.src_path):
                image_dict = crop_image(event.src_path)
                save_cropped_circles(image_dict, self.crop_out_path)

    def on_created(self, event):
        print("Watchdog received created event - % s." % event.src_path)



event_handler = Handler(c.crop_out_path)
observer = watchdog.observers.Observer()
observer.schedule(event_handler, path=c.listening_path, recursive=True)
observer.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()