import { z } from "zod";

export const loginSchema = z.object({
    email: z
    .string()
    .trim()
    .min(1, "Email не может быть пустым")
    .email("Некорректный формат email"),
    password: z
    .string()
    .trim()
    .min(1, "Пароль не может быть пустым")
    .min(8, "Пароль должен быть не менее 8 символов")
    .max(20, "Пароль должен быть не более 20 символов"),
    rememberMe: z.boolean().optional()

})