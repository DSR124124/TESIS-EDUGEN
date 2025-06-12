/*
 * API simple para SCORM 1.2
 * Permite la comunicación básica entre el contenido y un LMS
 */

// Variables globales para el estado del API
var _SCORM_API = {
    initialized: false,
    finished: false,
    score: 0,
    status: "not attempted",
    suspendData: "",
    errorCode: "0",
    errorString: "",
    studentName: "Estudiante",
    studentId: "STUDENT_001"
};

// Función para inicializar
function LMSInitialize(param) {
    console.log("LMSInitialize llamado con: " + param);
    
    if (_SCORM_API.initialized) {
        _SCORM_API.errorCode = "101";
        return "false";
    }
    
    if (param !== "") {
        _SCORM_API.errorCode = "201";
        return "false";
    }
    
    _SCORM_API.initialized = true;
    _SCORM_API.errorCode = "0";
    _SCORM_API.status = "incomplete";
    
    return "true";
}

// Función para terminar
function LMSFinish(param) {
    console.log("LMSFinish llamado con: " + param);
    
    if (!_SCORM_API.initialized) {
        _SCORM_API.errorCode = "301";
        return "false";
    }
    
    if (param !== "") {
        _SCORM_API.errorCode = "201";
        return "false";
    }
    
    _SCORM_API.initialized = false;
    _SCORM_API.finished = true;
    _SCORM_API.errorCode = "0";
    
    return "true";
}

// Función para obtener un valor
function LMSGetValue(param) {
    console.log("LMSGetValue llamado con: " + param);
    
    if (!_SCORM_API.initialized) {
        _SCORM_API.errorCode = "301";
        return "";
    }
    
    var value = "";
    
    switch (param) {
        case "cmi.core.student_name":
            value = _SCORM_API.studentName;
            break;
        case "cmi.core.student_id":
            value = _SCORM_API.studentId;
            break;
        case "cmi.core.score.raw":
            value = _SCORM_API.score;
            break;
        case "cmi.core.lesson_status":
            value = _SCORM_API.status;
            break;
        case "cmi.suspend_data":
            value = _SCORM_API.suspendData;
            break;
        default:
            _SCORM_API.errorCode = "401";
            break;
    }
    
    return value;
}

// Función para establecer un valor
function LMSSetValue(param, value) {
    console.log("LMSSetValue llamado con: " + param + ", " + value);
    
    if (!_SCORM_API.initialized) {
        _SCORM_API.errorCode = "301";
        return "false";
    }
    
    var success = "false";
    
    switch (param) {
        case "cmi.core.score.raw":
            _SCORM_API.score = value;
            success = "true";
            break;
        case "cmi.core.lesson_status":
            if (value === "completed" || value === "incomplete" || value === "not attempted" || 
                value === "failed" || value === "passed") {
                _SCORM_API.status = value;
                success = "true";
            } else {
                _SCORM_API.errorCode = "405";
            }
            break;
        case "cmi.suspend_data":
            _SCORM_API.suspendData = value;
            success = "true";
            break;
        default:
            _SCORM_API.errorCode = "401";
            break;
    }
    
    return success;
}

// Función para confirmar los cambios
function LMSCommit(param) {
    console.log("LMSCommit llamado con: " + param);
    
    if (!_SCORM_API.initialized) {
        _SCORM_API.errorCode = "301";
        return "false";
    }
    
    if (param !== "") {
        _SCORM_API.errorCode = "201";
        return "false";
    }
    
    _SCORM_API.errorCode = "0";
    return "true";
}

// Función para obtener el último error
function LMSGetLastError() {
    return _SCORM_API.errorCode;
}

// Función para obtener texto del error
function LMSGetErrorString(errorCode) {
    var errorString = "";
    
    switch (errorCode) {
        case "0":
            errorString = "No error";
            break;
        case "101":
            errorString = "General initialization failure";
            break;
        case "201":
            errorString = "Invalid parameter";
            break;
        case "301":
            errorString = "Not initialized";
            break;
        case "401":
            errorString = "Not implemented";
            break;
        case "405":
            errorString = "Incorrect data type";
            break;
        default:
            errorString = "Unknown error";
    }
    
    return errorString;
}

// Función para obtener información de diagnóstico
function LMSGetDiagnostic(errorCode) {
    return LMSGetErrorString(errorCode);
}

// Adaptador de API para diferentes versiones de SCORM
var API = {
    LMSInitialize: LMSInitialize,
    LMSFinish: LMSFinish,
    LMSGetValue: LMSGetValue,
    LMSSetValue: LMSSetValue,
    LMSCommit: LMSCommit,
    LMSGetLastError: LMSGetLastError,
    LMSGetErrorString: LMSGetErrorString,
    LMSGetDiagnostic: LMSGetDiagnostic
};

// Para SCORM 1.2 (asegurarse de que esté disponible en todos los frames)
window.API = API;
try {
    if (window.parent && window.parent !== window) {
        window.parent.API = API;
    }
    if (window.top && window.top !== window) {
        window.top.API = API;
    }
} catch (e) {
    console.error("Error al asignar API a framesets: " + e.message);
}

// Función para marcar el curso como completado
function marcarComoCompletado() {
    if (!_SCORM_API.initialized) {
        LMSInitialize("");
    }
    
    LMSSetValue("cmi.core.lesson_status", "completed");
    LMSCommit("");
}

// Inicializar automáticamente cuando se carga la página
document.addEventListener('DOMContentLoaded', function() {
    LMSInitialize("");
    console.log("SCORM API inicializada automáticamente");
}); 