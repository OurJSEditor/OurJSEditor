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
        cachedProgramLists[this.state.sort] = this.state.programList;
        
        if (this.state.programList.length === 0) {
            console.error("Just loaded with no programs. This shouldn't happen");
            this.loadMorePrograms();
        }
        
        this.state.hasShowMoreButton = props.initialProgramList.length === 20;
    }

    loadMorePrograms (newSort) {
        const sort = typeof newSort === "string" ? newSort : this.state.sort;
        
        const programList = cachedProgramLists[sort];
        
        this.api.getPrograms(this.baseUrl + sort, programList.length).then(newPrograms => {
            if (newPrograms.length < 20) {
                this.setState({ "hasShowMoreButton": false });
                programList.complete = true;
            }
            
            programList.push(...newPrograms);
            this.setState({ "programList": programList, "sort": sort});
            
            //This replaces history sometimes when it doesn't need to (ie, the sort hasn't changed)
            if (window.history.replaceState && window.location.pathname !== "/programs/" + sort) {
                window.history.replaceState({"sort": sort}, document.title, "/programs/" + sort);
            }
        }).catch(err => {
            console.error(err);
            this.setState({ "sort": this.state.sort });
            alert("Unable to load programs. Is the internet connection online?");
        });
    }
    
    sortChange (e) {
        const newSort = e.target.selectedOptions[0].value;
        //TODO: Same as e.target.value?

        /*
        The idea is that the cached list for the current sort and the current program list are always the same (===). 

        programList needs to be changed if we have programs cached
        loadMostPrograms needs to be called IFF we don't have any programs cached
        */
        
        if (cachedProgramLists[newSort].length === 0) {
            this.loadMorePrograms(newSort);
        }else {
            this.setState({
                "sort": newSort,
                "programList": cachedProgramLists[newSort],
                "hasShowMoreButton": !cachedProgramLists[newSort].complete
            })
        }
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
