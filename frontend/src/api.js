/**
 * TeamWeave API Client.
 * Connects to Python FastAPI backend running at http://localhost:8000/api
 */

const API_BASE = "http://127.0.0.1:8000/api";

let authToken = localStorage.getItem("teamweave_token") || "";

export const setToken = (token) => {
  authToken = token;
  if (token) {
    localStorage.setItem("teamweave_token", token);
  } else {
    localStorage.removeItem("teamweave_token");
  }
};

export const getToken = () => authToken;

async function request(endpoint, options = {}) {
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  if (authToken) {
    headers["Authorization"] = `Bearer ${authToken}`;
  }

  const res = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    let errorDetail = "API Error";
    try {
      const errJson = await res.json();
      errorDetail = errJson.detail || JSON.stringify(errJson);
    } catch (e) {
      errorDetail = await res.text();
    }
    throw new Error(errorDetail);
  }

  return res.json();
}

export const api = {
  // Auth
  register: (data) => request("/auth/register", { method: "POST", body: JSON.stringify(data) }),
  login: (data) => request("/auth/login", { method: "POST", body: JSON.stringify(data) }),
  getMe: () => request("/auth/me"),

  // Users & Profile
  updateProfile: (data) => request("/users/me", { method: "PUT", body: JSON.stringify(data) }),
  getSkillsCatalog: () => request("/users/skills/catalog"),
  getMySkills: () => request("/users/me/skills"),
  addOrUpdateSkill: (data) => request("/users/me/skills", { method: "POST", body: JSON.stringify(data) }),
  removeSkill: (skillId) => request(`/users/me/skills/${skillId}`, { method: "DELETE" }),
  getMyEvidence: () => request("/users/me/evidence"),
  addEvidence: (data) => request("/users/me/evidence", { method: "POST", body: JSON.stringify(data) }),
  removeEvidence: (evId) => request(`/users/me/evidence/${evId}`, { method: "DELETE" }),

  // Events
  listEvents: () => request("/events"),
  getEvent: (id) => request(`/events/${id}`),
  createEvent: (data) => request("/events", { method: "POST", body: JSON.stringify(data) }),
  updateEvent: (id, data) => request(`/events/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  getEventRequirements: (id) => request(`/events/${id}/requirements`),
  addEventRequirement: (id, data) => request(`/events/${id}/requirements`, { method: "POST", body: JSON.stringify(data) }),
  deleteEventRequirement: (id, reqId) => request(`/events/${id}/requirements/${reqId}`, { method: "DELETE" }),
  joinEvent: (id, data) => request(`/events/${id}/join`, { method: "POST", body: JSON.stringify(data) }),
  getEventParticipants: (id) => request(`/events/${id}/participants`),

  // Matching
  runMatching: (eventId) => request(`/matching/events/${eventId}/run`, { method: "POST" }),

  // Teams & Blueprint
  getEventTeams: (eventId) => request(`/teams/events/${eventId}`),
  getTeamBlueprint: (teamId) => request(`/teams/${teamId}`),
  publishTeam: (teamId) => request(`/teams/${teamId}/publish`, { method: "POST" }),
  publishAllTeams: (eventId) => request(`/teams/events/${eventId}/publish-all`, { method: "POST" }),
  withdrawMember: (teamId, userId) => request(`/teams/${teamId}/withdraw/${userId}`, { method: "POST" }),
  getReplacementCandidates: (teamId) => request(`/teams/${teamId}/replacement-candidates`),
  approveReplacement: (teamId, userId) => request(`/teams/${teamId}/approve-replacement/${userId}`, { method: "POST" }),

  // Gamification
  getDailyChallenge: () => request("/gamification/daily-challenge"),
  submitDailyChallenge: (selectedIndex) => request("/gamification/daily-challenge/submit", { method: "POST", body: JSON.stringify({ selected_index: selectedIndex }) }),
  getStreak: () => request("/gamification/streak"),
  getBadges: () => request("/gamification/badges"),

  // Feedback
  submitFeedback: (data) => request("/feedback", { method: "POST", body: JSON.stringify(data) }),
  getEventFeedback: (eventId) => request(`/feedback/events/${eventId}`),

  // Demo
  seedDemo: () => request("/demo/seed", { method: "POST" }),
  health: () => request("/health"),
};
