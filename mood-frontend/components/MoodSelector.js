import { useState } from "react";
import { postMood } from "../lib/api";

const MOODS = [
  { level: "LOW",    emoji: "😔", label: "Low" },
  { level: "MEDIUM", emoji: "😐", label: "Medium" },
  { level: "HIGH",   emoji: "😄", label: "High" },
];

export default function MoodSelector({ current, onChange }) {
  const [saving, setSaving] = useState(false);
  const [error, setError]   = useState("");

  async function select(level) {
    if (saving) return;
    setSaving(true);
    setError("");
    try {
      await postMood(level);
      onChange(level);
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="card">
      <p className="section-title">How are we feeling today?</p>
      <div className="mood-pills">
        {MOODS.map((m) => (
          <button
            key={m.level}
            className={`mood-pill${current === m.level ? " active" : ""}`}
            onClick={() => select(m.level)}
            disabled={saving}
          >
            <span className="emoji">{m.emoji}</span>
            {m.label}
          </button>
        ))}
      </div>
      {error && <p className="error" style={{ marginTop: 8 }}>{error}</p>}
    </div>
  );
}
