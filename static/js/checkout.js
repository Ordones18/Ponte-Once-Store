document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('paymentForm');
    const cedulaInput = document.getElementById('cedula');
    const cedulaError = document.getElementById('cedulaError');
    const payButton = document.getElementById('payButton');
    const statusMessage = document.getElementById('statusMessage');

    // Validador de Cédula Ecuatoriana
    function validarCedula(cedula) {
        if (cedula.length !== 10) return false;

        // NUEVO: Rechazar cédulas con todos los dígitos iguales (ej: 2222222222)
        if (/^(\d)\1{9}$/.test(cedula)) return false;

        const digitoRegion = parseInt(cedula.substring(0, 2));
        if (digitoRegion < 1 || digitoRegion > 24) return false;

        const ultimoDigito = parseInt(cedula.substring(9, 10));
        let pares = 0;
        let impares = 0;
        let sumaTotal = 0;

        for (let i = 0; i < 9; i++) {
            let digito = parseInt(cedula.charAt(i));
            if (i % 2 === 0) { // Posiciones impares (0, 2, 4...) en índice base 0
                digito *= 2;
                if (digito > 9) digito -= 9;
                impares += digito;
            } else {
                pares += digito;
            }
        }

        sumaTotal = pares + impares;
        const primerDigitoSuma = parseInt(String(sumaTotal).charAt(0));
        const decenaSuperior = (primerDigitoSuma + 1) * 10;

        let validacion = decenaSuperior - sumaTotal;
        if (validacion === 10) validacion = 0;

        // Caso especial si la suma termina en 0
        if (sumaTotal % 10 === 0) validacion = 0;

        return validacion === ultimoDigito;
    }

    // Validación en tiempo real (opcional, o al submit)
    cedulaInput.addEventListener('input', () => {
        const val = cedulaInput.value.replace(/\D/g, ''); // Solo números
        cedulaInput.value = val;

        if (val.length === 10) {
            if (validarCedula(val)) {
                cedulaError.textContent = "Cédula Valida";
                cedulaError.style.color = "#00c6ff";
            } else {
                cedulaError.textContent = "Cédula Inválida";
                cedulaError.style.color = "#ff4444";
            }
        } else {
            cedulaError.textContent = "";
        }
    });


    // --- Validar Tarjeta de Crédito (Simulación) ---
    const cardInput = document.getElementById('cardNumber');
    const cardError = document.getElementById('cardError');

    cardInput.addEventListener('input', () => {
        let val = cardInput.value.replace(/\D/g, ''); // Solo números
        const firstDigit = val.charAt(0);

        // Espaciado visual cada 4
        cardInput.value = val.replace(/(\d{4})(?=\d)/g, '$1 ').trim();

        if (val.length > 0) {
            if (firstDigit === '4') {
                cardError.textContent = "Visa detectada 🔵";
                cardError.style.color = "#00c6ff";
            } else if (firstDigit === '5') {
                cardError.textContent = "Mastercard detectada 🔴";
                cardError.style.color = "#ff9f00";
            } else if (firstDigit === '3') {
                cardError.textContent = "American Express detectada 🟢";
                cardError.style.color = "#2ecc71";
            } else if (firstDigit === '6') {
                cardError.textContent = "Discover detectada 🟠";
                cardError.style.color = "#e67e22";
            } else {
                cardError.textContent = "Tarjeta no reconocida / inválida ❌";
                cardError.style.color = "#ff4444";
            }
        } else {
            cardError.textContent = "";
        }
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const cedula = cedulaInput.value;
        if (!validarCedula(cedula)) {
            cedulaError.textContent = "Error: La cédula ingresada no es válida.";
            cedulaError.style.color = "#ff4444";
            return;
        }

        // Validar Tarjeta si está seleccionada
        const paymentMethod = document.querySelector('input[name="payment"]:checked').value;
        if (paymentMethod === 'card') {
            const cardVal = cardInput.value.replace(/\D/g, '');
            const firstDigit = cardVal.charAt(0);
            if (!['4', '5', '3', '6'].includes(firstDigit)) {
                cardError.textContent = "Error: La tarjeta debe ser Visa, Amex, MC o Discover.";
                cardError.style.color = "red";
                return;
            }
        }

        // Simulación de Proceso de Pago
        payButton.disabled = true;
        payButton.textContent = "Procesando...";
        statusMessage.textContent = "";

        // Datos para enviar
        const data = {
            name: document.getElementById('name').value,
            cedula: cedula,
            email: document.getElementById('email').value,
            phone: document.getElementById('phone').value,
            product_id: document.getElementById('productId').value,
            price: document.getElementById('productPrice').value
        };

        try {
            // Simular delay de red
            await new Promise(r => setTimeout(r, 2000));

            const csrfToken = document.getElementById('csrf_token').value;

            const response = await fetch('/api/buy', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify(data),
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Error del servidor (${response.status}): ${errorText.substring(0, 100)}...`);
            }

            const result = await response.json();

            if (result.status === 'success') {
                statusMessage.innerHTML = `<span style="color: #00c6ff; font-size: 1.2rem;">✨ ${result.message} ✨</span>`;
                form.reset();
                setTimeout(() => {
                    window.location.href = '/profile'; // Ir al perfil tras comprar
                }, 3000);
            } else {
                statusMessage.textContent = result.message || "Error al procesar el pago.";
            }

        } catch (error) {
            console.error('Error:', error);
            statusMessage.textContent = error.message || "Error de conexión.";
        } finally {
            payButton.disabled = false;
            payButton.textContent = "Pagar Ahora";
        }
    });
});

// Función para mostrar/ocultar detalles de tarjeta
function togglePayment(method) {
    const cardSection = document.getElementById('cardDetails');
    if (method === 'card') {
        cardSection.style.display = 'block';
    } else {
        cardSection.style.display = 'none';
    }
}

// Función global para cambiar imagen en galería
function changeImage(src, element) {
    document.getElementById('mainImage').src = src;

    // Remover clase active de todas las miniaturas
    const thumbnails = document.querySelectorAll('.thumbnail');
    thumbnails.forEach(thumb => thumb.classList.remove('active'));

    // Agregar clase active a la seleccionada
    element.classList.add('active');
}
