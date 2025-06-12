/*
 * SCORM API Implementation
 * Este es un archivo JavaScript básico que proporciona una implementación
 * simplificada de la API de SCORM 2004 para los paquetes educativos.
 */

var API_1484_11 = {
    // Variables de estado
    _initialized: false,
    _terminated: false,
    _lastError: "0",
    _errorString: {
        "0": "No error",
        "101": "General initialization failure",
        "102": "Initialization already called",
        "103": "Initialization not called",
        "104": "Termination already called",
        "111": "General termination failure",
        "112": "Termination before initialization",
        "113": "Termination after termination",
        "122": "Get value before initialization",
        "123": "Get value after termination",
        "132": "Set value before initialization",
        "133": "Set value after termination",
        "142": "Commit before initialization",
        "143": "Commit after termination"
    },
    _statusCodes: ["completed", "incomplete", "not attempted", "unknown"],
    
    // Datos de la lección
    _data: {
        "cmi.learner_id": "Student01",
        "cmi.learner_name": "Estudiante Demo",
        "cmi.completion_status": "incomplete",
        "cmi.success_status": "unknown",
        "cmi.score.scaled": "0",
        "cmi.score.raw": "0",
        "cmi.score.min": "0",
        "cmi.score.max": "100",
        "cmi.progress_measure": "0",
        "cmi.session_time": "PT0H0M0S",
        "cmi.location": "0",
        "cmi.exit": ""
    },
    
    // Métodos de la API
    Initialize: function(param) {
        console.log("SCORM API Initialize called with param: " + param);
        
        if (param !== "true" && param !== "false" && param !== true && param !== false) {
            this._lastError = "201";
            return "false";
        }
        
        if (this._initialized) {
            this._lastError = "102";
            return "false";
        }
        
        if (this._terminated) {
            this._lastError = "104";
            return "false";
        }
        
        this._initialized = true;
        this._lastError = "0";
        return "true";
    },
    
    Terminate: function(param) {
        console.log("SCORM API Terminate called with param: " + param);
        
        if (param !== "true" && param !== "false" && param !== true && param !== false) {
            this._lastError = "201";
            return "false";
        }
        
        if (!this._initialized) {
            this._lastError = "112";
            return "false";
        }
        
        if (this._terminated) {
            this._lastError = "113";
            return "false";
        }
        
        this._terminated = true;
        this._lastError = "0";
        return "true";
    },
    
    GetValue: function(element) {
        console.log("SCORM API GetValue called for: " + element);
        
        if (!this._initialized) {
            this._lastError = "122";
            return "";
        }
        
        if (this._terminated) {
            this._lastError = "123";
            return "";
        }
        
        if (this._data[element] === undefined) {
            this._lastError = "301";
            return "";
        }
        
        this._lastError = "0";
        return this._data[element];
    },
    
    SetValue: function(element, value) {
        console.log("SCORM API SetValue called for: " + element + " with value: " + value);
        
        if (!this._initialized) {
            this._lastError = "132";
            return "false";
        }
        
        if (this._terminated) {
            this._lastError = "133";
            return "false";
        }
        
        if (element === undefined || element === "") {
            this._lastError = "301";
            return "false";
        }
        
        // Validar y almacenar el valor
        this._data[element] = value;
        this._lastError = "0";
        return "true";
    },
    
    Commit: function(param) {
        console.log("SCORM API Commit called with param: " + param);
        
        if (!this._initialized) {
            this._lastError = "142";
            return "false";
        }
        
        if (this._terminated) {
            this._lastError = "143";
            return "false";
        }
        
        // En un entorno real, esto guardaría los datos en el LMS
        this._lastError = "0";
        return "true";
    },
    
    GetLastError: function() {
        return this._lastError;
    },
    
    GetErrorString: function(errorCode) {
        if (this._errorString[errorCode] !== undefined) {
            return this._errorString[errorCode];
        }
        return "Unknown error code";
    },
    
    GetDiagnostic: function(errorCode) {
        if (this._errorString[errorCode] !== undefined) {
            return "Diagnostic: " + this._errorString[errorCode];
        }
        return "Unknown error code";
    }
};

// Asignar la API al objeto ventana para que SCORM pueda encontrarla
window.API_1484_11 = API_1484_11; 