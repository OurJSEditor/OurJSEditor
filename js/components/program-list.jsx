import Preact from "preact";

import Program from "./program"

export default class ProgramList extends Preact.Component {
    constructor(props) {
        super(props);
    }

    render() {
        return (
            <table className="program-list">{
                someProgramList.map(program => (
                    <Program
                        id={program.id}
                        title={program.title}
                        author={program.author}
                    />
                ))
            }</table>
        );
    }
}
