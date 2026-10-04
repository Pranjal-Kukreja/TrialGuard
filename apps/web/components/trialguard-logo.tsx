import React from "react"

interface TrialGuardLogoProps {
  className?: string
  width?: number
  height?: number
  showSubtitle?: boolean
}

export function TrialGuardLogo({
  className = "h-8 w-auto",
  width,
  height,
  showSubtitle = false,
}: TrialGuardLogoProps) {
  return (
    <div className="inline-flex items-center gap-2.5">
      <img
        src="/trialguard-logo.svg"
        alt="trialGUARD AI"
        width={width}
        height={height}
        className={`object-contain ${className}`}
      />
      {showSubtitle && (
        <div className="hidden flex-col sm:flex">
          <span className="text-[10px] font-bold uppercase tracking-wider text-sky-400 font-mono">
            Investigational Gateway
          </span>
          <span className="text-[9px] text-slate-400 font-mono">
            FDA 21 CFR Part 11 · Multi-Agent Review
          </span>
        </div>
      )}
    </div>
  )
}
