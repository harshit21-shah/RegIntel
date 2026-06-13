import { NextRequest, NextResponse } from "next/server";

const API_BASE = process.env.API_URL || "http://localhost:8000";

type RouteContext = { params: Promise<{ path: string[] }> };

async function proxy(request: NextRequest, path: string[]): Promise<NextResponse> {
  const targetPath = path.join("/");
  const url = `${API_BASE}/api/${targetPath}${request.nextUrl.search}`;

  const headers = new Headers();
  const auth = request.headers.get("authorization");
  const contentType = request.headers.get("content-type");
  if (auth) headers.set("authorization", auth);
  if (contentType) headers.set("content-type", contentType);

  const init: RequestInit = {
    method: request.method,
    headers,
  };

  if (request.method !== "GET" && request.method !== "HEAD") {
    init.body = await request.text();
  }

  let upstream: Response;
  try {
    upstream = await fetch(url, init);
  } catch {
    return NextResponse.json(
      { error: { message: "API unavailable — is the backend running on port 8000?" } },
      { status: 502 },
    );
  }

  const body = await upstream.arrayBuffer();
  return new NextResponse(body, {
    status: upstream.status,
    headers: {
      "content-type": upstream.headers.get("content-type") || "application/json",
    },
  });
}

async function handle(request: NextRequest, context: RouteContext): Promise<NextResponse> {
  const { path } = await context.params;
  return proxy(request, path);
}

export async function GET(request: NextRequest, context: RouteContext): Promise<NextResponse> {
  return handle(request, context);
}

export async function POST(request: NextRequest, context: RouteContext): Promise<NextResponse> {
  return handle(request, context);
}

export async function PATCH(request: NextRequest, context: RouteContext): Promise<NextResponse> {
  return handle(request, context);
}

export async function PUT(request: NextRequest, context: RouteContext): Promise<NextResponse> {
  return handle(request, context);
}

export async function DELETE(request: NextRequest, context: RouteContext): Promise<NextResponse> {
  return handle(request, context);
}
