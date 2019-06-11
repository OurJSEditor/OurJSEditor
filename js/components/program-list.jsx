import Preact from "preact";

import Program from "./program"

import Api from "../util/wrapper"

export default class ProgramList extends Preact.Component {
    constructor (props) {
        super(props);
        
        this.api = new Api();
        this.baseUrl = props.baseUrl ? props.baseUrl : "/api/programs/"
        this.state.sort = props.sort;
        
        this.state.numCols = 4;
        
        this.state.programList = props.initialProgramList;
        this.state.offset = props.initialProgramList.length; //Offset is the offset to start the next request with. It should always be the length of programList
        console.log(this.state.offset, props.initialProgramList.length);
        
        if (this.state.programList.length === 0) {
            this.loadMorePrograms();
        }
        
        this.state.hasShowMoreButton = props.hasShowMoreButton;
    }

    loadMorePrograms () {
        const programList = this.state.programList;
        
        this.api.getPrograms(this.baseUrl + this.state.sort, this.state.offset).then(newPrograms => {
            if (newPrograms.length < 20) {
                this.setState({ "hasShowMoreButton": false });
            }
            programList.push(...newPrograms);
            this.setState({ "programList": programList, "offset": programList.length })
        });
    }
    
    render () {
        const programRows = [];
        
        //Collect array into sub arrays of four (or numCols)
        for (let i = 0; i < this.state.programList.length; i ++) {
            if (i % this.state.numCols === 0) {
                programRows.push([]);
            }
            programRows[programRows.length-1].push(this.state.programList[i]);
        }
        
        return (
            <div className="program-list">
                <table><tbody>{
                    programRows.map(row => (
                        <tr>{
                            row.map(program => (
                                <Program program={program} />
                            ))
                        }</tr>
                    ))
                }
                
                {
                    this.state.hasShowMoreButton ? 
                        (<tr>
                            <td></td>
                            <td colspan="2">
                                <button class="more-programs-button" onClick={this.loadMorePrograms.bind(this)}>Show More     Programs...</button>
                            </td>
                            <td></td>
                        </tr>) : null
                }
                </tbody></table>
            </div>
        );
    }
}
