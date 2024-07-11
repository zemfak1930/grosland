var myVariable;

fetch('/api/email')
.then(response => response.json())
.then(data => {
    myVariable = data.email;
})
.catch(error => {
    console.error('Помилка отримання даних:', error);
});