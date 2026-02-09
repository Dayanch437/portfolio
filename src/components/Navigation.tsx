interface NavigationProps {
  darkMode: boolean;
  onThemeToggle: () => void;
}

export default function Navigation({ onThemeToggle }: NavigationProps) {
  return (
    <nav className="nav">
      <div className="nav__links">
        <a href="#education">Education</a>
        <a href="#skills">Skills</a>
      </div>
      <button
        className="theme-toggle"
        onClick={onThemeToggle}
        aria-label="Toggle dark mode"
      />
    </nav>
  );
}
