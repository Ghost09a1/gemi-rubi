'use client';

import { useEffect } from 'react';

export default function ErrorHandler() {
  useEffect(() => {
    // Global error handler
    const originalError = console.error;
    console.error = (...args) => {
      // Check if it's our specific error
      const errorString = args.join(' ');

      // Log all errors in a more visible way
      console.log('%c JavaScript Error Detected! ', 'background: #ff6600; color: white; font-size: 14px; padding: 2px;');
      console.log('Error details:', args);

      // Try to get the stack trace and parse it to find the file and line number
      if (args[0] instanceof Error) {
        console.log('Stack trace:', args[0].stack);

        try {
          // Try to extract file path and line number from the stack
          const stackLines = args[0].stack.split('\n');
          const fileLineRegex = /at .*\((.*):(\d+):(\d+)\)$/;

          for (const line of stackLines) {
            const match = line.match(fileLineRegex);
            if (match) {
              const [, filePath, lineNumber, columnNumber] = match;

              // Only show file info if it's from our app code (not node_modules)
              if (!filePath.includes('node_modules')) {
                console.log('%c Error Location ', 'background: #ff6600; color: white; font-weight: bold;');
                console.log(`File: ${filePath}`);
                console.log(`Line: ${lineNumber}, Column: ${columnNumber}`);
                break;
              }
            }
          }
        } catch (parseError) {
          console.log('Could not parse stack trace:', parseError);
        }
      }

      // Specifically look for syntax errors
      if (errorString.includes('missing ) after argument list') ||
          errorString.includes('Unexpected token') ||
          errorString.includes('Unexpected end of input') ||
          errorString.includes('syntax error')) {
        console.log('%c SYNTAX ERROR DETECTED! ', 'background: #ff0000; color: white; font-size: 16px; padding: 4px;');
      }

      // Call the original error function
      originalError.apply(console, args);
    };

    // Window error handler
    const handleError = (event: ErrorEvent) => {
      console.log('Window error event:', event.message);
      console.log('Error location:', event.filename, 'Line:', event.lineno, 'Column:', event.colno);

      // Log all errors in a more visible way
      console.log('%c JavaScript Error Detected! ', 'background: #ff6600; color: white; font-size: 14px; padding: 2px;');
      console.log('Error details:', event);

      if (event.message.includes('missing ) after argument list') ||
          event.message.includes('Unexpected token') ||
          event.message.includes('Unexpected end of input') ||
          event.message.includes('syntax error')) {
        console.log('%c SYNTAX ERROR DETECTED! ', 'background: #ff0000; color: white; font-size: 16px; padding: 4px;');
        console.log('Error details:', event);

        // Show user-friendly alert about the error
        const alertMessage = `
Syntax error detected, likely a missing parenthesis!
File: ${event.filename.split('/').pop()}
Line: ${event.lineno}

Check your browser console for more details.`;

        setTimeout(() => {
          alert(alertMessage);
        }, 100);
      }
    };

    window.addEventListener('error', handleError);

    // Handle unhandled promise rejections
    const handleRejection = (event: PromiseRejectionEvent) => {
      console.log('Unhandled promise rejection:', event.reason);

      // If the reason is an error with a stack, analyze it
      if (event.reason instanceof Error) {
        const errorString = event.reason.message;

        if (errorString.includes('missing ) after argument list') ||
            errorString.includes('Unexpected token') ||
            errorString.includes('Unexpected end of input') ||
            errorString.includes('syntax error')) {
          console.log('%c SYNTAX ERROR IN ASYNC CODE! ', 'background: #ff0000; color: white; font-size: 16px; padding: 4px;');
          console.log('Stack trace:', event.reason.stack);
        }
      }
    };

    window.addEventListener('unhandledrejection', handleRejection);

    return () => {
      // Clean up
      console.error = originalError;
      window.removeEventListener('error', handleError);
      window.removeEventListener('unhandledrejection', handleRejection);
    };
  }, []);

  return null; // This component doesn't render anything
}
