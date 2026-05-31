import React, { useState, useEffect } from 'react';
import { 
  Sparkles, 
  Search, 
  Calendar, 
  ArrowLeft, 
  ArrowRight, 
  Mail, 
  TrendingUp, 
  ShieldCheck, 
  Coins, 
  BookOpen, 
  ExternalLink,
  Github
} from 'lucide-react';

export default function App() {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedArticle, setSelectedArticle] = useState(null);
  const [activeFilter, setActiveFilter] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');
  const [newsletterEmail, setNewsletterEmail] = useState('');
  const [subscribed, setSubscribed] = useState(false);

  // Fetch articles from the static dynamic JSON registry
  useEffect(() => {
    fetch('/data/articles.json')
      .then(response => {
        if (!response.ok) {
          throw new Error("Registry is empty or failed to load");
        }
        return response.json();
      })
      .then(data => {
        setArticles(data);
        setLoading(false);
      })
      .catch(error => {
        console.warn("Could not load registry. Using beautiful default templates.", error);
        // Generous high-quality pre-seeded templates to ensure the user has a working demo instantly!
        setArticles(mockArticles);
        setLoading(false);
      });
  }, []);

  // Filter & Search Logic
  const getUniqueNiches = () => {
    const nichesSet = new Set(articles.map(art => art.niche));
    return ['All', ...Array.from(nichesSet)];
  };

  const filteredArticles = articles.filter(art => {
    const matchesNiche = activeFilter === 'All' || art.niche === activeFilter;
    const matchesSearch = art.topic.toLowerCase().includes(searchQuery.toLowerCase()) || 
                          art.brief.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesNiche && matchesSearch;
  });

  // 100% Free & Resilient Markdown Parser
  const parseMarkdown = (markdownText) => {
    if (!markdownText) return '';
    
    // Split into lines
    const lines = markdownText.split('\n');
    let inList = false;
    let listItems = [];
    const htmlElements = [];

    lines.forEach((line, index) => {
      let trimmed = line.trim();

      // Heading 1
      if (trimmed.startsWith('# ')) {
        htmlElements.push(<h1 key={index} style={{ fontSize: '32px', margin: '24px 0 16px', color: 'var(--text-primary)' }}>{parseInlineMarkdown(trimmed.substring(2))}</h1>);
        return;
      }
      // Heading 2
      if (trimmed.startsWith('## ')) {
        htmlElements.push(<h2 key={index}>{parseInlineMarkdown(trimmed.substring(3))}</h2>);
        return;
      }
      // Heading 3
      if (trimmed.startsWith('### ')) {
        htmlElements.push(<h3 key={index}>{parseInlineMarkdown(trimmed.substring(4))}</h3>);
        return;
      }
      // Blockquote
      if (trimmed.startsWith('> ')) {
        htmlElements.push(<blockquote key={index}><p>{parseInlineMarkdown(trimmed.substring(2))}</p></blockquote>);
        return;
      }
      // Bullet lists
      if (trimmed.startsWith('* ') || trimmed.startsWith('- ')) {
        listItems.push(<li key={`li-${index}`}>{parseInlineMarkdown(trimmed.substring(2))}</li>);
        inList = true;
        return;
      } else if (inList && trimmed === '') {
        htmlElements.push(<ul key={`ul-${index}`} style={{ paddingLeft: '20px', marginBottom: '20px' }}>{listItems}</ul>);
        listItems = [];
        inList = false;
        return;
      }

      // Preformatted Code blocks
      if (trimmed.startsWith('```')) {
        // Safe placeholder for code block contents - we just render simple lines as paragraphs or code blocks in demo
        return;
      }

      // Paragraph
      if (trimmed !== '') {
        htmlElements.push(<p key={index}>{parseInlineMarkdown(trimmed)}</p>);
      }
    });

    // Catch remaining list
    if (inList && listItems.length > 0) {
      htmlElements.push(<ul key="ul-end" style={{ paddingLeft: '20px', marginBottom: '20px' }}>{listItems}</ul>);
    }

    return htmlElements;
  };

  // Helper for bold, code tags, and links inside sentences
  const parseInlineMarkdown = (text) => {
    // 1. Process bold text (**bold**)
    let parts = [text];
    
    // Process markdown links [anchor](url)
    const linkRegex = /\[([^\]]+)\]\(([^)]+)\)/g;
    let match;
    const elements = [];
    let lastIndex = 0;

    // A simpler replacement helper
    const boldRegex = /\*\*([^*]+)\*\*/g;
    
    // Since we are running on static content, let's render standard text.
    // If it includes links, parse them cleanly:
    let textWithLinks = text;
    const matches = [...text.matchAll(linkRegex)];
    
    if (matches.length > 0) {
      let lastPos = 0;
      matches.forEach((m, idx) => {
        const preText = text.substring(lastPos, m.index);
        const anchorText = m[1];
        const linkUrl = m[2];
        
        elements.push(parseBoldText(preText, `pre-${idx}`));
        elements.push(
          <a href={linkUrl} target="_blank" rel="noopener noreferrer" key={`link-${idx}`}>
            {anchorText}
          </a>
        );
        lastPos = m.index + m[0].length;
      });
      elements.push(parseBoldText(text.substring(lastPos), 'post'));
      return elements;
    }

    return parseBoldText(text, 'plain');
  };

  const parseBoldText = (text, keyPrefix) => {
    const boldParts = text.split(/\*\*([^*]+)\*\*/);
    return boldParts.map((part, i) => {
      if (i % 2 === 1) {
        return <strong key={`${keyPrefix}-bold-${i}`} style={{ color: 'var(--text-primary)', fontWeight: '700' }}>{part}</strong>;
      }
      return part;
    });
  };

  const handleSubscribe = (e) => {
    e.preventDefault();
    if (newsletterEmail) {
      setSubscribed(true);
      setNewsletterEmail('');
      setTimeout(() => setSubscribed(false), 5000);
    }
  };

  const calculateReadingTime = (text) => {
    if (!text) return '3 min';
    const words = text.split(/\s+/).length;
    const minutes = Math.ceil(words / 225); // Standard average reading pace
    return `${minutes} min`;
  };

  return (
    <div>
      {/* Dynamic Floating Glass Header */}
      <header className="nav-header">
        <div className="nav-container">
          <div className="brand-logo" onClick={() => setSelectedArticle(null)}>
            ⚡ ZenithPress <span className="brand-badge">AI v2</span>
          </div>
          <div style={{ display: 'flex', gap: '20px', alignItems: 'center' }}>
            <a href="https://github.com" target="_blank" rel="noreferrer" style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px', color: 'var(--text-secondary)' }}>
              <Github size={16} /> Repository
            </a>
          </div>
        </div>
      </header>

      <main className="app-container">
        {!selectedArticle ? (
          /* ================= BLOG HOMEPAGE ================= */
          <div>
            <section className="hero-section">
              <h1 className="hero-title">
                Autonomous Tech & AI <span className="hero-highlight">Blogging Engine</span>
              </h1>
              <p className="hero-subtitle">
                An ultra-fast, search-optimized static publication written by Gemini, covered by FLUX.1 art, and deployed entirely for free.
              </p>

              {/* Real-time Search Box */}
              <div style={{ position: 'relative', maxWidth: '480px', margin: '0 auto 40px' }}>
                <Search size={18} style={{ position: 'absolute', left: '16px', top: '14px', color: 'var(--text-muted)' }} />
                <input 
                  type="text" 
                  placeholder="Search articles, technology trends, keywords..." 
                  className="newsletter-input" 
                  style={{ paddingLeft: '48px', width: '100%', borderRadius: '40px' }}
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>

              {/* Niche Tag Filters */}
              <div className="filter-tabs">
                {getUniqueNiches().map((niche) => (
                  <button 
                    key={niche} 
                    className={`filter-pill ${activeFilter === niche ? 'active' : ''}`}
                    onClick={() => setActiveFilter(niche)}
                  >
                    {niche}
                  </button>
                ))}
              </div>
            </section>

            {loading ? (
              <div className="empty-state">Loading latest AI publications...</div>
            ) : filteredArticles.length > 0 ? (
              <div className="articles-grid">
                {filteredArticles.map((art) => (
                  <article 
                    key={art.id} 
                    className="article-card"
                    onClick={() => setSelectedArticle(art)}
                  >
                    <div className="card-img-container">
                      <img 
                        src={art.coverImageLink || 'https://picsum.photos/800/600'} 
                        alt={art.topic} 
                        className="card-img"
                        onError={(e) => { e.target.src = 'https://picsum.photos/800/600'; }}
                      />
                      <span className="card-niche-tag">{art.niche}</span>
                    </div>
                    <div className="card-content">
                      <div className="card-meta">
                        <Calendar size={12} />
                        <span>{new Date(art.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}</span>
                        <span>•</span>
                        <span>{calculateReadingTime(art.article)} read</span>
                      </div>
                      <h2 className="card-title">{art.topic}</h2>
                      <p className="card-brief">{art.brief}</p>
                      <div className="card-footer">
                        <span>Read Article</span>
                        <ArrowRight size={14} className="read-arrow" />
                      </div>
                    </div>
                  </article>
                ))}
              </div>
            ) : (
              <div className="empty-state">
                <p>No articles found matching your criteria.</p>
                <button onClick={() => { setSearchQuery(''); setActiveFilter('All'); }} className="newsletter-btn" style={{ marginTop: '16px' }}>
                  Clear Filters
                </button>
              </div>
            )}
          </div>
        ) : (
          /* ================= PREMIUM ARTICLE READER ================= */
          <div className="reader-container">
            <div>
              <div className="back-btn" onClick={() => setSelectedArticle(null)}>
                <ArrowLeft size={16} /> Back to Publications
              </div>
              <img 
                src={selectedArticle.coverImageLink || 'https://picsum.photos/800/600'} 
                alt={selectedArticle.topic} 
                className="article-main-img" 
                onError={(e) => { e.target.src = 'https://picsum.photos/800/600'; }}
              />
              <div className="reader-header">
                <span className="reader-niche">{selectedArticle.niche}</span>
                <h1 className="reader-title">{selectedArticle.topic}</h1>
                <div className="reader-meta">
                  <span>Published: {new Date(selectedArticle.date).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}</span>
                  <span>•</span>
                  <span>Estimated Read: {calculateReadingTime(selectedArticle.article)}</span>
                  {selectedArticle.sourceUrl && (
                    <>
                      <span>•</span>
                      <a href={selectedArticle.sourceUrl} target="_blank" rel="noreferrer" style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', color: 'var(--neon-cyan)' }}>
                        Source <ExternalLink size={12} />
                      </a>
                    </>
                  )}
                </div>
              </div>

              {/* Renders the full article with custom styles */}
              <div className="article-markdown-body">
                {parseMarkdown(selectedArticle.article)}
              </div>
            </div>

            {/* Sidebar Monetization Panels */}
            <div className="sidebar-panel">
              {/* 💰 WIDGET 1: GOOGLE ADSENSE SIDEBAR BANNER PLACEHOLDER 💰 */}
              <div className="sidebar-widget">
                <h3 className="widget-title">Sponsored</h3>
                <div className="ad-container-placeholder">
                  <span className="ad-badge">Advertisement</span>
                  <Coins size={36} style={{ color: 'var(--text-muted)', marginBottom: '8px' }} />
                  <p style={{ fontWeight: '600' }}>AdSense Sidebar Placement</p>
                  <p style={{ fontSize: '11px', color: 'var(--text-muted)' }}>This glassmorphic banner will load premium high-paying ads upon AdSense approval.</p>
                </div>
              </div>

              {/* WIDGET 2: TRENDING RECOMMENDATIONS */}
              <div className="sidebar-widget">
                <h3 className="widget-title">Trending Tech</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginTop: '16px' }}>
                  {articles.slice(0, 3).map((a) => (
                    <div 
                      key={a.id} 
                      style={{ cursor: 'pointer', display: 'flex', gap: '12px' }}
                      onClick={() => setSelectedArticle(a)}
                    >
                      <img src={a.coverImageLink} alt={a.topic} style={{ width: '60px', height: '60px', borderRadius: '8px', objectFit: 'cover' }} onError={(e) => { e.target.src = 'https://picsum.photos/120/120'; }} />
                      <div>
                        <h4 style={{ fontSize: '13px', lineHeight: '1.4', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>{a.topic}</h4>
                        <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>{a.niche}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* WIDGET 3: TRUSTED VERIFICATION BADGE */}
              <div className="sidebar-widget" style={{ border: '1px solid rgba(6, 182, 212, 0.2)', background: 'rgba(6, 182, 212, 0.03)' }}>
                <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-start' }}>
                  <ShieldCheck size={24} style={{ color: 'var(--neon-cyan)', flexShrink: 0 }} />
                  <div>
                    <h4 style={{ fontSize: '14px', marginBottom: '4px' }}>Autonomous Safety Verified</h4>
                    <p style={{ fontSize: '12px', color: 'var(--text-secondary)', lineHeight: '1.4' }}>
                      Written via multi-agent pipelines and human-edited to guarantee high originality scores and strip automated formatting patterns.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Global Bottom Newsletter Capture */}
        <section className="newsletter-card">
          <h2 className="newsletter-title">Subscribe to ZenithPress AI</h2>
          <p className="newsletter-desc">
            Stay ahead of the tech curve. Receive our autonomously harvested tech breakdowns and AI reviews straight to your inbox. Zero spam.
          </p>
          {subscribed ? (
            <div style={{ color: 'var(--neon-cyan)', fontWeight: '600', padding: '10px' }}>
              ✓ Thank you! You have successfully joined the autonomous newsletter.
            </div>
          ) : (
            <form onSubmit={handleSubscribe} className="newsletter-form">
              <input 
                type="email" 
                placeholder="Enter your professional email address" 
                className="newsletter-input"
                required
                value={newsletterEmail}
                onChange={(e) => setNewsletterEmail(e.target.value)}
              />
              <button type="submit" className="newsletter-btn">
                Subscribe Newsletter
              </button>
            </form>
          )}
        </section>
      </main>

      <footer className="nav-footer">
        <div className="app-container">
          <div className="footer-links">
            <span style={{ cursor: 'pointer' }} onClick={() => setSelectedArticle(null)}>Home</span>
            <span>•</span>
            <a href="https://github.com" target="_blank" rel="noreferrer">Open Source Code</a>
            <span>•</span>
            <a href="https://vercel.com" target="_blank" rel="noreferrer">Powered by Vercel</a>
          </div>
          <p>© {new Date().getFullYear()} ZenithPress AI. Built with Antigravity for zero-cost autonomous operations.</p>
        </div>
      </footer>
    </div>
  );
}

// Beautiful Pre-seeded High-Quality Articles to guarantee out-of-the-box working website!
const mockArticles = [
  {
    id: 1,
    date: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
    niche: "Artificial Intelligence",
    topic: "FLUX.1-schnell vs Stable Diffusion: The New Reign of Open-Source Art",
    brief: "A head-to-head comparison of prompt adherence, photorealistic details, and dynamic font rendering speeds in Black Forest Labs' brand new FLUX model against Stable Diffusion XL.",
    coverImageLink: "https://images.unsplash.com/photo-1677442136019-21780efad99a?q=80&w=800&auto=format&fit=crop",
    article: `## The Open-Source Visual Revolution

There is a major shift happening in the landscape of AI-generated art. For years, Stable Diffusion XL was the undisputed gold standard for running open-source visual generators on consumer-grade hardware. However, a new challenger called **FLUX.1** has suddenly disrupted the status quo. 

Created by Black Forest Labs—a team comprising original Stable Diffusion developers—**[FLUX.1-schnell](https://huggingface.co/black-forest-labs/FLUX.1-schnell)** represents a giant leap forward in image fidelity, photorealistic anatomy rendering, and accurate typography representation.

### A Head-to-Head Comparison

1. **Typography Generation:** Unlike SDXL, which constantly outputs gibberish characters, FLUX can render complex text prompts on signs, screens, and labels with perfect spelling.
2. **Anatomy and Hands:** Traditional AI generators struggle with five-finger rendering. FLUX outputs flawless skeletal anatomies and detailed hand grips in almost every single generation.
3. **Speed and Efficiency:** The 'schnell' (fast) model is highly optimized, requiring only 4 inference steps to output an ultra-HD 1024x1024 graphic, making it perfect for free cloud runs.

### Monetizing Visual Creation

As visual generation becomes 100x faster, creators are leverage tools like **[Jasper AI Copywriter](https://www.jasper.ai/?utm_source=affiliate)** to combine high-speed writing with customized visual layouts to dominate blogging networks. Hosting your blog statically using high-speed CDN platforms is crucial to handle the image loading speeds.`,
    status: "Published",
    sourceUrl: "https://huggingface.co"
  },
  {
    id: 2,
    date: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
    niche: "Tech",
    topic: "Why Edge CDNs and Static Web Hosting is Completely Redefining Blog SEO",
    brief: "Discover how moving away from bloated WordPress servers to modern static architectures like Vercel can boost your site loading speed by 400% and instantly rank your articles higher on Google.",
    coverImageLink: "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?q=80&w=800&auto=format&fit=crop",
    article: `## The Death of Slow Servers

For decades, WordPress has dominated the blogging world. But loading a heavy database server on every page click comes at a major cost. Slow load times kill your user experience and destroy your search ranking. Modern SEO is heavily driven by speed.

By utilizing high-speed CDN platforms, developers are compiling articles into static files. The result? Load times under 200 milliseconds.

### The Power of CDN Web Hosting

When you host your site on Vercel or Netlify, the serverless backend distributes your entire site to thousands of servers across the globe. When a visitor clicks on your blog post, they receive it from the nearest data center instantly.

*   **Core Web Vitals:** Passing Google's speed benchmarks instantly boosts search visibility.
*   **Zero Database Outages:** Static blogs cannot get "server overloaded" or suffer database crashes.
*   **Security:** There are no SQL databases to hack, ensuring your site remains perfectly secure.

### The Financial Advantage

Combining zero-cost static hosting with premium, lightweight ad frameworks allows you to scale to millions of monthly views without spending a single dollar on **[Premium Web Hosting Solutions](https://www.hostinger.com/?referral=placeholder_id)**. Speed is your ultimate leverage in the modern web landscape.`,
    status: "Published",
    sourceUrl: "https://techcrunch.com"
  }
];
