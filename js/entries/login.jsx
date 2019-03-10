import Preact from "preact";

import LoginForm from "../components/login-form";
import SignupForm from "../components/signup-form";

Preact.render(<LoginForm />, document.getElementById("login-form"));
Preact.render(<SignupForm />, document.getElementById("signup-form"));
