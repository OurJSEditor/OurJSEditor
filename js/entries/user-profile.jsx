import Preact from "preact";

import ProgramList from "../components/program-list";

Preact.render(<ProgramList 
    initialProgramList={window.initialProgramList}
    baseUrl={"/api/user/" + window.userData.username + "/programs/"}
    sort="top"
    title="Profile Programs"
    shouldShowAuthorName={false}
    shouldUpdateURL={false}
/>, document.getElementById("main-table"));