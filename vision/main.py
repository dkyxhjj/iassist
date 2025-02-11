from vision.imports import *
from vision.scene import Scene
from vision.priority_list import NavigationQueue
from vision.tts import TTSProcessor
import sys
import platform
from collections import deque
import time
import cv2

def find_available_camera():
    """Try to find an available camera by testing different indices."""
    print("Searching for available cameras...")
    
    # Try the first few camera indices
    for index in range(2):  # Try camera indices 0 and 1
        print(f"Trying camera index {index}...")
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print(f"Successfully found camera at index {index}")
                cap.release()
                return index
            cap.release()
    
    return None

def check_camera_access():
    """Check if camera is accessible and provide clear error messages."""
    try:
        # Print system information
        print(f"Operating System: {platform.system()} {platform.release()}")
        
        # Find available camera
        camera_index = find_available_camera()
        if camera_index is None:
            print("\nError: Could not access any cameras. Please check:")
            print("1. If a camera is connected to your computer")
            print("2. If you have granted camera permissions:")
            print("   - On macOS: System Preferences -> Security & Privacy -> Camera")
            print("   - On Linux: Check if you're in the 'video' group")
            print("   - On Windows: Settings -> Privacy -> Camera")
            print("\n3. If you're running this in a terminal, try:")
            print("   - Running from a different terminal")
            print("   - Running with sudo (if on Linux)")
            return False, None
            
        return True, camera_index
            
    except Exception as e:
        print(f"Error accessing camera: {str(e)}")
        return False, None

def main():
    # First check camera access
    camera_available, camera_index = check_camera_access()
    if not camera_available:
        return

    frame_size = (640, 480)  # Smaller frame size for faster processing
    fps_target = 30
    frame_interval = 1.0 / fps_target

    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print(f"Error: Failed to open camera {camera_index}")
        return

    # Set camera properties
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_size[0])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_size[1])

    # Fast tracking settings
    tracking_buffer_size = 5  # Keep last 5 frames for movement
    tracking_frame_skip = 1   # Process every frame for movement

    # Slow analysis settings
    analysis_buffer_size = 50  # Larger buffer for scene analysis
    analysis_frame_skip = 3  # Process every __ th frame for analysis
    analysis_interval = 2.0    # Summarize scene every __ seconds

    scene = Scene()
    
    # Separate buffers for tracking and analysis
    tracking_buffer = deque(maxlen=tracking_buffer_size)
    analysis_buffer = deque(maxlen=analysis_buffer_size)
    
    frame_count = 0
    last_analysis = time.time()

    scene = Scene()
    nav_queue = NavigationQueue()
    tts_processor = TTSProcessor()
    tts_processor.start_processing_thread()

    try:
        last_frame_time = time.time()
        while True:
            # Frame rate control
            current_time = time.time()
            if current_time - last_frame_time < frame_interval:
                continue

            ret, frame = cap.read()
            if not ret:
                break
            
            # Resize frame for faster processing
            frame = cv2.resize(frame, frame_size)

            frame_count += 1


            # Fast tracking loop
            if frame_count % tracking_frame_skip == 0:
                tracking_buffer.append((frame, current_time))
                movement = scene.process_movement(tracking_buffer)
                if movement:  # Only print if significant movement detected
                    # print("[Movement]", movement)
                    pass


            # Slower analysis loop
            if frame_count % analysis_frame_skip == 0:
                analysis_buffer.append((frame, current_time))

            # Periodic scene analysis
            if current_time - last_analysis >= analysis_interval:
                if len(analysis_buffer) > 0:
                    summary = scene.llm_summarize(analysis_buffer)
                    #print("[Scene]", summary)
                    response, tag = summary
                    priority_queue_item = scene._format_for_priority_queue(response, tag) # TURNED TO JSON
                    nav_queue = NavigationQueue()
                    nav_queue.add_json_item(priority_queue_item)

                    if nav_queue.queue:
                        message, priority = nav_queue.queue[0]
                        tts_processor.add_message(message, priority)
                        nav_queue.queue.pop(0)
                        
                    last_analysis = current_time
                    analysis_buffer.clear()
            
            if frame_count % analysis_frame_skip == 0:
                analysis_buffer.append((frame, current_time))

            # Display frame with annotations
            annotated_frame = scene.annotate_frame(frame)

            cv2.imshow("Camera", annotated_frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()