'use client';

import { useEffect, useState } from 'react';
import { scanForSyntaxErrors, checkForUnclosedTokens } from '@/lib/syntaxChecker';

interface SyntaxErrorDetectorProps {
  targetId?: string; // Optional ID of element to scan
  autoScan?: boolean; // Whether to scan automatically
}

export default function SyntaxErrorDetector({
  targetId,
  autoScan = false
}: SyntaxErrorDetectorProps) {
  const [errors, setErrors] = useState<string[]>([]);
  const [isVisible, setIsVisible] = useState(false);

  // Function to scan code in specific element
  const scanElement = (elementId: string) => {
    const element = document.getElementById(elementId);
    if (!element) {
      console.error(`Element with ID ${elementId} not found.`);
      return;
    }

    const code = element.innerHTML;
    const result = scanForSyntaxErrors(code);

    if (!result.isValid) {
      setErrors(result.errors);
      setIsVisible(true);
    } else {
      setErrors([]);
      setIsVisible(false);
    }
  };

  // Function to scan the entire page
  const scanPage = () => {
    try {
      const htmlContent = document.documentElement.outerHTML;
      const result = checkForUnclosedTokens(htmlContent);

      if (!result.isValid) {
        setErrors(result.errors);
        setIsVisible(true);
      } else {
        setErrors([]);
        setIsVisible(false);
      }
    } catch (error) {
      console.error('Error scanning page:', error);
    }
  };

  // Auto-scan on mount if enabled
  useEffect(() => {
    if (autoScan) {
      if (targetId) {
        scanElement(targetId);
      } else {
        scanPage();
      }
    }
  }, [autoScan, targetId]);

  // Expose scan functions to window for console use
  useEffect(() => {
    if (typeof window !== 'undefined') {
      (window as any).scanPageForSyntaxErrors = scanPage;
      (window as any).scanElementForSyntaxErrors = scanElement;
    }

    return () => {
      if (typeof window !== 'undefined') {
        delete (window as any).scanPageForSyntaxErrors;
        delete (window as any).scanElementForSyntaxErrors;
      }
    };
  }, []);

  if (!isVisible || errors.length === 0) {
    return null;
  }

  return (
    <div
      style={{
        position: 'fixed',
        bottom: '10px',
        right: '10px',
        zIndex: 9999,
        maxWidth: '500px',
        maxHeight: '300px',
        overflow: 'auto',
        backgroundColor: 'rgba(220, 38, 38, 0.9)',
        color: 'white',
        padding: '10px',
        borderRadius: '5px',
        boxShadow: '0 2px 10px rgba(0, 0, 0, 0.3)',
        fontFamily: 'monospace',
        fontSize: '14px',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
        <h3 style={{ margin: '0', fontWeight: 'bold' }}>Potential Syntax Errors Detected</h3>
        <button
          onClick={() => setIsVisible(false)}
          style={{ background: 'none', border: 'none', color: 'white', cursor: 'pointer', fontSize: '18px' }}
        >
          ×
        </button>
      </div>
      <ul style={{ margin: '0', padding: '0 0 0 20px' }}>
        {errors.map((error, index) => (
          <li key={index} style={{ marginBottom: '4px' }}>{error}</li>
        ))}
      </ul>
      <div style={{ marginTop: '10px', fontSize: '12px' }}>
        Note: These are potential issues that may need investigation.
      </div>
    </div>
  );
}
