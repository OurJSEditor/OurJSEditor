import Preact from "preact";

import HomePage from "../components/home"

Preact.render(<HomePage loggedIn={window.userData.loggedIn} programs={window.programs}/>, document.getElementById("main-content"));
