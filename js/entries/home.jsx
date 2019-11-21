import Preact from "preact";

import HomePage from "../components/home"

Preact.render(<HomePage loggedIn={userData.loggedIn} />, document.getElementById("main-content"));
