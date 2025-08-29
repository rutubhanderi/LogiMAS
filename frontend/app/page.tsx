import { redirect } from 'next/navigation';

export default function RootPage() {
  // In a real app, you'd check for authentication status here
  // and redirect to '/dashboard' if logged in.
  redirect('/login');
}