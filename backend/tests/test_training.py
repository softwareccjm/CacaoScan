import requests

# 1. Login
login_response = requests.post(
    'http://127.0.0.1:8000/api/v1/auth/login/',
    json={'username': 'admin_training', 'password': 'admin123'}
)

print("Login response:", login_response.json())
print("\n---\n")

# 2. Obtener token
login_data = login_response.json()
token = login_data.get('access') or login_data.get('data', {}).get('access')

if not token:
    print("ERROR: No se pudo obtener el token")
    print("Estructura de respuesta:", login_data)
    exit(1)

print(f"Token obtenido: {token[:50]}...")

# 3. Crear entrenamiento
training_response = requests.post(
    'http://127.0.0.1:8000/api/v1/ml/train/',
    headers={
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    },
    json={
        'job_type': 'regression',
        'model_name': 'resnet18',
        'dataset_size': 490,
        'epochs': 30,
        'batch_size': 16,
        'learning_rate': 0.001,
        'config_params': {
            'multi_head': False,
            'model_type': 'resnet18',
            'img_size': 224,
            'early_stopping_patience': 10,
            'save_best_only': True
        }
    }
)

print("\nTraining response:", training_response.json())