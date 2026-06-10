const DIFFICULTIES = ["EASY", "MEDIUM", "HARD"];

const COLORS = {
  EASY:   { fill: "var(--accent)",    bg: "var(--accent-lt)" },
  MEDIUM: { fill: "#A07030",          bg: "#FFF8EC" },
  HARD:   { fill: "#B04030",          bg: "#FFF0EE" },
};

function bar(tasks, difficulty) {
  const all  = tasks.filter((t) => t.difficulty === difficulty);
  const done = all.filter((t) => t.is_completed);
  const pct  = all.length ? Math.round((done.length / all.length) * 100) : 0;
  return { total: all.length, done: done.length, pct };
}

export default function ProgressChart({ tasks }) {
  const total    = tasks.length;
  const completed = tasks.filter((t) => t.is_completed).length;
  const overallPct = total ? Math.round((completed / total) * 100) : 0;

  return (
    <div className="card">
      <p className="section-title">Progress</p>

      {/* Overall */}
      <div className="prog-overall">
        <div className="prog-overall-row">
          <span className="prog-label">Overall</span>
          <span className="prog-frac">{completed}/{total}</span>
        </div>
        <div className="prog-track" style={{ background: "#EEEAE0" }}>
          <div
            className="prog-fill"
            style={{ width: `${overallPct}%`, background: "var(--accent)" }}
          />
        </div>
      </div>

      {/* By difficulty */}
      <div className="prog-rows">
        {DIFFICULTIES.map((d) => {
          const { total: t, done, pct } = bar(tasks, d);
          const col = COLORS[d];
          return (
            <div key={d} className="prog-row">
              <span className="prog-label" style={{ color: col.fill }}>
                {d[0] + d.slice(1).toLowerCase()}
              </span>
              <div className="prog-track" style={{ background: col.bg }}>
                <div
                  className="prog-fill"
                  style={{ width: `${pct}%`, background: col.fill }}
                />
              </div>
              <span className="prog-frac">{done}/{t}</span>
            </div>
          );
        })}
      </div>

      {total === 0 && (
        <p style={{ color: "var(--muted)", fontSize: 13, marginTop: 8 }}>
          Add tasks to see progress.
        </p>
      )}
    </div>
  );
}
