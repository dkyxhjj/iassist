import time
import logging
import pyttsx3
import queue
import threading
from typing import Optional
from vision.priority_list import NavigationQueue

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TTSProcessor:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.message_queue = queue.Queue()
        self.is_running = True
        self.current_priority = 0
        self.thread = None

    def process_message(self, message: str, priority: int):
        """Process a single message with priority."""
        if priority >= self.current_priority:
            self.current_priority = priority
            self.engine.say(message)
            self.engine.runAndWait()
            self.current_priority = 0

    def process_queue(self):
        """Process messages from the queue."""
        while self.is_running:
            try:
                message, priority = self.message_queue.get(timeout=1)
                self.process_message(message, priority)
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing message: {e}")

    def start_processing_thread(self):
        """Start the message processing thread."""
        self.thread = threading.Thread(target=self.process_queue)
        self.thread.daemon = True
        self.thread.start()

    def add_message(self, message: str, priority: int = 0):
        """Add a message to the queue."""
        self.message_queue.put((message, priority))

    def stop(self):
        """Stop the TTS processor."""
        self.is_running = False
        if self.thread:
            self.thread.join()

def main():
    tts = TTSProcessor()
    tts.start_processing_thread()
    
    # Test messages
    messages = [
        ("Hello, this is a test message.", 0),
        ("This is a high priority message!", 2),
        ("This is a low priority message.", 1)
    ]
    
    for msg, priority in messages:
        tts.add_message(msg, priority)
        time.sleep(1)
    
    time.sleep(5)  # Wait for messages to be processed
    tts.stop()

if __name__ == "__main__":
    main()
