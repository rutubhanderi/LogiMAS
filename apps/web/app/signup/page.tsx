import { AuthForm } from "../../components/auth/AuthForm";

export default function SignUpPage() {
  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
      <AuthForm mode="signup" />
    </div>
  );
}
