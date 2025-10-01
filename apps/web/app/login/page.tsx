// Update the import path below if the actual location is different
import { AuthForm } from "../../components/auth/AuthForm";

export default function LoginPage() {
  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
      <AuthForm mode="login" />
    </div>
  );
}
