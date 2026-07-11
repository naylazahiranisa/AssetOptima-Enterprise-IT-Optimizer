import { HardDrive } from "lucide-react";

export function Footer() {
  return (
    <footer className="border-border flex items-center justify-between border-t px-6 py-3">
      <div className="text-muted-foreground flex items-center gap-2 text-xs">
        <HardDrive size={12} />
        <span>AssetOptima Command Center</span>
      </div>
      <div className="text-muted-foreground flex items-center gap-4 text-xs">
        <a href="#" className="hover:text-foreground transition-colors">
          Privacy Policy
        </a>
        <a href="#" className="hover:text-foreground transition-colors">
          Terms of Service
        </a>
        <span>&copy; {new Date().getFullYear()}</span>
      </div>
    </footer>
  );
}
