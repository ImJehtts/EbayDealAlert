import { useState } from "react";

const API = import.meta.env.VITE_API_URL;

export default function App() {
  const [output, setOutput] = useState("");

  const testFetch = async () => {
    try {
      const res = await fetch(`${API}/categories?q=nintendo switch oled`);
      const data = await res.json();
      setOutput(JSON.stringify(data, null, 2));
    } catch (err) {
      setOutput(`ERROR: ${err.message}`);
    }
  };

  return (
    <div style={{ padding: 24 }}>
      <button onClick={testFetch}>Test API</button>
      <pre>{output}</pre>
    </div>
  );
}