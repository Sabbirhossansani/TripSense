import React, { useState } from "react";
import { motion, useScroll, useSpring } from "framer-motion";
import { cn } from "../../lib/utils";

export function ScrollProgressRail() {
  const { scrollYProgress } = useScroll();
  const scaleX = useSpring(scrollYProgress, {
    stiffness: 170,
    damping: 28,
    restDelta: 0.001,
  });

  return (
    <motion.div
      aria-hidden="true"
      className="fixed top-0 left-0 right-0 h-[2.5px] z-[120] origin-left pointer-events-none"
      style={{
        scaleX,
        background: "linear-gradient(90deg, #1E4D3F 0%, #D94E28 70%, #B8863B 100%)",
      }}
    />
  );
}

export function SpotlightCard({ children, className = "", onClick }) {
  const [pos, setPos] = useState({ x: 0, y: 0, visible: false });

  const handleMove = (e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    setPos({
      x: e.clientX - rect.left,
      y: e.clientY - rect.top,
      visible: true,
    });
  };

  return (
    <motion.div
      onMouseMove={handleMove}
      onMouseLeave={() => setPos((p) => ({ ...p, visible: false }))}
      onClick={onClick}
      whileHover={{ y: -2 }}
      transition={{ duration: 0.25, ease: [0.22, 1, 0.36, 1] }}
      className={cn(
        "relative overflow-hidden rounded-3xl bg-white border border-[#E6E1D6] shadow-[0_2px_10px_rgba(20,23,21,0.03)] transition-colors hover:border-[#D2C9B8]",
        className
      )}
    >
      <div
        aria-hidden="true"
        className="pointer-events-none absolute -inset-px transition-opacity duration-300"
        style={{
          opacity: pos.visible ? 1 : 0,
          background: `radial-gradient(420px circle at ${pos.x}px ${pos.y}px, rgba(217, 78, 40, 0.07), transparent 45%)`,
        }}
      />
      <div className="relative z-10 h-full">{children}</div>
    </motion.div>
  );
}

export function TextMaskReveal({ children, delay = 0, className = "" }) {
  return (
    <div className={cn("overflow-hidden", className)}>
      <motion.div
        initial={{ y: "100%", opacity: 0 }}
        animate={{ y: "0%", opacity: 1 }}
        transition={{ duration: 0.72, delay, ease: [0.22, 1, 0.36, 1] }}
      >
        {children}
      </motion.div>
    </div>
  );
}

export function InfiniteMarquee({ items, renderItem, className = "" }) {
  return (
    <div
      className={cn(
        "relative w-full overflow-hidden [mask-image:linear-gradient(to_right,transparent,black_6%,black_94%,transparent)]",
        className
      )}
    >
      <div className="marquee-track gap-5 py-2">
        {[...items, ...items].map((item, idx) => (
          <div key={`${item.id || idx}-${idx}`} className="shrink-0">
            {renderItem(item, idx)}
          </div>
        ))}
      </div>
    </div>
  );
}

export function SectionFade({ children, delay = 0, className = "" }) {
  return (
    <motion.section
      initial={{ opacity: 0, y: 24 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.12 }}
      transition={{ duration: 0.65, delay, ease: [0.22, 1, 0.36, 1] }}
      className={className}
    >
      {children}
    </motion.section>
  );
}
