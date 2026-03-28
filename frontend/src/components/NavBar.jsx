export default function NavBar({ apiStatus }) {
  return (
    <nav className="bg-gradient-to-r from-sky-900 to-sky-700 shadow-lg px-6 py-4 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <div className="bg-sky-400 rounded-lg p-2">
          <svg
            className="w-6 h-6 text-white"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
            />
          </svg>
        </div>
        <div>
          <h1 className="text-white font-bold text-xl tracking-tight">
            Retailers AI Pricing
          </h1>
          <p className="text-sky-200 text-xs">Dynamic pricing powered by ML</p>
        </div>
      </div>
      <div className="flex items-center gap-2">
        <div
          className={`w-2.5 h-2.5 rounded-full ${apiStatus === "ok" ? "bg-green-400 animate-pulse" : "bg-red-400"}`}
        />
        <span className="text-sky-100 text-sm">
          API {apiStatus === "ok" ? "Live" : "Offline"}
        </span>
      </div>
    </nav>
  );
}
