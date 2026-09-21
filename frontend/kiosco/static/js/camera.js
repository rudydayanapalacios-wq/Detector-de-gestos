/* =========================================================
   GESTUREKIOSK
   Captura y control del stream de cámara
   ========================================================= */

document.addEventListener("DOMContentLoaded", () => {

    const video = document.getElementById("cameraVideo");
    const startButton = document.getElementById("startCamera");
    const stopButton = document.getElementById("stopCamera");

    const cameraFrame = document.querySelector(".camera-frame");

    const cameraStatus = document.getElementById("cameraStatus");
    const cameraIndicator = document.getElementById("cameraIndicator");

    const cameraMessage = document.getElementById("cameraMessage");

    let cameraStream = null;


    /* =====================================================
       INICIAR CÁMARA
       ===================================================== */

    async function startCamera() {

        cameraMessage.textContent = "";

        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {

            showError(
                "Tu navegador no permite acceder a la cámara."
            );

            return;
        }


        try {

            cameraStream = await navigator.mediaDevices.getUserMedia({
                video: {
                    width: {
                        ideal: 1280
                    },

                    height: {
                        ideal: 720
                    },

                    facingMode: "user"
                },

                audio: false
            });


            video.srcObject = cameraStream;

            await video.play();


            cameraFrame.classList.add("camera-active");


            cameraStatus.textContent = "Cámara activa";

            cameraIndicator.textContent = "LIVE";


            startButton.disabled = true;

            stopButton.disabled = false;


        } catch (error) {

            console.error(
                "Error al acceder a la cámara:",
                error
            );


            handleCameraError(error);

        }

    }


    /* =====================================================
       DETENER CÁMARA
       ===================================================== */

    function stopCamera() {

        if (cameraStream) {

            cameraStream.getTracks().forEach(
                (track) => track.stop()
            );

            cameraStream = null;

        }


        video.srcObject = null;


        cameraFrame.classList.remove(
            "camera-active"
        );


        cameraStatus.textContent =
            "Cámara detenida";

        cameraIndicator.textContent =
            "STANDBY";


        startButton.disabled = false;

        stopButton.disabled = true;


        cameraMessage.textContent = "";

    }


    /* =====================================================
       ERRORES
       ===================================================== */

    function handleCameraError(error) {

        let message =
            "No fue posible acceder a la cámara.";

        if (error.name === "NotAllowedError") {

            message =
                "Permiso de cámara denegado. "
                + "Permite el acceso desde el navegador.";

        } else if (error.name === "NotFoundError") {

            message =
                "No se encontró ninguna cámara "
                + "conectada al dispositivo.";

        } else if (error.name === "NotReadableError") {

            message =
                "La cámara está siendo utilizada "
                + "por otra aplicación.";

        } else if (error.name === "OverconstrainedError") {

            message =
                "La cámara no admite la configuración solicitada.";

        }


        showError(message);

    }


    function showError(message) {

        cameraMessage.textContent = message;

        cameraStatus.textContent =
            "Cámara no disponible";

        cameraIndicator.textContent =
            "ERROR";

    }


    /* =====================================================
       EVENTOS
       ===================================================== */

    startButton.addEventListener(
        "click",
        startCamera
    );

    stopButton.addEventListener(
        "click",
        stopCamera
    );


    /* =====================================================
       LIMPIAR CÁMARA AL SALIR
       ===================================================== */

    window.addEventListener(
        "beforeunload",
        stopCamera
    );

});