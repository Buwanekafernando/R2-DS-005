import { useMemo, useState } from "react"
import { NavLink } from "react-router-dom"
import { BarChart3, FlaskConical, Home, Info, Menu, Sparkles, X } from "lucide-react"

const baseLinkClass =
  "inline-flex items-center gap-2 rounded-xl px-3 py-2 text-sm font-medium transition hover:bg-slate-100 hover:text-slate-900"

function NavItem({ to, icon: Icon, label, onClick }) {
  return (
    <NavLink
      to={to}
      onClick={onClick}
      className={({ isActive }) =>
        [
          baseLinkClass,
          isActive ? "bg-slate-100 text-slate-900" : "text-slate-600",
        ].join(" ")
      }
    >
      <Icon className="h-4 w-4" />
      <span>{label}</span>
    </NavLink>
  )
}

export default function Navbar() {
  const [open, setOpen] = useState(false)

  const items = useMemo(
    () => [
      //{ to: "/", label: "Home", icon: Home },
      { to: "/generate", label: "Generate", icon: Sparkles },
      { to: "/validate", label: "Validate", icon: FlaskConical },
      
    ],
    [],
  )

  return (
    <header className="sticky top-0 z-40 border-b border-slate-200 bg-white/80 backdrop-blur">
      <div className="mx-auto flex w-full max-w-6xl items-center justify-between gap-4 px-4 py-3">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-blue-600 to-purple-600 text-white shadow-sm">
            <Sparkles className="h-4 w-4" />
          </div>
          <div className="leading-tight">
            <div className="text-sm font-semibold text-slate-900">Emotion Propagation Agent</div>
            <div className="text-xs text-slate-500">Component 2 • Research Prototype</div>
          </div>
        </div>

        <nav className="hidden items-center gap-1 md:flex">
          {items.map((it) => (
            <NavItem key={it.to} to={it.to} icon={it.icon} label={it.label} />
          ))}
        </nav>

        <button
          type="button"
          className="inline-flex items-center justify-center rounded-xl border border-slate-200 bg-white p-2 text-slate-700 shadow-sm transition hover:bg-slate-50 md:hidden"
          onClick={() => setOpen((v) => !v)}
          aria-label="Toggle navigation"
        >
          {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </div>

      {open ? (
        <div className="border-t border-slate-200 bg-white md:hidden">
          <div className="mx-auto w-full max-w-6xl px-4 py-3">
            <div className="grid gap-2">
              {items.map((it) => (
                <NavItem
                  key={it.to}
                  to={it.to}
                  icon={it.icon}
                  label={it.label}
                  onClick={() => setOpen(false)}
                />
              ))}
            </div>
          </div>
        </div>
      ) : null}
    </header>
  )
}
