"use client";

import {
  useEffect,
  useRef,
  useState,
  type ElementType,
  type ReactNode,
} from "react";

type Direction = "up" | "left" | "right" | "scale" | "none";

type Props = {
  children: ReactNode;
  delay?: number;
  duration?: number;
  direction?: Direction;
  className?: string;
  /** distance in px for translate-based reveals */
  distance?: number;
  /** trigger once or every time it enters viewport */
  once?: boolean;
  /** intersection ratio threshold */
  threshold?: number;
  as?: ElementType;
  /**
   * If true, applies the .reveal-stagger CSS class so direct children
   * with .reveal class get sequential transition-delay (see globals.css).
   */
  stagger?: boolean;
  id?: string;
};

const DIRECTION_FROM: Record<Direction, (d: number) => string> = {
  up: (d) => `translate3d(0, ${d}px, 0)`,
  left: (d) => `translate3d(-${d}px, 0, 0)`,
  right: (d) => `translate3d(${d}px, 0, 0)`,
  scale: () => "scale(0.92)",
  none: () => "none",
};

/**
 * Lightweight scroll-reveal wrapper using IntersectionObserver.
 * Respects prefers-reduced-motion: shows content immediately, no animation.
 *
 * Two ways to stagger children:
 *   1. <Reveal stagger> wraps direct children carrying the `reveal` class
 *      with CSS-driven nth-child delays (see globals.css → .reveal-stagger).
 *   2. Use multiple <Reveal delay={...}> nested manually.
 */
export function Reveal({
  children,
  delay = 0,
  duration = 600,
  direction = "up",
  className = "",
  distance = 18,
  once = true,
  threshold = 0.15,
  as: Tag = "div",
  stagger = false,
  id,
}: Props) {
  const ref = useRef<HTMLElement | null>(null);
  const [shown, setShown] = useState(false);
  const [reduced, setReduced] = useState(false);

  useEffect(() => {
    if (typeof window === "undefined") return;
    const mq = window.matchMedia("(prefers-reduced-motion: reduce)");
    setReduced(mq.matches);
    const onChange = () => setReduced(mq.matches);
    mq.addEventListener?.("change", onChange);
    return () => mq.removeEventListener?.("change", onChange);
  }, []);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    if (reduced) {
      setShown(true);
      // Make sure CSS-stagger child reveals also show immediately.
      el.classList.add("is-visible");
      return;
    }
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) {
            setShown(true);
            el.classList.add("is-visible");
            if (once) io.unobserve(e.target);
          } else if (!once) {
            setShown(false);
            el.classList.remove("is-visible");
          }
        });
      },
      { threshold, rootMargin: "0px 0px -8% 0px" }
    );
    io.observe(el);
    return () => io.disconnect();
  }, [once, threshold, reduced]);

  const fromTransform = DIRECTION_FROM[direction](distance);

  const style: React.CSSProperties = reduced
    ? {}
    : {
        opacity: shown ? 1 : 0,
        transform: shown ? "none" : fromTransform,
        transition: `opacity ${duration}ms cubic-bezier(0.4,0,0.2,1) ${delay}ms, transform ${duration}ms cubic-bezier(0.4,0,0.2,1) ${delay}ms`,
        willChange: shown ? "auto" : "opacity, transform",
      };

  const cls = [stagger ? "reveal-stagger" : "", className]
    .filter(Boolean)
    .join(" ");

  return (
    <Tag ref={ref as React.Ref<HTMLElement>} id={id} className={cls} style={style}>
      {children}
    </Tag>
  );
}
