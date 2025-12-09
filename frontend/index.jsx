import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App";

const rootEl = document.createElement("div");
rootEl.id = "root";
document.body.appendChild(rootEl);

createRoot(document.getElementById("root")).render(<App />);
