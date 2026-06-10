export default function StreakDisplay({ streak }) {
  const count = streak?.current_streak ?? 0;
  const last  = streak?.last_active_date;

  return (
    <div className="card" style={{ textAlign: "center" }}>
      <p className="section-title">Current streak</p>
      <div className="streak-num">{count}</div>
      <p className="streak-label">
        {count === 0
          ? "Complete a task to start your streak"
          : count === 1
          ? "day — keep going!"
          : `days in a row 🔥`}
      </p>
      {last && (
        <p style={{ fontSize: 12, color: "var(--muted)", marginTop: 8 }}>
          Last active: {new Date(last).toLocaleDateString()}
        </p>
      )}
    </div>
  );
}
