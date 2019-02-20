import React from "react";
import Api from "../util/wrapper";

import UsernameInput from "./username-input";

const ICON_SIZE = 30;

export default class SignupForm extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            name: "",
            username: "",
            email: "",
            password: "",
            passwordRep: "",
            error: "",
            usernameOk: null,
        };
        this.api = new Api();
    }

    setField(property, e) {
        this.setState({ error: "", [property]: e.target.value });
    }

    async onUsername(e) {
        this.setField("username", e);
        this.setState({ usernameOk: await this.api.checkUsername(e.target.value).catch(_ => false) });
    }

    async onSubmit(e) {
        e.preventDefault();

        if (this.state.password != this.state.passwordRep) {
            this.setState({ error: "Make sure your passwords match" });
            return;
        } else if (!/^(?:[\w.+-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)+)?$/.test(this.state.email)) {
            this.setState({ error: "Please enter a valid email if you choose to enter one" });
            return;
        }

        const response = await this.api.createAccount(this.state.name, this.state.username,
            this.state.password, this.state.email).catch(_ => ({
                success: false, error: "Error sending request"
            }));

        if (response.success) {
            window.location = `/user/${response.username}`;
        } else {
            this.setState({ error: response.error });
        }
    }

    render() {
        return (
            <form className="basic-form" onSubmit={this.onSubmit.bind(this)}>
                <h2>Sign up</h2>
                <input
                    type="text"
                    placeholder="Name"
                    maxLength="45"
                    onChange={this.setField.bind(this, "name")}
                    required />
                <div class="validated-field">
                    <UsernameInput
                        onChange={this.onUsername.bind(this)}
                        required />
                    {this.state.usernameOk === null ?
                        <div style={{ width: `${ICON_SIZE + 1}px`, height: `${ICON_SIZE + 1}px` }}></div> :
                        <img
                            src={`/static/images/icons/${this.state.usernameOk ? "check" : "invalid"}.svg`}
                            alt="Username status"
                            width={ICON_SIZE}
                            height={ICON_SIZE} />}
                </div>
                <input
                    type="email"
                    placeholder="Email"
                    onChange={this.setField.bind(this, "email")} />
                <input
                    onChange={this.setField.bind(this, "password")}
                    type="password"
                    placeholder="Password"
                    minLength="8"
                    required />
                <input
                    onChange={this.setField.bind(this, "passwordRep")}
                    type="password"
                    placeholder="Repeat password"
                    minLength="8"
                    required />
                <input type="submit" value="Sign up" />
                <p class="error">{ this.state.error }</p>
            </form>
        );
    }
}
