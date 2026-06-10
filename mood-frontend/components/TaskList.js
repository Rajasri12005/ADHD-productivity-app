import { useState } from "react";
import { createTask } from "../lib/api";
import TaskItem from "./TaskItem";

export default function TaskList({ tasks, setTasks }) {
  const [title, setTitle]         = useState("");
  const [difficulty, setDifficulty] = useState("MEDIUM");
  const [adding, setAdding]       = useState(false);
  const [error, setError]         = useState("");

  async function handleAdd(e) {
    e.preventDefault();
    if (!title.trim()) return;
    setAdding(true);
    setError("");
    try {
      const task = await createTask(title.trim(), difficulty);
      setTasks((prev) => [task, ...prev]);
      setTitle("");
    } catch (err) {
      setError(err.message);
    } finally {
      setAdding(false);
    }
  }

  function handleComplete(id) {
    setTasks((prev) =>
      prev.map((t) => (t.id === id ? { ...t, is_completed: true } : t))
    );
  }

  function handleDelete(id) {
    setTasks((prev) => prev.filter((t) => t.id !== id));
  }

  const active    = tasks.filter((t) => !t.is_completed);
  const completed = tasks.filter((t) => t.is_completed);

  return (
    <div className="card" style={{ gridColumn: "1 / -1" }}>
      <p className="section-title">My tasks</p>

      <form className="add-form" onSubmit={handleAdd}>
        <input
          placeholder="Add a new task…"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />
        <select value={difficulty} onChange={(e) => setDifficulty(e.target.value)}>
          <option value="EASY">Easy</option>
          <option value="MEDIUM">Medium</option>
          <option value="HARD">Hard</option>
        </select>
        <button className="btn-primary" type="submit" disabled={adding} style={{ whiteSpace: "nowrap" }}>
          {adding ? "…" : "Add"}
        </button>
      </form>
      {error && <p className="error">{error}</p>}

      <div style={{ marginTop: 16 }}>
        {active.length === 0 && completed.length === 0 && (
          <p style={{ color: "var(--muted)", fontSize: 13 }}>No tasks yet. Add one above.</p>
        )}
        {active.map((t) => (
          <TaskItem key={t.id} task={t} onComplete={handleComplete} onDelete={handleDelete} />
        ))}
        {completed.length > 0 && (
          <>
            <p className="section-title" style={{ marginTop: 16 }}>Completed</p>
            {completed.map((t) => (
              <TaskItem key={t.id} task={t} showComplete={false} />
            ))}
          </>
        )}
      </div>
    </div>
  );
}
