# -----------------------------
# Archivo: crear_directorio.py
# -----------------------------
import json
import boto3
import botocore

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    
    try:
        # 1. Cargar el body
        body = json.loads(event.get('body', '{}'))
        
        bucket_name = body.get('bucket_name')
        directory_name = body.get('directory_name')
        
        if not bucket_name or not directory_name:
            return {
                'statusCode': 400,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps('Error: Faltan "bucket_name" o "directory_name".')
            }
            
        # Asegurarse de que el nombre del directorio termine en /
        if not directory_name.endswith('/'):
            directory_name += '/'

        # 2. Crear el objeto vacío (directorio)
        s3_client.put_object(
            Bucket=bucket_name,
            Key=directory_name,
            Body='' # Cuerpo vacío
        )
        
        # 3. Enviar respuesta
        return {
            'statusCode': 201,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps(f'Directorio "{directory_name}" creado en "{bucket_name}".')
        }

    except botocore.exceptions.ClientError as error:
        # Ej: El bucket no existe (NoSuchBucket)
        error_code = error.response['Error']['Code']
        return {
            'statusCode': 404, 
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps(f'Error de cliente: {error_code}')
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps(f'Error interno del servidor: {str(e)}')
        }
