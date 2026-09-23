// ============================================================
// GESTUREKIOSK
// Captura de cámara + reconocimiento de gestos
// ============================================================


// ============================================================
// CONFIGURACIÓN
// ============================================================

const config = window.GESTURE_CONFIG || {};

const API_URL = config.apiUrl || "";
const ACCESS_TOKEN = config.accessToken || "";

const RECOGNITION_ENDPOINT = `${API_URL}/api/v1/recognize-action`;


// ============================================================
// ELEMENTOS DEL DOM
// ============================================================

const video = document.getElementById("cameraVideo");

const startButton = document.getElementById("startCamera");
const stopButton = document.getElementById("stopCamera");

const cameraPlaceholder =
    document.getElementById("cameraPlaceholder");

const cameraState =
    document.getElementById("cameraState");

const cameraError =
    document.getElementById("cameraError");

const gestureStatus =
    document.getElementById("gestureStatus");

const gestureIndicator =
    document.getElementById("gestureIndicator");

const connectionStatus =
    document.getElementById("connectionStatus");

const connectionMessage =
    document.getElementById("connectionMessage");


// ============================================================
// VARIABLES DE CONTROL
// ============================================================

let cameraStream = null;

let recognitionInterval = null;

let recognitionInProgress = false;

let canvas = null;

let lastAction = null;

let lastActionTime = 0;


// ============================================================
// CONFIGURACIÓN DEL RECONOCIMIENTO
// ============================================================

// Tiempo entre capturas enviadas al backend.
// Evita enviar demasiadas peticiones por segundo.

const RECOGNITION_INTERVAL = 900;


// Tiempo mínimo antes de volver a considerar
// el mismo gesto como una nueva acción.

const ACTION_COOLDOWN = 1500;


// Calidad JPEG enviada al backend.

const IMAGE_QUALITY = 0.75;


// ============================================================
// MAPA DE GESTOS
// ============================================================

const ACTION_NAMES = {
    SELECT: "Seleccionar",
    BACK: "Volver",
    SWIPE_RIGHT: "Siguiente"
};


// ============================================================
// UTILIDADES DE INTERFAZ
// ============================================================

function showError(message) {
    if (!cameraError) {
        return;
    }

    cameraError.textContent = message;
    cameraError.hidden = false;
}


function hideError() {
    if (!cameraError) {
        return;
    }

    cameraError.textContent = "";
    cameraError.hidden = true;
}


function updateGesture(action) {
    if (!gestureStatus) {
        return;
    }

    if (!action) {
        gestureStatus.innerHTML =
            'Gesto detectado: <strong>Esperando gesto...</strong>';

        if (gestureIndicator) {
            gestureIndicator.classList.remove("active");
        }

        return;
    }

    const readableAction =
        ACTION_NAMES[action] || action;

    gestureStatus.innerHTML =
        `Gesto detectado: <strong>${readableAction}</strong>`;

    if (gestureIndicator) {
        gestureIndicator.classList.add("active");

        setTimeout(() => {
            gestureIndicator.classList.remove("active");
        }, 700);
    }
}


function updateConnectionStatus(status, message) {
    if (connectionStatus) {
        connectionStatus.textContent = status;
    }

    if (connectionMessage) {
        connectionMessage.textContent = message;
    }
}


// ============================================================
// INICIAR CÁMARA
// ============================================================

async function startCamera() {
    hideError();

    if (!navigator.mediaDevices ||
        !navigator.mediaDevices.getUserMedia) {

        showError(
            "Tu navegador no permite acceder a la cámara."
        );

        return;
    }

    if (cameraStream) {
        return;
    }

    try {
        cameraState.textContent = "Solicitando cámara...";

        cameraStream =
            await navigator.mediaDevices.getUserMedia({
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


        // --------------------------------------------------------
        // PREPARAR CANVAS
        // --------------------------------------------------------

        canvas = document.createElement("canvas");


        // --------------------------------------------------------
        // ACTUALIZAR INTERFAZ
        // --------------------------------------------------------

        cameraPlaceholder.classList.add("hidden");

        cameraState.textContent = "Cámara activa";

        startButton.disabled = true;
        stopButton.disabled = false;

        updateConnectionStatus(
            "Cámara activa",
            "Reconocimiento de gestos listo."
        );

        updateGesture(null);


        // --------------------------------------------------------
        // COMENZAR RECONOCIMIENTO
        // --------------------------------------------------------

        startRecognition();

    } catch (error) {

        console.error(
            "Error al iniciar la cámara:",
            error
        );

        cameraStream = null;

        cameraState.textContent = "Cámara detenida";

        startButton.disabled = false;
        stopButton.disabled = true;


        if (error.name === "NotAllowedError") {

            showError(
                "Permiso de cámara denegado. " +
                "Permite el acceso a la cámara desde el navegador."
            );

        } else if (error.name === "NotFoundError") {

            showError(
                "No se encontró ninguna cámara conectada."
            );

        } else if (error.name === "NotReadableError") {

            showError(
                "La cámara está siendo utilizada por otra aplicación."
            );

        } else {

            showError(
                "No fue posible iniciar la cámara."
            );
        }

        updateConnectionStatus(
            "Cámara no disponible",
            "Revisa los permisos de la cámara."
        );
    }
}


// ============================================================
// DETENER CÁMARA
// ============================================================

function stopCamera() {

    stopRecognition();


    if (cameraStream) {

        cameraStream
            .getTracks()
            .forEach(track => track.stop());

        cameraStream = null;
    }


    video.srcObject = null;


    cameraPlaceholder.classList.remove("hidden");


    cameraState.textContent = "Cámara detenida";


    startButton.disabled = false;
    stopButton.disabled = true;


    updateConnectionStatus(
        "Cámara detenida",
        "Inicia la cámara para comenzar el reconocimiento."
    );


    updateGesture(null);


    lastAction = null;
    lastActionTime = 0;
}


// ============================================================
// INICIAR RECONOCIMIENTO
// ============================================================

function startRecognition() {

    stopRecognition();


    recognitionInterval = setInterval(() => {

        if (!cameraStream) {
            return;
        }

        if (video.readyState < 2) {
            return;
        }

        if (recognitionInProgress) {
            return;
        }

        recognizeGesture();

    }, RECOGNITION_INTERVAL);
}


// ============================================================
// DETENER RECONOCIMIENTO
// ============================================================

function stopRecognition() {

    if (recognitionInterval) {

        clearInterval(recognitionInterval);

        recognitionInterval = null;
    }

    recognitionInProgress = false;
}


// ============================================================
// CAPTURAR FRAME
// ============================================================

function captureFrame() {

    if (!canvas) {
        canvas = document.createElement("canvas");
    }


    const width = video.videoWidth;
    const height = video.videoHeight;


    if (!width || !height) {
        return null;
    }


    // Reducimos un poco la imagen antes de enviarla.
    // Esto evita mandar archivos innecesariamente grandes.

    const maxWidth = 640;

    const scale =
        width > maxWidth
            ? maxWidth / width
            : 1;


    canvas.width = Math.round(width * scale);
    canvas.height = Math.round(height * scale);


    const context =
        canvas.getContext("2d");


    context.drawImage(
        video,
        0,
        0,
        canvas.width,
        canvas.height
    );


    return canvas;
}


// ============================================================
// CONVERTIR CANVAS A BLOB
// ============================================================

function canvasToBlob(canvasElement) {

    return new Promise((resolve, reject) => {

        canvasElement.toBlob(
            blob => {

                if (!blob) {

                    reject(
                        new Error(
                            "No fue posible crear la imagen."
                        )
                    );

                    return;
                }

                resolve(blob);
            },

            "image/jpeg",

            IMAGE_QUALITY
        );
    });
}


// ============================================================
// ENVIAR IMAGEN A FASTAPI
// ============================================================

async function recognizeGesture() {

    if (!ACCESS_TOKEN) {

        console.error(
            "No existe un token de autenticación."
        );

        return;
    }


    if (!API_URL) {

        console.error(
            "No está configurada la URL de FastAPI."
        );

        return;
    }


    recognitionInProgress = true;


    try {

        const frame =
            captureFrame();


        if (!frame) {
            return;
        }


        const imageBlob =
            await canvasToBlob(frame);


        // --------------------------------------------------------
        // FORMDATA
        // --------------------------------------------------------

        const formData =
            new FormData();


        // El backend espera exactamente:
        // file: UploadFile

        formData.append(
            "file",
            imageBlob,
            "gesture.jpg"
        );


        // --------------------------------------------------------
        // PETICIÓN HTTP
        // --------------------------------------------------------

        const response =
            await fetch(
                RECOGNITION_ENDPOINT,
                {
                    method: "POST",

                    headers: {
                        "Authorization":
                            `Bearer ${ACCESS_TOKEN}`
                    },

                    body: formData
                }
            );


        // --------------------------------------------------------
        // RESPUESTA NO EXITOSA
        // --------------------------------------------------------

        if (!response.ok) {

            let detail =
                "No fue posible reconocer el gesto.";

            try {

                const errorData =
                    await response.json();

                if (errorData.detail) {
                    detail = errorData.detail;
                }

            } catch (error) {
                // La respuesta no tenía JSON.
            }


            if (response.status === 401) {

                detail =
                    "La sesión no es válida. " +
                    "Inicia sesión nuevamente.";
            }


            throw new Error(
                `${detail} (${response.status})`
            );
        }


        // --------------------------------------------------------
        // LEER RESPUESTA
        // --------------------------------------------------------

        const data =
            await response.json();


        console.log(
            "Respuesta de FastAPI:",
            data
        );


        // --------------------------------------------------------
        // PROCESAR ACCIÓN
        // --------------------------------------------------------

        const action =
            data.action;


        if (!action) {

            updateGesture(null);

            return;
        }


        processAction(action);


    } catch (error) {

        console.error(
            "Error en reconocimiento:",
            error
        );

        updateConnectionStatus(
            "Error de conexión",
            "No fue posible comunicarse con el servidor."
        );

    } finally {

        recognitionInProgress = false;
    }
}


// ============================================================
// PROCESAR ACCIÓN DETECTADA
// ============================================================

function processAction(action) {

    const now =
        Date.now();


    // Evita repetir inmediatamente
    // la misma acción.

    if (
        action === lastAction &&
        now - lastActionTime < ACTION_COOLDOWN
    ) {
        return;
    }


    lastAction = action;
    lastActionTime = now;


    updateGesture(action);


    updateConnectionStatus(
        "Gesto reconocido",
        `Acción detectada: ${
            ACTION_NAMES[action] || action
        }`
    );


    console.log(
        "Acción detectada:",
        action
    );


    // ----------------------------------------------------------
    // ACCIONES DEL KIOSCO
    // ----------------------------------------------------------
    //
    // Por ahora solamente mostramos la acción.
    //
    // La navegación real del kiosco se puede conectar después.
    //
    // SELECT      → seleccionar
    // BACK        → volver
    // SWIPE_RIGHT → siguiente
    //
    // ----------------------------------------------------------

    switch (action) {

        case "SELECT":

            console.log(
                "Acción SELECT"
            );

            break;


        case "BACK":

            console.log(
                "Acción BACK"
            );

            break;


        case "SWIPE_RIGHT":

            console.log(
                "Acción SWIPE_RIGHT"
            );

            break;


        default:

            console.log(
                "Acción no mapeada:",
                action
            );
    }
}


// ============================================================
// EVENTOS
// ============================================================

if (startButton) {

    startButton.addEventListener(
        "click",
        startCamera
    );
}


if (stopButton) {

    stopButton.addEventListener(
        "click",
        stopCamera
    );
}


// ============================================================
// SEGURIDAD
// Detener cámara si se abandona la página.
// ============================================================

window.addEventListener(
    "beforeunload",
    () => {
        stopCamera();
    }
);


// ============================================================
// ESTADO INICIAL
// ============================================================

updateConnectionStatus(
    "Esperando cámara",
    "Inicia la cámara para comenzar el reconocimiento."
);

updateGesture(null);