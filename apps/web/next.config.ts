
import dotenv from 'dotenv';
import path from 'path';

const envPath = path.resolve(process.cwd(), '../../.env');

// Load the environment variables from the root file
console.log(`[next.config.ts] Loading environment variables from: ${envPath}`);
dotenv.config({ path: envPath });
// -----------------------------------------


/** @type {import('next').NextConfig} */
const nextConfig = {
  // Your Next.js config options, if any, go here.
  // For now, it's likely empty, which is fine.
};

export default nextConfig;