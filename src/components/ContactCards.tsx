interface ContactCard {
  title: string;
  items?: string[];
  description?: string;
  isAccent?: boolean;
  showButton?: boolean;
}

interface ContactCardsProps {
  cards: ContactCard[];
}

export default function ContactCards({ cards }: ContactCardsProps) {
  return (
    <div className="hero__card">
      {cards.map((card, index) => (
        <div
          key={index}
          className={`card ${card.isAccent ? "card--accent" : ""}`}
          id={card.isAccent ? "contact" : undefined}
        >
          <h3>{card.title}</h3>
          {card.items && (
            <ul>
              {card.items.map((item, i) => (
                <li key={i}>{item}</li>
              ))}
            </ul>
          )}
          {card.description && <p>{card.description}</p>}
          {card.showButton && (
            <a className="btn btn--primary" href="#contact-form">
              Message me
            </a>
          )}
        </div>
      ))}
    </div>
  );
}
