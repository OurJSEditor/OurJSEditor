import React from "react";

export default class UsernameInput extends React.Component {
    constructor(props) {
        super(props);
        this.state = { username: "" };
    }

    onChange(e) {
        const newVal = e.target.value;
        if (/^\w{0,45}$/.test(newVal)) {
            this.setState({ username: newVal });
            this.props.onChange(e);
        } else {
            e.target.value = this.state.username;
        }
    }

    render() {
        return <input
            type="text"
            placeholder="Username"
            maxLength="45"
            onChange={this.onChange.bind(this)}
            required={this.props.required} />
    }
}

UsernameInput.defaultProps = { onChange() {}, required: false };