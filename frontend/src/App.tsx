import { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [text, setText] = useState<string>();
  const [result, setResult] = useState<string[]>([]);

  const askAI = async () => {
    const result = await axios.post(
      "http://127.0.0.1:8000/monitoring-assistant",
      { text: text }
    );
    setResult(result.data.message);
  };

  return (
    <>
      <div>
        <h3>What do you want to know about your system today?</h3>
        <textarea
          name=""
          id=""
          cols="80"
          rows="10"
          onChange={(event) => setText(event.target.value)}
        ></textarea>
        <div>
          <button onClick={askAI}>ASK</button>
        </div>
        <div className="display-result">{result}</div>
      </div>
    </>
  );
}

export default App;
