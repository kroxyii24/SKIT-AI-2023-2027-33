"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { apiClient } from "@/lib/api";

interface DiseaseSummary {
  slug: string;
  name: string;
  category: string;
}

const CATEGORIES = [
  { value: "", label: "All" },
  { value: "communicable", label: "Communicable" },
  { value: "non_communicable", label: "Non-Communicable" },
  { value: "mental_health", label: "Mental Health" },
  { value: "maternal", label: "Maternal Health" },
  { value: "child", label: "Child Health" },
  { value: "elderly", label: "Elderly Care" },
];

export default function DiseaseExplorerPage() {
  const [diseases, setDiseases] = useState<DiseaseSummary[]>([]);
  const [category, setCategory] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    apiClient
      .get<DiseaseSummary[]>("/diseases/", { params: category ? { category } : {} })
      .then((res) => setDiseases(res.data))
      .finally(() => setLoading(false));
  }, [category]);

  return (
    <div className="max-w-3xl mx-auto p-6">
      <h1 className="text-2xl font-semibold text-emerald-800 mb-1">Disease Explorer</h1>
      <p className="text-sm text-gray-500 mb-6">
        Educational information from WHO, ICMR, and MoHFW. Not a diagnosis tool.
      </p>

      <div className="flex flex-wrap gap-2 mb-6">
        {CATEGORIES.map((c) => (
          <button
            key={c.value}
            onClick={() => setCategory(c.value)}
            className={`px-3 py-1.5 rounded-full text-sm border ${
              category === c.value
                ? "bg-emerald-700 text-white border-emerald-700"
                : "bg-white text-gray-600 border-gray-300"
            }`}
          >
            {c.label}
          </button>
        ))}
      </div>

      {loading ? (
        <p className="text-sm text-gray-400">Loading...</p>
      ) : (
        <div className="grid gap-3">
          {diseases.map((d) => (
            <Link
              key={d.slug}
              href={`/diseases/${d.slug}`}
              className="border rounded-xl p-4 hover:border-emerald-400 transition-colors bg-white"
            >
              <p className="font-medium text-gray-900">{d.name}</p>
              <p className="text-xs text-gray-500 capitalize mt-1">{d.category.replace("_", " ")}</p>
            </Link>
          ))}
          {diseases.length === 0 && (
            <p className="text-sm text-gray-400">No diseases found in this category yet.</p>
          )}
        </div>
      )}
    </div>
  );
}
