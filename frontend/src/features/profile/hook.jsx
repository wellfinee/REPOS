// src/features/user-profile/hooks.js
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getUserProfile, searchUsers, patchUserAdmin } from "../../shared/api/user";
import { patchStudentAdmin } from "../../shared/api/student";
import { listClasses } from "../../shared/api/classes";

export function useUserProfile(userId) {
  return useQuery({
    queryKey: ["user-profile", userId],
    queryFn: () => getUserProfile(userId),
    enabled: !!userId,
    staleTime: 30_000,
  });
}

export function useUserSearch() {
  return useMutation({
    mutationFn: (args) => searchUsers(args),
  });
}

export function usePatchUserAdmin(userId) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ payload }) => patchUserAdmin(userId, payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["user-profile", userId] });
    },
  });
}

export function usePatchStudentAdmin(userId) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ studentId, payload }) => patchStudentAdmin(studentId, payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["user-profile", userId] });
    },
  });
}

export function useClassSearch() {
  return useMutation({
    mutationFn: (args) => listClasses(args),
  });
}