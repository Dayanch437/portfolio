import { useEffect, useState } from "react";
import "./App.css";
import Navigation from "./components/Navigation";
import Avatar from "./components/Avatar";
import HeroContent from "./components/HeroContent";
import Education from "./components/Education";
import Skills from "./components/Skills";
import ChatWidget from "./components/ChatWidget";
import ContactForm from "./components/ContactForm";
import Footer from "./components/Footer";

interface Profile {
	id: number;
	name: string;
	role: string;
	subtitle: string;
	summary: string;
	email: string;
	github: string;
	linkedin: string;
	avatar_url: string;
	stats: Stat[];
	education: EducationItem[];
	skills: SkillItem[];
	projects: Project[];
}

interface Stat {
	id: number;
	value: string;
	label: string;
	order: number;
}

interface EducationItem {
	id: number;
	degree: string;
	institution: string;
	year: string;
	gpa: string;
	details: string;
	order: number;
}

interface SkillItem {
	id: number;
	name: string;
	description: string;
	order: number;
	photo: string | null;
	photo_url: string | null;
}

interface Project {
	id: number;
	title: string;
	description: string;
	technologies: string;
	github_url: string;
	live_url: string;
	image_url: string;
	is_featured: boolean;
	created_at: string;
}

function App() {
	const [chatOpen, setChatOpen] = useState(false);
	const [darkMode, setDarkMode] = useState(true);
	const [profile, setProfile] = useState<Profile | null>(null);
	const [loading, setLoading] = useState(true);

	useEffect(() => {
		const fetchProfile = async () => {
			try {
				const response = await fetch("http://213.21.235.119/api/profile/");
				const data = await response.json();
				setProfile(data);
			} catch (error) {
				console.error("Failed to fetch profile:", error);
			} finally {
				setLoading(false);
			}
		};

		fetchProfile();
	}, []);

	if (loading) {
		return <div className="page dark-mode" style={{ display: "grid", placeItems: "center", minHeight: "100vh" }}>Loading...</div>;
	}

	if (!profile) {
		return <div className="page dark-mode" style={{ display: "grid", placeItems: "center", minHeight: "100vh" }}>Failed to load profile</div>;
	}

	return (
		<div className={`page ${darkMode ? "dark-mode" : "light-mode"}`}>
			<header className="hero">
				<Navigation darkMode={darkMode} onThemeToggle={() => setDarkMode(!darkMode)} />
				<div className="hero__grid hero__grid--center">
					<div>
						<Avatar imageUrl={profile.avatar_url} altText={profile.name} />
						<HeroContent stats={profile.stats} />
					</div>
				</div>
			</header>

			<main>
				<Education items={profile.education} />
				<Skills skills={profile.skills} />
				<ContactForm />
			</main>

			<Footer />

			<ChatWidget
				isOpen={chatOpen}
				onToggle={() => setChatOpen(!chatOpen)}
			/>
		</div>
	);
}

export default App;
