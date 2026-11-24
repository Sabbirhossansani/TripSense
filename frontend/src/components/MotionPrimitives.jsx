import React, { useState } from "react";
import { motion } from "framer-motion";

export function ScrollReveal({ children, delay = 0, className = "", style = {} }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 22 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.12 }}
      transition={{ duration: 0.55, delay, ease: [0.16, 1, 0.3, 1] }}
      className={className}
      style={style}
    >
      {children}
    </motion.div>
  );
}

export function TiltCard({ children, className = "", style = {}, onClick }) {
  const [tilt, setTilt] = useState({ rotateX: 0, rotateY: 0 });

  const handleMouseMove = (e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = (e.clientX - rect.left) / rect.width;
    const y = (e.clientY - rect.top) / rect.height;
    setTilt({
      rotateX: (0.5 - y) * 6,
      rotateY: (x - 0.5) * 6,
    });
  };

  const handleMouseLeave = () => {
    setTilt({ rotateX: 0, rotateY: 0 });
  };

  return (
    <motion.div
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      onClick={onClick}
      animate={{
        rotateX: tilt.rotateX,
        rotateY: tilt.rotateY,
      }}
      transition={{ type: "spring", stiffness: 260, damping: 24 }}
      style={{
        transformPerspective: 900,
        transformStyle: "preserve-3d",
        ...style,
      }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

export function MagneticButton({ children, onClick, disabled = false, style = {}, className = "", title = "" }) {
  const [offset, setOffset] = useState({ x: 0, y: 0 });

  const handleMove = (e) => {
    if (disabled) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const dx = ((e.clientX - rect.left) / rect.width - 0.5) * 8;
    const dy = ((e.clientY - rect.top) / rect.height - 0.5) * 6;
    setOffset({ x: dx, y: dy });
  };

  return (
    <motion.button
      type="button"
      title={title}
      disabled={disabled}
      onClick={onClick}
      onMouseMove={handleMove}
      onMouseLeave={() => setOffset({ x: 0, y: 0 })}
      animate={{ x: offset.x, y: offset.y }}
      whileTap={disabled ? undefined : { scale: 0.96 }}
      transition={{ type: "spring", stiffness: 320, damping: 22 }}
      className={`liquid-btn ${className}`}
      style={style}
    >
      {children}
    </motion.button>
  );
}

export function ShimmerCardSkeleton({ height = 136 }) {
  return (
    <div
      className="shimmer-skeleton"
      style={{
        width: "100%",
        height: `${height}px`,
        borderRadius: "18px",
        border: "1px solid var(--stone-border)",
        marginBottom: "12px",
      }}
    />
  );
}
