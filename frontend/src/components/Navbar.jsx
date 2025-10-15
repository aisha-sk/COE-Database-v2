import { NavLink } from "react-router-dom";

const links = [
  { to: "/map", label: "Map" },
  { to: "/chat", label: "Chat" }
];

export default function Navbar() {
  return (
    <header className="navbar">
      <div className="navbar__brand">City of Edmonton Traffic Volume System</div>
      <nav className="navbar__links">
        {links.map(({ to, label }) => (
          <NavLink
            key={to}
            to={to}
            className={({ isActive }) =>
              ["navbar__link", isActive ? "navbar__link--active" : ""]
                .filter(Boolean)
                .join(" ")
            }
          >
            {label}
          </NavLink>
        ))}
      </nav>
    </header>
  );
}
