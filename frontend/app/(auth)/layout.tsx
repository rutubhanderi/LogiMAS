import Image from 'next/image';

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="grid min-h-screen grid-cols-1 lg:grid-cols-2">
      <div className="hidden bg-zinc-900 p-10 text-white lg:flex flex-col items-center justify-center">
        {/* Replace with your actual truck image */}
        <Image
          src="/truck-loading.png" // Make sure this path is correct
          alt="Loading Truck"
          width={500}
          height={300}
          className="opacity-75"
        />
        <h1 className="mt-4 text-4xl font-bold tracking-widest opacity-50">LOADING...</h1>
      </div>
      <div className="flex items-center justify-center p-8 bg-background">
        {children}
      </div>
    </div>
  );
}