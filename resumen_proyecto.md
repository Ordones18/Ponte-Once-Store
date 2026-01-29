# Resumen del Proyecto: PONTE ONCE STORE

**PONTE ONCE STORE** es una plataforma de comercio electrónico especializada en hardware gaming de alta gama. El proyecto combina una estética inmersiva con funcionalidades robustas de gestión y ventas.

## 🛠️ Tecnologías Clave
*   **Backend**: Python con **Flask**.
*   **Base de Datos**: **MySQL** (gestionada con SQLAlchemy).
*   **Frontend**: HTML5, CSS3 (Diseño Responsivo/Gamer), JavaScript Moderno.
*   **Seguridad**: Hashing de contraseñas (SHA-256), Protección de Rutas, Tokens seguros.

## ⭐ Características Principales

### 1. Experiencia de Usuario (UX/UI)
*   **Diseño Impactante**: Interfaz oscura con acentos neón (Azul/Amarillo), tipografías *Orbitron* y *Rajdhani*.
*   **Página de Inicio Dinámica**:
    *   Hero Section con diseño elegante.
    *   Sección "Nuestra Tienda" con video integrado.
    *   Grid de productos destacados con efectos hover.
*   **Catálogo Interactivo**: Tarjetas de producto con animaciones y acceso directo a compra o detalles.
*   **Detalles de Producto**: Galería de imágenes y descripción completa.

### 2. Sistema de Ventas y Checkout
*   **Flujo de Compra Realista**:
    *   Formulario de facturación validado.
    *   **Validación de Cédula Ecuatoriana**: Algoritmo Módulo 10 implementado en JS.
    *   **Simulación de Pagos**:
        *   Detección automática de franquicia de tarjeta (Visa, MC, Amex) por el primer dígito.
        *   Validación básica de campos financieros.
    *   **Control de Stock**: Descuento automático de inventario al comprar. Bloqueo de ventas sin stock.

### 3. Gestión de Usuarios
*   **Autenticación Completa**: Registro, Login y Logout seguros.
*   **Recuperación de Contraseñas**: Sistema de tokens temporales enviados por correo electrónico.
*   **Perfil de Usuario**: Historial de compras personal con fechas y montos.

### 4. Panel de Administración (Backoffice)
*   **Dashboard Exclusivo**: Accesible solo para usuarios con rol `is_admin`.
*   **Gestión de Pedidos**: Visualización tabular de todas las ventas con datos de contacto.
*   **Inventario Visual**: Semaforización de stock (Verde/Amarillo/Rojo) para alertas rápidas.
*   **Agregar Productos**: Formulario simplificado para subir nuevo inventario sin necesitar conocimientos de SQL.

### 5. Notificaciones
*   **Emails Transaccionales**: Envío automático de confirmación de compra con detalles del pedido y contacto, usando conexión SMTP segura (Gmail).

## 🚀 Estado Actual
El proyecto es **100% funcional**. El servidor corre localmente, la base de datos MySQL persiste toda la información (usuarios, productos, ventas), y todos los flujos (desde el registro hasta la compra y la administración) han sido verificados.
