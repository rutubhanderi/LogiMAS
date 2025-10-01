"use client";

import { FormEvent } from "react";
import { supabase } from "../../lib/supabaseClient";

export function AuthForm({ mode }: { mode: "login" | "signup" }) {
  const handleLogin = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const email = String(formData.get("email"));
    const password = String(formData.get("password"));

    console.log("Attempting to sign in with email:", email);

    const { error } = await supabase.auth.signInWithPassword({
      email,
      password,
    });

    if (error) {
      console.error("Supabase Sign-In Error:", error.message);
      alert(`Login Failed: ${error.message}`); // Use a simple alert for debugging
    } else {
      console.log(
        "Supabase sign-in successful. Forcing hard redirect to /dashboard..."
      );
      // Force a full page reload to the dashboard
      window.location.href = "/dashboard";
    }
  };

  // For now, we only focus on the login form.
  if (mode === "signup") {
    return (
      <div>
        Sign-up is temporarily disabled for debugging. Please use the login
        form.
      </div>
    );
  }

  return (
    <div className="w-full max-w-md p-8 space-y-6 bg-slate-800 rounded-lg shadow-lg text-white">
      <h1 className="text-2xl font-bold text-center">Sign In to LogiMAS</h1>
      <form onSubmit={handleLogin} className="space-y-6">
        <div>
          <label htmlFor="email" className="block mb-2 text-sm font-medium">
            Email
          </label>
          <input
            id="email"
            name="email"
            type="email"
            required
            className="w-full p-3 bg-slate-700 border border-slate-600 rounded-md"
          />
        </div>
        <div>
          <label htmlFor="password" className="block mb-2 text-sm font-medium">
            Password
          </label>
          <input
            id="password"
            name="password"
            type="password"
            required
            className="w-full p-3 bg-slate-700 border border-slate-600 rounded-md"
          />
        </div>
        <button
          type="submit"
          className="w-full p-3 font-semibold bg-blue-600 rounded-md hover:bg-blue-700"
        >
          Sign In
        </button>
      </form>
    </div>
  );
}
