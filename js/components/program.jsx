import Preact from "preact";

export default function Program (props) {
    return (
        <a className="program" href={"/program/" + props.id}>
            <div class="program-title">{props.title}</div>

            <a class="program-author" href={"/user/" + props.author.username}>{props.author.displayName}</a>
        </a>
            // <img class="thumbnail">
            /*<table class="vote-info"><tbody>
                <tr>
                    <td class="vote-stat"></td>
                    <td class="vote-stat"></td>
                    <td class="vote-stat"></td>
                </tr>
            </tbody></table>*/
            //TODO: Published/unpublished

    );
};
