/**
 * Nirogya AI — Dynamic Frontend API Config
 * Works seamlessly whether loaded from port 8080 (same origin) or port 3000 (standalone frontend)
 */

const API_BASE = (typeof window !== 'undefined' && window.location.port === "8000")
  ? ""
  : (typeof window !== 'undefined' && window.location.hostname)
    ? `http://${window.location.hostname}:8000`
    : "http://127.0.0.1:8000";
