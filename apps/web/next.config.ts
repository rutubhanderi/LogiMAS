// File: apps/web/next.config.ts

import dotenv from 'dotenv';
import path from 'path';

// --- This is the new, important part ---
// Construct the full path to the .env file in the project root
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