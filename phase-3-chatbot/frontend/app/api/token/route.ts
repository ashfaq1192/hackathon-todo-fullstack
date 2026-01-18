/**
 * JWT Token Generation API Route
 *
 * Generates JWT tokens for backend API authentication.
 * Validates Better Auth session and creates a JWT with user_id claim.
 */

import { NextRequest, NextResponse } from 'next/server';
import { auth } from '@/lib/auth/auth';
import * as jose from 'jose';

export async function GET(request: NextRequest) {
  try {
    // Get the Better Auth session
    const session = await auth.api.getSession({
      headers: request.headers,
    });

    if (!session) {
      return NextResponse.json(
        { error: 'Unauthorized - No valid session' },
        { status: 401 }
      );
    }

    // Generate JWT token for backend API
    const secret = new TextEncoder().encode(
      process.env.JWT_SECRET_KEY || process.env.BETTER_AUTH_SECRET
    );

    const token = await new jose.SignJWT({ user_id: session.user.id })
      .setProtectedHeader({ alg: 'HS256' })
      .setIssuedAt()
      .setExpirationTime('7d') // 7 days to match Better Auth session
      .sign(secret);

    return NextResponse.json({ token, user_id: session.user.id });
  } catch (error) {
    console.error('Token generation error:', error);
    return NextResponse.json(
      { error: 'Failed to generate token' },
      { status: 500 }
    );
  }
}
