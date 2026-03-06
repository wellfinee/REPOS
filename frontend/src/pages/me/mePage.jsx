import React from "react";
import { useMe } from "../../features/me/useMe";
import "./me.css"
import UserHeader from "./../../components/headers/UserHeader";
import WalletCard from "./../../components/WalletCard";
import ProfilesBlock from "./../../components/ProfilesBlock";
import AchievementsList from "./../../components/AchivmentList";

export default function MePage() {
  let { user, status, error, refetch } = useMe();

  if (status === "loading") return <div style={{ padding: 16 }}>Загрузка профиля…</div>;
  useEffect(() => {
    if (status === "failed") {
      refetch();
    }
  }, [status]);/*  */
  if (!user) return <div style={{ padding: 16 }}>Нет данных профиля</div>;

  return (
    <div style={{ padding: 16, display: "grid", gap: 12 }}>
      <UserHeader user={user} />

      <div className="profile__line">
        <WalletCard wallet={user.wallet} />
        <ProfilesBlock profiles={user.profiles} currentEnrollment={user.current_enrollment} />
      </div>



      <AchievementsList achievements={user.achievements} />
    </div>
  );
}