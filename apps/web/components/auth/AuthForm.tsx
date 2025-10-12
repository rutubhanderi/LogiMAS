"use client";

import { useState, FormEvent } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "../../contexts/AuthContext";
import axios from "axios";
import Link from "next/link";

export function AuthForm({ mode }: { mode: "login" | "signup" }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const { login } = useAuth();
  const router = useRouter();

  const handleAuth = async (e: FormEvent) => {
    e.preventDefault();
    setError(null);
    setMessage(null);
    setIsLoading(true);

    if (mode === "signup") {
      // NOTE: This requires a new `/users/signup` endpoint on your FastAPI backend
      // which has not been built yet.
      setMessage(
        "Sign-up functionality is handled directly in the Supabase dashboard for this demo."
      );
      setIsLoading(false);
      return;
    }

    try {
      const formData = new URLSearchParams();
      formData.append("username", email);
      formData.append("password", password);

      const response = await axios.post(
        "http://127.0.0.1:8000/auth/token",
        formData,
        {
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
        }
      );

      const { access_token } = response.data;
      if (access_token) {
        login(access_token);
        router.push("/dashboard");
      } else {
        throw new Error("Login successful, but no token was provided.");
      }
    } catch (err: any) {
      setError(
        err.response?.data?.detail ||
          "Login failed. Please check your credentials."
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md p-8 space-y-6 bg-slate-800 rounded-lg shadow-lg text-white">
      <h1 className="text-2xl font-bold text-center">
        {mode === "login" ? "Sign In to LogiMAS" : "Create an Account"}
      </h1>
      <form onSubmit={handleAuth} className="space-y-6">
        {mode === "signup" && (
          <div>
            <label htmlFor="name">Name</label>
            <input
              id="name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              className="w-full p-3 bg-slate-700 rounded-md"
            />
          </div>
        )}
        <div>
          <label htmlFor="email">Email</label>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="w-full p-3 bg-slate-700 rounded-md"
          />
        </div>
        <div>
          <label htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="w-full p-3 bg-slate-700 rounded-md"
          />
        </div>
        <button
          type="submit"
          disabled={isLoading}
          className="w-full p-3 font-semibold bg-blue-600 rounded-md hover:bg-blue-700 disabled:bg-slate-600"
        >
          {isLoading
            ? "Processing..."
            : mode === "login"
            ? "Sign In"
            : "Sign Up"}
        </button>
        {error && <p className="text-red-400 text-sm text-center">{error}</p>}
        {message && (
          <p className="text-green-400 text-sm text-center">{message}</p>
        )}
      </form>
      <div className="text-center text-sm">
        {mode === "login" ? (
          <p>
            Don't have an account?{" "}
            <Link
              href="/signup"
              className="font-medium text-blue-400 hover:underline"
            >
              Sign Up
            </Link>
          </p>
        ) : (
          <p>
            Already have an account?{" "}
            <Link
              href="/login"
              className="font-medium text-blue-400 hover:underline"
            >
              Sign In
            </Link>
          </p>
        )}
      </div>
    </div>
  );
}
