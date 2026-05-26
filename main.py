from fastapi import FastAPI, UploadFile, File, Form, HTTPException
import boto3
from botocore.exceptions import ClientError
from datetime import datetime

app = FastAPI(title="Final Sistemas Operativos - Punto 2")

BUCKET_NAME = "final-so-samuel-lopez-imagenes"

s3 = boto3.client("s3")

ALLOWED_CONTENT_TYPES = {
    "image/png",
    "image/jpeg",
    "image/jpg"
}

@app.post("/upload-image")
async def upload_image(
    username: str = Form(...),
    image: UploadFile = File(...)
):
    if image.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=415,
            detail="Formato inválido. Solo se permiten imágenes PNG, JPG o JPEG."
        )

    object_key = f"{username}/{image.filename}"

    try:
        s3.upload_fileobj(
            image.file,
            BUCKET_NAME,
            object_key,
            ExtraArgs={
                "ContentType": image.content_type,
                "Metadata": {
                    "username": username,
                    "upload_date": datetime.utcnow().isoformat()
                }
            }
        )

        return {
            "message": "Imagen subida correctamente",
            "username": username,
            "image_name": image.filename,
            "s3_path": object_key
        }

    except ClientError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error subiendo imagen a S3: {str(e)}"
        )
