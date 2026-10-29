"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { apiClient } from "@/lib/api";

interface DiseaseDetail {
  name: string;
  overview: string;
  symptoms: string[];
  risk_factors: string[];
  preventive_measures: string[];
  government_initiatives: string[];
  when_to_consult_doctor: string;
  emergency_signs: string[];
  trusted_references: { publisher: string; url: string }[];
}

function Section({ title, items }: { title: string; items: string[] }) {
  if (!items?.length) return null;
  return (
    <div className="mb-5">
      <h2 className="font-medium text-gray-900 mb-2">{title}</h2>
      <ul className="list-disc list-inside space-y-1 text-sm text-gray-700">
        {items.map((item, i) => <li key={i}>{item}</li>)}
      </ul>
    </div>
  );
}

export default function DiseaseDetailPage() {
  const { slug } = useParams<{ slug: string }>();
  const [disease, setDisease] = useState<DiseaseDetail | null>(null);

  useEffect(() => {
    apiClient.get<DiseaseDetail>(`/diseases/${slug}`).then((res) => setDisease(res.data));
  }, [slug]);

  if (!disease) return <div className="p-6 text-sm text-gray-400">Loading...</div>;

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h1 className="text-2xl font-semibold text-emerald-800 mb-3">{disease.name}</h1>
      <p className="text-sm text-gray-700 mb-6 leading-relaxed">{disease.overview}</p>

      <Section title="Symptoms" items={disease.symptoms} />
      <Section title="Risk Factors" items={disease.risk_factors} />
      <Section title="Prevention" items={disease.preventive_measures} />
      <Section title="Government Initiatives" items={disease.government_initiatives} />

      <div className="mb-5">
        <h2 className="font-medium text-gray-900 mb-2">When to Consult a Doctor</h2>
        <p className="text-sm text-gray-700">{disease.when_to_consult_doctor}</p>
      </div>

      <div className="mb-5 border-2 border-red-300 bg-red-50 rounded-xl p-4">
        <h2 className="font-medium text-red-800 mb-2">⚠️ Emergency Signs — Seek immediate care if you notice:</h2>
        <ul className="list-disc list-inside space-y-1 text-sm text-red-900">
          {disease.emergency_signs.map((s, i) => <li key={i}>{s}</li>)}
        </ul>
      </div>

      {disease.trusted_references?.length > 0 && (
        <div className="text-xs text-gray-400 pt-3 border-t">
          Sources: {disease.trusted_references.map((r) => r.publisher).join(", ")}
        </div>
      )}
    </div>
  );
}
