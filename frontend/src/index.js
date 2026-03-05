// Core React runtime.
import React from "react";
// DOM renderer for mounting React app.
import ReactDOM from "react-dom";
// Root application component.
import App from "./components/App";

// Mount App component into root DOM node from public/index.html.
ReactDOM.render(<App />, document.getElementById("root"));
