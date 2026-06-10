import { useState } from "react";
import { completeTask, deleteTask } from "../lib/api";

export default function TaskItem({ task, onComplete, onDelete, showComplete = true }) {
  const [busy, setBusy] = useState(false);

  async function handleComplete() {
    setBusy(true);
    try {
      await completeTask(task.id);
      onComplete && onComplete(task.id);
    } finally {
      setBusy(false);
    }
  }

  async function handleDelete() {
    setBusy(true);
    try {
      await deleteTask(task.id);
      onDelete && onDelete(task.id);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="task-item">
      <span className={`task-title${task.is_completed ? " done" : ""}`}>
        {task.title}
      </span>
      <span className={`diff-badge ${task.difficulty}`}>{task.difficulty}</span>
      {!task.is_completed && showComplete && (
        <button
          className="btn-primary"
          style={{ padding: "4px 12px", fontSize: 12 }}
          onClick={handleComplete}
          disabled={busy}
        >
          ✓
        </button>
      )}
      {task.id && !task.is_completed && (
        <button
          className="btn-ghost"
          style={{ padding: "4px 10px", fontSize: 12 }}
          onClick={handleDelete}
          disabled={busy}
        >
          ✕
        </button>
      )}
    </div>
  );
}
