interface StatsItem {
  value: string;
  label: string;
}

interface HeroContentProps {
  stats: StatsItem[];
}

export default function HeroContent({ stats }: HeroContentProps) {
  return (
    <div className="hero__content">
      <p className="eyebrow">Backend Engineer</p>
      <h1>Dayanch Salarov</h1>
      <p className="subtitle">
        Building secure, scalable platforms with Django & Python.
      </p>
      <p className="summary">
        I deliver production-ready backend systems, clean APIs, and
        data-driven solutions. I collaborate closely with product teams to
        ship reliable software that users love.
      </p>
      <div className="hero__actions">
        <a className="btn btn--primary" href="#education">Explore</a>
        <a className="btn btn--ghost" href="#skills">View Skills</a>
      </div>
      <div className="stats">
        {stats.map((stat, index) => (
          <div key={index}>
            <h3>{stat.value}</h3>
            <p>{stat.label}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
