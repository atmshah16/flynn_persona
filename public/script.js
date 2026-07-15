const setupCard = document.getElementById('setupCard');
const chatCard = document.getElementById('chatCard');
const chatWindow = document.getElementById('chatWindow');
const chatForm = document.getElementById('chatForm');
const userInput = document.getElementById('userInput');
const startBtn = document.getElementById('startBtn');

let messages = [];

function addBubble(text, role) {
  const bubble = document.createElement('div');
  bubble.className = `bubble ${role}`;
  bubble.textContent = text;
  chatWindow.appendChild(bubble);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

startBtn.addEventListener('click', () => {
  setupCard.classList.add('hidden');
  chatCard.classList.remove('hidden');
  addBubble('Flynn steps out of the shadows, flashing that famous grin...', 'system');
  addBubble("Well, well. Rapunzel. Didn't expect to run into you here. So... what's on your mind?", 'flynn');
  messages.push({ role: 'assistant', content: "Well, well. Rapunzel. Didn't expect to run into you here. So... what's on your mind?" });
  userInput.focus();
});

chatForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const text = userInput.value.trim();
  if (!text) return;

  addBubble(text, 'user');
  messages.push({ role: 'user', content: text });
  userInput.value = '';
  userInput.disabled = true;

  const thinkingBubble = document.createElement('div');
  thinkingBubble.className = 'bubble flynn';
  thinkingBubble.textContent = '...';
  chatWindow.appendChild(thinkingBubble);
  chatWindow.scrollTop = chatWindow.scrollHeight;

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages }),
    });

    const data = await res.json();
    thinkingBubble.remove();

    if (!res.ok) {
      addBubble(`(Something went wrong: ${data.error || 'unknown error'})`, 'system');
    } else {
      addBubble(data.reply, 'flynn');
      messages.push({ role: 'assistant', content: data.reply });
    }
  } catch (err) {
    thinkingBubble.remove();
    addBubble(`(Network error: ${err.message})`, 'system');
  } finally {
    userInput.disabled = false;
    userInput.focus();
  }
});
