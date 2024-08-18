import Styles from "./DarkMode.module.css";

export default function DarkMode(props) {
	const { darkMode, setDarkMode } = props;
	return (
		<div
			className={
				Styles["container"] + ` ${darkMode ? Styles["dark"] : ""}`
			}
		>
			<input
				type="checkbox"
				className={Styles["checkbox"]}
				id="checkbox"
				defaultChecked={darkMode}
				onChange={() => setDarkMode(!darkMode)}
			/>
			DARK MODE
			<label htmlFor="checkbox" className={Styles["checkbox-label"]}>
				<span className={Styles["ball"]}></span>
			</label>
		</div>
	);
}
