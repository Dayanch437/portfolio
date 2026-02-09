interface SkillItem {
  id: number;
  name: string;
  description: string;
  order: number;
  photo: string | null;
  photo_url: string | null;
}

interface SkillsProps {
  skills: SkillItem[];
}

export default function Skills({ skills }: SkillsProps) {
  return (
    <section id="skills" className="section section--alt">
      <div className="section__header">
        <h2>Skills</h2>
        <p>Technologies I use to build production-ready backends.</p>
      </div>
      <div className="skills">
        {skills.map((skill) => (
          <div key={skill.id} className="skill">
            {skill.photo_url && (
              <img src={skill.photo_url} alt={skill.name} className="skill__image" />
            )}
            <h4>{skill.name}</h4>
            <p>{skill.description}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
