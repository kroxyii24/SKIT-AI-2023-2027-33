
"use client";

import Link from "next/link";

export default function Home() {
  return (
    <main className="min-h-screen bg-slate-950 text-white">
      {/* Navbar */}
      <nav className="border-b border-white/10 bg-slate-950/80 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-5">
          <Link href="/" className="text-2xl font-bold">
            Jan<span className="text-emerald-400">Swasthya</span> AI
          </Link>

          <div className="flex items-center gap-4">
            <Link
              href="/login"
              className="rounded-lg px-4 py-2 text-sm font-medium text-gray-300 transition hover:text-white"
            >
              Login
            </Link>

            <Link
              href="/register"
              className="rounded-lg bg-emerald-500 px-5 py-2 text-sm font-semibold text-white transition hover:bg-emerald-600"
            >
              Get Started
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 -z-0">
          <div className="absolute left-1/2 top-20 h-72 w-72 -translate-x-1/2 rounded-full bg-emerald-500/10 blur-3xl" />
        </div>

        <div className="relative z-10 mx-auto flex min-h-[75vh] max-w-7xl items-center px-6 py-20">
          <div className="max-w-4xl">
            <div className="mb-6 inline-flex items-center rounded-full border border-emerald-400/20 bg-emerald-400/10 px-4 py-2 text-sm text-emerald-300">
              🩺 AI-powered public health awareness
            </div>

            <h1 className="text-5xl font-extrabold leading-tight tracking-tight sm:text-6xl lg:text-7xl">
              Healthcare information,
              <span className="block text-emerald-400">
                accessible to everyone.
              </span>
            </h1>

            <p className="mt-6 max-w-2xl text-lg leading-8 text-gray-400">
              JanSwasthya AI helps people access reliable health information,
              discover government healthcare schemes, find verified doctors,
              and navigate healthcare services more easily.
            </p>

            <div className="mt-10 flex flex-wrap gap-4">
              <Link
                href="/register"
                className="rounded-xl bg-emerald-500 px-7 py-3.5 font-semibold text-white shadow-lg shadow-emerald-500/20 transition hover:bg-emerald-600"
              >
                Get Started →
              </Link>

              <Link
                href="/login"
                className="rounded-xl border border-white/10 bg-white/5 px-7 py-3.5 font-semibold text-gray-200 transition hover:bg-white/10"
              >
                Sign In
              </Link>
            </div>

            <p className="mt-5 text-sm text-gray-500">
              AI provides health information and guidance — it does not
              diagnose conditions or prescribe treatment.
            </p>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="border-t border-white/10 bg-slate-900/50 px-6 py-20">
        <div className="mx-auto max-w-7xl">
          <div className="mb-12">
            <p className="text-sm font-semibold uppercase tracking-widest text-emerald-400">
              What JanSwasthya offers
            </p>

            <h2 className="mt-3 text-3xl font-bold sm:text-4xl">
              Healthcare support, all in one place.
            </h2>
          </div>

          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            <FeatureCard
              icon="🤖"
              title="AI Health Assistant"
              description="Ask health-related questions and receive accessible, evidence-aware information in supported languages."
            />

            <FeatureCard
              icon="🏥"
              title="Verified Doctors"
              description="Connect with information about verified healthcare professionals and available services."
            />

            <FeatureCard
              icon="💊"
              title="Government Schemes"
              description="Explore structured information about healthcare schemes and benefits."
            />

            <FeatureCard
              icon="🌐"
              title="Multilingual Support"
              description="Access health information in English, Hindi, and Hinglish."
            />

            <FeatureCard
              icon="🚨"
              title="Emergency Awareness"
              description="Emergency situations are handled through a dedicated safety-focused flow."
            />

            <FeatureCard
              icon="📚"
              title="Health Resources"
              description="Explore educational health content, videos, diseases, and other public health resources."
            />
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="px-6 py-24">
        <div className="mx-auto max-w-5xl rounded-3xl border border-emerald-400/20 bg-emerald-400/5 p-10 text-center sm:p-16">
          <h2 className="text-3xl font-bold sm:text-4xl">
            Your health information should be easy to understand.
          </h2>

          <p className="mx-auto mt-4 max-w-2xl text-gray-400">
            Start exploring JanSwasthya AI and make healthcare information
            easier to access.
          </p>

          <Link
            href="/register"
            className="mt-8 inline-block rounded-xl bg-emerald-500 px-7 py-3.5 font-semibold transition hover:bg-emerald-600"
          >
            Create Your Account
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/10 px-6 py-8">
        <div className="mx-auto flex max-w-7xl flex-col justify-between gap-4 text-sm text-gray-500 sm:flex-row">
          <p>© {new Date().getFullYear()} JanSwasthya AI</p>

          <p>
            Built for accessible public health awareness.
          </p>
        </div>
      </footer>
    </main>
  );
}

function FeatureCard({
  icon,
  title,
  description,
}: {
  icon: string;
  title: string;
  description: string;
}) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-6 transition hover:border-emerald-400/30 hover:bg-white/[0.05]">
      <div className="mb-5 text-3xl">{icon}</div>

      <h3 className="text-xl font-semibold">{title}</h3>

      <p className="mt-3 leading-7 text-gray-400">{description}</p>
    </div>
  );
}

