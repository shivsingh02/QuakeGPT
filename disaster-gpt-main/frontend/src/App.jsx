import { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { auth } from "./firebaseConfig";
import { onAuthStateChanged } from "firebase/auth";

import Home from "./pages/Home";
import Chat from "./pages/Chat";

import "./App.css";

function App() {
	const [user, setUser] = useState(auth.currentUser);
	useEffect(() => {
		const unsubscribe = onAuthStateChanged(auth, (user) => {
			setUser(user);
		});
		return () => unsubscribe();
	}, []);

	const [darkMode, setDarkMode] = useState(false);

	return (
		<BrowserRouter>
			<Routes>
				<Route
					path="/chat/:slug"
					element={
						<Chat darkMode={darkMode} setDarkMode={setDarkMode} />
					}
				/>
				<Route
					exact
					path="*"
					element={
						<Home darkMode={darkMode} setDarkMode={setDarkMode} />
					}
				/>
			</Routes>
		</BrowserRouter>
	);
}

export default App;
