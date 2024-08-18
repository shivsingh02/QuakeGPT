import React, { useEffect, useState, useRef } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { auth, db } from "../firebaseConfig";
import { onValue, ref, set } from "firebase/database";

import generatePDF, { Margin } from "react-to-pdf";

import DarkMode from "../components/DarkMode";
import Styles from "./Chat.module.css";

export default function Chat(props) {
	const { darkMode, setDarkMode } = props;

	const navigate = useNavigate();

	const [chatData, setChatData] = useState(null);

	useEffect(() => {
		if (!auth.currentUser) {
			alert("Please login to continue");
			navigate("/");
			return;
		}

		//get chat data from backend
		const query = ref(db, auth.currentUser.uid + "/chats");
		return onValue(
			query,
			(snapshot) => {
				let data = snapshot.val();
				if (snapshot.exists()) {
					setChatData(data);
				}
			},
			(error) => {
				alert("Error while fetching chat data: " + error.message);
			}
		);
	}, [auth.currentUser]);

	const { slug } = useParams();
	const [chatList, setChatList] = useState([]);
	const [chatContent, setChatContent] = useState({});

	const [input, setInput] = useState("");
	const [predictMode, setPredictMode] = useState(false);

	const targetRef = useRef();

	const [menuOpen, setMenuOpen] = useState(false);

	useEffect(() => {
		if (!chatData) return;

		//get user chat details from chatData
		let chatList = Object.keys(chatData)
			.map((slug) => {
				return {
					heading: chatData[slug].heading,
					slug,
				};
			})
			.sort((a, b) => {
				return (
					parseInt(a.slug.replace("chat-", "")) -
					parseInt(b.slug.replace("chat-", ""))
				);
			});
		if (slug === "new") {
			chatList = [...chatList, { heading: "New Chat", slug: "new" }];
		}
		setChatList(chatList);

		if (slug === "new") {
			setChatContent([]);
		} else if (chatData[slug]) {
			setChatContent(chatData[slug].content);
		} else {
			// invalid chat
			navigate("/");
			return;
		}
	}, [chatData, slug]);

	function onSend(e) {
		e.preventDefault();
		const query = input.trim();

		if (query === "") {
			setInput("");
			return;
		}

		chatContent[Object.keys(chatContent).length] = {
			query,
			response: "Loading...",
		};
		setChatContent(chatContent);
		setInput("");

		// scroll to bottom
		targetRef.current.scrollTop = targetRef.current.scrollHeight;

		// convert chatContent to object and remove last message
		let history = {};
		if (typeof chatContent === "array") {
			chatContent.forEach((pair, idx) => {
				if (idx == chatContent.length - 1) return;
				history[idx] = pair;
			});
		} else {
			Object.keys(chatContent).forEach((idx) => {
				if (idx == Object.keys(chatContent).length - 1) return;
				history[idx] = chatContent[idx];
			});
		}

		const endpoint = predictMode ? "answer_pred_route" : "answer_question";
		let specialUser = false;
		if (auth.currentUser.uid === "nBNLsIjSooXMn79I7LFRd7zYl1e2")
			specialUser = true;
		if (auth.currentUser.uid === "WlmmtlwJuOhZsTvurUSkKek5DA02")
			specialUser = true;
		if (auth.currentUser.uid === "d3yE9G5RhxTYAbYfwW94JygPhfm1")
			specialUser = true;
		if (auth.currentUser.uid === "UjWDh3E35Tb9HEBu07OxmccSvw72")
			specialUser = true;

		// send chat content to model and get response
		fetch("http://10.29.8.94:5000/api/" + endpoint, {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
			body: JSON.stringify({
				question: query,
				history: history,
				special: darkMode && specialUser,
			}),
		})
			.then((response) => {
				response.json().then((data) => {
					// copy chat content and update last message
					let temp = { ...chatContent };
					temp[Object.keys(chatContent).length - 1] = {
						query,
						response: data.result,
					};

					if (slug === "new") {
						//define new chat  and generate heading and unique slug
						let heading =
							"Chat " +
							(chatList.length == 0 ? 1 : chatList.length);
						let slug =
							"chat-" +
							(chatList.length == 0 ? 1 : chatList.length);

						//create new chat in backend
						set(ref(db, auth.currentUser.uid + "/chats/" + slug), {
							heading: heading,
							content: temp,
						})
							.then(() => {
								// alert("Chat saved successfully");
								navigate("/chat/" + slug);
							})
							.catch((error) => {
								alert(
									"Error while saving chat: " + error.message
								);
							});
					} else {
						//update chat content in backend
						set(
							ref(
								db,
								auth.currentUser.uid +
									"/chats/" +
									slug +
									"/content"
							),
							temp
						)
							.then(() => {
								// alert("Chat saved successfully");
							})
							.catch((error) => {
								alert(
									"Error while saving chat: " + error.message
								);
							});
					}
				});
			})
			.catch((error) => {
				alert("Error in sending message: " + error.message);
				// remove from chat content and put in input
				let temp = { ...chatContent };
				delete temp[Object.keys(chatContent).length - 1];
				setChatContent(temp);
				setInput(query);
			});
	}

	function newChat() {
		//find existing new chat item
		let newChat = chatList.find((chat) => chat.slug === "new");

		//if new chat item does not exist, create it
		if (!newChat) {
			setChatList((chatList) => [
				...chatList,
				{ heading: "New Chat", slug: "new" },
			]);
		}
	}

	function downloadChat() {
		targetRef.current.style.height = "unset";
		targetRef.current.style.overflowY = "unset";
		targetRef.current.style.color = "black";

		generatePDF(targetRef, {
			filename: "chat-" + slug + ".pdf",
			page: {
				margin: Margin.SMALL,
			},
		});
		targetRef.current.style.height = "85%";
		targetRef.current.style.overflowY = "scroll";
		targetRef.current.style.color = "";
	}

	// form submit on Shift+Enter
	useEffect(() => {
		function handleKeyDown(e) {
			if (e.shiftKey && e.key === "Enter") {
				onSend(e);
			}
		}
		document.addEventListener("keydown", handleKeyDown);
		return () => {
			document.removeEventListener("keydown", handleKeyDown);
		};
	}, [onSend]);

	return (
		<div
			className={
				Styles["page-container"] +
				` ${darkMode ? Styles["dark"] : ""}` +
				` ${menuOpen ? Styles["menuOpen"] : ""}`
			}
		>
			<div className={Styles["chat-menu-container"]}>
				<div
					className={Styles["hamburger"]}
					onClick={() => setMenuOpen(!menuOpen)}
				>
					<i className="fa fa-bars" aria-hidden="true" />
				</div>
				<Link to="/chat/new">
					<button onClick={newChat}>
						<i className="fa fa-plus" aria-hidden="true" />
						{menuOpen && " New Chat"}
					</button>
				</Link>
				{menuOpen && (
					<div className={Styles["chat-list"]}>
						{[...chatList].reverse().map((chat, idx) => (
							<Link
								key={idx}
								to={"/chat/" + chat.slug}
								className={
									slug === chat.slug ? Styles["active"] : null
								}
							>
								{chat.heading}
								{slug === chat.slug && slug !== "new" && (
									<i
										className="fa fa-download"
										aria-hidden="true"
										onClick={downloadChat}
									></i>
								)}
							</Link>
						))}
					</div>
				)}
			</div>
			<div className={Styles["chat-box-container"]}>
				<div className={Styles["chat-box-header"]}>
					<Link to="/">
						<h1>
							<img
								src="../android-chrome-512x512.png"
								alt="logo"
								height={50}
								width={50}
							/>
							Disaster GPT
						</h1>
					</Link>
					<DarkMode darkMode={darkMode} setDarkMode={setDarkMode} />
				</div>
				<div className={Styles["messages-list"]} ref={targetRef}>
					{chatContent.length > 0 ? (
						Object.keys(chatContent).map((idx) => {
							let pair = chatContent[idx];
							return (
								<React.Fragment key={idx}>
									{pair.query && (
										<div
											key={1}
											className={
												Styles["message-box"] +
												" " +
												Styles["user"]
											}
										>
											<img
												src={auth.currentUser.photoURL}
												alt="logo"
											/>
											<div className={Styles["message"]}>
												{pair.query}
											</div>
										</div>
									)}
									{pair.response && (
										<div
											key={2}
											className={
												Styles["message-box"] +
												" " +
												Styles["gpt"]
											}
										>
											<img
												src={
													"../android-chrome-512x512.png"
												}
												alt="logo"
											/>
											<div className={Styles["message"]}>
												{pair.response}
											</div>
										</div>
									)}
								</React.Fragment>
							);
						})
					) : (
						<div className={Styles["message-box-empty"]}>
							This could be a good place to start a conversation.
							Ask me anything!
						</div>
					)}
				</div>
				<form onSubmit={onSend} className={Styles["chat-box-footer"]}>
					<textarea
						type="text"
						value={input}
						onChange={(e) => setInput(e.target.value)}
						placeholder="Type your message...Press Shift+Enter to send"
					></textarea>
					<div
						style={{
							display: "flex",
							flexDirection: "column",
							alignItems: "center",
						}}
					>
						Predict
						<button
							onClick={(e) => {
								e.preventDefault();
								setPredictMode(!predictMode);
							}}
							style={{
								backgroundColor: predictMode ? "green" : "red",
								color: "white",
							}}
						>
							{predictMode ? "ON" : "OFF"}
						</button>
					</div>
					<button type="submit">
						<i className="fa fa-paper-plane" aria-hidden="true" />
					</button>
				</form>
			</div>
		</div>
	);
}
