import cv2
import mediapipe as mp


class GestureService:

    def __init__(self):
        self.hands = mp.tasks.vision.HandLandmarker.create_from_options(
            mp.tasks.vision.HandLandmarkerOptions(
                base_options=mp.tasks.BaseOptions(
                    model_asset_path="hand_landmarker.task"
                ),
                running_mode=mp.tasks.vision.RunningMode.IMAGE,
                num_hands=1,
                min_hand_detection_confidence=0.5,
                min_hand_presence_confidence=0.5,
                min_tracking_confidence=0.5
            )
        )

    def detect_hand(self, image):
        rgb_image = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2RGB
        )

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_image
        )

        results = self.hands.detect(mp_image)

        if not results.hand_landmarks:
            return None

        return results.hand_landmarks[0]

    def recognize_gesture(self, landmarks):
        if landmarks is None:
            return None

        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        middle_tip = landmarks[12]
        ring_tip = landmarks[16]
        pinky_tip = landmarks[20]

        index_pip = landmarks[6]
        middle_pip = landmarks[10]
        ring_pip = landmarks[14]
        pinky_pip = landmarks[18]

        # Índice levantado
        index_up = index_tip.y < index_pip.y

        # Otros dedos cerrados
        middle_closed = middle_tip.y > middle_pip.y
        ring_closed = ring_tip.y > ring_pip.y
        pinky_closed = pinky_tip.y > pinky_pip.y

        if index_up and middle_closed and ring_closed and pinky_closed:
            return "SELECT"

        # Mano abierta
        index_open = index_tip.y < index_pip.y
        middle_open = middle_tip.y < middle_pip.y
        ring_open = ring_tip.y < ring_pip.y
        pinky_open = pinky_tip.y < pinky_pip.y

        if index_open and middle_open and ring_open and pinky_open:
            return "BACK"

        # Pulgar arriba
        thumb_up = thumb_tip.y < landmarks[3].y

        if thumb_up and middle_closed and ring_closed and pinky_closed:
            return "SWIPE_RIGHT"

        return None

    def process_image(self, image):
        landmarks = self.detect_hand(image)
        return self.recognize_gesture(landmarks)