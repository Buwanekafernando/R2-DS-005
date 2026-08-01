import axios from "axios"

const BASE_URL = "http://localhost:5000"

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 300000,
})

export function healthCheck() {
  return api.get("/health").then((res) => res.data)
}

export function predictEmotion(text) {
  return api.post("/api/predict-emotion", { text }).then((res) => res.data)
}

export function generateMessage(payload) {
  return api.post("/api/generate-message", payload).then((res) => res.data)
}

export function generateVariations(payload) {
  return api.post("/api/generate-variations", payload).then((res) => res.data)
}

export function submitUserStudy(payload) {
  return api.post("/api/user-study", payload).then((res) => res.data)
}

export function getUserStudySummary() {
  return api.get("/api/user-study-summary").then((res) => res.data)
}

export function getUserStudyResponses() {
  return api.get("/api/user-study-responses").then((res) => res.data)
}

export { BASE_URL }
