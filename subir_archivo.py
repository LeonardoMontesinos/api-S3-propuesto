# -----------------------------
# Archivo: subir_archivo.py
# -----------------------------
import json
import boto3
import botocore
import logging

# Configurar logging para ver errores en CloudWatch
logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    
    try:
        # 1. Cargar el body
        logger.info(f"Evento recibido: {event}")
        body = json.loads(event.get('body', '{}'))
        
        bucket_name = body.get('bucket_name')
        file_name = body.get('file_name')
        content_type = body.get('content_type') # Ej: 'image/jpeg'
        
        if not bucket_name or not file_name or not content_type:
            return {
                'statusCode': 400,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps('Error: Faltan "bucket_name", "file_name" o "content_type".')
            }

        # 2. Preparar los parámetros para la URL pre-firmada
        presigned_params = {
            'Bucket': bucket_name,
            'Key': file_name,
            'ContentType': content_type
        }

        # 3. Generar la URL (válida por 3600 segundos = 1 hora)
        upload_url = s3_client.generate_presigned_url(
            'put_object',
            Params=presigned_params,
            ExpiresIn=3600 
        )
        
        # 4. Enviar la URL al cliente
        return {
            'statusCode': 200,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({
                'message': 'URL generada. Use esta URL para subir el archivo con un PUT.',
                'upload_url': upload_url,
                'file_name': file_name
            })
        }

    except botocore.exceptions.ClientError as error:
        logger.error(f"Error de Boto3: {error}")
        return {
            'statusCode': 500, 
            'headers': {'Access-Control-Ahllow-Origin': '*'},
            'body': json.dumps(f'Error de cliente S3: {error}')
        }
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        return {
            'statusCode': 500,
            'headers': {'Access-Control-Allow-Origin': '*'},
            'body': json.dumps(f'Error interno del servidor: {str(e)}')
        }
