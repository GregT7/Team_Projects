import watchdog.events
import watchdog.observers
import time
import image_cropping as crop
import os
 
# reference: https://www.geeksforgeeks.org/create-a-watchdog-in-python-to-look-for-filesystem-changes/
 
class Handler(watchdog.events.PatternMatchingEventHandler):
    def __init__(self, output_path):
        # Set the patterns for PatternMatchingEventHandler
        watchdog.events.PatternMatchingEventHandler.__init__(self, patterns=['*.png'],
                                                             ignore_directories=True, case_sensitive=False)
        self.output_path = output_path
 
    def on_created(self, event):
        if not event.is_directory:
            print("Watchdog received created event - % s." % event.src_path)
            self.process_image(event.src_path)
 
    def on_modified(self, event):
        if not event.is_directory:
            print("Watchdog received modified event - % s." % event.src_path)
            self.process_image(event.src_path)
            
    def process_image(self, file_path):
        if os.path.exists(file_path):
            image_dict = crop.crop_image(file_path)
            crop.save_cropped_image(image_dict, output_path)

    


# Set format for displaying path
listening_path = "../assets/test_cases/test_case50.11234/test/input/"
output_path = "../assets/test_cases/test_case50.11234/test/output/"
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