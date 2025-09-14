document.addEventListener('DOMContentLoaded', function() {
  const contentDiv = document.getElementById('content');
  const checkButton = document.getElementById('checkSelectedText');
  
  // Check if there's selected text when popup opens
  chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
    chrome.tabs.sendMessage(tabs[0].id, {action: "getSelectedText"}, function(response) {
      if (response && response.selectedText) {
        showSelectedText(response.selectedText);
      }
    });
  });
  
  // Handle check button click
  checkButton.addEventListener('click', function() {
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
      chrome.tabs.sendMessage(tabs[0].id, {action: "getSelectedText"}, function(response) {
        if (response && response.selectedText) {
          analyzeText(response.selectedText);
        } else {
          showMessage("Please select some text on the webpage first.", "instructions");
        }
      });
    });
  });
  
  function showSelectedText(text) {
    contentDiv.innerHTML = `
      <div class="selected-text">
        "${text.substring(0, 200)}${text.length > 200 ? '...' : ''}"
      </div>
      <button id="analyzeBtn" class="btn">Analyze This Text</button>
    `;
    
    document.getElementById('analyzeBtn').addEventListener('click', function() {
      analyzeText(text);
    });
  }
  
  function analyzeText(text) {
    showMessage("Analyzing text for factual accuracy...", "analyzing");
    
    // Simulate API call - replace with actual AI API integration later
    setTimeout(() => {
      const mockResult = generateMockResult(text);
      showResult(mockResult);
    }, 2000);
  }
  
  function generateMockResult(text) {
    // Mock analysis - replace with real AI analysis
    const results = [
      { status: "verified", message: "This claim appears to be factually accurate based on available sources." },
      { status: "questionable", message: "This claim requires verification. Consider checking additional sources." },
      { status: "verified", message: "Multiple reliable sources confirm this information." }
    ];
    
    return results[Math.floor(Math.random() * results.length)];
  }
  
  function showResult(result) {
    contentDiv.innerHTML = `
      <div class="status ${result.status}">
        <strong>${result.status === 'verified' ? '✓ Verified' : '⚠ Needs Verification'}</strong>
        <p>${result.message}</p>
      </div>
      <button id="checkAgain" class="btn">Check Another Text</button>
    `;
    
    document.getElementById('checkAgain').addEventListener('click', function() {
      location.reload();
    });
  }
  
  function showMessage(message, type) {
    contentDiv.innerHTML = `
      <div class="status ${type}">
        ${message}
      </div>
    `;
  }
});