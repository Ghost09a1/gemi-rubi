/**
 * Global error handler for debugging JavaScript errors
 * This file should be included at the top of the base.html file
 */

// Set up global error handler
window.onerror = function(message, source, lineno, colno, error) {
  // Create detailed error message
  const errorDetails = {
    message: message,
    source: source,
    line: lineno,
    column: colno,
    stack: error ? error.stack : null
  };

  // Log to console
  console.error('JavaScript Error Details:', errorDetails);

  // Show user-friendly error message
  const errorDiv = document.createElement('div');
  errorDiv.style.position = 'fixed';
  errorDiv.style.top = '10px';
  errorDiv.style.right = '10px';
  errorDiv.style.backgroundColor = '#ffebee';
  errorDiv.style.color = '#c62828';
  errorDiv.style.padding = '10px';
  errorDiv.style.borderRadius = '4px';
  errorDiv.style.boxShadow = '0 2px 10px rgba(0,0,0,0.2)';
  errorDiv.style.zIndex = '9999';
  errorDiv.style.maxWidth = '400px';
  errorDiv.style.fontFamily = 'monospace';

  errorDiv.innerHTML = `
    <div style="font-weight: bold; margin-bottom: 5px;">JavaScript Error:</div>
    <div>${message}</div>
    <div style="margin-top: 5px; font-size: 12px;">
      ${source ? `File: ${source.split('/').pop()}<br>` : ''}
      ${lineno ? `Line: ${lineno}, Column: ${colno}` : ''}
    </div>
    <div style="margin-top: 10px; text-align: right;">
      <button onclick="this.parentNode.parentNode.remove();" style="border: none; background: #c62828; color: white; padding: 2px 8px; border-radius: 2px; cursor: pointer;">
        Close
      </button>
    </div>
  `;

  document.body.appendChild(errorDiv);

  // Return true to prevent default browser error handling
  return true;
};

// Log unhandled promise rejections
window.addEventListener('unhandledrejection', function(event) {
  console.error('Unhandled Promise Rejection:', event.reason);
});

console.log('Error handler initialized');
