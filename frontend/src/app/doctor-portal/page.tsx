"use client";

import { useEffect, useState } from "react";
import { apiClient } from "@/lib/api";

interface Appointment {
  id: string;
  patient_id: string;
  scheduled_at: string;
  consultation_tier: string;
  status: string;
}

interface Video {
  id: string;
  title: string;
  is_approved: boolean;
  view_count: number;
}

export default function DoctorPortalPage() {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [uploadTitle, setUploadTitle] = useState("");
  const [uploadUrl, setUploadUrl] = useState("");
  const [uploadCategory, setUploadCategory] = useState("nutrition");
  const [message, setMessage] = useState<string | null>(null);

  useEffect(() => {
    apiClient.get<Appointment[]>("/appointments/me").then((res) => setAppointments(res.data));
  }, []);

  async function updateStatus(id: string, status: string) {
    await apiClient.patch(`/appointments/${id}/status`, { status });
    setAppointments((prev) => prev.map((a) => (a.id === id ? { ...a, status } : a)));
  }

  async function handleUpload(e: React.FormEvent) {
    e.preventDefault();
    setMessage(null);
    try {
      await apiClient.post("/videos/", {
        title: uploadTitle,
        video_url: uploadUrl,
        category: uploadCategory,
        language: "en",
      });
      setMessage("Video submitted — pending admin approval before it goes live.");
      setUploadTitle("");
      setUploadUrl("");
    } catch (err: any) {
      setMessage(err?.response?.data?.detail || "Upload failed. Make sure your doctor profile is verified.");
    }
  }

  return (
    <div className="max-w-2xl mx-auto p-6 space-y-8">
      <div>
        <h1 className="text-2xl font-semibold text-emerald-800 mb-4">Doctor Portal</h1>

        <h2 className="font-medium text-gray-900 mb-2">Upcoming Appointments</h2>
        <div className="space-y-2">
          {appointments.length === 0 && <p className="text-sm text-gray-400">No appointments yet.</p>}
          {appointments.map((a) => (
            <div key={a.id} className="border rounded-lg p-3 flex justify-between items-center text-sm">
              <div>
                <p className="font-medium">{new Date(a.scheduled_at).toLocaleString()}</p>
                <p className="text-gray-500 capitalize">{a.consultation_tier.replace("_", " ")} · {a.status}</p>
              </div>
              {a.status === "pending" && (
                <div className="flex gap-2">
                  <button onClick={() => updateStatus(a.id, "confirmed")} className="text-emerald-700 text-xs font-medium">Confirm</button>
                  <button onClick={() => updateStatus(a.id, "cancelled")} className="text-red-600 text-xs font-medium">Cancel</button>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      <div>
        <h2 className="font-medium text-gray-900 mb-2">Upload Educational Video</h2>
        <form onSubmit={handleUpload} className="space-y-3 border rounded-xl p-4 bg-white">
          <input
            required
            placeholder="Video title"
            value={uploadTitle}
            onChange={(e) => setUploadTitle(e.target.value)}
            className="w-full border rounded-lg px-3 py-2 text-sm"
          />
          <input
            required
            placeholder="Video URL (from object storage)"
            value={uploadUrl}
            onChange={(e) => setUploadUrl(e.target.value)}
            className="w-full border rounded-lg px-3 py-2 text-sm"
          />
          <select
            value={uploadCategory}
            onChange={(e) => setUploadCategory(e.target.value)}
            className="w-full border rounded-lg px-3 py-2 text-sm"
          >
            <option value="nutrition">Nutrition</option>
            <option value="maternal_health">Maternal Health</option>
            <option value="mental_health">Mental Health</option>
            <option value="child_health">Child Health</option>
          </select>
          <button type="submit" className="bg-emerald-700 text-white rounded-lg px-4 py-2 text-sm font-medium">
            Submit for Review
          </button>
          {message && <p className="text-sm text-gray-600">{message}</p>}
        </form>
      </div>
    </div>
  );
}
