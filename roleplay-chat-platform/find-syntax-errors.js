#!/usr/bin/env node

/**
 * Syntax Error Scanner for TypeScript/React projects
 *
 * This script scans your project files for potential syntax errors
 * that might cause "missing ) after argument list" and similar issues.
 *
 * Usage:
 *   node find-syntax-errors.js [directory]
 *
 * If no directory is specified, it will scan the current directory.
 */

const fs = require('fs');
const path = require('path');

// Extensions to check
const extensions = ['.ts', '.tsx', '.js', '.jsx'];

// Files to ignore
const ignorePatterns = [
  'node_modules',
  '.next',
  'out',
  'dist',
  'build',
  '.git',
  '.vscode',
];

// Counts
let fileChecked = 0;
let filesWithIssues = 0;
let totalIssues = 0;

// ANSI colors for terminal output
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
  bold: '\x1b[1m',
};

// Simple regex patterns to detect common issues
const patterns = [
  {
    name: 'Unclosed parentheses',
    // This pattern looks for opening parenthesis without matching closing one
    // Note: This is a simplified approach and will have false positives
    regex: /\([^()]*$/m,
    severity: 'high',
  },
  {
    name: 'Unclosed JSX tags',
    // This pattern tries to find JSX tags without closing
    regex: /<[A-Za-z][A-Za-z0-9]*(?:\s+[^>]*)?>[^<]*$/m,
    severity: 'high',
  },
  {
    name: 'Unclosed template literal',
    // This pattern looks for backtick without closing
    regex: /`[^`]*$/m,
    severity: 'high',
  },
  {
    name: 'Unclosed string',
    // This pattern looks for quote without closing
    regex: /(['"])[^'"]*$/m,
    severity: 'high',
  },
  {
    name: 'Unclosed JSX expression',
    // This pattern looks for { without matching }
    regex: /{[^{}]*$/m,
    severity: 'high',
  },
  {
    name: 'JSX attribute without value',
    // This pattern looks for attributes like foo= without a value
    regex: /\s+[a-zA-Z][a-zA-Z0-9]*=(?![{'"\\])/,
    severity: 'medium',
  },
  {
    name: 'Potential missing comma in object',
    // This finds patterns like { foo: 'bar' baz: 'qux' }
    regex: /['"](?:\s*|\s*\/\/[^\n]*\s*|\s*\/\*[^*]*\*\/\s*)}[^,;{]*{/,
    severity: 'medium',
  },
  {
    name: 'Double comma',
    // This finds double commas like { foo: 'bar',, baz: 'qux' }
    regex: /,,/,
    severity: 'medium',
  },
];

/**
 * Check a line for issues
 * @param {string} line - The line to check
 * @param {number} lineNumber - The line number
 * @param {string} filePath - The file path
 * @returns {Array} - Array of issues found
 */
function checkLine(line, lineNumber, filePath) {
  const issues = [];

  patterns.forEach((pattern) => {
    if (pattern.regex.test(line)) {
      issues.push({
        pattern: pattern.name,
        severity: pattern.severity,
        lineNumber,
        line: line.trim(),
        file: filePath,
      });
    }
  });

  return issues;
}

/**
 * Check a file for issues
 * @param {string} filePath - The file to check
 */
function checkFile(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    const lines = content.split('\n');
    let fileIssues = [];

    for (let i = 0; i < lines.length; i++) {
      const lineIssues = checkLine(lines[i], i + 1, filePath);
      fileIssues = fileIssues.concat(lineIssues);
    }

    // Check for potential unclosed pairs
    const pairs = {
      '(': { close: ')', count: 0 },
      '{': { close: '}', count: 0 },
      '[': { close: ']', count: 0 },
    };

    // Very simple check - doesn't handle strings, comments, etc.
    for (let i = 0; i < content.length; i++) {
      const char = content[i];
      if (pairs[char]) {
        pairs[char].count++;
      } else if (Object.values(pairs).some(p => p.close === char)) {
        const openChar = Object.keys(pairs).find(k => pairs[k].close === char);
        pairs[openChar].count--;
      }
    }

    // Check for imbalanced pairs
    Object.keys(pairs).forEach(openChar => {
      if (pairs[openChar].count !== 0) {
        fileIssues.push({
          pattern: `Imbalanced ${openChar}${pairs[openChar].close} pairs`,
          severity: 'high',
          lineNumber: null,
          line: null,
          file: filePath,
          count: pairs[openChar].count,
        });
      }
    });

    if (fileIssues.length > 0) {
      filesWithIssues++;
      totalIssues += fileIssues.length;

      console.log(`\n${colors.bold}${colors.blue}${filePath}${colors.reset}`);

      fileIssues.forEach((issue) => {
        const severityColor = issue.severity === 'high' ? colors.red : colors.yellow;

        if (issue.lineNumber) {
          console.log(`  ${severityColor}${issue.pattern}${colors.reset} (line ${issue.lineNumber}):`);
          console.log(`    ${issue.line}`);
        } else if (issue.count) {
          console.log(`  ${severityColor}${issue.pattern}${colors.reset}: ${issue.count > 0 ? 'more opening than closing' : 'more closing than opening'}`);
        }
      });
    }

    fileChecked++;
  } catch (error) {
    console.error(`Error reading file ${filePath}:`, error.message);
  }
}

/**
 * Recursively scan a directory for files to check
 * @param {string} dir - The directory to scan
 */
function scanDirectory(dir) {
  try {
    const entries = fs.readdirSync(dir, { withFileTypes: true });

    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name);

      // Skip ignored directories
      if (entry.isDirectory() && !ignorePatterns.some(pattern => entry.name.includes(pattern))) {
        scanDirectory(fullPath);
      } else if (entry.isFile() && extensions.includes(path.extname(entry.name))) {
        checkFile(fullPath);
      }
    }
  } catch (error) {
    console.error(`Error scanning directory ${dir}:`, error.message);
  }
}

// Get the directory to scan from command line or use current directory
const targetDir = process.argv[2] || '.';

console.log(`${colors.bold}${colors.magenta}Scanning for syntax errors in ${targetDir}...${colors.reset}`);
console.log(`${colors.blue}This tool checks for common syntax errors that might cause "missing ) after argument list" and similar issues.${colors.reset}`);
console.log(`${colors.blue}Note: This is a basic scan and might report false positives.${colors.reset}\n`);

scanDirectory(targetDir);

console.log(`\n${colors.bold}${colors.magenta}Scan complete!${colors.reset}`);
console.log(`Files checked: ${fileChecked}`);
console.log(`Files with potential issues: ${filesWithIssues}`);
console.log(`Total issues found: ${totalIssues}`);

if (filesWithIssues > 0) {
  console.log(`\n${colors.yellow}Some files may have syntax issues. Please review them carefully.${colors.reset}`);
} else {
  console.log(`\n${colors.green}No potential syntax issues found!${colors.reset}`);
}
