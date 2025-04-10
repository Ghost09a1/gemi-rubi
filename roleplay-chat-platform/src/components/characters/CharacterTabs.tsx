"use client";

import { useState } from "react";

interface Tab {
  id: string;
  label: string;
  icon?: React.ReactNode;
}

interface CharacterTabsProps {
  tabs: Tab[];
  activeTab: string;
  onChange: (tabId: string) => void;
}

export default function CharacterTabs({ tabs, activeTab, onChange }: CharacterTabsProps) {
  return (
    <div className="border-b border-slate-700 mb-6">
      <div className="flex overflow-x-auto hide-scrollbar -mb-px">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            className={`inline-flex items-center px-4 py-3 border-b-2 font-medium text-sm transition-colors whitespace-nowrap ${
              activeTab === tab.id
                ? "border-blue-500 text-blue-400"
                : "border-transparent text-slate-400 hover:text-slate-300 hover:border-slate-700"
            }`}
            onClick={() => onChange(tab.id)}
          >
            {tab.icon && <span className="mr-2">{tab.icon}</span>}
            {tab.label}
          </button>
        ))}
      </div>
    </div>
  );
}

interface TabPanelProps {
  id: string;
  activeId: string;
  children: React.ReactNode;
}

export function TabPanel({ id, activeId, children }: TabPanelProps) {
  if (id !== activeId) return null;
  return <div>{children}</div>;
}

// Form Stepper Component
interface Step {
  id: string;
  label: string;
  optional?: boolean;
}

interface FormStepperProps {
  steps: Step[];
  currentStep: string;
  onStepClick?: (stepId: string) => void;
  completedSteps?: string[];
}

export function FormStepper({
  steps,
  currentStep,
  onStepClick,
  completedSteps = []
}: FormStepperProps) {
  return (
    <div className="mb-8">
      <div className="flex items-center justify-between">
        {steps.map((step, index) => {
          const isActive = step.id === currentStep;
          const isCompleted = completedSteps.includes(step.id);

          return (
            <div key={step.id} className="flex flex-col items-center flex-1">
              <div className="relative flex items-center justify-center w-full">
                {/* Line before */}
                {index > 0 && (
                  <div
                    className={`absolute left-0 right-1/2 h-0.5 ${
                      isCompleted || completedSteps.includes(steps[index - 1].id)
                        ? "bg-blue-500"
                        : "bg-slate-700"
                    }`}
                  />
                )}

                {/* Step circle */}
                <button
                  onClick={() => onStepClick && onStepClick(step.id)}
                  disabled={!onStepClick}
                  className={`relative z-10 flex items-center justify-center w-8 h-8 rounded-full border-2 ${
                    isActive
                      ? "border-blue-500 bg-blue-500/20 text-blue-400"
                      : isCompleted
                      ? "border-blue-500 bg-blue-500 text-white"
                      : "border-slate-700 bg-slate-800 text-slate-500"
                  } ${onStepClick ? "cursor-pointer" : ""}`}
                >
                  {isCompleted ? (
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  ) : (
                    <span className="text-xs">{index + 1}</span>
                  )}
                </button>

                {/* Line after */}
                {index < steps.length - 1 && (
                  <div
                    className={`absolute left-1/2 right-0 h-0.5 ${
                      isCompleted ? "bg-blue-500" : "bg-slate-700"
                    }`}
                  />
                )}
              </div>

              <div className="mt-2 text-center">
                <span
                  className={`text-xs font-medium ${
                    isActive ? "text-blue-400" : isCompleted ? "text-slate-300" : "text-slate-500"
                  }`}
                >
                  {step.label}
                </span>
                {step.optional && (
                  <span className="block text-[10px] text-slate-500">(Optional)</span>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
