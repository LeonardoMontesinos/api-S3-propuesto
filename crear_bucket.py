# -----------------------------
# Archivo: crear_bucket.py
# -----------------------------
import json
import boto3
import botocore

# Es buena práctica inicializar el cliente fuera del handler
s3_client = boto3.client('s3')

# IMPORTANTE: AWS recomienda usar 'us-east-1' para compatibilidad global
# al crear buckets, a menos que necesites una región específica.
# Si tu rol tiene restricciones, cámbialo a tu región (ej: 'us-east-2')
DEFAULT_REGION = 'us-east-1' 

def lambda_handler(event, context):
    
    try:
        # 1. Cargar el body de la petición
        # El 'body' viene como un string, hay que convertirlo a JSON
        body = json.loads(event.get('body', '{}'))
        
        bucket_name = body.get('bucket_name')
        
        if not bucket_name:
            return {
                'statusCode': 400,
                'headers': {'Access-Control-Allow-Origin': '*'}, # Para CORS
                'body': json.dumps('Error: Falta el parametro "bucket_name" en el body.')
            }

        # 2. Crear el bucket
        # 'us-east-1' es la única región que no requiere 'LocationConstraint'
        if DEFAULT_REGION == 'us-east-1':
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            location = {'LocationConstraint': DEFAULT_REGION}
            s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration=location
            )
            
        # 3. Enviar respuesta exitosa
        return {
            'statusCode': 201, # 201 = "Created"
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps(f'Bucket "{bucket_name}" creado exitosamente.')
        }

    except botocore.exceptions.ClientError as error:
        # Capturar errores comunes de Boto3 (ej: bucket ya existe)
        error_code = error.response['Error']['Code']
        return {
            'statusCode': 409, # 409 = "Conflict"
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps(f'Error al crear bucket: {error_code}')
        }
    except Exception as e:
        # Capturar cualquier otro error (ej: JSON mal formado)
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps(f'Error interno del servidor: {str(e)}')
        }
