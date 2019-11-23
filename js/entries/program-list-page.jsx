import Preact from "preact";

import ProgramList from "../components/program-list";

Preact.render(<ProgramList 
    initialProgramList={window.initialProgramList}
    sort={window.sort}
    title="Program List"
/>, document.getElementById("main-content"));
