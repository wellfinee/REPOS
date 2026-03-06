// src/shared/api/student.js
import { http } from "./http";

export async function patchStudentAdmin(studentId, payload) {
  const { data } = await http.patch(`/api/students/${studentId}/`, payload);
  return data;
}