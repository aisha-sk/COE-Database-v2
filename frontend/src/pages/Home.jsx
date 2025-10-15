import { useNavigate } from "react-router-dom";

export default function Home() {
  const navigate = useNavigate();

  return (
    <section className="home-page">
      <div className="home-hero">
        <h1 className="home-title">City of Edmonton Traffic Volume Platform</h1>
        <p className="home-subtitle">
          Explore traffic data and visualize trends interactively.
        </p>
        <div className="home-actions">
          <button className="home-button" type="button" onClick={() => navigate("/map")}>Open Map</button>
          <button className="home-button" type="button" onClick={() => navigate("/chat")}>Chat with Database</button>
        </div>
      </div>
    </section>
  );
}
