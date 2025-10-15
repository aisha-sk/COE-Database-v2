export default function ChatView() {
  return (
    <section className="chat-page">
      <h2 className="chat-header">Traffic Volume Chat Assistant</h2>
      <div className="chat-frame-wrapper">
        <iframe
          className="chat-iframe"
          title="Traffic Volume Chat Assistant"
          src="http://localhost:8501"
          frameBorder="0"
          allowFullScreen
          loading="lazy"
        />
      </div>
    </section>
  );
}
