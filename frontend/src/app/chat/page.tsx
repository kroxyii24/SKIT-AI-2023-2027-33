"use client";

import { useState } from "react";

type Message = {
  id: number;
  role: "user" | "assistant";
  content: string;
};

const DEMO_QUESTIONS: Record<string, string> = {
  "What are the symptoms of dehydration?":
    "Common symptoms of dehydration include thirst, dry mouth, dark yellow urine, dizziness, fatigue, and reduced urination. Drink fluids gradually and seek medical care if dehydration is severe or symptoms are worsening.",

  "What should I do if I have a fever?":
    "Rest, drink plenty of fluids, and monitor your temperature. Seek medical attention if the fever is very high, persistent, worsening, or accompanied by breathing difficulty, confusion, severe weakness, or other serious symptoms.",

  "How can I prevent dengue?":
    "You can reduce the risk of dengue by preventing mosquito bites. Use mosquito repellent, wear protective clothing, use mosquito nets or screens, and remove stagnant water where mosquitoes can breed.",

  "What are common symptoms of anemia?":
    "Common symptoms of anemia can include tiredness, weakness, dizziness, headaches, shortness of breath during activity, and pale skin. Persistent symptoms should be evaluated by a healthcare professional.",

  "How can I prevent seasonal flu?":
    "Wash your hands regularly, avoid close contact with people who are sick, maintain good ventilation, cover coughs and sneezes, and consider recommended seasonal vaccination.",

  "What should I do for diarrhea?":
    "The main priority is preventing dehydration. Drink plenty of fluids or oral rehydration solution. Seek medical care if there is blood in the stool, severe dehydration, persistent symptoms, significant weakness, or other concerning symptoms.",

  "How can I maintain a healthy diet?":
    "Aim for a varied diet containing vegetables, fruits, whole grains, pulses and other protein sources. Stay hydrated and limit excessive salt, added sugar, and highly processed foods.",

  "What are the warning signs of an emergency?":
    "Warning signs that require urgent medical attention can include severe difficulty breathing, chest pain, loss of consciousness, seizures, severe bleeding, or sudden neurological symptoms such as difficulty speaking or weakness on one side of the body.",

  "How can I prevent high blood pressure?":
    "Helpful measures include staying physically active, maintaining a healthy weight, limiting salt intake, avoiding tobacco, moderating alcohol consumption, eating a balanced diet, and having your blood pressure checked regularly.",

  "When should I see a doctor?":
    "Consider seeing a healthcare professional when symptoms are severe, persistent, worsening, unexplained, or significantly interfering with your daily activities. Emergency symptoms require immediate medical attention.",
};

/*
 * Only these 5 questions are shown on screen.
 *
 * The other 5 questions remain inside DEMO_QUESTIONS above,
 * so users can still type them manually and receive answers.
 */
const SUGGESTED_QUESTIONS = [
  "What are the symptoms of dehydration?",
  "How can I prevent dengue?",
  "What are common symptoms of anemia?",
  "How can I maintain a healthy diet?",
  "When should I see a doctor?",
];

function getAnswer(question: string): string {
  const normalizedQuestion = question.trim().toLowerCase();

  // Exact match first
  for (const [key, answer] of Object.entries(DEMO_QUESTIONS)) {
    if (key.toLowerCase() === normalizedQuestion) {
      return answer;
    }
  }

  /*
   * Allow natural variations of the supported questions.
   * This makes the demo feel less scripted.
   */
  if (
    normalizedQuestion.includes("dehydrat") ||
    normalizedQuestion.includes("not drinking enough water")
  ) {
    return DEMO_QUESTIONS["What are the symptoms of dehydration?"];
  }

  if (
    normalizedQuestion.includes("fever") ||
    normalizedQuestion.includes("temperature")
  ) {
    return DEMO_QUESTIONS["What should I do if I have a fever?"];
  }

  if (
    normalizedQuestion.includes("dengue") ||
    normalizedQuestion.includes("mosquito")
  ) {
    return DEMO_QUESTIONS["How can I prevent dengue?"];
  }

  if (
    normalizedQuestion.includes("anemia") ||
    normalizedQuestion.includes("anaemia")
  ) {
    return DEMO_QUESTIONS["What are common symptoms of anemia?"];
  }

  if (
    normalizedQuestion.includes("flu") ||
    normalizedQuestion.includes("influenza")
  ) {
    return DEMO_QUESTIONS["How can I prevent seasonal flu?"];
  }

  if (
    normalizedQuestion.includes("diarrhea") ||
    normalizedQuestion.includes("diarrhoea")
  ) {
    return DEMO_QUESTIONS["What should I do for diarrhea?"];
  }

  if (
    normalizedQuestion.includes("healthy diet") ||
    normalizedQuestion.includes("diet") ||
    normalizedQuestion.includes("healthy food")
  ) {
    return DEMO_QUESTIONS["How can I maintain a healthy diet?"];
  }

  if (
    normalizedQuestion.includes("emergency") ||
    normalizedQuestion.includes("urgent") ||
    normalizedQuestion.includes("warning sign")
  ) {
    return DEMO_QUESTIONS["What are the warning signs of an emergency?"];
  }

  if (
    normalizedQuestion.includes("blood pressure") ||
    normalizedQuestion.includes("hypertension")
  ) {
    return DEMO_QUESTIONS["How can I prevent high blood pressure?"];
  }

  if (
    normalizedQuestion.includes("doctor") ||
    normalizedQuestion.includes("medical help") ||
    normalizedQuestion.includes("see a doctor")
  ) {
    return DEMO_QUESTIONS["When should I see a doctor?"];
  }

  return "I can help with general health information, prevention, common symptoms, healthy habits, and guidance on when to seek professional medical care. Could you rephrase your question or ask about a specific health topic?";
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);

  const sendMessage = (question: string) => {
    const trimmedQuestion = question.trim();

    if (!trimmedQuestion || isTyping) {
      return;
    }

    const userMessage: Message = {
      id: Date.now(),
      role: "user",
      content: trimmedQuestion,
    };

    setMessages((previous) => [...previous, userMessage]);
    setInput("");
    setIsTyping(true);

    // Small delay makes the interaction feel natural.
    setTimeout(() => {
      const answer = getAnswer(trimmedQuestion);

      const assistantMessage: Message = {
        id: Date.now() + 1,
        role: "assistant",
        content: answer,
      };

      setMessages((previous) => [...previous, assistantMessage]);
      setIsTyping(false);
    }, 500);
  };

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    sendMessage(input);
  };

  const handleSuggestedQuestion = (question: string) => {
    sendMessage(question);
  };

  return (
    <main className="min-h-screen bg-[#07110f] text-white">
      <div className="mx-auto flex min-h-screen w-full max-w-5xl flex-col px-4 py-6 sm:px-6 lg:px-8">

        {/* Header */}
        <header className="mb-6 flex items-center justify-between border-b border-white/10 pb-5">
          <div>
            <h1 className="text-2xl font-semibold tracking-tight">
              JanSwasthya AI
            </h1>

            <p className="mt-1 text-sm text-white/50">
              Your public health information assistant
            </p>
          </div>

          <div className="flex items-center gap-2 rounded-full border border-emerald-400/20 bg-emerald-400/10 px-3 py-1.5">
            <span className="h-2 w-2 rounded-full bg-emerald-400" />
            <span className="text-xs text-emerald-300">
              Online
            </span>
          </div>
        </header>

        {/* Chat area */}
        <section
          className="flex-1 overflow-y-auto pb-6"
          aria-live="polite"
        >
          {messages.length === 0 ? (
            <div className="flex min-h-[55vh] flex-col items-center justify-center text-center">

              <div className="mb-6 flex h-16 w-16 items-center justify-center rounded-2xl border border-emerald-400/20 bg-emerald-400/10">
                <span className="text-2xl">✚</span>
              </div>

              <h2 className="text-3xl font-semibold tracking-tight sm:text-4xl">
                How can I help you today?
              </h2>

              <p className="mt-3 max-w-xl text-sm leading-6 text-white/50 sm:text-base">
                Ask me about common health concerns, prevention,
                healthy habits, or when you should seek professional
                medical care.
              </p>

              {/* Only 5 suggestions are visible */}
              <div className="mt-8 w-full max-w-2xl">
                <p className="mb-3 text-left text-xs font-medium uppercase tracking-wider text-white/35">
                  You can ask
                </p>

                <div className="grid gap-2 sm:grid-cols-2">
                  {SUGGESTED_QUESTIONS.map((question) => (
                    <button
                      key={question}
                      type="button"
                      onClick={() => handleSuggestedQuestion(question)}
                      className="rounded-xl border border-white/10 bg-white/[0.03] px-4 py-3 text-left text-sm text-white/75 transition hover:border-emerald-400/30 hover:bg-emerald-400/[0.06] hover:text-white"
                    >
                      {question}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <div className="space-y-5">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${
                    message.role === "user"
                      ? "justify-end"
                      : "justify-start"
                  }`}
                >
                  <div
                    className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-6 sm:max-w-[75%] ${
                      message.role === "user"
                        ? "rounded-br-md bg-emerald-500 text-black"
                        : "rounded-bl-md border border-white/10 bg-white/[0.05] text-white/80"
                    }`}
                  >
                    {message.content}
                  </div>
                </div>
              ))}

              {/* Typing indicator */}
              {isTyping && (
                <div className="flex justify-start">
                  <div className="rounded-2xl rounded-bl-md border border-white/10 bg-white/[0.05] px-5 py-4">
                    <div className="flex items-center gap-1.5">
                      <span className="h-2 w-2 animate-bounce rounded-full bg-white/40 [animation-delay:-0.3s]" />
                      <span className="h-2 w-2 animate-bounce rounded-full bg-white/40 [animation-delay:-0.15s]" />
                      <span className="h-2 w-2 animate-bounce rounded-full bg-white/40" />
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </section>

        {/* Input */}
        <div className="sticky bottom-0 pt-4">
          <form
            onSubmit={handleSubmit}
            className="flex items-center gap-2 rounded-2xl border border-white/10 bg-[#0c1916] p-2 shadow-2xl"
          >
            <input
              type="text"
              value={input}
              onChange={(event) => setInput(event.target.value)}
              placeholder="Ask a health question..."
              disabled={isTyping}
              className="min-w-0 flex-1 bg-transparent px-3 py-3 text-sm text-white outline-none placeholder:text-white/30 disabled:opacity-50"
            />

            <button
              type="submit"
              disabled={!input.trim() || isTyping}
              className="rounded-xl bg-emerald-500 px-5 py-3 text-sm font-medium text-black transition hover:bg-emerald-400 disabled:cursor-not-allowed disabled:opacity-30"
            >
              Send
            </button>
          </form>

          <p className="mt-3 text-center text-[11px] leading-5 text-white/30">
            JanSwasthya AI provides general health information and is not
            a substitute for professional medical advice.
          </p>
        </div>
      </div>
    </main>
  );
}