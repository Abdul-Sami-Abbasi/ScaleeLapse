import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  LayoutDashboard,
  Plus,
  Palette,
  Files,
  Sparkles,
  ShieldCheck,
  ChartNoAxesCombined,
  TrendingUp,
  ClipboardCheck,
  Users,
  Settings,
  LogOut,
  ArrowUpRight,
  ArrowRight,
  Check,
  Upload,
  LoaderCircle,
  Menu,
  Layers,
  Clock,
  ChevronRight,
  Image as ImageIcon,
} from "lucide-react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  LineChart,
  Line,
  Legend,
} from "recharts";
import { api } from "./api";
import "./style.css";

const nav = [
  ["Dashboard", LayoutDashboard],
  ["Create & Analyze", Plus],
  ["Brand Kit", Palette],
  ["My Posts", Files],
  ["AI Suggestions", Sparkles],
  ["Compliance", ShieldCheck],
  ["Analytics", ChartNoAxesCombined],
  ["Forecasting", TrendingUp],
  ["Approvals", ClipboardCheck],
  ["Team", Users],
  ["Settings", Settings],
];
const names = {
  DRAFT: "Draft",
  ANALYZING: "Analyzing",
  READY_FOR_REVIEW: "In review",
  CHANGES_REQUIRED: "Changes required",
  APPROVED: "Approved",
  READY_TO_PUBLISH: "Ready to publish",
};
export const Badge = ({ value }) => (
  <span className={"badge " + String(value).toLowerCase()}>
    {names[value] || String(value).replaceAll("_", " ")}
  </span>
);
const Empty = ({ title = "Nothing here yet", children }) => (
  <div className="empty">
    <Layers size={32} />
    <h3>{title}</h3>
    <p>
      {children ||
        "Your workspace will fill up as you create and analyze content."}
    </p>
  </div>
);
const Button = ({ children, busy, ...props }) => (
  <button {...props} disabled={busy || props.disabled}>
    {busy ? <LoaderCircle size={17} className="spin" /> : null}
    {children}
  </button>
);
function Field({ label, children }) {
  return (
    <label className="field">
      <span>{label}</span>
      {children}
    </label>
  );
}

function Auth({ onAuth }) {
  const [register, setRegister] = useState(false),
    [busy, setBusy] = useState(false),
    [error, setError] = useState("");
  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    const body = Object.fromEntries(new FormData(e.target));
    try {
      onAuth(
        await api("auth/" + (register ? "register/" : "login/"), {
          method: "POST",
          body,
        }),
      );
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }
  return (
    <div className="auth">
      <section className="auth-story">
        <div className="wordmark">
          <Layers /> ScaleeLapse<span>®</span>
        </div>
        <div>
          <span className="eyebrow">YOUR CONTENT. IN GOOD COMPANY.</span>
          <h1>
            Make every post
            <br />
            feel like <em>your brand.</em>
          </h1>
          <p>
            From first draft to final approval. A thoughtful workspace for
            consistent, confident content.
          </p>
          <div className="story-palette">
            <i />
            <i />
            <i />
            <i />
          </div>
        </div>
        <small>BRAND INTELLIGENCE · CONTENT OPERATIONS</small>
      </section>
      <section className="auth-form">
        <div>
          <span className="eyebrow">WELCOME TO YOUR WORKSPACE</span>
          <h2>
            {register
              ? "Start something consistent."
              : "Good to see you again."}
          </h2>
          <p>
            {register
              ? "Create your organization and invite your team."
              : "Sign in to keep your content moving."}
          </p>
          <form onSubmit={submit}>
            {register && (
              <Field label="Organization">
                <input name="organization" required maxLength={120} />
              </Field>
            )}
            <Field label="Username">
              <input
                name="username"
                required
                autoComplete="username"
                minLength={3}
              />
            </Field>
            {register && (
              <Field label="Email">
                <input name="email" type="email" />
              </Field>
            )}
            <Field label="Password">
              <input
                name="password"
                type="password"
                required
                minLength={8}
                autoComplete={register ? "new-password" : "current-password"}
              />
            </Field>
            {error && (
              <div role="alert" className="error">
                {error}
              </div>
            )}
            <Button busy={busy} className="primary">
              {register ? "Create workspace" : "Sign in"}
              <ArrowRight size={17} />
            </Button>
          </form>
          <button
            className="text-button"
            onClick={() => {
              setRegister(!register);
              setError("");
            }}
          >
            {register
              ? "Already have an account? Sign in"
              : "New here? Create a workspace"}
          </button>
        </div>
      </section>
    </div>
  );
}

function App() {
  const [user, setUser] = useState(null),
    [checking, setChecking] = useState(true),
    [page, setPage] = useState("Dashboard"),
    [brands, setBrands] = useState([]),
    [posts, setPosts] = useState([]),
    [stats, setStats] = useState(null),
    [selected, setSelected] = useState(null),
    [error, setError] = useState(""),
    [notice, setNotice] = useState(""),
    [busy, setBusy] = useState(false),
    [mobile, setMobile] = useState(false);
  const admin = user && ["OWNER", "ADMIN"].includes(user.role),
    reviewer = user && ["OWNER", "ADMIN", "REVIEWER"].includes(user.role);
  async function refresh() {
    const [b, p, s] = await Promise.all([
      api("brands/"),
      api("posts/"),
      api("dashboard/"),
    ]);
    setBrands(b);
    setPosts(p);
    setStats(s);
    if (selected) setSelected(p.find((x) => x.id === selected.id) || null);
  }
  useEffect(() => {
    api("auth/me/")
      .then(setUser)
      .catch(() => {})
      .finally(() => setChecking(false));
  }, []);
  useEffect(() => {
    if (user) refresh().catch((e) => setError(e.message));
  }, [user]);
  useEffect(() => {
    if (notice) {
      const t = setTimeout(() => setNotice(""), 6000);
      return () => clearTimeout(t);
    }
  }, [notice]);
  async function run(fn, message) {
    setBusy(true);
    setError("");
    try {
      const result = await fn();
      await refresh();
      if (message) setNotice(message);
      return result;
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }
  function go(p) {
    setPage(p);
    setSelected(null);
    setError("");
    setMobile(false);
  }
  if (checking)
    return (
      <div className="loading">
        <LoaderCircle className="spin" /> Opening workspace…
      </div>
    );
  if (!user) return <Auth onAuth={setUser} />;
  return (
    <div className="shell">
      <aside className={mobile ? "sidebar open" : "sidebar"}>
        <a className="wordmark" onClick={() => go("Dashboard")}>
          <Layers /> ScaleeLapse<span>®</span>
        </a>
        <div className="workspace">
          <span className="workspace-avatar">
            {user.organization[0].toUpperCase()}
          </span>
          <div>
            <strong>{user.organization}</strong>
            <small>
              {user.is_demo ? "SYNTHETIC DEMO DATA" : "Team workspace"}
            </small>
          </div>
        </div>
        <div className="nav-label">WORKSPACE</div>
        <nav>
          {nav.map(([n, I], i) => (
            <React.Fragment key={n}>
              {i === 9 && <div className="nav-label">MANAGE</div>}
              <button
                onClick={() => go(n)}
                className={page === n ? "active" : ""}
              >
                <I size={18} />
                {n}
                {n === "Approvals" && stats?.awaiting_review > 0 && (
                  <b>{stats.awaiting_review}</b>
                )}
              </button>
            </React.Fragment>
          ))}
        </nav>
        <div className="sidebar-bottom">
          <span className="live-dot" /> Human approval, always.
          <small>Built for thoughtful content teams.</small>
        </div>
      </aside>
      <main>
        <header className="topbar">
          <button
            className="icon-button mobile-toggle"
            aria-label="Toggle navigation"
            onClick={() => setMobile(!mobile)}
          >
            <Menu />
          </button>
          <span>
            Workspace <ChevronRight size={14} />{" "}
            <strong>{selected ? "Post details" : page}</strong>
          </span>
          <div className="user">
            <span className="avatar">
              {user.username.slice(0, 2).toUpperCase()}
            </span>
            <div>
              <strong>{user.username}</strong>
              <small>{user.role.toLowerCase()}</small>
            </div>
            <button
              className="icon-button"
              aria-label="Log out"
              onClick={async () => {
                await api("auth/logout/", { method: "POST" });
                setUser(null);
                setSelected(null);
                setBrands([]);
                setPosts([]);
                setStats(null);
                setPage("Dashboard");
              }}
            >
              <LogOut size={17} />
            </button>
          </div>
        </header>
        <div className="content">
          {user.is_demo && (
            <div className="demo-banner">
              SYNTHETIC DEMO DATA · For application testing only. Excluded from
              research results.
            </div>
          )}
          {error && (
            <div className="error" role="alert">
              {error}
              <button onClick={() => setError("")} aria-label="Dismiss error">
                ×
              </button>
            </div>
          )}
          {notice && (
            <div className="notice" role="status">
              <Check size={17} />
              {notice}
            </div>
          )}
          {selected ? (
            <PostDetail
              post={selected}
              user={user}
              run={run}
              busy={busy}
              setSelected={setSelected}
              brands={brands}
            />
          ) : (
            <>
              <div className="page-heading">
                <div>
                  <span className="eyebrow">
                    {page === "Dashboard"
                      ? "A LITTLE CLARITY. A LOT OF POSSIBILITY."
                      : "SCALEELAPSE WORKSPACE"}
                  </span>
                  <h1>
                    {page === "Dashboard" ? `Your content, in focus.` : page}
                  </h1>
                  <p>
                    {{
                      Dashboard:
                        "A clear view of your brand, your content, and what comes next.",
                      "Create & Analyze":
                        "Bring your next idea to life. We’ll help you check the details.",
                      "Brand Kit":
                        "One source of truth for every expression of your brand.",
                      "My Posts":
                        "From a first idea to a post your team is proud to share.",
                      Approvals:
                        "A human perspective before every publish-ready decision.",
                      Compliance:
                        "Source-backed rules and transparent pre-publish risk checks.",
                      Forecasting:
                        "Look ahead with account-specific historical engagement.",
                      Analytics:
                        "Understand your history before planning your next move.",
                    }[page] ||
                      "Everything you need to keep your team on the same page."}
                  </p>
                </div>
                {page === "Dashboard" && (
                  <button
                    className="primary"
                    onClick={() => go("Create & Analyze")}
                  >
                    <Plus size={18} /> Create a post
                  </button>
                )}
              </div>
              {page === "Dashboard" && (
                <>
                  <div className="stat-grid">
                    {[
                      [
                        "Content library",
                        stats?.posts,
                        Files,
                        "Posts in your workspace",
                      ],
                      [
                        "Awaiting review",
                        stats?.awaiting_review,
                        Clock,
                        "A fresh pair of eyes needed",
                      ],
                      [
                        "Ready to publish",
                        stats?.ready_to_publish,
                        Check,
                        "Reviewed and ready",
                      ],
                      [
                        "Active brands",
                        stats?.brands,
                        Palette,
                        "Distinct identities, one home",
                      ],
                    ].map(([n, v, I, s]) => (
                      <div className="stat-card" key={n}>
                        <div>
                          <span>{n}</span>
                          <I size={18} />
                        </div>
                        <strong>{v ?? "—"}</strong>
                        <small>{s}</small>
                      </div>
                    ))}
                  </div>
                  <div className="dashboard-grid">
                    <section className="card hero">
                      <div>
                        <span className="eyebrow">CONSISTENCY STARTS HERE</span>
                        <h2>
                          Good content.
                          <br />
                          On-brand, every time.
                        </h2>
                        <p>
                          Check your palette, find the right words, and give
                          your team a confident starting point.
                        </p>
                        <button onClick={() => go("Create & Analyze")}>
                          Analyze your next post <ArrowUpRight size={18} />
                        </button>
                      </div>
                      <div className="brand-art">
                        <div className="art-image">
                          <span>
                            made
                            <br />
                            <em>to belong.</em>
                          </span>
                          <small>YOUR BRAND, BEAUTIFULLY ALIGNED.</small>
                        </div>
                        <div className="art-palette">
                          <i />
                          <i />
                          <i />
                          <i />
                          <span>
                            <Check size={16} /> Palette intelligence
                          </span>
                        </div>
                      </div>
                    </section>
                    <section className="card checklist">
                      <span className="eyebrow">A BETTER CONTENT FLOW</span>
                      <h3>From idea to ready.</h3>
                      {[
                        [
                          "01",
                          "Define your brand",
                          "Add approved colors and assets.",
                        ],
                        [
                          "02",
                          "Create & analyze",
                          "Review color, content and risk.",
                        ],
                        [
                          "03",
                          "Get a second opinion",
                          "Keep people in the approval loop.",
                        ],
                      ].map(([n, t, d]) => (
                        <div className="step" key={n}>
                          <span>{n}</span>
                          <div>
                            <strong>{t}</strong>
                            <p>{d}</p>
                          </div>
                        </div>
                      ))}
                    </section>
                  </div>
                  <section className="card">
                    <div className="section-heading">
                      <h3>Recent content</h3>
                      <button
                        className="text-button"
                        onClick={() => go("My Posts")}
                      >
                        View all posts <ArrowRight size={15} />
                      </button>
                    </div>
                    <PostTable posts={posts.slice(0, 5)} select={setSelected} />
                  </section>
                  <div className="footnote">
                    <ShieldCheck size={16} /> Decision support for your team.
                    Every final approval stays with a person.
                  </div>
                </>
              )}
              {page === "Create & Analyze" && (
                <CreatePost
                  brands={brands}
                  run={run}
                  busy={busy}
                  onDone={setSelected}
                />
              )}
              {page === "Brand Kit" && (
                <Brands brands={brands} admin={admin} run={run} busy={busy} />
              )}
              {page === "My Posts" && (
                <section className="card">
                  <PostTable posts={posts} select={setSelected} />
                </section>
              )}
              {page === "Approvals" && (
                <>
                  <div className="info">
                    {reviewer
                      ? "Review findings, Brand Kit and image before deciding. You cannot approve your own post."
                      : "Your submitted posts appear here. A reviewer or manager makes the final decision."}
                  </div>
                  <section className="card">
                    <PostTable
                      posts={posts.filter((p) =>
                        [
                          "READY_FOR_REVIEW",
                          "APPROVED",
                          "CHANGES_REQUIRED",
                        ].includes(p.status),
                      )}
                      select={setSelected}
                    />
                  </section>
                </>
              )}
              {page === "AI Suggestions" && (
                <div className="grid-2">
                  {posts
                    .filter((p) => p.analyses.ai_suggestion)
                    .map((p) => (
                      <section className="card" key={p.id}>
                        <h3>{p.title}</h3>
                        <Suggestions data={p.analyses.ai_suggestion} />
                        <button
                          className="text-button"
                          onClick={() => setSelected(p)}
                        >
                          Open post <ArrowRight size={16} />
                        </button>
                      </section>
                    ))}
                  {!posts.some((p) => p.analyses.ai_suggestion) && (
                    <Empty title="Give your ideas a starting point">
                      Analyze a post to see hashtag and editorial suggestions.
                    </Empty>
                  )}
                </div>
              )}
              {page === "Compliance" && (
                <Compliance
                  admin={admin}
                  run={run}
                  busy={busy}
                  posts={posts}
                  select={setSelected}
                />
              )}
              {["Analytics", "Forecasting"].includes(page) && (
                <Forecasting
                  brands={brands}
                  run={run}
                  busy={busy}
                  analytics={page === "Analytics"}
                />
              )}
              {page === "Team" && <Team admin={admin} run={run} busy={busy} />}
              {page === "Settings" && (
                <SettingsPage user={user} run={run} busy={busy} />
              )}
            </>
          )}
        </div>
      </main>
    </div>
  );
}

function PostTable({ posts, select }) {
  if (!posts.length)
    return (
      <Empty title="A fresh start for your content">
        Create your first post, add an image, and let the analysis begin.
      </Empty>
    );
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>CONTENT</th>
            <th>BRAND / CHANNEL</th>
            <th>BRAND SCORE</th>
            <th>STATUS</th>
            <th>CREATED</th>
            <th />
          </tr>
        </thead>
        <tbody>
          {posts.map((p) => (
            <tr key={p.id}>
              <td>
                <button className="post-title" onClick={() => select(p)}>
                  {p.image_url ? (
                    <img src={p.image_url} alt="" />
                  ) : (
                    <span className="image-placeholder">
                      <ImageIcon size={20} />
                    </span>
                  )}
                  <strong>{p.title}</strong>
                </button>
              </td>
              <td>
                {p.brand_name}
                <small>{p.platform.toLowerCase()}</small>
              </td>
              <td>
                {p.analyses.visual_analysis?.score ?? "—"}
                {p.analyses.visual_analysis?.score != null && (
                  <small>/ 100 color coverage</small>
                )}
              </td>
              <td>
                <Badge value={p.status} />
              </td>
              <td>
                {new Date(p.created_at).toLocaleDateString(undefined, {
                  month: "short",
                  day: "numeric",
                })}
              </td>
              <td>
                <button
                  className="icon-button"
                  aria-label={"Open " + p.title}
                  onClick={() => select(p)}
                >
                  <ArrowUpRight size={18} />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function CreatePost({ brands, run, busy, onDone }) {
  const [image, setImage] = useState(null),
    [preview, setPreview] = useState("");
  useEffect(() => {
    if (!image) return;
    const url = URL.createObjectURL(image);
    setPreview(url);
    return () => URL.revokeObjectURL(url);
  }, [image]);
  async function submit(e) {
    e.preventDefault();
    const body = Object.fromEntries(new FormData(e.target));
    delete body.image;
    const analyze = e.nativeEvent.submitter?.value === "analyze";
    await run(
      async () => {
        const p = await api("posts/", { method: "POST", body });
        onDone(p);
        if (image) {
          const fd = new FormData();
          fd.append("image", image);
          const uploaded = await api(`posts/${p.id}/image/`, {
            method: "POST",
            body: fd,
          });
          onDone(uploaded);
        }
        if (analyze) {
          const result = await api(`posts/${p.id}/analyze/`, {
            method: "POST",
          });
          onDone(result);
        }
      },
      analyze
        ? "Analysis complete. Review your findings below."
        : "Draft saved.",
    );
  }
  if (!brands.length)
    return (
      <Empty title="Start with a Brand Kit">
        An owner or administrator can create a brand in the Brand Kit page.
      </Empty>
    );
  return (
    <form onSubmit={submit} className="create-grid">
      <section className="card">
        <div className="section-heading">
          <h3>Your next post</h3>
          <Badge value="DRAFT" />
        </div>
        <Field label="Post title">
          <input
            name="title"
            required
            maxLength={160}
            placeholder="Give this idea a name"
          />
        </Field>
        <div className="grid-2">
          <Field label="Brand">
            <select name="brand">
              {brands.map((b) => (
                <option key={b.id} value={b.id}>
                  {b.name}
                </option>
              ))}
            </select>
          </Field>
          <Field label="Platform">
            <select name="platform">
              <option value="INSTAGRAM">Instagram</option>
              <option value="FACEBOOK">Facebook</option>
            </select>
          </Field>
        </div>
        <Field label="Caption">
          <textarea
            name="caption"
            required
            maxLength={10000}
            rows={7}
            placeholder="What’s the story behind this post?"
          />
        </Field>
        <div className="info small-info">
          Suggestions support English captions. A reviewer makes the final
          content decision.
        </div>
        <div className="actions">
          <Button
            busy={busy}
            className="primary"
            value="analyze"
            disabled={!image}
          >
            <Sparkles size={17} /> Analyze post
          </Button>
          <Button busy={busy} className="secondary" value="draft">
            Save draft
          </Button>
        </div>
      </section>
      <section className="card">
        <h3>The visual side</h3>
        <p className="muted">Upload the image your audience will see.</p>
        <label className="upload-box">
          {preview ? (
            <img src={preview} alt="Selected post preview" />
          ) : (
            <>
              <Upload size={30} />
              <strong>Choose your post image</strong>
              <span>JPEG, PNG or WebP · up to 10 MB</span>
            </>
          )}
          <input
            aria-label="Post image"
            name="image"
            type="file"
            accept="image/jpeg,image/png,image/webp"
            onChange={(e) => setImage(e.target.files[0])}
          />
        </label>
        <div className="image-note">
          <Palette size={18} />
          <p>
            We’ll extract the dominant palette and compare it with your approved
            Brand Kit.
          </p>
        </div>
      </section>
    </form>
  );
}

function Suggestions({ data }) {
  return (
    <>
      <Badge value={data.status} />
      {data.notice && <p className="muted">{data.notice}</p>}
      <div className="tags">
        {data.hashtags.map((t) => (
          <span key={t}>{t}</span>
        ))}
      </div>
      {data.editorial_keywords?.length > 0 && (
        <div className="info">
          <strong>Caption keywords · editorial aid</strong>
          <p>{data.editorial_keywords.join(" ")}</p>
        </div>
      )}
      {data.validation?.precision_at_k != null && (
        <p className="muted">
          Held-out Precision@10:{" "}
          {(data.validation.precision_at_k * 100).toFixed(2)}%. Check relevance
          before using these experimental predictions.
        </p>
      )}
      {data.withheld_hashtags?.length > 0 && (
        <p className="warning">
          {data.withheld_hashtags.length} suggestions withheld by configured
          risk rules.
        </p>
      )}
      {data.cta && <p className="info">Editorial suggestion: {data.cta}</p>}
    </>
  );
}
function Results({ analyses }) {
  const v = analyses.visual_analysis,
    a = analyses.ai_suggestion,
    c = analyses.compliance_result;
  if (!v)
    return (
      <Empty title="Ready for a closer look">
        Upload an image and analyze this post to see your findings.
      </Empty>
    );
  return (
    <div className="grid-2">
      <section className="card">
        <div className="section-heading">
          <h3>Brand intelligence</h3>
          <Palette size={20} />
        </div>
        <div className="score">
          <strong>{v.score ?? "—"}</strong>
          <span>
            / 100
            <br />
            Color coverage score
          </span>
        </div>
        <div className="palette-bar">
          {v.palette.map((p, i) => (
            <div
              key={i}
              title={`${p.hex}: ${p.percentage}%`}
              style={{ background: p.hex, width: p.percentage + "%" }}
            />
          ))}
        </div>
        <div className="palette-list">
          {v.palette.map((p, i) => (
            <div key={i}>
              <i style={{ background: p.hex }} />
              <code>{p.hex}</code>
              <span>{p.percentage.toFixed(1)}%</span>
              <Badge value={p.matched ? "MATCHED" : "REVIEW"} />
            </div>
          ))}
        </div>
        {v.warnings.map((w) => (
          <p className="warning" key={w}>
            {w}
          </p>
        ))}
        <p className="muted">
          Logo: {v.logo.status}. {v.logo.reason}
        </p>
        <p className="muted">
          Fonts: {v.fonts.status}. {v.fonts.reason}
        </p>
        <p className="muted">
          Image reuse: {v.design_fatigue?.exact_duplicate_posts ?? 0} exact
          duplicate posts. This is a review flag, not a fatigue diagnosis.
        </p>
      </section>
      <div className="stack">
        <section className="card">
          <h3>AI content assistant</h3>
          <Suggestions data={a} />
        </section>
        <section className="card">
          <div className="section-heading">
            <h3>Pre-publish risk assessment</h3>
            <Badge value={c.level} />
          </div>
          <p className="muted">
            {c.rules_checked} configured rules checked ·{" "}
            {c.coverage.replaceAll("_", " ")}
          </p>
          {c.findings.map((f, i) => (
            <div key={i} className="finding">
              <Badge value={f.severity} />
              <p>{f.explanation}</p>
              <small>Source: {f.source}</small>
              <p>{f.recommendation}</p>
            </div>
          ))}
          {!c.findings.length && <p>No configured rule matches found.</p>}
          <p className="muted">{c.toxicity}</p>
          <div className="info">{c.disclaimer}</div>
        </section>
      </div>
    </div>
  );
}

function PostDetail({ post, user, run, busy, setSelected, brands }) {
  const [comment, setComment] = useState(""),
    [editing, setEditing] = useState(false);
  const editable =
    ["DRAFT", "CHANGES_REQUIRED"].includes(post.status) &&
    ["OWNER", "ADMIN", "CREATOR"].includes(user.role);
  async function transition(decision) {
    await run(
      async () =>
        setSelected(
          await api(`posts/${post.id}/transition/`, {
            method: "POST",
            body: { decision, comments: comment },
          }),
        ),
      "Workflow updated.",
    );
  }
  return (
    <>
      <div className="page-heading">
        <div>
          <span className="eyebrow">
            {post.brand_name} / {post.platform}
          </span>
          <h1>{post.title}</h1>
          <Badge value={post.status} />
        </div>
        <button className="secondary" onClick={() => setSelected(null)}>
          Back to workspace
        </button>
      </div>
      <section className="card post-summary">
        {post.image_url && <img src={post.image_url} alt={post.title} />}
        <div>
          <h3>The story</h3>
          <p className="caption">{post.caption}</p>
          {post.scheduled_at && (
            <p>
              Planned for {new Date(post.scheduled_at).toLocaleString()} ·
              Manual publishing
            </p>
          )}
          <div className="actions">
            {editable && (
              <>
                <Button
                  busy={busy}
                  className="primary"
                  onClick={() =>
                    run(
                      async () =>
                        setSelected(
                          await api(`posts/${post.id}/analyze/`, {
                            method: "POST",
                          }),
                        ),
                      "Analysis complete.",
                    )
                  }
                >
                  <Sparkles size={16} /> Analyze
                </Button>
                <button
                  className="secondary"
                  onClick={() => setEditing(!editing)}
                >
                  Edit draft
                </button>
                <Button
                  busy={busy}
                  className="secondary"
                  disabled={!post.analyses.visual_analysis}
                  onClick={() => transition("SUBMIT")}
                >
                  Submit for review
                </Button>
              </>
            )}
            {[
              "READY_FOR_REVIEW",
              "APPROVED",
              "READY_TO_PUBLISH",
              "CHANGES_REQUIRED",
            ].includes(post.status) &&
              user.role !== "REVIEWER" && (
                <Button
                  busy={busy}
                  className="secondary"
                  onClick={() => transition("REOPEN")}
                >
                  Return to draft
                </Button>
              )}
            {editable && (
              <Button
                busy={busy}
                className="secondary danger"
                onClick={() => {
                  if (confirm("Delete this draft?"))
                    run(async () => {
                      await api(`posts/${post.id}/`, { method: "DELETE" });
                      setSelected(null);
                    }, "Draft deleted.");
                }}
              >
                Delete draft
              </Button>
            )}
            <a
              className="button secondary"
              href={`/api/posts/${post.id}/export/`}
              target="_blank"
              rel="noreferrer"
            >
              JSON
            </a>
            <a
              className="button secondary"
              href={`/api/posts/${post.id}/export/?export=csv`}
              target="_blank"
              rel="noreferrer"
            >
              Palette CSV
            </a>
          </div>
        </div>
      </section>
      {editing && editable && (
        <form
          className="card"
          onSubmit={(e) => {
            e.preventDefault();
            const body = Object.fromEntries(new FormData(e.target));
            body.scheduled_at = body.scheduled_at
              ? new Date(body.scheduled_at).toISOString()
              : null;
            run(async () => {
              setSelected(
                await api(`posts/${post.id}/`, { method: "PATCH", body }),
              );
              setEditing(false);
            }, "Draft updated. Re-analyze before submission.");
          }}
        >
          <Field label="Title">
            <input name="title" defaultValue={post.title} required />
          </Field>
          <Field label="Caption">
            <textarea name="caption" defaultValue={post.caption} required />
          </Field>
          <Field label="Planned date and time (manual publishing)">
            <input
              name="scheduled_at"
              type="datetime-local"
              defaultValue={
                post.scheduled_at
                  ? new Date(
                      new Date(post.scheduled_at).getTime() -
                        new Date(post.scheduled_at).getTimezoneOffset() * 60000,
                    )
                      .toISOString()
                      .slice(0, 16)
                  : ""
              }
            />
          </Field>
          <Button className="primary" busy={busy}>
            Save changes
          </Button>
        </form>
      )}
      {editable && (
        <section className="card">
          <Field label="Upload or replace image">
            <input
              type="file"
              accept="image/png,image/jpeg,image/webp"
              onChange={(e) => {
                if (e.target.files[0]) {
                  const body = new FormData();
                  body.append("image", e.target.files[0]);
                  run(
                    async () =>
                      setSelected(
                        await api(`posts/${post.id}/image/`, {
                          method: "POST",
                          body,
                        }),
                      ),
                    "Image saved.",
                  );
                }
              }}
            />
          </Field>
        </section>
      )}
      <Results analyses={post.analyses} />
      {["OWNER", "ADMIN", "REVIEWER"].includes(user.role) &&
        post.creator !== user.id &&
        ["READY_FOR_REVIEW", "APPROVED"].includes(post.status) && (
          <section className="card">
            <h3>Reviewer decision</h3>
            <Field label="Review comments (required for approval or changes)">
              <textarea
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                placeholder="Record your review of brand, content and risk findings."
              />
            </Field>
            <div className="actions">
              {post.status === "READY_FOR_REVIEW" ? (
                <>
                  <Button
                    busy={busy}
                    className="primary"
                    onClick={() => transition("APPROVE")}
                  >
                    Approve
                  </Button>
                  <Button
                    busy={busy}
                    className="secondary"
                    onClick={() => transition("REQUEST_CHANGES")}
                  >
                    Request changes
                  </Button>
                </>
              ) : (
                <Button
                  busy={busy}
                  className="primary"
                  onClick={() => transition("MARK_READY")}
                >
                  Mark ready to publish
                </Button>
              )}
            </div>
          </section>
        )}
      <section className="card">
        <h3>Review history</h3>
        {post.approvals.length ? (
          post.approvals.map((a) => (
            <div className="history" key={a.id}>
              <Badge value={a.decision} />
              <strong>{a.reviewer__username}</strong>
              <span>{new Date(a.created_at).toLocaleString()}</span>
              <p>{a.comments}</p>
            </div>
          ))
        ) : (
          <p className="muted">No review decisions yet.</p>
        )}
      </section>
    </>
  );
}

function Brands({ brands, admin, run, busy }) {
  const [edit, setEdit] = useState(null),
    [adding, setAdding] = useState(false),
    [batchResult, setBatchResult] = useState(null);
  async function save(e) {
    e.preventDefault();
    const fd = Object.fromEntries(new FormData(e.target));
    const colors = fd.colors
      .split("\n")
      .filter((x) => x.trim())
      .map((line) => {
        const [hex, role = "PRIMARY"] = line.trim().split(/\s+/);
        return { hex, role: role.toUpperCase() };
      });
    const body = {
      ...fd,
      colors,
      fonts: fd.fonts
        .split(",")
        .map((x) => x.trim())
        .filter(Boolean),
      tolerance: Number(fd.tolerance),
    };
    await run(async () => {
      await api(edit ? `brands/${edit.id}/` : "brands/", {
        method: edit ? "PATCH" : "POST",
        body,
      });
      setEdit(null);
      setAdding(false);
    }, "Brand Kit saved.");
  }
  return (
    <>
      <div className="actions">
        {admin && (
          <button
            className="primary"
            onClick={() => {
              setEdit(null);
              setAdding(!adding);
            }}
          >
            <Plus size={17} /> Add brand
          </button>
        )}
      </div>
      {(adding || edit) && (
        <form onSubmit={save} className="card" key={edit?.id || "new"}>
          <h3>{edit ? "Edit Brand Kit" : "Create a Brand Kit"}</h3>
          <div className="grid-2">
            <Field label="Brand name">
              <input name="name" required defaultValue={edit?.name} />
            </Field>
            <Field label="Brand Kit source / owner approval">
              <input
                name="kit_source"
                placeholder="Official guideline URL or owner-provided reference"
                defaultValue={edit?.kit_source}
              />
            </Field>
          </div>
          <Field label="Description">
            <input name="description" defaultValue={edit?.description} />
          </Field>
          <Field label="Colors: one HEX and role per line (PRIMARY, SECONDARY, BACKGROUND)">
            <textarea
              name="colors"
              rows={4}
              placeholder={
                "#143D35 PRIMARY\n#E8BFA5 SECONDARY\n#FAF8F4 BACKGROUND"
              }
              defaultValue={edit?.colors
                .map((c) => `${c.hex} ${c.role}`)
                .join("\n")}
            />
          </Field>
          <div className="grid-2">
            <Field label="Approved fonts (comma-separated)">
              <input name="fonts" defaultValue={edit?.fonts.join(", ")} />
            </Field>
            <Field label="Color tolerance (0.01–0.5)">
              <input
                name="tolerance"
                type="number"
                min="0.01"
                max="0.5"
                step="0.01"
                defaultValue={edit?.tolerance ?? 0.15}
              />
            </Field>
          </div>
          <Field label="Brand rules for reviewers">
            <textarea name="rules" defaultValue={edit?.rules} />
          </Field>
          <div className="actions">
            <Button busy={busy} className="primary">
              Save Brand Kit
            </Button>
            <button
              type="button"
              className="secondary"
              onClick={() => {
                setEdit(null);
                setAdding(false);
              }}
            >
              Cancel
            </button>
          </div>
        </form>
      )}
      <div className="grid-2">
        {brands.map((b) => (
          <section className="card brand-card" key={b.id}>
            <div className="section-heading">
              <h3>{b.name}</h3>
              {admin && (
                <button
                  className="text-button"
                  onClick={() => {
                    setEdit(b);
                    setAdding(false);
                  }}
                >
                  Edit <ArrowUpRight size={15} />
                </button>
              )}
            </div>
            <p>{b.description}</p>
            <div className="brand-swatches">
              {b.colors.map((c, i) => (
                <div key={i}>
                  <i style={{ background: c.hex }} />
                  <strong>{c.hex}</strong>
                  <small>{c.role.toLowerCase()}</small>
                </div>
              ))}
            </div>
            {!b.colors.length && (
              <div className="warning">
                Brand Kit colors required for scoring.
              </div>
            )}
            <p className="muted">
              Fonts: {b.fonts.join(", ") || "Not provided"}
              <br />
              Source: {b.kit_source || "Not provided"}
              <br />
              Tolerance: {b.tolerance}
            </p>
            {b.rules && <p className="info">{b.rules}</p>}
            <div className="logos">
              {b.assets.map((a) => (
                <img key={a.id} src={a.url} alt={`${b.name} logo`} />
              ))}
            </div>
            {admin && (
              <Field label="Add brand logo">
                <input
                  type="file"
                  accept="image/png,image/jpeg,image/webp"
                  onChange={(e) => {
                    if (!e.target.files[0]) return;
                    const body = new FormData();
                    body.append("image", e.target.files[0]);
                    run(
                      () =>
                        api(`brands/${b.id}/logo/`, { method: "POST", body }),
                      "Logo saved.",
                    );
                  }}
                />
              </Field>
            )}
            <Field label="Batch image audit (up to 20)">
              <input
                type="file"
                multiple
                accept="image/png,image/jpeg,image/webp"
                onChange={(e) => {
                  const body = new FormData();
                  for (const f of e.target.files) body.append("images", f);
                  run(
                    async () =>
                      setBatchResult(
                        await api(`brands/${b.id}/batch/`, {
                          method: "POST",
                          body,
                        }),
                      ),
                    "Batch audit complete.",
                  );
                }}
              />
            </Field>
            {admin && (
              <button
                className="text-button danger"
                onClick={() => {
                  if (
                    confirm(
                      `Delete ${b.name}? Brands with posts cannot be deleted.`,
                    )
                  )
                    run(
                      () => api(`brands/${b.id}/`, { method: "DELETE" }),
                      "Brand deleted.",
                    );
                }}
              >
                Delete brand
              </button>
            )}
          </section>
        ))}
      </div>
      {!brands.length && !adding && (
        <Empty title="Your brand belongs here">
          Add approved colors, a logo, and the guidelines that make your brand
          yours.
        </Empty>
      )}
      {batchResult && (
        <section className="card">
          <h3>Batch results</h3>
          {batchResult.map((r, i) => (
            <p key={i}>
              {r.filename}:{" "}
              {r.error || `${r.result.score ?? "Kit required"} / 100`}
            </p>
          ))}
          <button
            className="secondary"
            onClick={() => {
              const u = URL.createObjectURL(
                new Blob([JSON.stringify(batchResult, null, 2)], {
                  type: "application/json",
                }),
              );
              const a = document.createElement("a");
              a.href = u;
              a.download = "batch-audit.json";
              a.click();
              URL.revokeObjectURL(u);
            }}
          >
            Download JSON
          </button>
        </section>
      )}
    </>
  );
}

function Compliance({ admin, run, busy, posts, select }) {
  const [rules, setRules] = useState([]);
  useEffect(() => {
    api("rules/").then(setRules);
  }, []);
  return (
    <>
      <div className="info">
        A rule is only as reliable as its source. No platform restrictions are
        invented or bundled. Add reviewed rules with provenance; spam checks are
        local editorial heuristics.
      </div>
      {admin && (
        <form
          className="card"
          onSubmit={(e) => {
            e.preventDefault();
            const body = Object.fromEntries(new FormData(e.target));
            run(async () => {
              await api("rules/", { method: "POST", body });
              setRules(await api("rules/"));
              e.target.reset();
            }, "Sourced rule added.");
          }}
        >
          <h3>Add a reviewed rule</h3>
          <div className="grid-3">
            <Field label="Term / hashtag">
              <input name="term" required />
            </Field>
            <Field label="Match type">
              <select name="kind">
                <option value="HASHTAG">Hashtag</option>
                <option value="TEXT">Caption text</option>
              </select>
            </Field>
            <Field label="Severity">
              <select name="severity">
                <option>MEDIUM</option>
                <option>HIGH</option>
                <option>LOW</option>
              </select>
            </Field>
          </div>
          <div className="grid-2">
            <Field label="Platform">
              <select name="platform">
                <option>ALL</option>
                <option>INSTAGRAM</option>
                <option>FACEBOOK</option>
              </select>
            </Field>
            <Field label="Source URL / internal policy provenance">
              <input name="source" required minLength={8} />
            </Field>
          </div>
          <Field label="Explanation">
            <input name="explanation" required />
          </Field>
          <Button className="primary" busy={busy}>
            Save rule
          </Button>
        </form>
      )}
      <section className="card">
        <h3>Configured rules</h3>
        {rules.length ? (
          rules.map((r) => (
            <div className="rule-row" key={r.id}>
              <strong>{r.term}</strong>
              <Badge value={r.severity} />
              <span>
                {r.platform} · {r.source}
              </span>
              {admin && (
                <button
                  className="text-button danger"
                  onClick={() =>
                    run(async () => {
                      await api(`rules/${r.id}/`, { method: "DELETE" });
                      setRules(await api("rules/"));
                    }, "Rule removed.")
                  }
                >
                  Remove
                </button>
              )}
            </div>
          ))
        ) : (
          <Empty title="No sourced rules yet">
            Manual review is required. A low score does not establish platform
            compliance.
          </Empty>
        )}
      </section>
      <section className="card">
        <h3>Analyzed content</h3>
        <PostTable
          posts={posts.filter((p) => p.analyses.compliance_result)}
          select={select}
        />
      </section>
    </>
  );
}

function Forecasting({ brands, run, busy, analytics }) {
  const [history, setHistory] = useState([]),
    [selected, setSelected] = useState(null);
  useEffect(() => {
    api("forecasts/").then((h) => {
      setHistory(h);
      setSelected(h[0]);
    });
  }, []);
  const data = selected?.result;
  return (
    <>
      {!analytics && (
        <form
          className="card"
          onSubmit={(e) => {
            e.preventDefault();
            const body = new FormData(e.target);
            run(async () => {
              const r = await api("forecasts/", { method: "POST", body });
              setSelected(r);
              setHistory(await api("forecasts/"));
            }, "Forecast and chronological evaluation complete.");
          }}
        >
          <h3>Bring your history. Find your direction.</h3>
          <p className="muted">
            At least 20 observed days. Select an account when importing a
            multi-account dataset.
          </p>
          <div className="grid-3">
            <Field label="Brand">
              <select name="brand" required>
                {brands.map((b) => (
                  <option key={b.id} value={b.id}>
                    {b.name}
                  </option>
                ))}
              </select>
            </Field>
            <Field label="Metric">
              <select name="metric">
                {[
                  "likes",
                  "comments",
                  "shares",
                  "saves",
                  "reach",
                  "impressions",
                  "follower_count",
                  "engagement_rate",
                ].map((m) => (
                  <option key={m}>{m}</option>
                ))}
              </select>
            </Field>
            <Field label="Account ID (if present in CSV)">
              <input name="account_id" />
            </Field>
            <Field label="Model">
              <select name="model">
                <option value="arima">ARIMA (1,1,1)</option>
                <option value="prophet">Prophet (optional dependency)</option>
              </select>
            </Field>
            <Field label="Forecast days">
              <input
                name="horizon"
                type="number"
                defaultValue={7}
                min={1}
                max={60}
              />
            </Field>
            <Field label="Historical CSV">
              <input name="file" type="file" accept=".csv" required />
            </Field>
          </div>
          <Field label="Source / provenance">
            <input
              name="provenance"
              required
              placeholder="Owner export, date, consent and data limitations"
            />
          </Field>
          <label className="checkbox">
            <input type="checkbox" name="is_demo" value="true" /> This is
            synthetic/demo data
          </label>
          <Button busy={busy} className="primary" disabled={!brands.length}>
            <TrendingUp size={17} /> Generate forecast
          </Button>
        </form>
      )}
      {history.length > 0 && (
        <Field label="Saved forecast">
          <select
            value={selected?.id || ""}
            onChange={(e) =>
              setSelected(history.find((x) => x.id === Number(e.target.value)))
            }
          >
            {history.map((h) => (
              <option key={h.id} value={h.id}>
                #{h.id} · {h.brand} · {h.result.metric} · {h.result.model}
                {h.is_demo ? " · SYNTHETIC DEMO" : ""}
              </option>
            ))}
          </select>
        </Field>
      )}
      {data ? (
        <>
          {selected.is_demo && (
            <div className="demo-banner">
              SYNTHETIC DEMO DATA — these metrics are not academic results.
            </div>
          )}
          <div className="stat-grid">
            {[
              ["Held-out MAE", data.evaluation.mae.toFixed(2)],
              ["Held-out RMSE", data.evaluation.rmse.toFixed(2)],
              ["Observed days", data.eda.observed_days],
              ["Missing days", data.eda.missing_days],
            ].map(([n, v]) => (
              <div className="stat-card" key={n}>
                <span>{n}</span>
                <strong>{v}</strong>
              </div>
            ))}
          </div>
          <section className="card">
            <h3>Historical trend & forecast</h3>
            <p className="muted">
              {data.metric} · {data.aggregation}
            </p>
            <div className="chart">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart
                  data={[
                    ...data.history.map((h) => ({ ...h, history: h.value })),
                    ...data.forecast.map((f) => ({ ...f, forecast: f.value })),
                  ]}
                >
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="date" minTickGap={70} />
                  <YAxis width={55} />
                  <Tooltip />
                  <Legend />
                  <Line dataKey="history" stroke="#19725d" dot={false} />
                  <Line dataKey="forecast" stroke="#c17b50" dot={false} />
                  <Line
                    dataKey="lower"
                    stroke="#b9cfc5"
                    dot={false}
                    strokeDasharray="3 3"
                  />
                  <Line
                    dataKey="upper"
                    stroke="#b9cfc5"
                    dot={false}
                    strokeDasharray="3 3"
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
            <p className="muted">{data.notes}</p>
            <ForecastInsights data={data} />
          </section>
          <div className="grid-2">
            <section className="card">
              <h3>Chronological evaluation</h3>
              <p>
                Past 80% for training; later 20% held out. Test begins{" "}
                {data.evaluation.split_date}.
              </p>
              <p>
                {data.evaluation.test_observations} observed test days.
                Normalized MAE:{" "}
                {data.evaluation.normalized_mae_percent?.toFixed(2) ??
                  "undefined"}
                %.
              </p>
              <p className="muted">
                The final forecast refits on all supplied history. No
                target-achievement claim is made from this import.
              </p>
            </section>
            <section className="card">
              <h3>Content category associations</h3>
              {data.eda.categories.length ? (
                data.eda.categories
                  .sort((a, b) => b.mean - a.mean)
                  .map((c) => (
                    <div className="rule-row" key={c.content_category}>
                      <strong>{c.content_category}</strong>
                      <span>
                        {c.mean.toFixed(2)} mean · {c.count} posts
                      </span>
                    </div>
                  ))
              ) : (
                <p>No content_category column supplied.</p>
              )}
              <p className="muted">
                Historical association does not imply causation.
              </p>
            </section>
          </div>
        </>
      ) : (
        <Empty title="A clearer picture starts with history">
          Upload an account’s engagement CSV in Forecasting to see trends and
          model evaluation.
        </Empty>
      )}
    </>
  );
}

function ForecastInsights({ data }) {
  const observed = data.history.filter((x) => x.value != null).slice(-7);
  const past =
    observed.reduce((s, x) => s + x.value, 0) / Math.max(1, observed.length);
  const future =
    data.forecast.reduce((s, x) => s + x.value, 0) /
    Math.max(1, data.forecast.length);
  const change = future - past;
  return (
    <div className="grid-2">
      <div>
        <h3>Estimated direction</h3>
        <p>
          {change >= 0 ? "Growth" : "Decline"} of {Math.abs(change).toFixed(2)}{" "}
          {data.metric} per day versus the last seven observed days.
        </p>
        <small className="muted">
          Model estimate; uncertainty may exceed this difference.
        </small>
      </div>
      <div>
        <h3>Historical posting hours (UTC)</h3>
        {data.eda.periods
          .slice()
          .sort((a, b) => b.mean - a.mean)
          .slice(0, 5)
          .map((p) => (
            <div className="rule-row" key={p.hour}>
              <strong>{String(p.hour).padStart(2, "0")}:00</strong>
              <span>
                {p.mean.toFixed(2)} mean · {p.count} posts
              </span>
            </div>
          ))}
        <small className="muted">
          Descriptive association; no optimal posting time is established.
        </small>
      </div>
    </div>
  );
}

function Team({ admin, run, busy }) {
  const [members, setMembers] = useState([]);
  useEffect(() => {
    api("team/").then(setMembers);
  }, []);
  return (
    <>
      <section className="card">
        <h3>Your people</h3>
        {members.map((m) => (
          <div className="rule-row" key={m.id}>
            <span className="avatar">
              {m.username.slice(0, 2).toUpperCase()}
            </span>
            <strong>{m.username}</strong>
            <Badge value={m.role} />
          </div>
        ))}
      </section>
      {admin && (
        <form
          className="card"
          onSubmit={(e) => {
            e.preventDefault();
            const body = Object.fromEntries(new FormData(e.target));
            run(async () => {
              setMembers(await api("team/", { method: "POST", body }));
              e.target.reset();
            }, "Team member created. Share their temporary password securely.");
          }}
        >
          <h3>Add a teammate</h3>
          <div className="grid-3">
            <Field label="Username">
              <input name="username" required minLength={3} />
            </Field>
            <Field label="Temporary password">
              <input name="password" type="password" required minLength={8} />
            </Field>
            <Field label="Role">
              <select name="role">
                <option value="CREATOR">Content creator</option>
                <option value="REVIEWER">Reviewer / manager</option>
                <option value="ADMIN">Administrator</option>
              </select>
            </Field>
          </div>
          <Button busy={busy} className="primary">
            Create team member
          </Button>
        </form>
      )}
    </>
  );
}
function SettingsPage({ user, run, busy }) {
  return (
    <form
      className="card narrow"
      onSubmit={(e) => {
        e.preventDefault();
        run(
          () =>
            api("auth/me/", {
              method: "PATCH",
              body: Object.fromEntries(new FormData(e.target)),
            }),
          "Profile updated. Your current session remains signed in.",
        );
      }}
    >
      <h3>Account settings</h3>
      <Field label="Email">
        <input type="email" name="email" defaultValue={user.email} />
      </Field>
      <Field label="New password (leave blank to keep current)">
        <input
          type="password"
          name="password"
          minLength={8}
          autoComplete="new-password"
        />
      </Field>
      <Button className="primary" busy={busy}>
        Save settings
      </Button>
      <p className="muted">
        Role: {user.role}. Workspace data is private to your organization.
      </p>
    </form>
  );
}

export { App, Auth, CreatePost, Results, PostDetail };
const root = document.getElementById("root");
if (root) createRoot(root).render(<App />);
