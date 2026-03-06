import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { fetchMe, selectMeError, selectMeStatus, selectMeUser } from "../../app/BLL/myReducer"; 

export function useMe({ auto = true } = {}) {
  const dispatch = useDispatch();
  const user = useSelector(selectMeUser);
  const status = useSelector(selectMeStatus);
  const error = useSelector(selectMeError);

  useEffect(() => {
    if (!auto) return;
    if (status === "idle") dispatch(fetchMe());
  }, [auto, status, dispatch]);

  return { user, status, error, refetch: () => dispatch(fetchMe()) };
}