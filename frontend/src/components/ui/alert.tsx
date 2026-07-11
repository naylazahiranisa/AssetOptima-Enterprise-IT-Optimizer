import {
  AlertCircle,
  AlertTriangle,
  CheckCircle2,
  Info,
  X,
} from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";

type AlertVariant = "info" | "success" | "warning" | "error";

interface AlertProps {
  variant?: AlertVariant;
  title?: string;
  message: string;
  onClose?: () => void;
  className?: string;
}

const iconMap: Record<AlertVariant, typeof Info> = {
  info: Info,
  success: CheckCircle2,
  warning: AlertTriangle,
  error: AlertCircle,
};

const styleMap: Record<AlertVariant, string> = {
  info: "border-primary/20 bg-primary/5 text-primary",
  success: "border-success/20 bg-success/5 text-success",
  warning: "border-warning/20 bg-warning/5 text-warning",
  error: "border-danger/20 bg-danger/5 text-danger",
};

export function Alert({
  variant = "info",
  title,
  message,
  onClose,
  className,
}: AlertProps) {
  const Icon = iconMap[variant];

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0, y: -8 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -8 }}
        role="alert"
        aria-live="assertive"
        className={cn(
          "flex items-start gap-3 rounded-lg border p-4 text-sm",
          styleMap[variant],
          className,
        )}
      >
        <Icon size={18} className="mt-0.5 shrink-0" aria-hidden="true" />
        <div className="flex-1">
          {title && <p className="font-medium">{title}</p>}
          <p>{message}</p>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            aria-label="Dismiss alert"
            className="shrink-0 rounded p-0.5 opacity-60 transition-opacity hover:opacity-100 focus:ring-2 focus:ring-current focus:outline-none"
          >
            <X size={16} />
          </button>
        )}
      </motion.div>
    </AnimatePresence>
  );
}
