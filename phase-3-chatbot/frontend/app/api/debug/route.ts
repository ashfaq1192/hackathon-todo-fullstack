/**
 * Debug endpoint to check environment configuration
 * Access at: /api/debug
 * DELETE THIS FILE after debugging!
 */

import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({
    envCheck: {
      hasDatabase: !!process.env.DATABASE_URL,
      hasBetterAuthSecret: !!process.env.BETTER_AUTH_SECRET,
      hasJwtSecret: !!process.env.JWT_SECRET_KEY,
      betterAuthUrl: process.env.BETTER_AUTH_URL || 'not set',
      nextPublicBetterAuthUrl: process.env.NEXT_PUBLIC_BETTER_AUTH_URL || 'not set',
      // Don't expose actual values, just check if they exist
    },
    databaseUrlPrefix: process.env.DATABASE_URL?.substring(0, 20) || 'not set',
  });
}
