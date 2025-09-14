// Content script - runs on every webpage
let selectedText = '';
let factifyWidget = null;

// Listen for text selection
document.addEventListener('mouseup', function(e) {
  const selection = window.getSelection();
  selectedText = selection.toString().trim();
  
  if (selectedText.length > 0) {
    // Store selected text for popup access
    chrome.storage.local.set({lastSelectedText: selectedText});
    
    // Show a small indicator that text can be fact-checked
    showFactCheckIndicator(e.pageX, e.pageY);
  }
});

// Show small fact-check indicator
function showFactCheckIndicator(x, y) {
  // Remove existing indicator
  const existing = document.getElementById('factify-indicator');
  if (existing) existing.remove();
  
  const indicator = document.createElement('div');
  indicator.id = 'factify-indicator';
  indicator.innerHTML = '🔍 Fact-check';
  indicator.style.cssText = `
    position: absolute;
    left: ${x}px;
    top: ${y - 40}px;
    background: #2196F3;
    color: white;
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 12px;
    cursor: pointer;
    z-index: 9999;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    animation: fadeIn 0.3s ease;
  `;
  
  // Add fade in animation
  const style = document.createElement('style');
  style.textContent = `
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(10px); }
      to { opacity: 1; transform: translateY(0); }
    }
  `;
  document.head.appendChild(style);
  
  document.body.appendChild(indicator);
  
  // Click to show widget
  indicator.addEventListener('click', function() {
    showFactifyWidget();
    indicator.remove();
  });
  
  // Auto-hide after 3 seconds
  setTimeout(() => {
    if (indicator.parentNode) {
      indicator.remove();
    }
  }, 3000);
}

// Listen for messages from popup and background
chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
  if (request.action === "getSelectedText") {
    const selection = window.getSelection();
    const currentSelected = selection.toString().trim();
    
    // Return current selection or last stored selection
    sendResponse({
      selectedText: currentSelected || selectedText
    });
  }
  
  if (request.action === "showFactifyWidget") {
    showFactifyWidget(request.text);
  }
  
  return true; // Keep message channel open for async response
});

// Add context menu functionality (right-click option)
document.addEventListener('contextmenu', function(e) {
  const selection = window.getSelection();
  const text = selection.toString().trim();
  
  if (text.length > 0) {
    selectedText = text;
    chrome.storage.local.set({lastSelectedText: text});
  }
});

// Create draggable Factify widget
function showFactifyWidget(text = null) {
  // Remove existing widget if present
  if (factifyWidget) {
    factifyWidget.remove();
  }
  
  const textToAnalyze = text || selectedText || window.getSelection().toString().trim();
  
  if (!textToAnalyze) {
    alert('Please select some text first!');
    return;
  }
  
  // Create widget container
  factifyWidget = document.createElement('div');
  factifyWidget.id = 'factify-widget';
  factifyWidget.innerHTML = `
    <div class="factify-header">
      <div class="factify-logo">🔍 Factify</div>
      <button class="factify-close">×</button>
    </div>
    <div class="factify-content">
      <div class="factify-selected-text">
        "${textToAnalyze.substring(0, 150)}${textToAnalyze.length > 150 ? '...' : ''}"
      </div>
      <div class="factify-status analyzing">
        Analyzing text for factual accuracy...
      </div>
    </div>
  `;
  
  // Add styles
  const style = document.createElement('style');
  style.textContent = `
    #factify-widget {
      position: fixed;
      top: 50px;
      right: 50px;
      width: 350px;
      background: white;
      border-radius: 16px;
      box-shadow: 0 8px 32px rgba(0,0,0,0.2);
      z-index: 10000;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      border: 1px solid #e0e0e0;
      cursor: move;
    }
    
    .factify-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 16px;
      border-bottom: 1px solid #e0e0e0;
      cursor: move;
      background: #f8f9fa;
      border-radius: 16px 16px 0 0;
    }
    
    .factify-logo {
      font-size: 16px;
      font-weight: bold;
      color: #2196F3;
    }
    
    .factify-close {
      background: none;
      border: none;
      font-size: 20px;
      cursor: pointer;
      color: #666;
      padding: 0;
      width: 24px;
      height: 24px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    
    .factify-close:hover {
      background: #f0f0f0;
      color: #333;
    }
    
    .factify-content {
      padding: 16px;
    }
    
    .factify-selected-text {
      background-color: #f8f9fa;
      padding: 12px;
      border-radius: 12px;
      margin-bottom: 16px;
      font-style: italic;
      border-left: 3px solid #2196F3;
      font-size: 14px;
    }
    
    .factify-status {
      padding: 12px;
      border-radius: 12px;
      text-align: center;
      font-size: 14px;
    }
    
    .factify-status.analyzing {
      background-color: #fff3cd;
      color: #856404;
      border: 1px solid #ffeaa7;
    }
    
    .factify-status.verified {
      background-color: #d4edda;
      color: #155724;
      border: 1px solid #c3e6cb;
    }
    
    .factify-status.questionable {
      background-color: #f8d7da;
      color: #721c24;
      border: 1px solid #f5c6cb;
    }
  `;
  
  document.head.appendChild(style);
  document.body.appendChild(factifyWidget);
  
  // Make draggable
  makeDraggable(factifyWidget);
  
  // Add close functionality
  factifyWidget.querySelector('.factify-close').addEventListener('click', function() {
    factifyWidget.remove();
    factifyWidget = null;
  });
  
  // Simulate analysis
  setTimeout(() => {
    analyzeText(textToAnalyze);
  }, 2000);
}

// Make widget draggable
function makeDraggable(element) {
  let isDragging = false;
  let currentX;
  let currentY;
  let initialX;
  let initialY;
  let xOffset = 0;
  let yOffset = 0;
  
  const header = element.querySelector('.factify-header');
  
  header.addEventListener('mousedown', dragStart);
  document.addEventListener('mousemove', drag);
  document.addEventListener('mouseup', dragEnd);
  
  function dragStart(e) {
    initialX = e.clientX - xOffset;
    initialY = e.clientY - yOffset;
    
    if (e.target === header || header.contains(e.target)) {
      isDragging = true;
    }
  }
  
  function drag(e) {
    if (isDragging) {
      e.preventDefault();
      currentX = e.clientX - initialX;
      currentY = e.clientY - initialY;
      
      xOffset = currentX;
      yOffset = currentY;
      
      element.style.transform = `translate(${currentX}px, ${currentY}px)`;
    }
  }
  
  function dragEnd() {
    initialX = currentX;
    initialY = currentY;
    isDragging = false;
  }
}

// Analyze text function
function analyzeText(text) {
  if (!factifyWidget) return;
  
  // Mock analysis - replace with real AI API later
  const results = [
    { status: "verified", message: "✓ Verified - This claim appears to be factually accurate based on available sources." },
    { status: "questionable", message: "⚠ Needs Verification - This claim requires additional verification. Consider checking multiple sources." },
    { status: "verified", message: "✓ Verified - Multiple reliable sources confirm this information." }
  ];
  
  const result = results[Math.floor(Math.random() * results.length)];
  
  const statusElement = factifyWidget.querySelector('.factify-status');
  statusElement.className = `factify-status ${result.status}`;
  statusElement.textContent = result.message;
}