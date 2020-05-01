import Preact from "preact";

import Program from "./program"

export function PageSection(props) {
    return (
        <section id={props.id} className="page-section">
            <div className="section-header">
                <span className="left">
                    <div>{props.title}</div>
                </span>
                <span className="right">
                    {props.headerRight}
                </span>
            </div>
            <div className="section-content">
                {props.children}
            </div>
        </section>
    )
}

export default class Home extends Preact.Component {
    constructor (props) {
        super(props);

        this.loggedIn = props.loggedIn;
        this.programs = props.programs; // Has 3 lists of programs: popular, recent, subscriptions
    }

    render () {
        return (
            <div>
                <PageSection id="banner"
                    title={<img src="/static/images/logo-text.png" />}
                    headerRight={
                        <span className="button-wrap">

                        </span>
                    }/>

                <PageSection id="user-specific" title={(this.loggedIn && this.programs.recent.length) ? "You were working on" : "Welcome to OurJSEditor"}>
                        { (this.loggedIn && this.programs.recent.length) ?
                            <table className="program-list">
                                <tr>
                                    {
                                        this.programs.recent.map(program => <Program program={program} />)
                                    }

                                    <td className="button-wrap program">
                                        <a className="button half" href="/new">New program</a>
                                        <a className="button half" href={"/user/" + userData.username}>All your programs</a>
                                    </td>
                                </tr>
                            </table>
                        :
                            <div>

                                <div class="row">
                                  <div class="column">
                                  <img src="/static/images/ChatBubbles.png" />
                                    <h2>Community Driven.</h2>
                                    <p>OurJSE is centered around the community. You can see and vote on other peoples projects.</p>
                                  </div>
                                  <div class="column">
                                  <img src="/static/images/pencilTriangle.png" />
                                    <h2>lightweight & customizable</h2>
                                    <p>OurJSE is incredibly lightweight and completely customizable.</p>
                                  </div>
                                  <div class="column">
                                  <img src="/static/images/cogWrench.png" />
                                    <h2>Open Source</h2>
                                    <p>And it has a 100% open source backend, so if want a feature, you can add it!</p>
                                  </div>
                                </div>
                                <br />
                                <br />
                                {
                                    this.loggedIn ?
                                    <a className="cta button" href="/new">Make your first program</a>
                                    :
                                    <a className="cta button" href="/user/login">Get Started!</a>
                                }
                                <br />
                            </div>
                        }
                </PageSection>

                <PageSection id="popular" title="Popular Programs">
                    <table className="program-list">
                        <tr>
                            {
                                this.programs.popular.map(program => <Program program={program} />)
                            }
                            <a id="showMore" href="/programs/top"><span>Browse Programs &#10095;</span></a>
                        </tr>
                    </table>
                </PageSection>

                { (this.loggedIn && this.programs.subscriptions.length) ?
                <PageSection id="subscriptions" title="Recent from your subscriptions">
                    <table className="program-list">
                        <tr>
                            {
                                this.programs.subscriptions.map(program => <Program program={program} />)
                            }
                        </tr>
                    </table>
                </PageSection> : null
                }
            </div>
        );
    }
}
