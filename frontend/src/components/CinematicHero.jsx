import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Sparkles, ArrowRight, Bot, MapPin, Calendar, Compass, ChevronDown } from "lucide-react";
import { TextMaskReveal } from "./ui/AnimatedPrimitives";

const HERO_SLIDES = [
  {
    city: "Chittagong",
    coords: "22.3569° N • 91.7832° E",
    caption: "Bay of Bengal Sunset Coast & Emerald Ridges",
    image: "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1800&q=85",
  },
  {
    city: "Bandarban",
    coords: "22.1953° N • 92.2184° E",
    caption: "Cloud-Wrapped Peaks & Boga Crater Trails",
    image: "https://images.unsplash.com/photo-1519681393784-d120267933ba?auto=format&fit=crop&w=1800&q=85",
  },
  {
    city: "Sylhet",
    coords: "24.8949° N • 91.8687° E",
    caption: "Ratargul Canopy & Misty Tea Valleys",
    image: "https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&w=1800&q=85",
  },
];

export default function CinematicHero({
  city = "Chittagong",
  days = 3,
  availableDestinations = ["Chittagong", "Bandarban", "Sylhet", "Cox's Bazar", "Dhaka", "Tokyo", "Paris"],
  fairnessScore = 97.5,
  lang = "EN",
  onLaunchPlan,
  onStartSwipe,
  onOpenCopilot,
}) {
  const [slideIdx, setSlideIdx] = useState(0);
  const [selectedCity, setSelectedCity] = useState(city);
  const [selectedDays, setSelectedDays] = useState(days);
  const [vibePrompt, setVibePrompt] = useState("");
  const isBn = lang === "BN";

  useEffect(() => {
    const id = setInterval(() => {
      setSlideIdx((prev) => (prev + 1) % HERO_SLIDES.length);
    }, 6800);
    return () => clearInterval(id);
  }, []);

  const currentSlide = HERO_SLIDES[slideIdx];

  const handleSubmit = (e) => {
    e.preventDefault();
    if (onLaunchPlan) {
      onLaunchPlan({ city: selectedCity, days: Number(selectedDays), prompt: vibePrompt.trim() });
    }
  };

  return (
    <div className="w-full max-w-[1440px] mx-auto px-3 sm:px-6 pt-3">
      <section className="relative min-h-[84vh] sm:min-h-[88vh] w-full overflow-hidden rounded-[28px] sm:rounded-[36px] flex flex-col justify-between p-6 sm:p-10 lg:p-14 shadow-[0_28px_70px_rgba(20,23,21,0.16)] bg-[#141715]">
        {/* Full-Bleed Ken Burns Background Slideshow */}
        <div className="absolute inset-0 z-0">
          <AnimatePresence mode="sync">
            <motion.img
              key={currentSlide.image}
              src={currentSlide.image}
              alt={currentSlide.caption}
              initial={{ opacity: 0, scale: 1.09 }}
              animate={{ opacity: 1, scale: 1.01 }}
              exit={{ opacity: 0 }}
              transition={{
                opacity: { duration: 1.3, ease: "easeInOut" },
                scale: { duration: 7.2, ease: "linear" },
              }}
              className="absolute inset-0 w-full h-full object-cover"
            />
          </AnimatePresence>
          <div className="absolute inset-0 bg-gradient-to-b from-[#141715]/60 via-[#141715]/35 to-[#141715]/85" />
        </div>

        {/* Quiet Top Meta Bar inside Hero */}
        <div className="relative z-10 flex items-center justify-between gap-4 text-white/90">
          <div className="inline-flex items-center gap-2 rounded-full bg-white/12 backdrop-blur-md border border-white/20 px-3.5 py-1.5 text-[11px] font-semibold tracking-[0.14em] uppercase">
            <Compass className="w-3.5 h-3.5 text-[#F4A586]" />
            <span>TripSense FairNet • AI Group Travel</span>
          </div>
          <div className="hidden sm:flex items-center gap-2 font-mono-num text-[11px] tracking-[0.12em] uppercase text-white/75">
            <span>{currentSlide.coords}</span>
            <span className="opacity-40">•</span>
            <span>{currentSlide.city}</span>
          </div>
        </div>

        {/* Center Editorial Headline & Floating Mindtrip-Style Prompt Bar */}
        <div className="relative z-10 max-w-4xl mx-auto text-center my-auto py-10 sm:py-12 w-full">
          <TextMaskReveal delay={0.05}>
            <h1 className="font-display text-[2.45rem] sm:text-6xl lg:text-[4.55rem] font-semibold tracking-[-0.03em] leading-[1.03] text-white">
              {isBn ? (
                <>
                  একসাথে ভ্রমণ করুন,{" "}
                  <span className="italic font-normal text-[#F7B69B]">কোনো আপস ছাড়াই।</span>
                </>
              ) : (
                <>
                  Travel together, without{" "}
                  <span className="italic font-normal text-[#F7B69B]">compromise.</span>
                </>
              )}
            </h1>
          </TextMaskReveal>

          <motion.p
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.65, delay: 0.22, ease: [0.22, 1, 0.36, 1] }}
            className="mt-5 text-sm sm:text-lg text-white/82 max-w-2xl mx-auto leading-relaxed font-normal"
          >
            {isBn
              ? "বন্ধুদের আলাদা পছন্দ ও বাজেট ব্যালেন্স করে পরিবেশবান্ধব রুট তৈরি করুন—এক ক্লিকেই।"
              : "Curated group itineraries that balance every friend's taste and budget, shield against monsoon rain, and champion local communities."}
          </motion.p>

          {/* Floating Frosted-Glass Prompt & Quick-Planner Bar */}
          <motion.form
            onSubmit={handleSubmit}
            initial={{ opacity: 0, y: 18 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, delay: 0.34, ease: [0.22, 1, 0.36, 1] }}
            className="mt-9 max-w-[840px] mx-auto bg-white/14 backdrop-blur-2xl border border-white/25 rounded-3xl sm:rounded-full p-2 shadow-[0_24px_60px_rgba(0,0,0,0.35)] flex flex-col sm:flex-row items-stretch sm:items-center gap-2"
          >
            {/* Destination Select */}
            <div className="flex items-center gap-2 bg-white/12 hover:bg-white/18 transition rounded-2xl sm:rounded-full px-4 py-2.5 sm:w-44 shrink-0">
              <MapPin className="w-4 h-4 text-[#F4A586] shrink-0" />
              <select
                aria-label="Choose destination"
                value={selectedCity}
                onChange={(e) => setSelectedCity(e.target.value)}
                className="bg-transparent text-white text-sm font-semibold focus:outline-none w-full cursor-pointer [&>option]:text-[#141715]"
              >
                {availableDestinations.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </div>

            {/* Duration Select */}
            <div className="flex items-center gap-2 bg-white/12 hover:bg-white/18 transition rounded-2xl sm:rounded-full px-4 py-2.5 sm:w-32 shrink-0 whitespace-nowrap">
              <Calendar className="w-4 h-4 text-white/75 shrink-0" />
              <select
                aria-label="Choose trip days"
                value={selectedDays}
                onChange={(e) => setSelectedDays(Number(e.target.value))}
                className="bg-transparent text-white text-sm font-semibold focus:outline-none w-full cursor-pointer whitespace-nowrap [&>option]:text-[#141715]"
              >
                <option value={2}>2 Days</option>
                <option value={3}>3 Days</option>
                <option value={4}>4 Days</option>
                <option value={5}>5 Days</option>
              </select>
            </div>

            {/* Conversational Vibe Input */}
            <input
              type="text"
              value={vibePrompt}
              onChange={(e) => setVibePrompt(e.target.value)}
              placeholder={isBn ? "পছন্দ লিখুন (যেমন: সমুদ্র, খাবার)..." : "Hidden gems, local food, calm pace..."}
              className="flex-1 bg-transparent px-4 py-2.5 text-sm text-white placeholder:text-white/70 focus:outline-none min-w-0"
            />

            {/* Primary CTA */}
            <motion.button
              type="submit"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="bg-[#D94E28] hover:bg-[#C1411E] text-white font-semibold text-sm px-6 py-3 rounded-2xl sm:rounded-full shadow-lg flex items-center justify-center gap-2 transition cursor-pointer shrink-0"
            >
              <span>{isBn ? "প্ল্যান তৈরি করুন" : "Plan Fair Trip"}</span>
              <ArrowRight className="w-4 h-4" />
            </motion.button>
          </motion.form>

          {/* Quiet Secondary Ghost Actions */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.7, delay: 0.48 }}
            className="mt-5 flex flex-wrap items-center justify-center gap-3"
          >
            <button
              type="button"
              onClick={onStartSwipe}
              className="inline-flex items-center gap-2 rounded-full bg-white/10 hover:bg-white/20 backdrop-blur-md border border-white/20 text-white text-xs sm:text-sm font-medium px-4 py-2 transition cursor-pointer"
            >
              <Sparkles className="w-3.5 h-3.5 text-[#F4A586]" />
              <span>{isBn ? "৬০ সেকেন্ডে টেস্ট সোয়াইপ" : "60-Sec Taste Swipe"}</span>
            </button>

            <button
              type="button"
              onClick={onOpenCopilot}
              className="inline-flex items-center gap-2 rounded-full bg-white/10 hover:bg-white/20 backdrop-blur-md border border-white/20 text-white text-xs sm:text-sm font-medium px-4 py-2 transition cursor-pointer"
            >
              <Bot className="w-3.5 h-3.5 text-[#9CE0C2]" />
              <span>{isBn ? "AI কনসিয়ার্জকে জিজ্ঞাসা করুন" : "Ask AI Concierge"}</span>
            </button>
          </motion.div>
        </div>

        {/* Bottom Minimal Proof Strip + Slide Dots */}
        <div className="relative z-10 flex flex-wrap items-center justify-between gap-4 pt-4 border-t border-white/15 text-white/80 text-xs">
          <div className="flex flex-wrap items-center gap-x-6 gap-y-2">
            <span className="font-mono-num">
              <strong className="text-white">{fairnessScore}%</strong> Group Fairness
            </span>
            <span className="font-mono-num">
              <strong className="text-white">68</strong> Verified POIs
            </span>
            <span className="font-mono-num">
              <strong className="text-[#9CE0C2]">0%</strong> Hallucination Guarantee
            </span>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5">
              {HERO_SLIDES.map((s, idx) => (
                <button
                  key={s.city}
                  type="button"
                  aria-label={`Show ${s.city}`}
                  onClick={() => setSlideIdx(idx)}
                  className={`h-1.5 rounded-full transition-all cursor-pointer ${
                    idx === slideIdx ? "w-7 bg-white" : "w-2 bg-white/35 hover:bg-white/60"
                  }`}
                />
              ))}
            </div>
            <ChevronDown className="w-4 h-4 text-white/60 animate-bounce hidden sm:block" />
          </div>
        </div>
      </section>
    </div>
  );
}
