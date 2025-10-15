import { BrowserRouter, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import Home from "./pages/Home";
import MapView from "./pages/MapView";
import ChatView from "./pages/ChatView";
import "./App.css";

export default function App() {
  return (
    <BrowserRouter>
      <div className="app-shell">
        <Navbar />
        <main className="app-main">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/map" element={<MapView />} />
            <Route path="/chat" element={<ChatView />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </BrowserRouter>
  );
}
