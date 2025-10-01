import Link from "next/link";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-slate-900 text-white flex flex-col items-center justify-center text-center p-4">
      <div className="max-w-3xl">
        <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-500">
          Welcome to LogiMAS
        </h1>
        <p className="mt-6 text-lg md:text-xl text-slate-300">
          The Retrieval-Augmented Multi-Agent System for intelligent logistics
          optimization. Gain real-time insights into tracking, routing, and
          warehouse management.
        </p>
        <div className="mt-10 flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            href="/login"
            className="px-8 py-3 bg-blue-600 rounded-md font-semibold text-white hover:bg-blue-700 transition-transform transform hover:scale-105"
          >
            Sign In
          </Link>
          <Link
            href="/signup"
            className="px-8 py-3 bg-slate-700 rounded-md font-semibold text-white hover:bg-slate-600 transition-transform transform hover:scale-105"
          >
            Create an Account
          </Link>
        </div>
      </div>
    </div>
  );
}
