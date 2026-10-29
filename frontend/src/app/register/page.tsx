"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import {
  requestRegistrationOTP,
  verifyRegistrationOTP,
  resendRegistrationOTP,
} from "@/lib/api";

const LANGUAGES = [
  { code: "en", label: "English" },
  { code: "hi", label: "हिन्दी (Hindi)" },
  { code: "hi-en", label: "Hinglish" },
];

export default function RegisterPage() {
  const [step, setStep] = useState<"register" | "otp">("register");

  const [fullName, setFullName] = useState("");
  const [phoneNumber, setPhoneNumber] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [language, setLanguage] = useState("en");

  const [otp, setOtp] = useState("");

  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [resending, setResending] = useState(false);

  const router = useRouter();

  async function handleRequestOTP(e: React.FormEvent) {
    e.preventDefault();

    setError(null);
    setSuccess(null);

    if (password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }

    if (!email.includes("@")) {
      setError("Please enter a valid email address.");
      return;
    }

    setLoading(true);

    try {
      await requestRegistrationOTP(
        fullName,
        phoneNumber,
        email,
        password,
        language
      );

      setSuccess(
        `A verification code has been sent to ${email}.`
      );

      setStep("otp");
    } catch (err: any) {
      setError(
        err?.response?.data?.detail ||
          "Unable to send verification code."
      );
    } finally {
      setLoading(false);
    }
  }

  async function handleVerifyOTP(e: React.FormEvent) {
    e.preventDefault();

    setError(null);
    setSuccess(null);

    if (otp.length !== 6) {
      setError("Please enter the 6-digit OTP.");
      return;
    }

    setLoading(true);

    try {
      await verifyRegistrationOTP(email, otp);

      setSuccess(
        "Email verified and account created successfully. Redirecting to login..."
      );

      setTimeout(() => {
        router.push("/login");
      }, 1200);
    } catch (err: any) {
      setError(
        err?.response?.data?.detail ||
          "Invalid verification code."
      );
    } finally {
      setLoading(false);
    }
  }

  async function handleResend() {
    setError(null);
    setSuccess(null);
    setResending(true);

    try {
      await resendRegistrationOTP(email);

      setSuccess("A new OTP has been sent to your email.");
      setOtp("");
    } catch (err: any) {
      setError(
        err?.response?.data?.detail ||
          "Unable to resend OTP."
      );
    } finally {
      setResending(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-sm border p-6">

        {step === "register" ? (
          <>
            <h1 className="text-xl font-semibold text-emerald-800 mb-1">
              Create your account
            </h1>

            <p className="text-sm text-gray-500 mb-6">
              Join JanSwasthya AI — free, always
            </p>

            <form
              onSubmit={handleRequestOTP}
              className="space-y-4"
            >
              <div>
                <label className="text-sm font-medium text-gray-700">
                  Full Name
                </label>

                <input
                  required
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="mt-1 w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
                  placeholder="USER"
                />
              </div>

              <div>
                <label className="text-sm font-medium text-gray-700">
                  Phone Number
                </label>

                <input
                  type="tel"
                  required
                  minLength={10}
                  maxLength={15}
                  value={phoneNumber}
                  onChange={(e) =>
                    setPhoneNumber(e.target.value)
                  }
                  className="mt-1 w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
                  placeholder="9876543210"
                />
              </div>

              <div>
                <label className="text-sm font-medium text-gray-700">
                  Email Address
                </label>

                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="mt-1 w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
                  placeholder="you@example.com"
                />
              </div>

              <div>
                <label className="text-sm font-medium text-gray-700">
                  Password
                </label>

                <input
                  type="password"
                  required
                  minLength={8}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="mt-1 w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
                />
              </div>

              <div>
                <label className="text-sm font-medium text-gray-700">
                  Preferred Language
                </label>

                <select
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  className="mt-1 w-full border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
                >
                  {LANGUAGES.map((l) => (
                    <option
                      key={l.code}
                      value={l.code}
                    >
                      {l.label}
                    </option>
                  ))}
                </select>
              </div>

              {error && (
                <p className="text-sm text-red-600">
                  {error}
                </p>
              )}

              {success && (
                <p className="text-sm text-emerald-700">
                  {success}
                </p>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-emerald-700 text-white rounded-lg py-2.5 text-sm font-medium disabled:opacity-50"
              >
                {loading
                  ? "Sending verification code..."
                  : "Verify Email & Continue"}
              </button>
            </form>

            <p className="text-sm text-gray-500 mt-4 text-center">
              Already have an account?{" "}
              <a
                href="/login"
                className="text-emerald-700 font-medium"
              >
                Log in
              </a>
            </p>
          </>
        ) : (
          <>
            <div className="text-center mb-6">
              <div className="text-4xl mb-3">
                ✉️
              </div>

              <h1 className="text-xl font-semibold text-emerald-800">
                Verify your email
              </h1>

              <p className="text-sm text-gray-500 mt-2">
                We've sent a 6-digit verification code to
              </p>

              <p className="text-sm font-medium text-gray-700 mt-1">
                {email}
              </p>
            </div>

            <form
              onSubmit={handleVerifyOTP}
              className="space-y-4"
            >
              <div>
                <label className="text-sm font-medium text-gray-700">
                  Verification Code
                </label>

                <input
                  type="text"
                  inputMode="numeric"
                  maxLength={6}
                  required
                  value={otp}
                  onChange={(e) =>
                    setOtp(
                      e.target.value
                        .replace(/\D/g, "")
                        .slice(0, 6)
                    )
                  }
                  className="mt-1 w-full border rounded-lg px-3 py-3 text-center text-2xl tracking-[0.5em] font-semibold focus:outline-none focus:ring-2 focus:ring-emerald-500"
                  placeholder="••••••"
                />
              </div>

              {error && (
                <p className="text-sm text-red-600 text-center">
                  {error}
                </p>
              )}

              {success && (
                <p className="text-sm text-emerald-700 text-center">
                  {success}
                </p>
              )}

              <button
                type="submit"
                disabled={loading || otp.length !== 6}
                className="w-full bg-emerald-700 text-white rounded-lg py-2.5 text-sm font-medium disabled:opacity-50"
              >
                {loading
                  ? "Verifying..."
                  : "Verify & Create Account"}
              </button>
            </form>

            <div className="text-center mt-5">
              <button
                type="button"
                onClick={handleResend}
                disabled={resending}
                className="text-sm text-emerald-700 font-medium disabled:opacity-50"
              >
                {resending
                  ? "Sending..."
                  : "Didn't receive the code? Resend OTP"}
              </button>
            </div>

            <button
              type="button"
              onClick={() => {
                setStep("register");
                setOtp("");
                setError(null);
                setSuccess(null);
              }}
              className="w-full mt-4 text-sm text-gray-500 hover:text-gray-700"
            >
              ← Change registration details
            </button>
          </>
        )}
      </div>
    </div>
  );
}