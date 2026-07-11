import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ShieldX } from "lucide-react";

export default function UnauthorizedPage() {
  return (
    <div className="bg-background flex min-h-screen flex-col items-center justify-center px-4 text-center">
      <ShieldX
        size={48}
        className="text-muted-foreground/30 mb-6"
        strokeWidth={1.5}
      />
      <h1 className="text-foreground text-xl font-semibold">Access Denied</h1>
      <p className="text-muted-foreground mt-2 text-sm">
        You are not authorized to view this resource.
      </p>
      <Link href="/dashboard">
        <Button className="mt-6">Back to Dashboard</Button>
      </Link>
    </div>
  );
}
