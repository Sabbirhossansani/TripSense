import React, { useState, useEffect } from "react";
import { Sparkles, Check, Users, CloudRain, Navigation, ShieldCheck, Scale } from "lucide-react";

const SOLVER_STEPS = [
  {
    step: 1,
    title: "Least-Misery Preference Consensus",
    subtitle: "Harmonizing tripmate tastes so no member gets alienated...",
    icon: Users,
    color: "#E85D2A"
  },
  {
    step: 2,
    title: "Live Weather & Rain Radar Scan",
    subtitle: "Verifying dry window conditions and indoor backup suitability...",
    icon: CloudRain,
    color: "#06b6d4"
  },
  {
    step: 3,
    title: "2-Opt TSP Route Minimization",
    subtitle: "Running Travelling Salesperson heuristic to minimize traffic transit...",
    icon: Navigation,
    color: "#f59e0b"
  },
  {
    step: 4,
    title: "Fairness Disparity & Budget Engine",
    subtitle: "Ensuring Pareto efficiency and optimal BDT/USD spending allocation...",
    icon: Scale,
    color: "#10b981"
  },
  {
    step: 5,
    title: "Passport Stamped & Route Locked",
    subtitle: "Welcome to your intelligent, conflict-free trip itinerary!",
    icon: ShieldCheck,
    color: "#ec4899"
  }
];

export default function AiSolverModal({ city = "Chittagong", onFinish }) {
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [progress, setProgress] = useState(15);

  useEffect(() => {
    const timer1 = setTimeout(() => {
      setCurrentStepIndex(1);
      setProgress(40);
    }, 700);

    const timer2 = setTimeout(() => {
      setCurrentStepIndex(2);
      setProgress(68);
    }, 1500);

    const timer3 = setTimeout(() => {
      setCurrentStepIndex(3);
      setProgress(88);
    }, 2300);

    const timer4 = setTimeout(() => {
      setCurrentStepIndex(4);
      setProgress(100);
    }, 3100);

    const timer5 = setTimeout(() => {
      if (onFinish) onFinish();
    }, 3900);

    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);
      clearTimeout(timer4);
      clearTimeout(timer5);
    };
  }, [onFinish]);

  const activeStep = SOLVER_STEPS[currentStepIndex];
  const StepIcon = activeStep.icon;

  return (
    <div style={{
      position: "fixed",
      inset: 0,
      zIndex: 100000,
      background: "linear-gradient(135deg, #090d16 0%, #25463B 100%)",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      padding: "20px",
      fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    }}>
      <div style={{
        background: "rgba(255, 255, 255, 0.96)",
        borderRadius: "32px",
        padding: "36px 30px",
        maxWidth: "460px",
        width: "100%",
        textAlign: "center",
        boxShadow: "0 25px 60px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.2)",
        animation: "slideUp 0.35s ease"
      }}>
        {/* Glowing Dynamic Icon */}
        <div style={{
          position: "relative",
          width: "80px",
          height: "80px",
          margin: "0 auto 20px auto",
          borderRadius: "26px",
          background: `linear-gradient(135deg, ${activeStep.color} 0%, #CC4A1B 100%)`,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          color: "#ffffff",
          boxShadow: `0 12px 30px ${activeStep.color}55`,
          transition: "all 0.4s ease"
        }}>
          <StepIcon size={40} strokeWidth={2.2} />
        </div>

        {/* Solver Title */}
        <div style={{
          display: "inline-flex",
          alignItems: "center",
          gap: "6px",
          background: "#FFF0EA",
          color: "#CC4A1B",
          padding: "4px 12px",
          borderRadius: "20px",
          fontSize: "11px",
          fontWeight: 800,
          marginBottom: "10px",
          letterSpacing: "0.5px"
        }}>
          <Sparkles size={13} />
          TRIPSENSE AI ENGINE • {city.toUpperCase()}
        </div>

        <h3 style={{
          fontSize: "20px",
          fontWeight: 900,
          color: "#1A1D1C",
          margin: "0 0 8px 0",
          minHeight: "28px"
        }}>
          {activeStep.title}
        </h3>

        <p style={{
          fontSize: "13px",
          color: "#59615E",
          lineHeight: 1.5,
          margin: "0 0 24px 0",
          minHeight: "40px"
        }}>
          {activeStep.subtitle}
        </p>

        {/* Progress Bar */}
        <div style={{
          width: "100%",
          height: "10px",
          background: "#E2DDD3",
          borderRadius: "999px",
          overflow: "hidden",
          marginBottom: "18px"
        }}>
          <div style={{
            width: `${progress}%`,
            height: "100%",
            background: "linear-gradient(90deg, #E85D2A 0%, #06b6d4 50%, #10b981 100%)",
            borderRadius: "999px",
            transition: "width 0.4s ease-in-out"
          }} />
        </div>

        {/* Steps Checkmarks List */}
        <div style={{
          display: "flex",
          flexDirection: "column",
          gap: "8px",
          textAlign: "left",
          background: "#F6F4EF",
          border: "1px solid #E2DDD3",
          borderRadius: "16px",
          padding: "12px 14px"
        }}>
          {SOLVER_STEPS.map((s, idx) => {
            const isDone = idx < currentStepIndex;
            const isCurrent = idx === currentStepIndex;

            return (
              <div
                key={s.step}
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "10px",
                  fontSize: "12px",
                  fontWeight: isCurrent ? 800 : 600,
                  color: isDone ? "#059669" : isCurrent ? "#E85D2A" : "#94a3b8"
                }}
              >
                <div style={{
                  width: "18px",
                  height: "18px",
                  borderRadius: "50%",
                  background: isDone ? "#10b981" : isCurrent ? "#E85D2A" : "#cbd5e1",
                  color: "#ffffff",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontSize: "10px",
                  flexShrink: 0
                }}>
                  {isDone ? <Check size={11} strokeWidth={3} /> : s.step}
                </div>
                <span>{s.title}</span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
