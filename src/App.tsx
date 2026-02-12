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

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "https://dayanch.pythonanywhere.com";
const PROFILE_ENDPOINT = `${API_BASE_URL}/api/profile/`;

interface Profile {
	id: number;
	name: string;
	role: string;
	subtitle: string;
	summary: string;
	email: string;
	github: string;
	linkedin: string;
	avatar_url: string | null;
	avatar_urls: {
		original: string | null;
		icon: string | null;
		normal: string | null;
		large: string | null;
	} | null;
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

interface SkillUrls {
	original: string | null;
	icon: string | null;
	normal: string | null;
	large: string | null;
}

interface SkillItem {
	id: number;
	name: string;
	description: string;
	order: number;
	photo_urls: SkillUrls | null;
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

interface ApiPhotoUrls {
	original?: string | null;
	icon?: string | null;
	normal?: string | null;
	large?: string | null;
}

interface ApiSkillItem {
	id: number;
	name: string;
	description: string;
	order: number;
	photo?: ApiPhotoUrls | null;
	photo_urls?: ApiPhotoUrls | null;
}

interface ApiProject {
	id: number;
	title: string;
	description: string;
	technologies: string;
	github_url: string;
	live_url: string;
	image?: string | null;
	image_url?: string | null;
	is_featured: boolean;
	created_at: string;
}

interface ApiProfile {
	id: number;
	name: string;
	role: string;
	subtitle: string;
	summary: string;
	email: string;
	github: string;
	linkedin: string;
	avatar?: string | ApiPhotoUrls | null;
	avatar_url?: string | null;
	avatar_urls?: ApiPhotoUrls | null;
	stats: Stat[];
	education: EducationItem[];
	skills: ApiSkillItem[];
	projects: ApiProject[];
}

const normalizeAvatarUrl = (avatar?: string | ApiPhotoUrls | null, avatarUrls?: ApiPhotoUrls | null) => {
	if (typeof avatar === "string") {
		return resolveMediaUrl(avatar);
	}

	if (avatar && typeof avatar === "object") {
		return resolveMediaUrl(avatar.normal ?? avatar.original ?? avatar.icon ?? avatar.large ?? null);
	}

	return resolveMediaUrl(avatarUrls?.normal ?? avatarUrls?.original ?? avatarUrls?.icon ?? avatarUrls?.large ?? null);
};

const resolveMediaUrl = (url?: string | null | unknown) => {
	if (typeof url !== "string" || !url) return null;
	if (url.startsWith("http://") || url.startsWith("https://")) {
		return url;
	}
	return `${API_BASE_URL}${url}`;
};

const normalizePhotoUrls = (photo?: ApiPhotoUrls | null): SkillUrls | null => {
	if (!photo) return null;
	return {
		original: resolveMediaUrl(photo.original) ?? null,
		icon: resolveMediaUrl(photo.icon) ?? null,
		normal: resolveMediaUrl(photo.normal) ?? null,
		large: resolveMediaUrl(photo.large) ?? null,
	};
};

const normalizeProfile = (apiProfile: ApiProfile): Profile => {
	const avatarUrl = normalizeAvatarUrl(apiProfile.avatar ?? apiProfile.avatar_url ?? null, apiProfile.avatar_urls ?? null);

	return {
		id: apiProfile.id,
		name: apiProfile.name,
		role: apiProfile.role,
		subtitle: apiProfile.subtitle,
		summary: apiProfile.summary,
		email: apiProfile.email,
		github: apiProfile.github,
		linkedin: apiProfile.linkedin,
		avatar_url: avatarUrl,
		avatar_urls: apiProfile.avatar_urls ? normalizePhotoUrls(apiProfile.avatar_urls) : null,
		stats: apiProfile.stats,
		education: apiProfile.education,
		skills: apiProfile.skills.map((skill) => ({
			id: skill.id,
			name: skill.name,
			description: skill.description,
			order: skill.order,
			photo_urls: normalizePhotoUrls(skill.photo ?? skill.photo_urls),
		})),
		projects: apiProfile.projects.map((project) => ({
			id: project.id,
			title: project.title,
			description: project.description,
			technologies: project.technologies,
			github_url: project.github_url,
			live_url: project.live_url,
			image_url: resolveMediaUrl(project.image_url ?? project.image) ?? "",
			is_featured: project.is_featured,
			created_at: project.created_at,
		})),
	};
};

function App() {
	const [chatOpen, setChatOpen] = useState(false);
	const [darkMode, setDarkMode] = useState(true);
	const [profile, setProfile] = useState<Profile | null>(null);
	const [loading, setLoading] = useState(true);

	useEffect(() => {
		const fetchProfile = async () => {
			try {
				const response = await fetch(PROFILE_ENDPOINT);
				if (!response.ok) {
					throw new Error(`Failed to fetch profile: ${response.status}`);
				}
				const data = (await response.json()) as ApiProfile;
				setProfile(normalizeProfile(data));
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
