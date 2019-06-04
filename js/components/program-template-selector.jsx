import Preact from "preact";

function TemplateType (props) {
    return (
        <a class="template" href={`/program/unsaved?template=${props.src}`}>
            <div class="title">{props.title}</div>
            <div class="description">{props.description}</div>
        </a>
    );
}

export default class TemplateSelector extends Preact.Component {
    constructor (props) {
        super(props);
    }

    render () {
        const content = (
            <div>
                <h2>Select A Template:</h2>
                <div>
                    {
                        programTemplates.map(template => (
                        <TemplateType
                            description={template.description}
                            title={template.title}
                            src={template.key}
                            key={template.key} />
                        ))
                    }
                </div>
            </div>
        );

        return content;
    }
}
