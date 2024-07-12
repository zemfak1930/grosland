var myVariable;
var testParams = {}


//  Отримання данних про користувача
fetch('/api/email')
.then(response => response.json())
.then(data => {
    myVariable = data.email;
})
.catch(error => {
    console.error('Помилка отримання даних:', error);
});


//  Отримання параметрів для фільтрації ділянок
fetch('/api/parameters')
.then(response => response.json())
.then(data => {
    testParams = data;
})
.catch(error => {
    console.error('Помилка отримання даних:', error);
});