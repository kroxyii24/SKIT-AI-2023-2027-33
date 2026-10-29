"use client";

import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api";

interface Stats {
  total_users: number;
  verified_doctors: number;
  pending_doctor_verifications: number;
  videos_pending_approval: number;
  total_appointments: number;
  emergency_flags_triggered: number;
}

export default function AdminDashboard() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiClient
      .get<Stats>("/admin/stats")
      .then((res) => setStats(res.data))
      .catch(() => setError("Failed to load stats. You may not have admin access."));
  }, []);

  if (error) return <div className="p-6 text-red-600 text-sm">{error}</div>;
  if (!stats) return <div className="p-6 text-sm text-gray-400">Loading dashboard...</div>;

  const cards = [
    { label: "Total Users", value: stats.total_users },
    { label: "Verified Doctors", value: stats.verified_doctors },
    { label: "Pending Doctor Verifications", value: stats.pending_doctor_verifications, highlight: stats.pending_doctor_verifications > 0 },
    { label: "Videos Pending Approval", value: stats.videos_pending_approval, highlight: stats.videos_pending_approval > 0 },
    { label: "Total Appointments", value: stats.total_appointments },
    { label: "Emergency Flags Triggered", value: stats.emergency_flags_triggered },
  ];

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-2xl font-semibold text-emerald-800 mb-6">Admin Dashboard</h1>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {cards.map((c) => (
          <div
            key={c.label}
            className={`rounded-xl border p-4 ${c.highlight ? "bg-amber-50 border-amber-300" : "bg-white"}`}
          >
            <p className="text-sm text-gray-500">{c.label}</p>
            <p className="text-3xl font-semibold mt-1">{c.value}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
