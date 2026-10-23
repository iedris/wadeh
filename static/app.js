const form = document.querySelector('#analyze-form');
const text = document.querySelector('#document');
const count = document.querySelector('#character-count');
const button = document.querySelector('#analyze-button');
const updateCount = () => { count.textContent = `${text.value.length.toLocaleString()} characters`; };
text.addEventListener('input', updateCount);
updateCount();
form.addEventListener('submit', () => {
  button.disabled = true;
  button.textContent = 'Analyzing…';
  document.querySelector('#progress').hidden = false;
});
window.addEventListener('pageshow', () => {
  button.disabled = false;
  button.textContent = 'Explain my document ↗';
  document.querySelector('#progress').hidden = true;
});
