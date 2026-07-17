import { SessionDetailPage } from "@/features/sessions/session-detail-page";

type SessionDetailRouteProps = {
  params: Promise<{
    sessionId: string;
  }>;
};

export default async function SessionDetailRoute({ params }: SessionDetailRouteProps) {
  const { sessionId } = await params;
  return <SessionDetailPage sessionId={sessionId} />;
}
