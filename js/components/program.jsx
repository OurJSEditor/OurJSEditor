import Preact from "preact";

export default function Program (props) {
    const program = props.program;
    
    const voteTypes = Object.keys(program.votes);
    
    return (
        <td className="program">
            <div class="title-wrap">
                <a class="program-title" href={"/program/" + program.id}>{program.title}</a>
            </div>
            
            <a href={"/program/" + program.id} className="program-link">
                <img class="thumbnail" src={program.thumbnailUrl} title={
                    program.thumbnailUrl === "/static/media/program_thumbnails/nophoto.png" ? 
                        "This program is unpublished and doesn't have a thumbnail" :
                        program.title
                } />
            </a>
            
            <a className="program-author program-link" href={"/user/" + program.author.username}>{program.author.displayName}</a>
            
            <table class="vote-info"><tbody>
                <tr>
                    {
                        voteTypes.map(type => //TODO, yes this looks trash I'm sorry
                            <td class="vote-stat">{type[0].toUpperCase()}: {program.votes[type]}</td>
                        )
                    }
                </tr>
            </tbody></table>
        </td>
    );
};
