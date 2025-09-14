// Background service worker
chrome.runtime.onInstalled.addListener(function() {
  // Create context menu item
  chrome.contextMenus.create({
    id: "factifyCheck",
    title: "Fact-check with Factify",
    contexts: ["selection"]
  });
});

// Handle context menu clicks
chrome.contextMenus.onClicked.addListener(function(info, tab) {
  if (info.menuItemId === "factifyCheck" && info.selectionText) {
    // Send message to content script to show widget
    chrome.tabs.sendMessage(tab.id, {
      action: "showFactifyWidget",
      text: info.selectionText
    });
  }
});

// Handle extension icon click
chrome.action.onClicked.addListener(function(tab) {
  // Send message to content script to show widget with selected text
  chrome.tabs.sendMessage(tab.id, {
    action: "showFactifyWidget"
  });
});