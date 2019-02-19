import React from "react";
import ReactDOM from "react-dom";

import LoginForm from "../components/login-form";
import SignupForm from "../components/signup-form";

ReactDOM.render(<LoginForm />, document.getElementById("login-form"));
ReactDOM.render(<SignupForm />, document.getElementById("signup-form"));
