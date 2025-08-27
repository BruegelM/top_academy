function sum(a, b) {
   let sum = 0;
    const start = Math.min(a, b);
    const end = Math.max(a, b);

    // Используем start и end для корректной работы с любым порядком чисел
    for (let i = start; i <= end; i++) {
        sum += i;
    }

    return sum;
}

console.log(sum(1, 7));
