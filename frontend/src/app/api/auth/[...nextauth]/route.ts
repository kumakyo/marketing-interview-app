import NextAuth, { NextAuthOptions } from "next-auth";
import GoogleProvider from "next-auth/providers/google";
import { SignJWT } from "jose";

const secret = new TextEncoder().encode(process.env.NEXTAUTH_SECRET || "");

async function createBackendToken(payload: {
  sub: string;
  email?: string | null;
  name?: string | null;
}): Promise<string> {
  return await new SignJWT({
    sub: payload.sub,
    email: payload.email ?? undefined,
    name: payload.name ?? undefined,
  })
    .setProtectedHeader({ alg: "HS256" })
    .setIssuedAt()
    .setExpirationTime("24h")
    .sign(secret);
}

export const authOptions: NextAuthOptions = {
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID || "",
      clientSecret: process.env.GOOGLE_CLIENT_SECRET || "",
    }),
  ],
  callbacks: {
    async signIn({ user }) {
      console.log("Google Login Success:", user.email);
      return true;
    },
    async jwt({ token, user }) {
      if (user) {
        token.id = user.id;
      }
      token.backendToken = await createBackendToken({
        sub: token.sub || "",
        email: token.email,
        name: token.name,
      });
      return token;
    },
    async session({ session, token }) {
      if (session.user) {
        session.user.id = token.sub || "";
        (session as any).backendToken = token.backendToken;
      }
      return session;
    },
  },
  pages: {
    signIn: "/auth/signin",
    error: "/auth/error",
  },
  secret: process.env.NEXTAUTH_SECRET,
};

const handler = NextAuth(authOptions);

export { handler as GET, handler as POST };
