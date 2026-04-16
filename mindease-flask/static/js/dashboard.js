// Dashboard JavaScript - Extracted from templates/dashboard.html

// Popup Management
function showPopup(title, content, type) {
  const overlay = document.querySelector('.modal-overlay');
  const popup = document.querySelector('.popup-container');
  const header = popup.querySelector('.popup-header h2');
  const contentArea = popup.querySelector('.popup-content');
  
  header.innerHTML = title;
  contentArea.innerHTML = content;
  
  overlay.classList.add('active');
  popup.classList.remove('closing');
}

function showModulePopup(title, status, description) {
  const overlay = document.querySelector('.modal-overlay');
  const popup = document.querySelector('.popup-container');
  const header = popup.querySelector('.popup-header h2');
  const contentArea = popup.querySelector('.popup-content');
  
  const statusColor = status === 'Active' ? '#10b981' : status === 'Completed' ? '#3b82f6' : '#f59e0b';
  header.innerHTML = title;
  contentArea.innerHTML = `
    <div style="margin-bottom: 12px;">
      <span style="display: inline-block; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; background: ${statusColor}20; color: ${statusColor};">
        ${status}
      </span>
    </div>
    <p style="line-height: 1.6;">${description}</p>
    <div style="margin-top: 16px; padding-top: 16px; border-top: 1px solid rgba(0, 0, 0, 0.1);">
      <p style="font-size: 13px; color: var(--text-secondary);">Last updated: Today at 2:45 PM</p>
    </div>
  `;
  
  overlay.classList.add('active');
  popup.classList.remove('closing');
}

function closePopup() {
  const overlay = document.querySelector('.modal-overlay');
  const popup = document.querySelector('.popup-container');
  
  popup.classList.add('closing');
  setTimeout(() => {
    overlay.classList.remove('active');
  }, 300);
}

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
  // Popup overlay click
  const overlay = document.querySelector('.modal-overlay');
  if (overlay) {
    overlay.addEventListener('click', function(e) {
      if (e.target === overlay) {
        closePopup();
      }
    });
  }

  // Escape key close
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
      closePopup();
    }
  });

  initDashboard();
  initQuickActions();
  initReflectionButton();
  initResourceLinks();
  if (typeof lucide !== 'undefined') lucide.createIcons();
});

// Dark mode integration
function initDashboard() {
  const chatInput = document.querySelector('.chat-input');
  const chatSendBtn = document.querySelector('.chat-send-btn');
  const chatMessages = document.querySelector('.chat-messages');

  if (chatSendBtn) {
    chatSendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') sendMessage();
    });
  }

  function sendMessage() {
    const message = chatInput.value.trim();
    if (!message) return;

    const userMessageDiv = document.createElement('div');
    userMessageDiv.className = 'message user';
    userMessageDiv.innerHTML = `<div class="message-content">${escapeHtml(message)}</div>`;
    chatMessages.appendChild(userMessageDiv);

    chatInput.value = '';
    chatMessages.scrollTop = chatMessages.scrollHeight;

    setTimeout(() => {
      const aiMessageDiv = document.createElement('div');
      aiMessageDiv.className = 'message ai';
      const responses = [
        'That sounds important. How are you feeling about it?',
        'I appreciate you sharing. Let\\'s explore this together. 🌿',
        'You\\'re doing great! Remember to be kind to yourself. 💚',
        'What small step could help you right now?'
      ];
      const response = responses[Math.floor(Math.random() * responses.length)];
      aiMessageDiv.innerHTML = `<div class="message-content">${response}</div>`;
      chatMessages.appendChild(aiMessageDiv);
      chatMessages.scrollTop = chatMessages.scrollHeight;
    }, 500);
  }

  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
}

function initQuickActions() {
  const quickActionBtns = document.querySelectorAll('.quick-action-btn');
  quickActionBtns.forEach(btn => {
    btn.addEventListener('click', function(e) {
      this.style.transform = 'scale(0.98)';
      setTimeout(() => {
        this.style.transform = '';
      }, 150);
    });
    
    btn.addEventListener('mouseenter', function() {
      this.style.boxShadow = '0 8px 16px rgba(0, 191, 165, 0.2)';
    });
    
    btn.addEventListener('mouseleave', function() {
      this.style.boxShadow = '';
    });
  });
}

function initReflectionButton() {
  const reflectionBtn = document.querySelector('.reflection-btn');
  if (reflectionBtn) {
    reflectionBtn.addEventListener('click', function(e) {
      e.preventDefault();
      window.location.href = '/wellness-check';
    });
  }
}

function initResourceLinks() {
  const resourceLinks = document.querySelectorAll('.resource-link');
  resourceLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      e.preventDefault();
      const resourceTitle = this.textContent;
      console.log('Resource accessed:', resourceTitle);
    });
  });
}

