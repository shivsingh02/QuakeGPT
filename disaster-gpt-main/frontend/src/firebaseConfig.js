// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAuth, signOut } from "firebase/auth";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

import { getDatabase } from "firebase/database";

// Your web app's Firebase configuration
const firebaseConfig = {
	apiKey: "AIzaSyAkSmV3lVrdVBZYAkqhnImHEO6qlBhKEE8",
	authDomain: "quakegpt-45c7a.firebaseapp.com",
	projectId: "quakegpt-45c7a",
	storageBucket: "quakegpt-45c7a.appspot.com",
	messagingSenderId: "899056697306",
	appId: "1:899056697306:web:86b6eb300b4fc865ac0ae3",
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
export const db = getDatabase(
	app,
	"https://quakegpt-45c7a-default-rtdb.asia-southeast1.firebasedatabase.app/"
);

// Initialize Firebase Authentication and get a reference to the service
export const auth = getAuth(app);

export function logout() {
	signOut(auth)
		.then(() => {
			alert("Logged out");
		})
		.catch((error) => {
			alert(error.message + " Please try again");
		});
}
