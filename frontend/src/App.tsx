/**
 * Main App Component with Routing and Document Q&A Panel
 */
import { useState } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import TicketDetail from "./pages/TicketDetail";
import DocumentQAPanel from "./components/DocumentQAPanel";

function App() {
  const [isQAPanelOpen, setIsQAPanelOpen] = useState(false);

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/ticket/:id" element={<TicketDetail />} />
      </Routes>
      <DocumentQAPanel
        isOpen={isQAPanelOpen}
        onToggle={() => setIsQAPanelOpen(!isQAPanelOpen)}
      />
    </BrowserRouter>
  );
}

export default App;
