import React, { useRef, useState } from "react";
import { motion, useScroll, useSpring, useTransform } from "framer-motion";

export function ScrollProgressRail() {
  const { scrollYProgress } = useScroll();
  const scaleX = useSpring(scrollYProgress, {
    stiffness: 180,
    damping: 26,
    restDelta: 0.001,
  });

  return (
    <motion.div
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        height: "3px",
        background: "linear-gradient(90deg, var(--alpine-moss) 0%, var(--safety-orange) 70%, var(--brass-ochre) 100%)",
        transformOrigin: "0% 50%",
        scaleX,
        zIndex: 12000,
        pointerEvents: "none",
      }}
    />
  );
}

export function ScrollReveal({ children, delay = 0, className = "", style = {} }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.08 }}
      transition={{ duration: 0.58, delay, ease: [0.22, 1, 0.36, 1] }}
      className={className}
      style={style}
    >
      {children}
    </motion.div>
  );
}

export function ParallaxPhoto({ src, alt, style = {}, imgStyle = {} }) {
  const containerRef = useRef(null);
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start end", "end start"],
  });
  const y = useTransform(scrollYProgress, [0, 1], [-12, 12]);

  return (
    <div ref={containerRef} style={{ position: "relative", overflow: "hidden", ...style }}>
      <motion.img
        src={src}
        alt={alt}
        style={{
          width: "100%",
          height: "110%",
          objectFit: "cover",
          display: "block",
          y,
          scale: 1.04,
          ...imgStyle,
        }}
      />
    </div>
  );
}

export function StaggerContainer({ children, className = "", style = {}, delayChildren = 0.04 }) {
  return (
    <motion.div
      initial="hidden"
      animate="visible"
      variants={{
        hidden: {},
        visible: {
          transition: {
            staggerChildren: 0.06,
            delayChildren,
          },
        },
      }}
      className={className}
      style={style}
    >
      {children}
    </motion.div>
  );
}

export function StaggerItem({ children, className = "", style = {} }) {
  return (
    <motion.div
      variants={{
        hidden: { opacity: 0, y: 14 },
        visible: {
          opacity: 1,
          y: 0,
          transition: { duration: 0.42, ease: [0.22, 1, 0.36, 1] },
        },
      }}
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
      rotateX: (0.5 - y) * 5,
      rotateY: (x - 0.5) * 5,
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
      transition={{ type: "spring", stiffness: 240, damping: 24 }}
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
    const dx = ((e.clientX - rect.left) / rect.width - 0.5) * 7;
    const dy = ((e.clientY - rect.top) / rect.height - 0.5) * 5;
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
      transition={{ type: "spring", stiffness: 300, damping: 22 }}
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
