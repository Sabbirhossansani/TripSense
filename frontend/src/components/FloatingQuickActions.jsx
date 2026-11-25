import React from "react";
import { motion } from "framer-motion";
import { Bot } from "lucide-react";

export default function FloatingQuickActions({ onOpenCopilot }) {
  return (
    <motion.button
      type="button"
      onClick={onOpenCopilot}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.96 }}
      aria-label="Open TripSense AI Concierge"
      className="desktop-only-fab fixed bottom-6 right-6 z-40 inline-flex flex-nowrap items-center gap-2.5 whitespace-nowrap rounded-full bg-[#141715] hover:bg-[#232926] text-white pl-4 pr-5 py-3 text-xs font-semibold shadow-[0_14px_34px_rgba(20,23,21,0.28)] border border-white/15 cursor-pointer"
    >
      <span className="relative flex h-2.5 w-2.5">
        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#D94E28] opacity-75" />
        <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-[#D94E28]" />
      </span>
      <Bot className="w-4 h-4 text-[#F4A586]" />
      <span>AI Concierge</span>
    </motion.button>
  );
}
