import { useState } from "react";
import {
  ArrowRight,
  ArrowUpRight,
  CheckCircle2,
  ChevronRight,
  Clock3,
  Droplets,
  Headset,
  MapPin,
  Menu,
  MessageCircle,
  Navigation,
  ShieldCheck,
  Sparkles,
  Wrench,
  X,
  Zap,
  Snowflake,
  CalendarCheck,
  Wallet,
  ClipboardCheck,
} from "lucide-react";
import "./styles.css";

const BACKEND_URL = (import.meta.env.VITE_BACKEND_URL || "https://seva-bandhu-src9060.onrender.com").replace(/\/+$/, "");
const backendHref = (path) => BACKEND_URL + path;

const routes = {
  customerLogin: "/customer/login/",
  customerSignup: "/customer/signup/",
  technicianLogin: "/technician/login/",
  technicianSignup: "/technician/signup/",
  adminLogin: "/admin-login/",
};

const services = [
  {
    title: "AC repair",
    detail: "Cooling, servicing and common AC issues.",
    icon: Snowflake,
    tone: "mint",
  },
  {
    title: "Electrical",
    detail: "Everyday electrical repairs and help.",
    icon: Zap,
    tone: "sun",
  },
  {
    title: "Plumbing",
    detail: "Leaks, fittings and plumbing support.",
    icon: Droplets,
    tone: "sky",
  },
  {
    title: "Cleaning",
    detail: "Practical help to keep your home fresh.",
    icon: Sparkles,
    tone: "lilac",
  },
];

const highlights = [
  {
    icon: CalendarCheck,
    title: "Request a service",
    detail: "Choose a service and submit your request online.",
  },
  {
    icon: Navigation,
    title: "Follow the journey",
    detail: "Check technician tracking when the journey starts.",
  },
  {
    icon: MessageCircle,
    title: "Stay connected",
    detail: "Use the in-app chat for an active service request.",
  },
];

function Brand({ light = false }) {
  return (
    <a className={"brand" + (light ? " brand-light" : "")} href="#top" aria-label="Seva Bandhu home">
      <span className="brand-mark"><Wrench size={21} strokeWidth={2.5} /></span>
      <span className="brand-name">seva<span>bandhu</span></span>
    </a>
  );
}

function App() {
  const [menuOpen, setMenuOpen] = useState(false);
  const closeMenu = () => setMenuOpen(false);

  return (
    <div className="site-shell" id="top">
      <div className="announcement">
        <span className="announcement-dot" />
        A simpler way to arrange everyday home services
        <ArrowRight size={14} />
      </div>

      <header className="site-header">
        <div className="container nav-inner">
          <Brand />
          <button
            type="button"
            className="menu-toggle"
            onClick={() => setMenuOpen((open) => !open)}
            aria-label={menuOpen ? "Close navigation menu" : "Open navigation menu"}
            aria-expanded={menuOpen}
          >
            {menuOpen ? <X size={22} /> : <Menu size={22} />}
          </button>
          <nav className={"main-nav" + (menuOpen ? " nav-open" : "")} aria-label="Main navigation">
            <a href="#services" onClick={closeMenu}>Services</a>
            <a href="#how-it-works" onClick={closeMenu}>How it works</a>
            <a href="#why-seva" onClick={closeMenu}>Why Seva Bandhu</a>
            <div className="mobile-nav-actions">
              <a className="button button-quiet" href={backendHref(routes.customerLogin)}>Customer login</a>
              <a className="button button-dark" href={backendHref(routes.customerSignup)}>Get started <ArrowUpRight size={16} /></a>
            </div>
          </nav>
          <div className="desktop-nav-actions">
            <a className="nav-login" href={backendHref(routes.customerLogin)}>Log in</a>
            <a className="button button-dark button-small" href={backendHref(routes.customerSignup)}>
              Get started <ArrowUpRight size={15} />
            </a>
          </div>
        </div>
      </header>

      <main>
        <section className="hero-section">
          <div className="hero-glow hero-glow-one" />
          <div className="hero-glow hero-glow-two" />
          <div className="container hero-grid">
            <div className="hero-copy">
              <div className="eyebrow"><span className="eyebrow-icon"><Sparkles size={14} /></span> HOME SERVICES, MADE SIMPLER</div>
              <h1>Fix the little things.<br /><span>Enjoy the big things.</span></h1>
              <p className="hero-description">
                From a faulty switch to an AC that needs attention, Seva Bandhu helps you request home services and stay updated along the way.
              </p>
              <div className="hero-actions">
                <a className="button button-green" href={backendHref(routes.customerSignup)}>
                  Book a service <ArrowRight size={18} />
                </a>
                <a className="button button-outline" href={backendHref(routes.technicianSignup)}>
                  Join as a technician <ArrowUpRight size={17} />
                </a>
              </div>
              <div className="hero-proof">
                <div className="proof-icon"><ShieldCheck size={18} /></div>
                <div>
                  <strong>One place to manage your request</strong>
                  <span>Booking, updates and communication in one flow.</span>
                </div>
              </div>
            </div>

            <div className="hero-art" aria-label="Seva Bandhu service features">
              <div className="art-grid" />
              <div className="art-badge art-badge-top"><span className="badge-check"><CheckCircle2 size={16} /></span> Service requests, simplified</div>
              <div className="house-illustration">
                <div className="house-sun" />
                <div className="house-roof" />
                <div className="house-body">
                  <div className="house-window house-window-left" />
                  <div className="house-door"><span /></div>
                  <div className="house-window house-window-right" />
                </div>
                <div className="house-ground" />
                <div className="plant plant-left"><i /><i /><i /><b /></div>
                <div className="plant plant-right"><i /><i /><i /><b /></div>
                <div className="service-person">
                  <div className="person-head" />
                  <div className="person-body"><Wrench size={23} /></div>
                  <div className="person-leg person-leg-left" />
                  <div className="person-leg person-leg-right" />
                </div>
              </div>
              <div className="art-floating-card tracking-card">
                <span className="floating-icon tracking-icon"><MapPin size={18} /></span>
                <span className="floating-copy"><strong>Live tracking</strong><small>Stay in the loop</small></span>
                <span className="floating-status" aria-label="Tracking feature" />
              </div>
              <div className="art-floating-card chat-card">
                <span className="floating-icon chat-icon"><MessageCircle size={18} /></span>
                <span className="floating-copy"><strong>Easy communication</strong><small>Chat during your request</small></span>
              </div>
              <div className="art-caption"><span className="caption-line" /> Helpful service, closer to home</div>
            </div>
          </div>
        </section>

        <section className="services-section section-pad" id="services">
          <div className="container">
            <div className="section-heading">
              <div>
                <div className="eyebrow eyebrow-muted">WHAT CAN WE HELP WITH?</div>
                <h2>Home help for the things<br className="desktop-break" /> that matter every day.</h2>
              </div>
              <a className="text-link" href={backendHref(routes.customerLogin)}>Explore services <ArrowRight size={17} /></a>
            </div>
            <div className="service-grid">
              {services.map((service) => {
                const Icon = service.icon;
                return (
                  <a className="service-card" href={backendHref(routes.customerLogin)} key={service.title}>
                    <div className={"service-icon " + service.tone}><Icon size={24} strokeWidth={1.8} /></div>
                    <div className="service-card-copy">
                      <h3>{service.title}</h3>
                      <p>{service.detail}</p>
                    </div>
                    <span className="service-arrow"><ArrowUpRight size={17} /></span>
                  </a>
                );
              })}
            </div>
            <p className="section-note">Service availability and categories are managed by the Seva Bandhu platform.</p>
          </div>
        </section>

        <section className="process-section section-pad" id="how-it-works">
          <div className="container process-grid">
            <div className="process-intro">
              <div className="eyebrow eyebrow-light">A CLEARER SERVICE JOURNEY</div>
              <h2>From request to<br /><span>resolved.</span></h2>
              <p>Keep the process straightforward. Submit your request, follow progress, and communicate through the platform while your service is active.</p>
              <a className="button button-white" href={backendHref(routes.customerSignup)}>Get started <ArrowRight size={17} /></a>
            </div>
            <div className="process-steps">
              <div className="step-item">
                <div className="step-number">01</div>
                <div className="step-content"><h3>Choose what you need</h3><p>Find a service and submit the details of your request.</p></div>
                <div className="step-symbol"><ClipboardCheck size={21} /></div>
              </div>
              <div className="step-connector" />
              <div className="step-item">
                <div className="step-number">02</div>
                <div className="step-content"><h3>Keep track of progress</h3><p>Follow request status and see the technician's journey when tracking is active.</p></div>
                <div className="step-symbol"><Navigation size={21} /></div>
              </div>
              <div className="step-connector" />
              <div className="step-item">
                <div className="step-number">03</div>
                <div className="step-content"><h3>Stay in the conversation</h3><p>Use chat and your request details to stay connected through the service journey.</p></div>
                <div className="step-symbol"><MessageCircle size={21} /></div>
              </div>
            </div>
          </div>
        </section>

        <section className="benefits-section section-pad" id="why-seva">
          <div className="container">
            <div className="benefits-top">
              <div className="eyebrow eyebrow-muted">DESIGNED AROUND YOUR EXPERIENCE</div>
              <h2>Less chasing.<br /><span>More clarity.</span></h2>
              <p>Useful features that make service requests easier to manage for both customers and technicians.</p>
            </div>
            <div className="benefit-grid">
              {highlights.map((item, index) => {
                const Icon = item.icon;
                return (
                  <article className="benefit-card" key={item.title}>
                    <span className="benefit-number">0{index + 1}</span>
                    <div className="benefit-icon"><Icon size={23} strokeWidth={1.8} /></div>
                    <h3>{item.title}</h3>
                    <p>{item.detail}</p>
                  </article>
                );
              })}
              <article className="benefit-card">
                <span className="benefit-number">04</span>
                <div className="benefit-icon"><Wallet size={23} strokeWidth={1.8} /></div>
                <h3>Technician tools</h3>
                <p>Technicians can manage jobs and access wallet and incentive information.</p>
              </article>
            </div>
          </div>
        </section>

        <section className="role-section">
          <div className="container">
            <div className="role-banner">
              <div className="role-banner-copy">
                <span className="role-kicker">LET'S GET YOU STARTED</span>
                <h2>Good help starts<br />with one simple step.</h2>
                <p>Choose the path that fits you. You can return to your account whenever you need.</p>
              </div>
              <div className="role-actions">
                <a className="role-action" href={backendHref(routes.customerLogin)}>
                  <span className="role-action-icon"><Headset size={20} /></span>
                  <span><strong>I'm a customer</strong><small>Book and manage services</small></span>
                  <ChevronRight size={19} />
                </a>
                <a className="role-action" href={backendHref(routes.technicianLogin)}>
                  <span className="role-action-icon"><Wrench size={20} /></span>
                  <span><strong>I'm a technician</strong><small>Manage your assigned jobs</small></span>
                  <ChevronRight size={19} />
                </a>
                <a className="role-admin-link" href={backendHref(routes.adminLogin)}>Administrator access <ArrowUpRight size={14} /></a>
              </div>
              <div className="role-decoration role-decoration-one" />
              <div className="role-decoration role-decoration-two" />
            </div>
          </div>
        </section>
      </main>

      <footer className="site-footer">
        <div className="container footer-main">
          <div className="footer-brand-block">
            <Brand light />
            <p>Helping customers and technicians manage everyday home services with more clarity.</p>
          </div>
          <div className="footer-column"><strong>For customers</strong><a href={backendHref(routes.customerSignup)}>Create account</a><a href={backendHref(routes.customerLogin)}>Customer login</a><a href={backendHref(routes.customerLogin)}>Browse services</a></div>
          <div className="footer-column"><strong>For technicians</strong><a href={backendHref(routes.technicianSignup)}>Join the network</a><a href={backendHref(routes.technicianLogin)}>Technician login</a><a href={backendHref(routes.technicianLogin)}>Manage jobs</a></div>
          <div className="footer-column"><strong>Platform</strong><a href="#how-it-works">How it works</a><a href="#why-seva">Features</a><a href={backendHref(routes.adminLogin)}>Admin access</a></div>
        </div>
        <div className="container footer-bottom"><span>© {new Date().getFullYear()} Seva Bandhu</span><span>Built to bring service and support closer to home.</span></div>
      </footer>
    </div>
  );
}

export default App;
