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
                            <a className="button" href="https://discord.gg/WSHpEPa">DISCORD</a>
                            <a className="button" href="https://github.com/OurJSEditor/OurJSEditor">GITHUB</a>
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
                            <div className="welcome">
                                {
                                    this.loggedIn ?
                                        <span className="button-wrap">
                                            <a className="button" href="/new">Make your first program</a>
                                        </span>
                                            :
                                        <span className="button-wrap">
                                            <a className="button" href="/user/login">Sign Up</a>
                                            <a className="button" href="https://github.com/OurJSEditor/OurJSEditor">Source on Github</a>
                                        </span>
                                }
                                <span className="copy">
                                    Our JS Editor is an online code editor. But it&#8217;s different.<br />
                                    <ul>
                                        <li>It&#8217;s community based, so you can see and vote on other people&#8217;s programs.</li>
                                        <li>It&#8217;s lightweight and it&#8217;s customizable.</li>
                                        <li>And it has a 100% open source backend, so if you want more, you can help add it.</li>
                                    </ul>
                                </span>
                            </div>
                        }
                </PageSection>

                <PageSection id="popular" title="Popular Programs">
                    <table className="program-list">
                        <tr>
                            {
                                this.programs.popular.map(program => <Program program={program} />)
                            }
                            <td className="button-wrap program">
                                <a className="button full" href="/programs/top">See More</a>
                            </td>
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
