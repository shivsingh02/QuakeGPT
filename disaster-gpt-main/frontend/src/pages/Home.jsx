import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
	getRedirectResult,
	GoogleAuthProvider,
	signInWithRedirect,
} from "firebase/auth";
import { auth, logout } from "../firebaseConfig";

import DarkMode from "../components/DarkMode";
import Styles from "./Home.module.css";

export default function Home(props) {
	const { darkMode, setDarkMode } = props;

	const [loading, setLoading] = useState(false);

	const googleSignIn = () => {
		signInWithRedirect(auth, new GoogleAuthProvider()).catch((error) => {
			const errorMessage = error.message;
			alert(errorMessage + " Please try again");
		});
	};
	useEffect(() => {
		setLoading(true);
		getRedirectResult(auth)
			.then((result) => {
				if (!result) return;
				alert("Logged in");
				// This gives you a Google Access Token. You can use it to access the Google API.
				const credential =
					GoogleAuthProvider.credentialFromResult(result);
				const token = credential.accessToken;
				const user = result.user;
			})
			.catch((error) => {
				const errorMessage = error.message;
				alert(errorMessage + " Please try again");
			})
			.finally(() => {
				setLoading(false);
			});
	}, []);

	return (
		<div
			className={
				Styles["container"] + ` ${darkMode ? Styles["dark"] : ""}`
			}
		>
			<img
				src={"android-chrome-512x512.png"}
				alt="logo"
				height={200}
				width={200}
			/>
			<br />
			<div className={Styles["user-box"]}>
				{auth.currentUser && (
					<img
						src={auth.currentUser.photoURL}
						alt="logo"
						height={50}
						width={50}
					/>
				)}
				<h1>
					Welcome{" "}
					{auth.currentUser ? auth.currentUser.displayName : "Guest"}
				</h1>
			</div>
			<br />
			<p>
				Disaster GPT - A chatbot that can talk about any natural
				disaster.
			</p>
			<br />
			{auth.currentUser ? (
				<>
					<Link to="/chat/new">
						<button>New Chat</button>
					</Link>
					<button onClick={logout}>Sign out</button>
				</>
			) : loading ? (
				<p>Loading...</p>
			) : (
				<button
					onClick={() => {
						googleSignIn();
					}}
				>
					<img src="https://img.icons8.com/color/48/000000/google-logo.png" />
					Sign in with Google
				</button>
			)}
			<DarkMode darkMode={darkMode} setDarkMode={setDarkMode} />
		</div>
	);
}
