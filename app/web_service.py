"""Inferencia por foto. Modelos compartidos bajo lock, sin archivos persistentes."""
import base64
import io
import json
import logging
import math
import threading
import time
import zipfile
from dataclasses import dataclass
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps, UnidentifiedImageError

logger = logging.getLogger(__name__)
MAX_PIXELS = 20_000_000
Image.MAX_IMAGE_PIXELS = MAX_PIXELS

class ImageError(ValueError):
    pass

class ModelsError(RuntimeError):
    pass

@dataclass(frozen=True)
class WebSettings:
    weights: Path
    device: str = 'auto'
    default_confidence: float = 0.60

def decode_image(data):
    try:
        with Image.open(io.BytesIO(data)) as photo:
            if photo.format not in {'JPEG', 'PNG', 'WEBP', 'BMP'}:
                raise ImageError('Usa una foto JPG, PNG, WEBP o BMP.')
            if photo.width * photo.height > MAX_PIXELS:
                raise ImageError('La foto supera 20 megapíxeles. Reduce su resolución.')
            if getattr(photo, 'n_frames', 1) != 1:
                raise ImageError('Usa una imagen estática.')
            photo.load()
            oriented = ImageOps.exif_transpose(photo).convert('RGBA')
            background = Image.new('RGBA', oriented.size, (255,255,255,255))
            return Image.alpha_composite(background, oriented).convert('RGB')
    except ImageError:
        raise
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError) as exc:
        raise ImageError('No se pudo leer la foto. Comprueba que no esté dañada.') from exc

def encoded_image(photo, format='JPEG'):
    stream=io.BytesIO()
    photo.save(stream,format=format,**({'quality':92} if format=='JPEG' else {}))
    return stream.getvalue()

def image_url(data, mime='image/jpeg'):
    return f'data:{mime};base64,'+base64.b64encode(data).decode('ascii')

def font(size):
    for path in ['C:/Windows/Fonts/arial.ttf','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']:
        if Path(path).exists():return ImageFont.truetype(path,size)
    return ImageFont.load_default()

def build_models(settings):
    if not settings.weights.is_file():
        raise ModelsError('No se encontró el modelo entrenado. Revisa --weights y models/best.pt.')
    try:
        import torch
        from src.config import LicensePlateConfig
        from src.providers import ComputeBackend
        from src.plate_detector import PlateDetector
        from app.web_ocr import WebOCR
        available=torch.cuda.is_available()
        device='0' if settings.device=='auto' and available else ('cpu' if settings.device=='auto' else settings.device)
        if device=='0' and not available:
            raise ModelsError('CUDA no está disponible. Inicia con --device cpu.')
        cfg=LicensePlateConfig(detector_backend='yolo',weights_path=str(settings.weights),
            device=device,compute_backend=ComputeBackend.CPU,det_conf=settings.default_confidence,det_iou=0.7)
        detector=PlateDetector(cfg)
        ocr=WebOCR(cfg)
        return detector,ocr,device
    except ModelsError:
        raise
    except Exception as exc:
        logger.exception('Error cargando modelos')
        raise ModelsError('No se pudieron cargar los modelos. Revisa la consola; el primer uso del OCR necesita Internet.') from exc

class PlateService:
    def __init__(self, settings, factory=build_models):
        self.settings=settings
        self.factory=factory
        self.lock=threading.Lock()
        self.models=None

    def status(self):
        return {'weights_found':self.settings.weights.is_file(),'models_loaded':self.models is not None,
                'default_confidence':self.settings.default_confidence}

    def process(self,photo,filename,confidence):
        # Una sola inferencia a la vez. La confianza se cambia dentro del mismo lock.
        with self.lock:
            load_ms=0.0
            if self.models is None:
                started=time.perf_counter()
                self.models=self.factory(self.settings)
                load_ms=(time.perf_counter()-started)*1000
            detector,ocr,device=self.models
            detector.cfg.det_conf=confidence
            started=time.perf_counter()
            bgr=np.ascontiguousarray(np.asarray(photo)[:,:,::-1])
            detections=detector.detect(bgr)
            plates=[];crops=[]
            width,height=photo.size
            annotated=photo.copy();draw=ImageDraw.Draw(annotated)
            text_font=font(max(15,min(36,round(width/50))))
            line_width=max(2,round(width/450))
            for box in detections:
                if len(box)<6 or not np.isfinite(box[:6]).all() or int(box[5])!=0:continue
                x1=max(0,min(width,math.floor(float(box[0]))));y1=max(0,min(height,math.floor(float(box[1]))))
                x2=max(0,min(width,math.ceil(float(box[2]))));y2=max(0,min(height,math.ceil(float(box[3]))))
                if x2<=x1 or y2<=y1:continue
                index=len(plates)+1;crop=photo.crop((x1,y1,x2,y2));crop_bytes=encoded_image(crop,'PNG')
                crop_bgr=bgr[y1:y2,x1:x2].copy()
                error=None
                try:
                    chars,probs=ocr.read(crop_bgr)
                    if len(chars)!=len(probs):raise ValueError('Confianzas desalineadas')
                    probs=[float(v) for v in probs]
                    if any(not math.isfinite(v) or not 0<=v<=1 for v in probs):raise ValueError('Confianza inválida')
                    text=''.join(chars)
                except Exception:
                    logger.exception('Error OCR en placa %s',index)
                    text='';probs=[];error='El OCR falló en este recorte. Puedes descargarlo y revisar la consola.'
                row={'id':index,'bbox':[x1,y1,x2,y2],'plate_text':text,
                     'detection_confidence':float(box[4]),'character_confidences':probs,
                     'ocr_mean_confidence':float(np.mean(probs)) if probs else None,
                     'ocr_status':'error' if error else ('read' if text else 'empty'),
                     'ocr_error':error,'crop_file':f'placa_{index:03d}.png'}
                plates.append(row);crops.append(crop_bytes)
                color=(19,160,123) if text else (205,126,25)
                draw.rectangle((x1,y1,x2-1,y2-1),outline=color,width=line_width)
                label=f'{index}. {text or "Sin lectura"}'
                rect=draw.textbbox((0,0),label,font=text_font);tw=min(width,rect[2]-rect[0]+12);th=rect[3]-rect[1]+10
                tx=max(0,min(x1,width-tw));ty=max(0,y1-th)
                draw.rectangle((tx,ty,tx+tw,ty+th),fill=color)
                draw.text((tx+6,ty+4-rect[1]),label,font=text_font,fill='white')
            elapsed=(time.perf_counter()-started)*1000
            result={'image':filename,'image_size':{'width':width,'height':height},'plates':plates,
                    'processing_ms':round(elapsed,2),'model_load_ms':round(load_ms,2),
                    'detection_threshold':confidence,'detector_device':device,
                    'ocr_model':'cct-s-v2-global-model',
                    'note':'El promedio OCR describe la confianza por carácter; no es una probabilidad calibrada de matrícula correcta.'}
            jpg=encoded_image(annotated)
            archive=io.BytesIO()
            with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
                z.writestr('foto_anotada.jpg',jpg)
                z.writestr('resultados.json',json.dumps(result,ensure_ascii=False,indent=2))
                for row,crop in zip(plates,crops):z.writestr(row['crop_file'],crop)
            return {'result':result,'annotated_image':image_url(jpg),
                    'crops':[image_url(v,'image/png') for v in crops],
                    'download_zip':base64.b64encode(archive.getvalue()).decode('ascii')}
