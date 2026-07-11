import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Lock } from "lucide-react";

export default function ForbiddenPage() {
  return (
    <div className="bg-background flex min-h-screen flex-col items-center justify-center px-4 text-center">
      <Lock
        size={48}
        className="text-muted-foreground/30 mb-6"
        strokeWidth={1.5}
      />
      <h1 className="text-foreground text-3xl font-semibold">403</h1>
      <p className="text-muted-foreground mt-2 text-sm">
        You do not have permission to access this page.
      </p>
      <Link href="/dashboard">
        <Button className="mt-6">Back to Dashboard</Button>
      </Link>
    </div>
  );
}
