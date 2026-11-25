import React from "react";
import { Compass, Leaf, ShieldCheck, ArrowUpRight } from "lucide-react";

export default function EditorialFooter({ onOpenMlLab }) {
  return (
    <footer className="mt-auto border-t border-[#E6E1D6] bg-[#EFECE4]/60 text-[#141715]">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 py-12">
        <div className="grid grid-cols-1 md:grid-cols-12 gap-8 pb-10 border-b border-[#DFD8CA]">
          <div className="md:col-span-5">
            <div className="flex items-center gap-2.5 mb-3">
              <span className="w-7 h-7 rounded-lg bg-[#D94E28] text-white flex items-center justify-center">
                <Compass className="w-4 h-4" />
              </span>
              <span className="font-display text-lg font-bold tracking-tight">TripSense</span>
            </div>
            <p className="text-xs text-[#5A605C] leading-relaxed max-w-sm m-0">
              Neural group travel consensus, active Bayesian cold-start elicitation, and carbon-aware local SME discovery. Built with CLIP ViT-B/32, PyTorch FairNet, and Neuro-Symbolic RAG.
            </p>
          </div>

          <div className="md:col-span-4 space-y-2 text-xs">
            <div className="text-[10px] font-bold uppercase tracking-[0.14em] text-[#5A605C] mb-2">
              Research &amp; Architecture
            </div>
            <button
              type="button"
              onClick={onOpenMlLab}
              className="flex items-center gap-1 text-[#141715] hover:text-[#D94E28] font-semibold bg-transparent border-none p-0 cursor-pointer"
            >
              <span>Inspect Q1 Benchmark Lab</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </button>
            <div className="flex items-center gap-1.5 text-[#5A605C]">
              <ShieldCheck className="w-3.5 h-3.5 text-[#1E4D3F]" />
              <span>Zero-Hallucination Symbolic Verifier</span>
            </div>
            <div className="flex items-center gap-1.5 text-[#5A605C]">
              <Leaf className="w-3.5 h-3.5 text-[#1E4D3F]" />
              <span>68 Verified Community &amp; Global POIs</span>
            </div>
          </div>

          <div className="md:col-span-3 space-y-2 text-xs">
            <div className="text-[10px] font-bold uppercase tracking-[0.14em] text-[#5A605C] mb-2">
              Open Source
            </div>
            <a
              href="https://github.com/Sabbirhossansani/TripSense"
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-1 text-[#141715] hover:text-[#D94E28] font-semibold no-underline"
            >
              <span>GitHub Repository</span>
              <ArrowUpRight className="w-3.5 h-3.5" />
            </a>
            <div className="text-[#5A605C]">MIT Research Prototype</div>
          </div>
        </div>

        <div className="pt-6 flex flex-col sm:flex-row items-center justify-between gap-3 text-[11px] text-[#5A605C]">
          <span>© 2026 TripSense • Sabbirhossansani</span>
          <span className="font-mono-num">FairNet v3.5 • Warm Alabaster Editorial System</span>
        </div>
      </div>
    </footer>
  );
}
