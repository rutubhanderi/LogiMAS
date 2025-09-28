import { createClient } from '@supabase/supabase-js'
import path from 'path';
import dotenv from 'dotenv';
dotenv.config({ path: path.resolve(__dirname, '../../../.env') });
// Get Supabase credentials from environment variables
const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
console.log(supabaseUrl)
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
console.log(supabaseAnonKey)
// Check if the environment variables are set
if (!supabaseUrl) {
  throw new Error('Missing Supabase URL  in environment variables.')
}
if(!supabaseAnonKey){
  throw new Error('Missing Anon Key in environment variables.')
}
// Create and export the Supabase client instance
export const supabase = createClient(supabaseUrl, supabaseAnonKey)