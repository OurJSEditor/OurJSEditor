import React from "react";
import Api from "../util/wrapper";

import UsernameInput from "./username-input";

export default class LoginForm extends React.Component {
    constructor(props) {
        super(props);
        this.state = { username: "", password: "", error: "" };
        this.api = new Api();
    }

    setField(property, e) {
        this.setState({ error: "", [property]: e.target.value });
    }

    async submit(e) {
        e.preventDefault();

        let result = await this.api.login(this.state.username, this.state.password).catch(_ => ({
            success: false,
            error: "Error in making HTTP request",
        }));

        if (result.success) {
            const params = new URLSearchParams(window.location.search);
            const next = params.get("next") || "";
            location.href = next.startsWith("/") ? next : `/user/${result.username}`;
        } else {
            this.setState({ error: result.error });
        }
    }

    render() {
        return (
            <form className="basic-form" onSubmit={this.submit.bind(this)}>
                <h2>Log in</h2>
                <UsernameInput
                    onChange={this.setField.bind(this, "username")}
                    required />
                <input
                    type="password"
                    placeholder="Password"
                    required
                    onChange={this.setField.bind(this, "password")} />
                <input
                    type="submit"
                    value="Log in" />
                <p class="error">{ this.state.error }</p>
            </form>
        );
    }
}

