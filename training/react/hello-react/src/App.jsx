import React, { useState } from "react";

export default function App() {
  const [name, setName] = useState("");
  const who = name.trim() || "World";
  return (
    <div style={{ fontFamily: "system-ui, sans-serif", padding: 24 }}>
      <h1>Hello, {who}!</h1>
      <input
        placeholder="Type your name"
        value={name}
        onChange={(e) => setName(e.target.value)}
        aria-label="name"
      />
      <p style={{ opacity: 0.7 }}>React training starter ✨</p>
    </div>
  );
}
