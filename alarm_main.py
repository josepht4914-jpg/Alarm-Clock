import datetime
import time
import pygame
import cv2
import webbrowser


def set_alarm(alarm_time):
    print(f"Alarm set for {alarm_time}")

    sound_file = "mixkit-classic-alarm-995.wav"
    is_running = True

    pygame.mixer.init()

    try:
        pygame.mixer.music.load(sound_file)

        while is_running:
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            print(current_time)

            if current_time == alarm_time:
                print("WAKE UP! Press Control + C to stop.")

                pygame.mixer.music.play(loops=-1)
                is_running = False

            time.sleep(1)

        open_camera()
        # Keep Python running while the alarm sound repeats.
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)

    finally:
        pygame.mixer.quit()

def open_camera():
    # Set up OpenCV's built-in person detector.
    detector = cv2.HOGDescriptor()
    detector.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

    camera = cv2.VideoCapture(0)
    detection_count = 0
    person_found = False

    try:
        if not camera.isOpened():
            print("Camera unavailable. Alarm keeps ringing.")
            print("Control + C stops the program.")
            return

        print("Step back so your whole body is visible.")
        print("Press Q in the camera window to stop manually.")

        while pygame.mixer.music.get_busy():
            success, frame = camera.read()

            if not success:
                print("Camera image unavailable. Alarm keeps ringing.")
                return

            # Make the picture smaller so detection runs faster.
            height, width = frame.shape[:2]
            frame = cv2.resize(
                frame, (640, int(height * 640 / width))
            )

            # Search the picture for people.
            people, _ = detector.detectMultiScale(
                frame,
                winStride=(8, 8),
                padding=(8, 8),
                scale=1.05
            )

            if len(people) > 0:
                detection_count += 1
            else:
                detection_count = 0

            # Draw a green rectangle around each detection.
            for x, y, w, h in people:
                cv2.rectangle(
                    frame,
                    (x, y),
                    (x + w, y + h),
                    (0, 255, 0),
                    2
                )

            cv2.imshow("Alarm Camera", frame)

            # Keep a manual stop option while testing.
            if cv2.waitKey(1) & 0xFF == ord("q"):
                pygame.mixer.music.stop()
                break

            # Require a person in five consecutive pictures.
            if detection_count >= 5:
                pygame.mixer.music.stop()
                person_found = True
                break

    finally:
        camera.release()
        cv2.destroyAllWindows()

    # Open weather after the camera has closed.
    if person_found:
        print("Person detected! Opening Austin weather...")

        weather_url = (
            "https://weather.com/us/texas/city/austin/today"
        )

        if not webbrowser.open(weather_url, new=2):
            print("Open this forecast in your browser:", weather_url)

if __name__ == "__main__":
    try:
        alarm_time = input("Set an alarm (HH:MM:SS): ").strip()
        set_alarm(alarm_time)

    except KeyboardInterrupt:
        print("\nAlarm stopped.")


