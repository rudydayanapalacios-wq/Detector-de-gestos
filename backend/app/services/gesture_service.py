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

        # =====================================================
        # PUNTOS DE LA MANO
        # =====================================================

        wrist = landmarks[0]

        thumb_tip = landmarks[4]
        thumb_ip = landmarks[3]

        index_tip = landmarks[8]
        index_pip = landmarks[6]

        middle_tip = landmarks[12]
        middle_pip = landmarks[10]

        ring_tip = landmarks[16]
        ring_pip = landmarks[14]

        pinky_tip = landmarks[20]
        pinky_pip = landmarks[18]

        # =====================================================
        # FUNCIÓN PARA CALCULAR DISTANCIA
        # =====================================================

        def distance(a, b):
            return (
                (a.x - b.x) ** 2 +
                (a.y - b.y) ** 2
            ) ** 0.5

        # =====================================================
        # DISTANCIAS DE LOS DEDOS
        # =====================================================

        index_distance = distance(
            wrist,
            index_tip
        )

        index_pip_distance = distance(
            wrist,
            index_pip
        )

        middle_distance = distance(
            wrist,
            middle_tip
        )

        middle_pip_distance = distance(
            wrist,
            middle_pip
        )

        ring_distance = distance(
            wrist,
            ring_tip
        )

        ring_pip_distance = distance(
            wrist,
            ring_pip
        )

        pinky_distance = distance(
            wrist,
            pinky_tip
        )

        pinky_pip_distance = distance(
            wrist,
            pinky_pip
        )

        # =====================================================
        # DETECCIÓN DE DEDOS ABIERTOS
        # =====================================================

        index_open = (
            index_distance >
            index_pip_distance * 1.15
            and
            index_tip.y <
            index_pip.y - 0.02
        )

        middle_open = (
            middle_distance >
            middle_pip_distance * 1.15
            and
            middle_tip.y <
            middle_pip.y - 0.02
        )

        ring_open = (
            ring_distance >
            ring_pip_distance * 1.15
            and
            ring_tip.y <
            ring_pip.y - 0.02
        )

        pinky_open = (
            pinky_distance >
            pinky_pip_distance * 1.15
            and
            pinky_tip.y <
            pinky_pip.y - 0.02
        )

        # =====================================================
        # DETECCIÓN DE DEDOS CERRADOS
        # =====================================================

        index_closed = (
            index_distance <
            index_pip_distance * 1.10
        )

        middle_closed = (
            middle_distance <
            middle_pip_distance * 1.10
        )

        ring_closed = (
            ring_distance <
            ring_pip_distance * 1.10
        )

        pinky_closed = (
            pinky_distance <
            pinky_pip_distance * 1.10
        )

        # =====================================================
        # SELECT
        #
        # Índice arriba
        # Otros tres dedos cerrados
        # =====================================================

        if (
            index_open
            and
            middle_closed
            and
            ring_closed
            and
            pinky_closed
        ):
            return "SELECT"

        # =====================================================
        # BACK
        #
        # Los cuatro dedos abiertos
        # =====================================================

        if (
            index_open
            and
            middle_open
            and
            ring_open
            and
            pinky_open
        ):
            return "BACK"

        # =====================================================
        # SWIPE_RIGHT
        #
        # Pulgar arriba
        # Los otros cuatro dedos cerrados
        # =====================================================

        thumb_distance = distance(
            wrist,
            thumb_tip
        )

        thumb_ip_distance = distance(
            wrist,
            thumb_ip
        )

        thumb_up = (
            thumb_distance >
            thumb_ip_distance * 1.10
            and
            thumb_tip.y <
            thumb_ip.y - 0.025
        )

        if (
            thumb_up
            and
            index_closed
            and
            middle_closed
            and
            ring_closed
            and
            pinky_closed
        ):
            return "SWIPE_RIGHT"

        # =====================================================
        # POSICIÓN AMBIGUA
        #
        # No reconocer nada.
        # =====================================================

        return None

    def process_image(self, image):
        landmarks = self.detect_hand(image)

        return self.recognize_gesture(landmarks)