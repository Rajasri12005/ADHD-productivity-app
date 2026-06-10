import { useEffect, useState } from "react";
import { useRouter } from "next/router";
import { getTodayMood, getTasks, getRecommended, getStreak } from "../lib/api";
import ADHDTips from "../components/ADHDTips";
import BoostTasks from "../components/BoostTasks";
import ProgressChart from "../components/ProgressChart";
import MoodSelector from "../components/MoodSelector";
import StreakDisplay from "../components/StreakDisplay";
import TaskList from "../components/TaskList";
import RecommendedTasks from "../components/RecommendedTasks";

export default function Dashboard() {
  const router = useRouter();

  const [mood,        setMood]        = useState(null);
  const [tasks,       setTasks]       = useState([]);
  const [recommended, setRecommended] = useState([]);
  const [streak,      setStreak]      = useState(null);
  const [loading,     setLoading]     = useState(true);

  useEffect(() => {
    if (!localStorage.getItem("token")) { router.replace("/login"); return; }
    loadAll();
  }, []);

  async function loadAll() {
    setLoading(true);
    try {
      const [tasksData, streakData] = await Promise.all([
        getTasks(),
        getStreak(),
      ]);
      setTasks(tasksData);
      setStreak(streakData);

      // Mood may 404 if not set yet
      try {
        const moodData = await getTodayMood();
        setMood(moodData.mood_level);
      } catch { /* no mood today */ }

      // Recommendations always available
      try {
        const recData = await getRecommended();
        setRecommended(recData);
      } catch { /* ignore */ }
    } catch (err) {
      if (err.message === "Invalid token" || err.message === "User not found") {
        localStorage.removeItem("token");
        router.replace("/login");
      }
    } finally {
      setLoading(false);
    }
  }

  async function handleMoodChange(level) {
    setMood(level);
    // Refresh recommendations after mood change
    try {
      const recData = await getRecommended();
      setRecommended(recData);
    } catch { /* ignore */ }
  }

  async function handleTaskComplete(id) {
    setTasks((prev) =>
      prev.map((t) => (t.id === id ? { ...t, is_completed: true } : t))
    );
    setRecommended((prev) =>
      prev.map((t) => (t.id === id ? { ...t, is_completed: true } : t))
    );
    // Refresh streak
    try {
      const s = await getStreak();
      setStreak(s);
    } catch { /* ignore */ }
  }

  function logout() {
    localStorage.removeItem("token");
    router.push("/login");
  }

  if (loading) {
    return (
      <div className="auth-wrap">
        <p style={{ color: "var(--muted)" }}>Loading…</p>
      </div>
    );
  }

  return (
    <div className="dash-wrap">
      <div className="dash-header">
        <h1>Good day 👋</h1>
        <button className="btn-ghost" onClick={logout}>Log out</button>
      </div>

      <div className="dash-grid">
        {/* Row 1: Mood + Streak */}
        <MoodSelector current={mood} onChange={handleMoodChange} />
        <StreakDisplay streak={streak} />

        {/* Row 2: Recommended */}
        <RecommendedTasks tasks={recommended} onComplete={handleTaskComplete} />

        {/* Row 3: Task list — full width */}
        <TaskList tasks={tasks} setTasks={setTasks} />
	<ProgressChart />
	<BoostTasks />
	<ADHDTips />
      </div>
    </div>
  );
}
