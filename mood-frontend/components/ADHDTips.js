import { useState } from "react";

const TIPS = [
  { icon: "🎯", tip: "Body double: work alongside someone (video call counts)." },
  { icon: "⏱️", tip: "Use a 25-min timer. Stop when it rings — no exceptions." },
  { icon: "📝", tip: "Brain-dump everything onto paper before starting." },
  { icon: "🔀", tip: "Switch tasks every 25 min if you feel stuck — momentum matters." },
  { icon: "🔕", tip: "Put your phone in another room, not just face-down." },
  { icon: "🌊", tip: "Ride the hyperfocus wave — schedule admin after, not during." },
  { icon: "✅", tip: "Break tasks into the smallest possible first step." },
  { icon: "💧", tip: "Dehydration tanks focus fast. Keep water visible on your desk." },
];

export default function ADHDTips() {
  const [open, setOpen] = useState(false);
  const [current, setCurrent] = useState(
    () => Math.floor(Math.random() * TIPS.length)
  );

  return (
    <div className="card">
      <div className="tips-header" onClick={() => setOpen((o) => !o)}>
        <p className="section-title" style={{ margin: 0 }}>🧠 ADHD tips</p>
        <span className="tips-toggle">{open ? "▲" : "▼"}</span>
      </div>

      {!open && (
        <div className="tip-spotlight">
          <span className="tip-icon">{TIPS[current].icon}</span>
          <p className="tip-text">{TIPS[current].tip}</p>
          <button
            className="btn-ghost"
            style={{ fontSize: 11, padding: "3px 10px", marginTop: 10 }}
            onClick={(e) => {
              e.stopPropagation();
              setCurrent((c) => (c + 1) % TIPS.length);
            }}
          >
            Next tip →
          </button>
        </div>
      )}

      {open && (
        <ul className="tips-list">
          {TIPS.map((t, i) => (
            <li key={i} className="tips-item">
              <span>{t.icon}</span>
              <span>{t.tip}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
