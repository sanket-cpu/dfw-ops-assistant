import { useState } from 'react';
import ChatPanel from './components/ChatPanel';
import './App.css';

function App() {
  const [isChatOpen, setIsChatOpen] = useState(false);
//destructuring operation --> useState returns an array with two elements: the current state value and a function to update that state.
  return (
    <div className="app">
      {/* Main landing page content */}
      <div className="landing-page">
        <div className="landing-content">
          <h1>DFW Airport Operations Copilot</h1>
          <p className="subtitle">
            Your AI assistant for airport operations and design criteria
          </p>
        </div>

        {/* Floating chat button */}
        <button
          className="chat-trigger-button"
          onClick={() => setIsChatOpen(true)} // system will trigger onclick and setIsChatOpen to true --> opens chat panel
          aria-label="Open chat"
        >
          <span className="chat-icon">💬</span>
        </button>
      </div>

      {/* Side panel chat */}
      <ChatPanel
        isOpen={isChatOpen}
        onClose={() => setIsChatOpen(false)}
      />

      {/* Backdrop overlay when chat is open */}
      {isChatOpen && (
        <div
          className="backdrop"
          onClick={() => setIsChatOpen(false)}
        />
      )}
    </div>
  );
}

export default App;
