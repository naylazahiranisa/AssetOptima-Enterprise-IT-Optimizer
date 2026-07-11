"use client";

import { useRef } from "react";
import { Download, Printer, QrCode } from "lucide-react";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";

interface QRPreviewProps {
  assetCode: string;
  assetName: string;
}

function generateQRPattern(code: string): string[][] {
  const size = 21;
  const grid: string[][] = Array.from({ length: size }, () =>
    Array.from({ length: size }, () => "white"),
  );

  const hash = code
    .split("")
    .reduce((acc, c) => ((acc << 5) - acc + c.charCodeAt(0)) | 0, 0);

  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      if (
        (x < 7 && y < 7) ||
        (x >= size - 7 && y < 7) ||
        (x < 7 && y >= size - 7)
      ) {
        if (
          x === 0 ||
          x === 6 ||
          y === 0 ||
          y === 6 ||
          (x >= 2 && x <= 4 && y >= 2 && y <= 4)
        ) {
          grid[y][x] = "black";
        }
        continue;
      }

      const seed = ((hash + x * 31 + y * 37) * 13) & 1;
      if (seed) grid[y][x] = "black";
    }
  }

  for (let i = 0; i < 8; i++) {
    const maskY = 8;
    const maskX = i;
    if (maskX < size) grid[maskY][maskX] = i % 2 === 0 ? "black" : "white";
  }

  return grid;
}

export function QRPreview({ assetCode, assetName }: QRPreviewProps) {
  const canvasRef = useRef<HTMLDivElement>(null);
  const pattern = generateQRPattern(assetCode);

  const handleDownload = () => {
    const canvas = document.createElement("canvas");
    canvas.width = 290;
    canvas.height = 290;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const cellSize = 10;
    ctx.fillStyle = "#ffffff";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    const offsetX = (canvas.width - pattern[0].length * cellSize) / 2;
    const offsetY = (canvas.height - pattern.length * cellSize) / 2;

    for (let y = 0; y < pattern.length; y++) {
      for (let x = 0; x < pattern[y].length; x++) {
        ctx.fillStyle = pattern[y][x] === "black" ? "#0f172a" : "#ffffff";
        ctx.fillRect(
          offsetX + x * cellSize,
          offsetY + y * cellSize,
          cellSize,
          cellSize,
        );
      }
    }

    const link = document.createElement("a");
    link.download = `qr-${assetCode}.png`;
    link.href = canvas.toDataURL("image/png");
    link.click();
  };

  const handlePrint = () => {
    const win = window.open("", "_blank");
    if (!win) return;

    const qrHtml = pattern
      .map(
        (row) =>
          `<tr>${row
            .map(
              (cell) =>
                `<td style="width:6px;height:6px;background:${cell === "black" ? "#0f172a" : "#fff"}"></td>`,
            )
            .join("")}</tr>`,
      )
      .join("");

    win.document.write(`
      <html>
        <head><title>QR Code — ${assetCode}</title></head>
        <body style="display:flex;flex-direction:column;align-items:center;justify-content:center;height:100vh;font-family:sans-serif;">
          <table style="border-collapse:collapse;">${qrHtml}</table>
          <p style="margin-top:16px;font-size:14px;color:#666;">${assetCode} — ${assetName}</p>
          <script>window.print();<\/script>
        </body>
      </html>
    `);
    win.document.close();
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>QR Code</CardTitle>
        <CardDescription>Asset identification tag</CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col items-center">
        <div
          ref={canvasRef}
          className="bg-card border-border mb-4 flex items-center justify-center rounded-xl border p-4"
        >
          <div className="flex flex-col items-center gap-2">
            <div
              style={{
                display: "grid",
                gridTemplateColumns: `repeat(${pattern[0].length}, 6px)`,
                gap: "1px",
              }}
            >
              {pattern.map((row, y) =>
                row.map((cell, x) => (
                  <div
                    key={`${y}-${x}`}
                    style={{
                      width: 6,
                      height: 6,
                      backgroundColor:
                        cell === "black" ? "var(--foreground)" : "transparent",
                      borderRadius: cell === "black" ? "1px" : 0,
                    }}
                  />
                )),
              )}
            </div>
            <p className="text-muted-foreground font-mono text-[10px]">
              {assetCode}
            </p>
          </div>
        </div>

        <div className="text-center">
          <p className="text-foreground text-sm font-medium">{assetName}</p>
          <p className="text-muted-foreground text-xs">{assetCode}</p>
        </div>
      </CardContent>
      <CardFooter className="flex gap-2">
        <Button
          variant="outline"
          size="sm"
          className="flex-1 gap-1.5"
          onClick={handleDownload}
        >
          <Download size={14} />
          Download
        </Button>
        <Button
          variant="outline"
          size="sm"
          className="flex-1 gap-1.5"
          onClick={handlePrint}
        >
          <Printer size={14} />
          Print
        </Button>
      </CardFooter>
    </Card>
  );
}
