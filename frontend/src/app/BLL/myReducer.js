import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import { getMe } from "../../shared/api/me";


export const fetchMe = createAsyncThunk("me/fetchMe", async (_, { rejectWithValue }) => {
  try {
    const user = await getMe();
    return user;
  } catch (e) {
    return rejectWithValue(e?.message || "Failed to load profile");
  }
});

const initialState = {
  user: null,
  status: "idle", // idle | loading | succeeded | failed
  error: null,
};

const meSlice = createSlice({
  name: "me",
  initialState,
  reducers: {
    clearMe(state) {
      state.user = null;
      state.status = "idle";
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchMe.pending, (state) => {
        state.status = "loading";
        state.error = null;
      })
      .addCase(fetchMe.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.user = action.payload;
      })
      .addCase(fetchMe.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.payload || "Failed";
      });
  },
});

export const { clearMe } = meSlice.actions;
export default meSlice.reducer;

export const selectMeUser = (state) => state?.me ?? null;
export const selectMeStatus = (s) => s?.me?.status ?? null;
export const selectMeError = (s) => s?.me.error?.status ?? null;