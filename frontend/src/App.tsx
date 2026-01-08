/**
 * Main App Component with Routing
 */
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import TicketDetail from "./pages/TicketDetail";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/ticket/:id" element={<TicketDetail />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
