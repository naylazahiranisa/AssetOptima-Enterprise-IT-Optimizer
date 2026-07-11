"use client";

import { useAuth } from "@/hooks/useAuth";
import { PageHeader } from "@/components/ui/page-header";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Avatar } from "@/components/ui/avatar";
import { Separator } from "@/components/ui/separator";
import { getInitials } from "@/lib/utils";

export default function ProfilePage() {
  const { user } = useAuth();

  const displayName = user?.full_name ?? "User";
  const initials = getInitials(displayName);

  return (
    <div className="max-w-2xl space-y-8">
      <PageHeader title="Profile" description="Your personal information" />

      <Card>
        <CardHeader>
          <div className="flex items-center gap-4">
            <Avatar size="lg" fallback={initials} />
            <div>
              <CardTitle>{displayName}</CardTitle>
              <CardDescription>{user?.email ?? "No email"}</CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <p className="text-muted-foreground text-xs font-medium tracking-wider uppercase">
              Role
            </p>
            <p className="text-foreground mt-1 text-sm">
              {user?.role
                ?.replace("_", " ")
                .replace(/\b\w/g, (c) => c.toUpperCase()) ?? "—"}
            </p>
          </div>
          <Separator />
          <div>
            <p className="text-muted-foreground text-xs font-medium tracking-wider uppercase">
              Department
            </p>
            <p className="text-foreground mt-1 text-sm">
              {user?.department ?? "—"}
            </p>
          </div>
          <Separator />
          <div>
            <p className="text-muted-foreground text-xs font-medium tracking-wider uppercase">
              Member Since
            </p>
            <p className="text-foreground mt-1 text-sm">
              {user?.created_at
                ? new Date(user.created_at).toLocaleDateString()
                : "—"}
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
