import Preact from "preact";

import Program from "./program"

import Api from "../util/wrapper"

const sorts = [
    "new",
    "top",
    "artistic",
    "entertaining",
    "informative"
];

window.cachedProgramLists = {};
for (let sort of sorts) {
    cachedProgramLists[sort] = [];
    cachedProgramLists[sort].complete = false; //Set the complete key on the array
}

export default class ProgramList extends Preact.Component {
    constructor (props) {
        super(props);
        
        this.api = new Api();
        this.baseUrl = props.baseUrl ? props.baseUrl : "/api/programs/"
        
        this.state.sort = props.sort;
        
        this.state.numCols = 4;
        
        this.state.programList = props.initialProgramList;
        this.state.offset = props.initialProgramList.length; //Offset is the offset to start the next request with. It should always be the length of programList
        cachedProgramLists[this.state.sort] = this.state.programList;
        
        if (this.state.programList.length === 0) { //TODO: add a comment, when is this true?
            console.log("Just loaded with no programs??");
            this.loadMorePrograms();
        }
        
        this.state.hasShowMoreButton = props.hasShowMoreButton;
    }

    loadMorePrograms () {
        const programList = this.state.programList;
        
        this.api.getPrograms(this.baseUrl + this.state.sort, this.state.offset).then(newPrograms => {
            if (newPrograms.length < 20) {
                this.setState({ "hasShowMoreButton": false });
                programList.complete = true;
            }
            programList.push(...newPrograms);
            this.setState({ "programList": programList, "offset": programList.length });
        });
    }
    
    sortChange (e) {
        const select = e.target;
        const newSort = select.selectedOptions[0].value;

        //The idea is that the cached list for the current sort and the current program list are always the same (===). 
        
        //state.sort needs to be changed.
        //programList needs to be changed.
        //offset needs to be updated
        //loadMostPrograms needs to be called IFF we don't have any programs cached
        
        if (window.history.replaceState) {
            window.history.replaceState({"sort": newSort}, document.title, "/programs/" + newSort);
        }
        
        this.setState({
            "sort": newSort,
            "programList": cachedProgramLists[newSort],
            "offset": cachedProgramLists[newSort].length,
            "hasShowMoreButton": !cachedProgramLists[newSort].complete
        }, () => {
            if (this.state.programList.length === 0) {
                this.loadMorePrograms();
            }
        })
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
            <div id="program-list">
                <div class="header">
                    <div class="left section"><div>Program List</div></div>
            
                    <div class="right section">
                        <select onChange={ this.sortChange.bind(this) } value={ this.state.sort }>{
                            sorts.map(sort =>
                                <option value={sort}>{sort[0].toUpperCase() + sort.slice(1)}</option>
                            )
                        }</select>
                    </div>
                </div>
            
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
                                    <button class="more-programs-button" onClick={this.loadMorePrograms.bind(this)}>Show More Programs...</button>
                                </td>
                                <td></td>
                            </tr>) : null
                    }
                    </tbody></table>
                </div>
            </div>
        );
    }
}
