/**
 * Protección de Campos de Contraseña
 * Evita que se pueda ver la contraseña al modificar el atributo 'type' en el inspector.
 */
document.addEventListener('DOMContentLoaded', function () {
    // Seleccionar todos los campos de contraseña
    const passwordFields = document.querySelectorAll('input[type="password"]');

    passwordFields.forEach(function (input) {
        // Guardar el valor original del type
        let originalType = 'password';

        // Crear un observador que detecta cambios en los atributos
        const observer = new MutationObserver(function (mutations) {
            mutations.forEach(function (mutation) {
                if (mutation.type === 'attributes' && mutation.attributeName === 'type') {
                    // Si alguien cambió el type a algo diferente de 'password'
                    if (input.type !== 'password') {
                        // Limpiar el valor para que no se vea
                        input.value = '';
                        // Restaurar el tipo a password
                        input.type = 'password';
                        // Mostrar advertencia en consola
                        console.warn('⚠️ Intento de modificación detectado. Campo reiniciado por seguridad.');
                    }
                }
            });
        });

        // Configurar el observador para detectar cambios en atributos
        observer.observe(input, {
            attributes: true,
            attributeFilter: ['type']
        });

        // Protección adicional: evitar que se copie el valor
        input.addEventListener('copy', function (e) {
            e.preventDefault();
        });
    });
});
