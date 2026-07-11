"use client";

import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, UserPlus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { useEmployees } from "@/features/assets/services/assets.service";

interface AssignmentModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAssign: (payload: {
    employee_id: string;
    assigned_date: string;
    expected_return?: string;
    notes?: string;
  }) => void;
  isPending?: boolean;
  assetName?: string;
}

export function AssignmentModal({
  isOpen,
  onClose,
  onAssign,
  isPending,
  assetName,
}: AssignmentModalProps) {
  const { data: employees, isLoading: employeesLoading } = useEmployees();

  const [employeeId, setEmployeeId] = useState("");
  const [assignedDate, setAssignedDate] = useState(
    new Date().toISOString().split("T")[0],
  );
  const [expectedReturn, setExpectedReturn] = useState("");
  const [notes, setNotes] = useState("");

  const prevOpenRef = useRef(isOpen);
  useEffect(() => {
    const wasClosed = !prevOpenRef.current && isOpen;
    prevOpenRef.current = isOpen;
    if (!wasClosed) return;
    setEmployeeId("");
    setAssignedDate(new Date().toISOString().split("T")[0]);
    setExpectedReturn("");
    setNotes("");
  }, [isOpen]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!employeeId) return;
    onAssign({
      employee_id: employeeId,
      assigned_date: assignedDate,
      expected_return: expectedReturn || undefined,
      notes: notes || undefined,
    });
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm"
            onClick={onClose}
          />
          <motion.div
            initial={{ opacity: 0, scale: 0.96, y: 10 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.96, y: 10 }}
            transition={{ duration: 0.2 }}
            className="bg-card border-border shadow-modal fixed top-1/2 left-1/2 z-50 w-full max-w-md -translate-x-1/2 -translate-y-1/2 rounded-xl border"
          >
            <div className="border-border flex items-center justify-between border-b px-6 py-4">
              <div className="flex items-center gap-2">
                <div className="bg-primary/10 text-primary rounded-lg p-1.5">
                  <UserPlus size={16} />
                </div>
                <h2 className="text-lg font-semibold tracking-tight">
                  Assign Asset
                </h2>
              </div>
              <button
                type="button"
                onClick={onClose}
                className="text-muted-foreground hover:text-foreground rounded-lg p-1.5 transition-colors"
              >
                <X size={16} />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-5 p-6">
              {assetName && (
                <p className="text-muted-foreground text-sm">
                  Assigning:{" "}
                  <span className="text-foreground font-medium">
                    {assetName}
                  </span>
                </p>
              )}

              <div className="space-y-2">
                <label className="text-foreground text-sm font-medium">
                  Employee
                </label>
                {employeesLoading ? (
                  <Skeleton className="h-9 w-full rounded-lg" />
                ) : (
                  <select
                    value={employeeId}
                    onChange={(e) => setEmployeeId(e.target.value)}
                    required
                    className="border-border bg-card text-foreground focus:border-primary/50 focus:ring-primary/20 h-9 w-full rounded-lg border px-3 text-sm transition-colors outline-none focus:ring-1"
                  >
                    <option value="">Select an employee...</option>
                    {employees?.map((emp) => (
                      <option key={emp.id} value={emp.id}>
                        {emp.name} — {emp.department}
                      </option>
                    ))}
                  </select>
                )}
              </div>

              <div className="space-y-2">
                <label className="text-foreground text-sm font-medium">
                  Assignment Date
                </label>
                <input
                  type="date"
                  value={assignedDate}
                  onChange={(e) => setAssignedDate(e.target.value)}
                  required
                  className="border-border bg-card text-foreground focus:border-primary/50 focus:ring-primary/20 h-9 w-full rounded-lg border px-3 text-sm transition-colors outline-none focus:ring-1"
                />
              </div>

              <div className="space-y-2">
                <label className="text-foreground text-sm font-medium">
                  Expected Return{" "}
                  <span className="text-muted-foreground font-normal">
                    (optional)
                  </span>
                </label>
                <input
                  type="date"
                  value={expectedReturn}
                  onChange={(e) => setExpectedReturn(e.target.value)}
                  className="border-border bg-card text-foreground focus:border-primary/50 focus:ring-primary/20 h-9 w-full rounded-lg border px-3 text-sm transition-colors outline-none focus:ring-1"
                />
              </div>

              <div className="space-y-2">
                <label className="text-foreground text-sm font-medium">
                  Notes{" "}
                  <span className="text-muted-foreground font-normal">
                    (optional)
                  </span>
                </label>
                <textarea
                  value={notes}
                  onChange={(e) => setNotes(e.target.value)}
                  rows={3}
                  placeholder="Add any notes about this assignment..."
                  className="border-border bg-card text-foreground placeholder:text-muted-foreground/60 focus:border-primary/50 focus:ring-primary/20 w-full resize-none rounded-lg border px-3 py-2 text-sm transition-colors outline-none focus:ring-1"
                />
              </div>

              <div className="flex items-center justify-end gap-3 pt-2">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={onClose}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  size="sm"
                  disabled={!employeeId || isPending}
                >
                  {isPending ? "Assigning..." : "Assign Asset"}
                </Button>
              </div>
            </form>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
