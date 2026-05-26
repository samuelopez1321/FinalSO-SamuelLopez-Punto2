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

@app.get("/get-image")
def get_image(username: str, image_name: str):
    object_key = f"{username}/{image_name}"

    try:
        response = s3.head_object(
            Bucket=BUCKET_NAME,
            Key=object_key
        )

        presigned_url = s3.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": BUCKET_NAME,
                "Key": object_key
            },
            ExpiresIn=3600
        )

        metadata = response.get("Metadata", {})
        last_modified = response.get("LastModified")

        return {
            "message": "Imagen encontrada correctamente",
            "username": username,
            "image_name": image_name,
            "url": presigned_url,
            "storage_date_metadata": metadata.get("upload_date", "No disponible"),
            "last_modified_s3": str(last_modified)
        }

    except ClientError as e:
        error_code = e.response["Error"]["Code"]

        if error_code == "404":
            raise HTTPException(
                status_code=404,
                detail="No existe el usuario o la imagen solicitada en el bucket S3."
            )

        raise HTTPException(
            status_code=500,
            detail=f"Error consultando imagen en S3: {str(e)}"
        )
