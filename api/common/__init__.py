from fastapi import UploadFile, Form
from pydantic import BaseModel
from dataclasses import dataclass, field
from cv2.typing import MatLike

class FindCoordsSchema(BaseModel):
    baseImage: UploadFile
    refImage: UploadFile
    baseImageName: str
    refImageName: str
    index: int

@dataclass
class imageControllerSchema():
    baseImage: str
    refImage: str
    index: int
    x: int
    y: int
    req_id: str

class ImageResponse(BaseModel):
    img: str
    accuracy: float
    x: int
    y: int


# To convert the File object to a string for Pydantic validation
def find_coords_schema(
    baseImage: UploadFile = Form(..., media_type="multipart/form-data"),
    refImage: UploadFile = Form(..., media_type="multipart/form-data"),
    index: int = Form(..., media_type="multipart/form-data"),
    baseImageName: str = Form(..., media_type="multipart/form-data"),
    refImageName: str = Form(..., media_type="multipart/form-data"),

):
    return FindCoordsSchema(baseImage=baseImage, refImage=refImage, index=index, baseImageName=baseImageName, refImageName=refImageName)


@dataclass
class imageControllerError():
    status: str = field(init=False, default="error")
    message: str

@dataclass
class imageControllerSuccess():
    status: str = field(init=False, default="success")
    matches: list
    result: MatLike
    image: MatLike
    refImg: MatLike