function fetchEvents() {
  fetch('/events')
    .then(res => res.json())
    .then(data => {
      const list = document.getElementById('eventList');
      list.innerHTML = '';
      data.forEach(item => {
        const li = document.createElement('li');
        li.textContent = item;
        list.appendChild(li);
      });
    });
}

setInterval(fetchEvents, 15000);
window.onload = fetchEvents;
