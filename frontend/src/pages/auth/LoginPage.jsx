import { loginSchema } from "./schemas/login";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm, FormProvider } from "react-hook-form";
import "./login.css";
import { login as loginThunk} from "../../app/BLL/authReducer";
import { useDispatch, useSelector } from "react-redux";
import Input from "../../components/input-hook-form/Input";
import Button from "../../components/buttons/Button";
import { useMemo } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useEffect } from "react";

import { getSafeRedirect, DEFAULT_AFTER_LOGIN } from "../../shared/lib/authRedirect";

export default function LoginPage() {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const location = useLocation();

  const hydrated = useSelector((s) => s.auth?.hydrated);
  const accessToken = useSelector((s) => s.auth?.accessToken);

  // Вычисляем "куда возвращать" один раз
  const redirectTo = useMemo(() => {
    return getSafeRedirect(location.state?.from, {
      fallback: DEFAULT_AFTER_LOGIN,
      blockedPrefixes: ["/login", "/register", "/forgot-password", "/auth"],
    });
  }, [location.state]);

  const methods = useForm({
    resolver: zodResolver(loginSchema),
    mode: "onChange",
    reValidateMode: "onChange",
    defaultValues: {
      email: "",
      password: "",
      rememberMe: false,
    },
    shouldFocusError: true,
  });

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting, isValid, isDirty },
  } = methods;

 useEffect(() => {
    if (hydrated && accessToken) {
      navigate(DEFAULT_AFTER_LOGIN, { replace: true });
    }
  }, [hydrated, accessToken, navigate]);

  // Рендерим пока идёт гидрация или если нет токена
  if (hydrated && accessToken) {
    return null; // или loader
  }
  const onSubmit = async (data) => {
    const action = await dispatch(
      loginThunk({
        email: data.email,
        password: data.password,
        rememberMe: data.rememberMe,
      })
    );

    // Только если логин успешен — редирект
    if (loginThunk.fulfilled.match(action)) {
      navigate(redirectTo, { replace: true });
    } else {
      // тут можно показать toast, но не обязательно
      console.error("Login failed:", action.payload || action.error);
    }
  };

  return (
    <section className="login">
      <h1 className="login__title">Войдите в систему</h1>

      <FormProvider {...methods}>
        <form className="login__form" onSubmit={handleSubmit(onSubmit)} noValidate>
          <Input type="email" name="email" autoComplete="email" className="login__input" />
          {errors.email && <p className="login__error">{errors.email.message}</p>}

          <Input
            type="password"
            name="password"
            autoComplete="current-password"
            className="login__input"
          />
          {errors.password && <p className="login__error">{errors.password.message}</p>}

          <label className="login__remember">
            <input type="checkbox" {...register("rememberMe")} />
            Запомнить меня
          </label>

          <Button
            type="submit"
            disabled={!isValid || !isDirty || isSubmitting}
            text={isSubmitting ? "Входим..." : "Войти"}
          />
        </form>
      </FormProvider>
    </section>
  );
}