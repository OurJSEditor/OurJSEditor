import Preact from "preact";

import ProgramList from "../components/program-list";

Preact.render(<ProgramList
    baseUrl={"/api/user/" + window.user.id + "/programs/"}
    title="Profile Programs"
    shouldShowAuthorName={false}
    shouldUpdateURL={false}
    listOptions={window.listOptions}
/>, document.getElementById("main-table"));
