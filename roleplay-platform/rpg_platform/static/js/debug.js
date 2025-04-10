/**
 * Debug utility to help identify JavaScript syntax errors
 */

console.log('Debug script loaded');

// This function will scan the page for script tags and try to evaluate them
// to identify syntax errors
function scanForScriptErrors() {
  try {
    const scripts = document.querySelectorAll('script:not([src])');
    console.log(`Found ${scripts.length} inline scripts to analyze`);

    scripts.forEach((script, index) => {
      const content = script.textContent;
      if (content && content.trim()) {
        try {
          // Try to evaluate the script
          new Function(content);
          console.log(`Script #${index} is valid`);
        } catch (error) {
          console.error(`Syntax error in script #${index}:`, error);
          console.log(`Problem script content: ${content.substring(0, 200)}...`);

          // Create error indicator
          const errorDiv = document.createElement('div');
          errorDiv.style = `
            position: fixed;
            top: ${10 + (index * 60)}px;
            right: 10px;
            background-color: #ffebee;
            color: #c62828;
            padding: 10px;
            border-radius: 4px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            z-index: 9999;
            max-width: 400px;
            font-family: monospace;
          `;

          errorDiv.innerHTML = `
            <div style="font-weight: bold; margin-bottom: 5px;">JavaScript Error in inline script #${index}:</div>
            <div>${error.message}</div>
            <div style="margin-top: 5px; font-size: 12px;">
              <pre style="max-height: 100px; overflow: auto;">${content.substring(0, 200)}...</pre>
            </div>
            <div style="margin-top: 10px; text-align: right;">
              <button onclick="this.parentNode.parentNode.remove();"
                     style="border: none; background: #c62828; color: white; padding: 2px 8px; border-radius: 2px; cursor: pointer;">
                Close
              </button>
            </div>
          `;

          document.body.appendChild(errorDiv);
        }
      }
    });
  } catch (e) {
    console.error('Error in scanForScriptErrors:', e);
  }
}

// Run the scan when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', scanForScriptErrors);
