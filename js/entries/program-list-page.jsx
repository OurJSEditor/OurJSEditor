import Preact from "preact";

import ProgramList from "../components/program-list"

Preact.render(<ProgramList 
    initialProgramList={window.initialProgramList}
    sort={window.sort} />, document.getElementById("main-content"));
