import React from "react";
import { ArrowUpRight, Sparkles, ShieldCheck, Leaf, CloudRain, Compass } from "lucide-react";
import CinematicHero from "./CinematicHero";
import BeforeAfterComparer from "./BeforeAfterComparer";
import { InfiniteMarquee, SpotlightCard, SectionFade } from "./ui/AnimatedPrimitives";

const CURATED_DESTINATIONS = [
  {
    id: "bandarban",
    city: "Bandarban",
    subtitle: "Cloud Peaks & Boga Crater Lake",
    coords: "22.19° N, 92.21° E",
    eco: "Eco 94/100",
    image: "https://images.unsplash.com/photo-1519681393784-d120267933ba?auto=format&fit=crop&w=900&q=80",
  },
  {
    id: "chittagong",
    city: "Chittagong",
    subtitle: "Patenga Coast, Lakes & Heritage",
    coords: "22.35° N, 91.78° E",
    eco: "Eco 91/100",
    image: "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=900&q=80",
  },
  {
    id: "sylhet",
    city: "Sylhet",
    subtitle: "Ratargul Canopy & Tea Sanctuaries",
    coords: "24.89° N, 91.86° E",
    eco: "Eco 95/100",
    image: "https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&w=900&q=80",
  },
  {
    id: "coxsbazar",
    city: "Cox's Bazar",
    subtitle: "Inani Coral Coast & Marine Drive",
    coords: "21.42° N, 92.00° E",
    eco: "Eco 89/100",
    image: "https://images.unsplash.com/photo-1473116763249-2faaef81ccda?auto=format&fit=crop&w=900&q=80",
  },
  {
    id: "dhaka",
    city: "Dhaka",
    subtitle: "Mughal Forts & Culinary Heritage",
    coords: "23.81° N, 90.41° E",
    eco: "Eco 86/100",
    image: "https://images.unsplash.com/photo-1587474260584-136574528ed5?auto=format&fit=crop&w=900&q=80",
  },
  {
    id: "tokyo",
    city: "Tokyo",
    subtitle: "Craft Alleys, Gardens & Design",
    coords: "35.67° N, 139.65° E",
    eco: "Eco 92/100",
    image: "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?auto=format&fit=crop&w=900&q=80",
  },
];

export default function ExploreLandingView({
  city,
  days,
  availableDestinations,
  fairnessScore,
  co2SavedKg,
  lang,
  onLaunchPlan,
  onStartSwipe,
  onOpenCopilot,
  onOpenItinerary,
  onOpenMlLab,
}) {
  return (
    <div className="w-full pb-24 space-y-24">
      {/* 1. Full-Viewport Cinematic Hero */}
      <CinematicHero
        city={city}
        days={days}
        availableDestinations={availableDestinations}
        fairnessScore={fairnessScore}
        lang={lang}
        onLaunchPlan={onLaunchPlan}
        onStartSwipe={onStartSwipe}
        onOpenCopilot={onOpenCopilot}
      />

      {/* 2. Infinite Editorial Destination Marquee */}
      <SectionFade className="max-w-[1440px] mx-auto px-4 sm:px-6">
        <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 mb-8 max-w-6xl mx-auto">
          <div>
            <p className="text-[11px] font-bold uppercase tracking-[0.18em] text-[#1E4D3F] mb-2">
              Curated Regions
            </p>
            <h2 className="font-display text-3xl sm:text-4xl font-semibold tracking-tight text-[#141715]">
              Where will your squad roam next?
            </h2>
          </div>
          <p className="text-sm text-[#5A605C] max-w-sm">
            Tap any destination below to instantly generate a balanced multi-day route backed by verified local hosts.
          </p>
        </div>

        <InfiniteMarquee
          items={CURATED_DESTINATIONS}
          renderItem={(dest) => (
            <button
              type="button"
              onClick={() => onLaunchPlan({ city: dest.city, days: 3 })}
              className="group relative w-[290px] sm:w-[330px] text-left rounded-3xl overflow-hidden bg-white border border-[#E6E1D6] shadow-[0_4px_18px_rgba(20,23,21,0.04)] hover:shadow-[0_18px_40px_rgba(20,23,21,0.1)] transition-all duration-300 cursor-pointer"
            >
              <div className="relative aspect-[4/3] overflow-hidden bg-[#EFECE4]">
                <img
                  src={dest.image}
                  alt={dest.city}
                  loading="lazy"
                  className="w-full h-full object-cover transition-transform duration-700 ease-out group-hover:scale-105"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-[#141715]/70 via-transparent to-transparent" />
                <span className="absolute top-3.5 left-3.5 rounded-full bg-[#1E4D3F]/90 backdrop-blur-md text-white text-[10px] font-bold px-2.5 py-1">
                  {dest.eco}
                </span>
                <span className="absolute bottom-3.5 left-4 font-mono-num text-[10px] tracking-wider text-white/80">
                  {dest.coords}
                </span>
              </div>

              <div className="p-4 flex items-center justify-between gap-3">
                <div>
                  <h3 className="font-display text-lg font-semibold text-[#141715] group-hover:text-[#D94E28] transition-colors">
                    {dest.city}
                  </h3>
                  <p className="text-xs text-[#5A605C] mt-0.5">{dest.subtitle}</p>
                </div>
                <div className="w-9 h-9 rounded-full bg-[#F8F6F1] group-hover:bg-[#D94E28] group-hover:text-white text-[#141715] flex items-center justify-center transition-colors shrink-0">
                  <ArrowUpRight className="w-4 h-4" />
                </div>
              </div>
            </button>
          )}
        />
      </SectionFade>

      {/* 3. Asymmetric Spotlight Bento Showcase */}
      <SectionFade className="max-w-6xl mx-auto px-4 sm:px-6">
        <div className="mb-10 max-w-2xl">
          <p className="text-[11px] font-bold uppercase tracking-[0.18em] text-[#D94E28] mb-2">
            Engineered for Calm Group Decisions
          </p>
          <h2 className="font-display text-3xl sm:text-4xl font-semibold tracking-tight text-[#141715]">
            No spreadsheets. No tourist traps. Zero group arguments.
          </h2>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Card 1 (7 Cols): Interactive Before/After Comparer */}
          <SpotlightCard className="lg:col-span-7 p-2 sm:p-4">
            <BeforeAfterComparer city={city} />
          </SpotlightCard>

          {/* Card 2 (5 Cols): Active Bayesian Taste Swipe */}
          <SpotlightCard className="lg:col-span-5 p-7 flex flex-col justify-between bg-[#141715] text-[#F8F6F1] border-[#262C29]">
            <div>
              <div className="inline-flex items-center gap-2 rounded-full bg-white/10 px-3 py-1 text-[11px] font-semibold text-[#F4A586] mb-5">
                <Sparkles className="w-3.5 h-3.5" />
                <span>Active Bayesian EIG</span>
              </div>
              <h3 className="font-display text-2xl sm:text-3xl font-semibold text-white leading-tight">
                Calibrate your real taste in 5 quick swipes.
              </h3>
              <p className="text-sm text-white/70 mt-3 leading-relaxed">
                Skip tedious 30-checkbox forms. Our diagonal-Gaussian Bayesian sampler picks the most informative travel cards to infer your true style in under 60 seconds.
              </p>
            </div>

            <div className="mt-8 pt-6 border-t border-white/12 flex items-center justify-between gap-4">
              <div className="font-mono-num text-xs text-white/70">
                <span className="text-white font-semibold block text-base">+59%</span>
                Cold-start accuracy gain
              </div>
              <button
                type="button"
                onClick={onStartSwipe}
                className="inline-flex items-center gap-2 rounded-full bg-[#D94E28] hover:bg-[#BF401E] text-white text-xs sm:text-sm font-semibold px-5 py-2.5 transition cursor-pointer"
              >
                <span>Start Swipe Deck</span>
                <ArrowUpRight className="w-4 h-4" />
              </button>
            </div>
          </SpotlightCard>

          {/* Card 3 (6 Cols): Live Monsoon Shield & Nash Veto */}
          <SpotlightCard className="lg:col-span-6 p-7 flex flex-col justify-between">
            <div>
              <div className="w-10 h-10 rounded-2xl bg-[#E8F2EE] text-[#1E4D3F] flex items-center justify-center mb-5">
                <CloudRain className="w-5 h-5" />
              </div>
              <h3 className="font-display text-2xl font-semibold text-[#141715]">
                Monsoon Rain Shield & One-Tap Nash Veto
              </h3>
              <p className="text-sm text-[#5A605C] mt-2.5 leading-relaxed">
                If sudden rain hits or one friend vetoes a stop, TripSense swaps it instantaneously for an unscheduled indoor sanctuary or higher-welfare alternative—without duplicating spots across days.
              </p>
            </div>

            <div className="mt-7 flex items-center justify-between pt-4 border-t border-[#EFECE4]">
              <span className="inline-flex items-center gap-1.5 text-xs font-semibold text-[#1E4D3F]">
                <ShieldCheck className="w-4 h-4" />
                Zero cross-day duplicates
              </span>
              <button
                type="button"
                onClick={onOpenItinerary}
                className="inline-flex items-center gap-1.5 text-xs font-bold text-[#141715] hover:text-[#D94E28] transition cursor-pointer"
              >
                <span>Open Trip Workspace</span>
                <ArrowUpRight className="w-4 h-4" />
              </button>
            </div>
          </SpotlightCard>

          {/* Card 4 (6 Cols): Carbon & Local SME Economy */}
          <SpotlightCard className="lg:col-span-6 p-7 flex flex-col justify-between">
            <div>
              <div className="w-10 h-10 rounded-2xl bg-[#FDF0EB] text-[#D94E28] flex items-center justify-center mb-5">
                <Leaf className="w-5 h-5" />
              </div>
              <h3 className="font-display text-2xl font-semibold text-[#141715]">
                Lower Carbon. Higher Local Community Share.
              </h3>
              <p className="text-sm text-[#5A605C] mt-2.5 leading-relaxed">
                Every generated itinerary computes real CO₂ savings ({co2SavedKg} kg saved on your active trip), favors low-congestion hidden gems, and channels 80%+ of voucher revenue straight to verified community collectives.
              </p>
            </div>

            <div className="mt-7 flex items-center justify-between pt-4 border-t border-[#EFECE4]">
              <span className="inline-flex items-center gap-1.5 text-xs font-semibold text-[#5A605C]">
                <Compass className="w-4 h-4 text-[#D94E28]" />
                CLIP + FairNet Q1 Verified
              </span>
              <button
                type="button"
                onClick={onOpenMlLab}
                className="inline-flex items-center gap-1.5 text-xs font-bold text-[#141715] hover:text-[#D94E28] transition cursor-pointer"
              >
                <span>Inspect Q1 Lab & Eco</span>
                <ArrowUpRight className="w-4 h-4" />
              </button>
            </div>
          </SpotlightCard>
        </div>
      </SectionFade>
    </div>
  );
}
