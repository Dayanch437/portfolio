interface TimelineItem {
  id: number;
  degree: string;
  institution: string;
  year: string;
  gpa: string;
  details?: string;
  order: number;
}

interface EducationProps {
  items: TimelineItem[];
}

export default function Education({ items }: EducationProps) {
  return (
    <section id="education" className="section">
      <div className="section__header">
        <h2>Education</h2>
        <p>My academic background and learning journey.</p>
      </div>
      <div className="timeline">
        {items.map((item) => (
          <div key={item.id} className="timeline__item">
            <div>
              <h3>{item.degree}</h3>
              <p className="muted">{item.institution}</p>
              {item.gpa && (
                <p className="muted" style={{ fontSize: "0.85rem", marginTop: "0.5rem" }}>
                  GPA: {item.gpa}
                </p>
              )}
              {item.details && (
                <p className="muted" style={{ fontSize: "0.85rem", marginTop: "0.5rem" }}>
                  {item.details}
                </p>
              )}
            </div>
            <span className="pill">{item.year}</span>
          </div>
        ))}
      </div>
    </section>
  );
}
