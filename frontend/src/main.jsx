import React from "react";
import ReactDOM from "react-dom/client";

import { Provider } from "react-redux";
import { StrictMode } from "react";
import App from "./App";
import { RouterProvider } from "react-router-dom";
import { router } from "./app/router/router";

import { store } from "./app/BLL/store";
import { hydrateAuth } from "./app/BLL/authReducer";
import { useEffect } from "react";
import QueryProvider from "./app/providers/tanstack";



ReactDOM.createRoot(document.getElementById('root')).render(
  <StrictMode>
    <QueryProvider>
      <Provider store={store}>
        <App />
      </Provider>
    </QueryProvider>
  </StrictMode>
)
