import Link from "next/link";
import { Button } from "@/components/ui/button";
import { FileQuestion } from "lucide-react";

export default function NotFoundPage() {
  return (
    <div className="bg-background flex min-h-screen flex-col items-center justify-center px-4 text-center">
      <FileQuestion
        size={48}
        className="text-muted-foreground/30 mb-6"
        strokeWidth={1.5}
      />
      <h1 className="text-foreground text-3xl font-semibold">404</h1>
      <p className="text-muted-foreground mt-2 text-sm">
        The page you are looking for does not exist.
      </p>
      <Link href="/dashboard">
        <Button className="mt-6">Back to Dashboard</Button>
      </Link>
    </div>
  );
}
