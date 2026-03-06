// src/shared/http/user.js
import {http} from "./http"; // или как у тебя axios instance

export async function getUserProfile(userId) {
  const { data } = await http.get(`/api/users/${userId}/`);
  return data;
}

export async function searchUsers(args) {
  const { data } = await http.get(`/api/users/search/`, { params: args });
  return data;
}

export async function patchUserAdmin(userId, payload) {
  const { data } = await http.patch(`/api/students/${userId}/`, payload);
  return data;
}

