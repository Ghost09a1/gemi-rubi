/**
 * Syntax Error Checker Utility
 *
 * This utility helps scan the codebase for potential syntax errors
 * by checking for common patterns that might cause issues.
 */

/**
 * Helper function to check a string for unclosed brackets, parentheses, and quotes
 */
export function checkForUnclosedTokens(code: string): { isValid: boolean; errors: string[] } {
  const errors: string[] = [];

  // Count of opening and closing tokens
  const stacks: { [key: string]: string[] } = {
    parentheses: [],   // ()
    brackets: [],      // []
    braces: [],        // {}
    quotes: [],        // ""
    singleQuotes: [],  // ''
    backticks: [],     // ``
  };

  const lineNumbers: number[] = [];
  const lines = code.split('\n');

  let inSingleLineComment = false;
  let inMultiLineComment = false;
  let inString: string | null = null; // null, 'single', 'double', or 'backtick'

  // Process each character with line and column tracking
  for (let lineNum = 0; lineNum < lines.length; lineNum++) {
    const line = lines[lineNum];
    inSingleLineComment = false; // Reset for each line

    for (let colNum = 0; colNum < line.length; colNum++) {
      const char = line[colNum];
      const nextChar = colNum < line.length - 1 ? line[colNum + 1] : '';

      // Handle comments (don't check for tokens inside comments)
      if (!inString) {
        // Start of single line comment //
        if (char === '/' && nextChar === '/') {
          inSingleLineComment = true;
          colNum++; // Skip next char
          continue;
        }

        // Start of multi-line comment /*
        if (char === '/' && nextChar === '*' && !inMultiLineComment) {
          inMultiLineComment = true;
          colNum++; // Skip next char
          continue;
        }

        // End of multi-line comment */
        if (char === '*' && nextChar === '/' && inMultiLineComment) {
          inMultiLineComment = false;
          colNum++; // Skip next char
          continue;
        }
      }

      // Skip the rest of the processing if in a comment
      if (inSingleLineComment || inMultiLineComment) continue;

      // Handle string literals
      if (!inString) {
        if (char === '"') {
          inString = 'double';
          stacks.quotes.push(`${lineNum + 1}:${colNum + 1}`);
          continue;
        }
        if (char === "'") {
          inString = 'single';
          stacks.singleQuotes.push(`${lineNum + 1}:${colNum + 1}`);
          continue;
        }
        if (char === '`') {
          inString = 'backtick';
          stacks.backticks.push(`${lineNum + 1}:${colNum + 1}`);
          continue;
        }
      } else {
        // Check for string end or escaped character
        if (char === '\\') {
          colNum++; // Skip the escaped character
          continue;
        }

        if ((inString === 'double' && char === '"') ||
            (inString === 'single' && char === "'") ||
            (inString === 'backtick' && char === '`')) {
          // End of string
          if (inString === 'double') stacks.quotes.pop();
          if (inString === 'single') stacks.singleQuotes.pop();
          if (inString === 'backtick') stacks.backticks.pop();
          inString = null;
          continue;
        }
      }

      // Only check for brackets if not in a string
      if (!inString) {
        // Opening tokens
        if (char === '(') stacks.parentheses.push(`${lineNum + 1}:${colNum + 1}`);
        if (char === '[') stacks.brackets.push(`${lineNum + 1}:${colNum + 1}`);
        if (char === '{') stacks.braces.push(`${lineNum + 1}:${colNum + 1}`);

        // Closing tokens
        if (char === ')') {
          if (stacks.parentheses.length === 0) {
            errors.push(`Extra closing parenthesis at line ${lineNum + 1}, column ${colNum + 1}`);
          } else {
            stacks.parentheses.pop();
          }
        }
        if (char === ']') {
          if (stacks.brackets.length === 0) {
            errors.push(`Extra closing bracket at line ${lineNum + 1}, column ${colNum + 1}`);
          } else {
            stacks.brackets.pop();
          }
        }
        if (char === '}') {
          if (stacks.braces.length === 0) {
            errors.push(`Extra closing brace at line ${lineNum + 1}, column ${colNum + 1}`);
          } else {
            stacks.braces.pop();
          }
        }
      }
    }
  }

  // Check for unclosed tokens
  if (stacks.parentheses.length > 0) {
    errors.push(`Unclosed parentheses at positions: ${stacks.parentheses.join(', ')}`);
  }
  if (stacks.brackets.length > 0) {
    errors.push(`Unclosed brackets at positions: ${stacks.brackets.join(', ')}`);
  }
  if (stacks.braces.length > 0) {
    errors.push(`Unclosed braces at positions: ${stacks.braces.join(', ')}`);
  }
  if (stacks.quotes.length > 0) {
    errors.push(`Unclosed double quotes at positions: ${stacks.quotes.join(', ')}`);
  }
  if (stacks.singleQuotes.length > 0) {
    errors.push(`Unclosed single quotes at positions: ${stacks.singleQuotes.join(', ')}`);
  }
  if (stacks.backticks.length > 0) {
    errors.push(`Unclosed backticks (template literals) at positions: ${stacks.backticks.join(', ')}`);
  }

  return {
    isValid: errors.length === 0,
    errors
  };
}

/**
 * Check for potential JSX errors
 */
export function checkForJSXErrors(code: string): { isValid: boolean; errors: string[] } {
  const errors: string[] = [];

  // Check for common JSX errors

  // Missing closing tags
  const openingTags = code.match(/<[a-zA-Z][a-zA-Z0-9]*(?:\s+[^>]*)?>/g) || [];
  const selfClosingTags = code.match(/<[a-zA-Z][a-zA-Z0-9]*(?:\s+[^>]*)?\s*\/>/g) || [];
  const closingTags = code.match(/<\/[a-zA-Z][a-zA-Z0-9]*>/g) || [];

  // Simple check - not perfect but can catch obvious issues
  if (openingTags.length - selfClosingTags.length !== closingTags.length) {
    errors.push(`Potential missing JSX closing tags (this is a simple check and may give false positives)`);
  }

  // Check for improper JSX attribute values missing quotes
  const lines = code.split('\n');
  lines.forEach((line, index) => {
    if (line.includes('<') && !line.includes('//')) {
      // This regex tries to find attributes without proper quotes
      const badAttrs = line.match(/\s+([a-zA-Z][a-zA-Z0-9]*)=(?!["{'\[])/g);
      if (badAttrs) {
        errors.push(`Line ${index + 1} may have JSX attributes without proper quotes: ${badAttrs.join(', ')}`);
      }
    }
  });

  return {
    isValid: errors.length === 0,
    errors
  };
}

/**
 * Scans a piece of code for common syntax errors
 */
export function scanForSyntaxErrors(code: string): { isValid: boolean; errors: string[] } {
  const unclosedTokens = checkForUnclosedTokens(code);
  const jsxErrors = checkForJSXErrors(code);

  return {
    isValid: unclosedTokens.isValid && jsxErrors.isValid,
    errors: [...unclosedTokens.errors, ...jsxErrors.errors]
  };
}

/**
 * Use this in your browser console to check a specific file for syntax errors
 * Example: checkCurrentFile()
 */
export function checkCurrentFile(): void {
  // This function is meant to be used in the browser console
  console.log("Trying to analyze the current file for syntax errors...");

  try {
    // Try to get the current file content from the DOM
    // This is a heuristic approach and might not work in all cases
    const scripts = document.querySelectorAll('script');
    const styles = document.querySelectorAll('style');

    if (scripts.length === 0 && styles.length === 0) {
      console.log("No inline scripts or styles found to analyze.");
      return;
    }

    let foundErrors = false;

    scripts.forEach((script, index) => {
      if (script.textContent) {
        console.log(`Analyzing script ${index + 1}...`);
        const result = scanForSyntaxErrors(script.textContent);
        if (!result.isValid) {
          console.log(`%c Found ${result.errors.length} potential errors in script ${index + 1}:`, 'color: red; font-weight: bold');
          result.errors.forEach(error => console.log(`- ${error}`));
          foundErrors = true;
        }
      }
    });

    styles.forEach((style, index) => {
      if (style.textContent) {
        console.log(`Analyzing style ${index + 1}...`);
        const result = checkForUnclosedTokens(style.textContent);
        if (!result.isValid) {
          console.log(`%c Found ${result.errors.length} potential errors in style ${index + 1}:`, 'color: red; font-weight: bold');
          result.errors.forEach(error => console.log(`- ${error}`));
          foundErrors = true;
        }
      }
    });

    if (!foundErrors) {
      console.log("%c No obvious syntax errors found in inline scripts and styles.", "color: green; font-weight: bold");
    }
  } catch (error) {
    console.error("Error analyzing the current file:", error);
  }
}
