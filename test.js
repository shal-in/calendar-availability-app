console.log('test.js')

// /?name=TestName&date=2024-03-03&days=7&duration=1.5

// Get the URL query string
const queryString = window.location.search;

// Create a new URLSearchParams object with the query string
const searchParams = new URLSearchParams(queryString);

// Use the get() method to retrieve the value of a specific query parameter
let name = searchParams.get('name');
let date = searchParams.get('date');
let days = searchParams.get('days');
if (!days) {
  days = 7
}
let duration = searchParams.get('duration');

console.log(name)
console.log(date)
console.log(days)
console.log(duration)

const nameInputEl = document.getElementById('nameInput');
const durationInputEl = document.getElementById('durationInput');
const startDateInputEl = document.getElementById('startDateInput');
const findTimesBtnEl = document.getElementById('findTimesBtn');

if (name) {
    nameInputEl.value = name
}

if (duration) {
  for (let i = 0; i < durationInputEl.options.length; i++) {
    if (durationInputEl.options[i].value === duration) {
      durationInputEl.options[i].selected = true

      break
    }
  }
}

if (date) {
  startDateInputEl.value = date
}

findTimesBtnEl.addEventListener('click', findTimesBtnFunction)

url = 'http://127.0.0.1:2020//api/tutoring-availability/get';

data = {
  'start_date': date,
  'days': days,
  'duration': duration
}

const jsonData = JSON.stringify(data);

function findTimesBtnFunction() {
  console.log('find times')

    fetch(url, {
      method: 'POST',
      headers: {
          'Content-Type': 'application/json',
          // Add any additional headers if needed
      },
      body: jsonData // Pass the JSON data as the request body
  })
  .then(response => {
      // Check if the response is successful
      if (!response.ok) {
          throw new Error('Network response was not ok');
      }
      // Parse the JSON response
      return response.json();
  })
  .then(data => {
      // Store the response as a dictionary
      const responseData = data;

      console.log(responseData)

  })
  .catch(error => {
      // Handle errors
      console.error('Error:', error);
  });
}