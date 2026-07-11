"use client";

import { motion } from "framer-motion";
import {
  Brain,
  AlertTriangle,
  TrendingDown,
  Scan,
  CalendarCheck,
  ArrowRight,
  Lightbulb,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";

const aiFeatures = [
  {
    icon: AlertTriangle,
    label: "Dormant Licenses",
    description: "Detect unused licenses wasting budget",
    color: "text-warning",
    bgColor: "bg-warning/10",
  },
  {
    icon: TrendingDown,
    label: "Potential Savings",
    description: "AI-optimized license allocation recommendations",
    color: "text-success",
    bgColor: "bg-success/10",
  },
  {
    icon: Scan,
    label: "Anomaly Detection",
    description: "Identify unusual usage patterns and spikes",
    color: "text-primary",
    bgColor: "bg-primary/10",
  },
  {
    icon: CalendarCheck,
    label: "Predicted Renewal Needs",
    description: "Forecast license requirements before renewal",
    color: "text-ai",
    bgColor: "bg-ai/10",
  },
];

export function AiReadinessPanel() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: 0.1 }}
    >
      <Card className="border-ai/20 from-card to-ai/[0.02] bg-gradient-to-br">
        <CardHeader>
          <div className="flex items-center gap-2">
            <div className="bg-ai/10 text-ai flex h-8 w-8 items-center justify-center rounded-lg">
              <Brain size={16} />
            </div>
            <div>
              <CardTitle>AI Readiness</CardTitle>
              <CardDescription>
                Intelligent insights coming in Sprint S21
              </CardDescription>
            </div>
            <Badge variant="ai" className="ml-auto">
              Coming Soon
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-5">
          <div className="grid gap-3 sm:grid-cols-2">
            {aiFeatures.map((feature, i) => {
              const Icon = feature.icon;
              return (
                <motion.div
                  key={feature.label}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.25, delay: i * 0.05 }}
                  className="border-border bg-muted/30 hover:bg-muted/50 rounded-lg border p-3 transition-colors"
                >
                  <div className="flex items-start gap-2.5">
                    <div
                      className={`${feature.bgColor} ${feature.color} flex h-7 w-7 shrink-0 items-center justify-center rounded-md`}
                    >
                      <Icon size={14} />
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="text-foreground text-sm font-medium">
                        {feature.label}
                      </p>
                      <p className="text-muted-foreground mt-0.5 text-xs leading-snug">
                        {feature.description}
                      </p>
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </div>

          <Separator />

          <div className="bg-ai/5 border-ai/10 rounded-lg border p-4">
            <div className="flex items-start gap-3">
              <div className="text-ai mt-0.5">
                <Lightbulb size={16} />
              </div>
              <div className="flex-1">
                <p className="text-foreground text-sm font-medium">
                  AI Recommendation
                </p>
                <p className="text-muted-foreground mt-1 text-xs leading-relaxed">
                  Based on your current license portfolio, AI analysis could
                  identify cost-saving opportunities, flag underutilized
                  subscriptions, and predict future renewal needs across your
                  organization.
                </p>
              </div>
            </div>
          </div>

          <Button
            variant="outline"
            className="border-ai/20 text-ai hover:bg-ai/5 w-full gap-2"
            disabled
          >
            <Brain size={14} />
            Analyze with AI
            <ArrowRight size={14} className="ml-auto" />
          </Button>
        </CardContent>
      </Card>
    </motion.div>
  );
}
