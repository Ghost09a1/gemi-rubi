/**
 * BBC Code Editor
 * A simple editor for handling BBCode formatting
 */

class BBCodeEditor {
  constructor(options) {
    this.textarea = options.textarea;
    this.previewContainer = options.previewContainer;
    this.toggleButton = options.toggleButton;
    this.mode = 'bbc'; // 'bbc' or 'css'

    this.buttons = {
      bold: options.buttons.bold,
      italic: options.buttons.italic,
      underline: options.buttons.underline,
      strikethrough: options.buttons.strikethrough,
      color: options.buttons.color,
      size: options.buttons.size,
      url: options.buttons.url,
      image: options.buttons.image,
      quote: options.buttons.quote,
      code: options.buttons.code,
      list: options.buttons.list,
      center: options.buttons.center,
      right: options.buttons.right,
      heading: options.buttons.heading,
    };

    this.bindEvents();
  }

  bindEvents() {
    // Formatting buttons
    if (this.buttons.bold) {
      this.buttons.bold.addEventListener('click', () => this.insertBBCode('b'));
    }

    if (this.buttons.italic) {
      this.buttons.italic.addEventListener('click', () => this.insertBBCode('i'));
    }

    if (this.buttons.underline) {
      this.buttons.underline.addEventListener('click', () => this.insertBBCode('u'));
    }

    if (this.buttons.strikethrough) {
      this.buttons.strikethrough.addEventListener('click', () => this.insertBBCode('s'));
    }

    if (this.buttons.color) {
      this.buttons.color.addEventListener('change', (e) => {
        const color = e.target.value;
        this.insertBBCode('color', color);
        e.target.value = ''; // Reset the color picker
      });
    }

    if (this.buttons.size) {
      this.buttons.size.addEventListener('change', (e) => {
        const size = e.target.value;
        this.insertBBCode('size', size);
      });
    }

    if (this.buttons.url) {
      this.buttons.url.addEventListener('click', () => {
        const url = prompt('Enter URL:');
        if (url) {
          const text = prompt('Enter link text (optional):');
          if (text) {
            this.insertText(`[url=${url}]${text}[/url]`);
          } else {
            this.insertBBCode('url', '', url);
          }
        }
      });
    }

    if (this.buttons.image) {
      this.buttons.image.addEventListener('click', () => {
        const url = prompt('Enter image URL:');
        if (url) {
          this.insertText(`[img]${url}[/img]`);
        }
      });
    }

    if (this.buttons.quote) {
      this.buttons.quote.addEventListener('click', () => {
        const author = prompt('Enter quote author (optional):');
        if (author) {
          this.insertBBCode('quote', author);
        } else {
          this.insertBBCode('quote');
        }
      });
    }

    if (this.buttons.code) {
      this.buttons.code.addEventListener('click', () => this.insertBBCode('code'));
    }

    if (this.buttons.list) {
      this.buttons.list.addEventListener('click', () => {
        const items = prompt('Enter list items, one per line:');
        if (items) {
          const lines = items.split('\n');
          let listText = '[list]\n';

          lines.forEach(line => {
            if (line.trim()) {
              listText += `[*]${line.trim()}\n`;
            }
          });

          listText += '[/list]';
          this.insertText(listText);
        }
      });
    }

    if (this.buttons.center) {
      this.buttons.center.addEventListener('click', () => this.insertBBCode('center'));
    }

    if (this.buttons.right) {
      this.buttons.right.addEventListener('click', () => this.insertBBCode('right'));
    }

    if (this.buttons.heading) {
      this.buttons.heading.addEventListener('click', () => this.insertBBCode('h'));
    }

    // Toggle BBC/CSS mode if the toggle button exists
    if (this.toggleButton) {
      this.toggleButton.addEventListener('click', () => this.toggleMode());
    }

    // Preview functionality
    if (this.previewContainer) {
      // Update preview on input
      this.textarea.addEventListener('input', () => this.updatePreview());

      // Initial preview
      this.updatePreview();
    }
  }

  insertBBCode(tag, param = '', selectedText = null) {
    const textarea = this.textarea;
    let startTag = `[${tag}${param ? '=' + param : ''}]`;
    let endTag = `[/${tag}]`;

    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedContent = selectedText !== null ? selectedText : textarea.value.substring(start, end);

    const content = textarea.value.substring(0, start) + startTag + selectedContent + endTag + textarea.value.substring(end);

    textarea.value = content;
    textarea.focus();

    // Set cursor position after the inserted content
    const newCursorPos = start + startTag.length + selectedContent.length + endTag.length;
    textarea.setSelectionRange(newCursorPos, newCursorPos);

    // Update preview if available
    if (this.previewContainer) {
      this.updatePreview();
    }
  }

  insertText(text) {
    const textarea = this.textarea;
    const start = textarea.selectionStart;

    textarea.value = textarea.value.substring(0, start) + text + textarea.value.substring(textarea.selectionEnd);
    textarea.focus();

    // Set cursor position after the inserted text
    const newCursorPos = start + text.length;
    textarea.setSelectionRange(newCursorPos, newCursorPos);

    // Update preview if available
    if (this.previewContainer) {
      this.updatePreview();
    }
  }

  updatePreview() {
    if (!this.previewContainer) return;

    if (this.mode === 'bbc') {
      // Convert BBCode to HTML for preview
      let html = this.bbcodeToHtml(this.textarea.value);
      this.previewContainer.innerHTML = html;
    } else {
      // CSS mode - show raw HTML/CSS
      this.previewContainer.innerHTML = this.textarea.value;
    }
  }

  toggleMode() {
    this.mode = this.mode === 'bbc' ? 'css' : 'bbc';

    if (this.toggleButton) {
      this.toggleButton.textContent = this.mode === 'bbc' ? 'Switch to CSS Mode' : 'Switch to BBC Mode';
    }

    // Update textarea class
    this.textarea.classList.toggle('bbc-editor', this.mode === 'bbc');
    this.textarea.classList.toggle('css-editor', this.mode === 'css');

    // Update preview
    this.updatePreview();
  }

  bbcodeToHtml(bbcode) {
    let html = bbcode;

    // Basic formatting
    html = html.replace(/\[b\]([\s\S]*?)\[\/b\]/g, '<strong>$1</strong>');
    html = html.replace(/\[i\]([\s\S]*?)\[\/i\]/g, '<em>$1</em>');
    html = html.replace(/\[u\]([\s\S]*?)\[\/u\]/g, '<u>$1</u>');
    html = html.replace(/\[s\]([\s\S]*?)\[\/s\]/g, '<strike>$1</strike>');

    // Color and size
    html = html.replace(/\[color=([^\]]+)\]([\s\S]*?)\[\/color\]/g, '<span style="color:$1">$2</span>');
    html = html.replace(/\[size=([^\]]+)\]([\s\S]*?)\[\/size\]/g, '<span style="font-size:$1">$2</span>');

    // Links and images
    html = html.replace(/\[url\]([\s\S]*?)\[\/url\]/g, '<a href="$1" target="_blank">$1</a>');
    html = html.replace(/\[url=([^\]]+)\]([\s\S]*?)\[\/url\]/g, '<a href="$1" target="_blank">$2</a>');
    html = html.replace(/\[img\]([\s\S]*?)\[\/img\]/g, '<img src="$1" alt="" style="max-width:100%">');

    // Quotes and code blocks
    html = html.replace(/\[quote\]([\s\S]*?)\[\/quote\]/g, '<blockquote>$1</blockquote>');
    html = html.replace(/\[quote=([^\]]+)\]([\s\S]*?)\[\/quote\]/g,
      '<blockquote><strong>$1 wrote:</strong><br>$2</blockquote>'
    );
    html = html.replace(/\[code\]([\s\S]*?)\[\/code\]/g, '<pre><code>$1</code></pre>');

    // Lists
    html = html.replace(/\[list\]([\s\S]*?)\[\/list\]/g, function(match, content) {
      return '<ul>' + content.replace(/\[\*\]([^\[]*)/g, '<li>$1</li>') + '</ul>';
    });

    // Alignment
    html = html.replace(/\[center\]([\s\S]*?)\[\/center\]/g, '<div style="text-align:center">$1</div>');
    html = html.replace(/\[right\]([\s\S]*?)\[\/right\]/g, '<div style="text-align:right">$1</div>');

    // Headings
    html = html.replace(/\[h\]([\s\S]*?)\[\/h\]/g, '<h3>$1</h3>');

    // Convert newlines to <br> tags
    html = html.replace(/\n/g, '<br>');

    return html;
  }
}

// Initialize the editor on page load
document.addEventListener('DOMContentLoaded', function() {
  // Look for editors on the page
  const textareas = document.querySelectorAll('.bbc-editor');

  textareas.forEach(textarea => {
    // Find related elements
    const editorContainer = textarea.closest('.editor-container');
    if (!editorContainer) return;

    const previewContainer = editorContainer.querySelector('.preview-container');
    const toggleButton = editorContainer.querySelector('.toggle-mode');

    // Find formatting buttons
    const buttons = {
      bold: editorContainer.querySelector('.btn-bold'),
      italic: editorContainer.querySelector('.btn-italic'),
      underline: editorContainer.querySelector('.btn-underline'),
      strikethrough: editorContainer.querySelector('.btn-strikethrough'),
      color: editorContainer.querySelector('.btn-color'),
      size: editorContainer.querySelector('.btn-size'),
      url: editorContainer.querySelector('.btn-url'),
      image: editorContainer.querySelector('.btn-image'),
      quote: editorContainer.querySelector('.btn-quote'),
      code: editorContainer.querySelector('.btn-code'),
      list: editorContainer.querySelector('.btn-list'),
      center: editorContainer.querySelector('.btn-center'),
      right: editorContainer.querySelector('.btn-right'),
      heading: editorContainer.querySelector('.btn-heading'),
    };

    // Initialize editor
    new BBCodeEditor({
      textarea,
      previewContainer,
      toggleButton,
      buttons
    });
  });
});
