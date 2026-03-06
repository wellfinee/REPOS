import { useEffect } from "react";
import { RouterProvider } from "react-router-dom";
import { useDispatch, useSelector } from "react-redux";
import { router } from "./app/router/router";
import "./App.css"
import {
  hydrateAuth,
  fetchMe,
  selectAuthHydrated,
  selectAccessToken,
  selectMe,
} from "./app/BLL/authReducer";

function App() {
  const dispatch = useDispatch();
  const hydrated = useSelector(selectAuthHydrated);
  const accessToken = useSelector(selectAccessToken);
  const me = useSelector(selectMe);

  useEffect(() => {
    dispatch(hydrateAuth());
  }, [dispatch]);

  useEffect(() => {
    if (!hydrated) return;
    if (accessToken && !me) dispatch(fetchMe());
  }, [hydrated, accessToken, me, dispatch]);

  return <RouterProvider router={router} />;
}

export default App;