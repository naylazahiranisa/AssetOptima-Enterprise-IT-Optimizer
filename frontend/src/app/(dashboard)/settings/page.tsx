"use client";

import { PageHeader } from "@/components/ui/page-header";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { useTheme } from "@/hooks/useTheme";

export default function SettingsPage() {
  const { isDark, toggle } = useTheme();

  return (
    <div className="max-w-2xl space-y-8">
      <PageHeader
        title="Settings"
        description="Manage your application preferences"
      />

      <Card>
        <CardHeader>
          <CardTitle>Appearance</CardTitle>
          <CardDescription>Customize the interface theme</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-foreground text-sm font-medium">Dark Mode</p>
              <p className="text-muted-foreground text-xs">
                Switch between light and dark themes
              </p>
            </div>
            <Button variant="outline" size="sm" onClick={toggle}>
              {isDark ? "Switch to Light" : "Switch to Dark"}
            </Button>
          </div>
          <Separator />
          <div className="flex items-center justify-between">
            <div>
              <p className="text-foreground text-sm font-medium">Theme</p>
              <p className="text-muted-foreground text-xs">
                Current: {isDark ? "Dark" : "Light"}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Notifications</CardTitle>
          <CardDescription>Configure notification preferences</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground text-sm">
            Notification settings will be available once the backend is
            connected.
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Account</CardTitle>
          <CardDescription>Manage your account settings</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground text-sm">
            Account settings will be available once the backend is connected.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
