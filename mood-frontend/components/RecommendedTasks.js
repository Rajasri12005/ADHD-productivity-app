import TaskItem from "./TaskItem";

export default function RecommendedTasks({ tasks, onComplete }) {
  if (!tasks || tasks.length === 0) {
    return (
      <div className="card">
        <p className="section-title">Recommended</p>
        <p style={{ color: "var(--muted)", fontSize: 13 }}>
          Log your mood to get personalised recommendations.
        </p>
      </div>
    );
  }

  return (
    <div className="card">
      <p className="section-title">Recommended for you</p>
      {tasks.map((t, i) => (
        <TaskItem
          key={t.id ?? i}
          task={t}
          onComplete={onComplete}
          onDelete={null}
          showComplete={!t.is_completed && !!t.id}
        />
      ))}
    </div>
  );
}
