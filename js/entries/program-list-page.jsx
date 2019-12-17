import Preact from "preact";

import ProgramList from "../components/program-list";

Preact.render(<ProgramList
    listOptions={window.listOptions}
    title="Program List"
    shouldUpdateURL={true}
/>, document.getElementById("main-content"));
