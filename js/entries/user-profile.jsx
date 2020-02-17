import Preact from "preact";

import ProgramList from "../components/program-list";

Preact.render(<ProgramList
    baseUrl={"/api/user/" + window.user.id + "/programs/"}
    title="Profile Programs"
    shouldShowAuthorName={false}
    shouldUpdateURL={false}
    listOptions={window.listOptions}
    fallback={<span>
        <span>Looks like {user.id === userData.id ? "you haven't" : "this user hasn't"} made any programs. </span>
        {user.id === userData.id ? <a href="/new">Make a new program.</a> : null}
    </span>} //A message to show if there are no programs
/>, document.getElementById("main-table"));
