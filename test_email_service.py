import requests
import json

def test_email():
    print("--- Test de Microservicio de Email ---")
    url = input("Ingresa la URL del servicio (ej: https://ponte-once-store.vercel.app/api): ").strip()
    
    # Asegurar que tenga /send-email
    if not url.endswith('/send-email'):
        if url.endswith('/api'):
            url += '/send-email'
        elif url.endswith('/'):
             url += 'api/send-email'
        else:
             url += '/api/send-email'
            
    print(f"\nProbando URL: {url}")
    
    to_email = input("Ingresa tu correo para recibir la prueba: ").strip()
    
    payload = {
        "to": to_email,
        "subject": "Test desde Script Local 🚀",
        "html": "<h1>Funciona!</h1><p>El microservicio de Vercel está respondiendo correctamente.</p>"
    }
    
    try:
        print("\nEnviando solicitud (Timeout 30s)...")
        response = requests.post(url, json=payload, timeout=30)
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response Body: {response.text}")
        
        if response.status_code == 200:
            print("\n✅ ÉXITO: El correo debería haber llegado (revisa Spam también).")
        else:
            print("\n❌ ERROR: El servicio respondió con error.")
            
    except Exception as e:
        print(f"\n❌ EXCEPCIÓN: {e}")

if __name__ == "__main__":
    test_email()
