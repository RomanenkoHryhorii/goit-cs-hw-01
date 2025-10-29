; File: calculate.asm

org 0x100 ; Вказуємо, що це програма .COM

section .data
    a db 5             ; Визначаємо a = 5
    b db 3             ; Визначаємо b = 3
    c db 2             ; Визначаємо c = 2
    resultMsg db 'Result (b - c + a): $' ; Рядок для виведення результату

section .text
_start:
    ; 1. Обчислення b - c + a

    mov al, [b]        ; Завантажуємо b в al
    sub al, [c]        ; Віднімаємо c від al: (b - c)
    add al, [a]        ; Додаємо a до al: (b - c + a)

    ; Перетворення результату в ASCII символ
    ; Приклад: якщо b-c+a = 6, то al = 06h. Додаємо 30h (ASCII '0'), 
    ; отримуємо 36h (ASCII '6').
    add al, 30h        ; Перетворюємо число в ASCII символ

    ; 2. Виведення рядка "Result (b - c + a): "
    mov ah, 09h        ; Функція DOS для виведення рядка
    lea dx, resultMsg  ; Встановлюємо DX на адресу resultMsg
    int 21h            ; Виклик DOS-переривання

    ; 3. Виведення числа (результату)
    mov dl, al         ; Поміщаємо ASCII-результат в dl для виводу
    mov ah, 02h        ; Функція DOS для виводу символу
    int 21h            ; Виклик DOS-переривання

    ; 4. Завершення програми
    mov ax, 4c00h      ; Функція DOS для завершення програми
    int 21h            ; Виклик DOS-переривання
