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
        const templateKeys = Object.keys(programTemplates);

        const content = (
            <div>
                <h2>Select A Template:</h2>
                <div>
                    {
                        templateKeys.map(template => (
                        <TemplateType
                            description={programTemplates[template].description}
                            title={programTemplates[template].title}
                            src={template}
                            key={template} />
                        ))
                    }
                </div>
            </div>
        );

        return content;
    }
}
