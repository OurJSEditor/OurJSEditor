import Preact from "preact";

function TemplateType (props) {
    console.log(props);

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

        return (
            <div>
                <h2>Select A Template</h2>
                <div className="subheading">You're not picking a type of program you're bound to, just a template.</div>
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
        );
    }
}
