import { useState } from "react";

const BOOST_TASKS = [
  { id: 1, text: "Drink a full glass of water", time: "1 min" },
  { id: 2, text: "Step outside for 5 minutes", time: "5 min" },
  { id: 3, text: "Write down one thing on your mind", time: "2 min" },
  { id: 4, text: "Do 10 slow deep breaths", time: "2 min" },
  { id: 5, text: "Stretch your neck and shoulders", time: "2 min" },
  { id: 6, text: "Clear one thing off your desk", time: "3 min" },
];

export default function BoostTasks({ mood, taskCount }) {
  const [done, setDone] = useState({});

  const show = mood === "LOW" || taskCount === 0;
  if (!show) return null;

  function toggle(id) {
    setDone((prev) => ({ ...prev, [id]: !prev[id] }));
  }

  const completed = Object.values(done).filter(Boolean).length;

  return (
    <div className="card boost-card">
      <p className="section-title">⚡ Quick wins</p>
      <p className="boost-sub">
        {mood === "LOW"
          ? "Feeling low — start tiny. Each one counts."
          : "No tasks yet — try one of these to get moving."}
      </p>

      <div className="boost-progress-row">
        <div className="boost-bar-track">
          <div
            className="boost-bar-fill"
            style={{ width: `${(completed / BOOST_TASKS.length) * 100}%` }}
          />
        </div>
        <span className="boost-count">{completed}/{BOOST_TASKS.length}</span>
      </div>

      <div className="boost-list">
        {BOOST_TASKS.map((t) => (
          <div key={t.id} className={`boost-item${done[t.id] ? " done" : ""}`}>
            <button
              className="boost-check"
              onClick={() => toggle(t.id)}
              aria-label="Mark done"
            >
              {done[t.id] ? "✓" : ""}
            </button>
            <span className="boost-text">{t.text}</span>
            <span className="boost-time">{t.time}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
