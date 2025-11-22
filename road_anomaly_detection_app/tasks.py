from road_anomaly_detection_model.model import *
from road_anomaly_detection_app.models import RoadAnomalyReport, MediaContent, StatusTypeChoise
# from celery import shared_task
# from road_anomaly_detection import settings

import logging
import functools
import time
from typing import Callable, Any, Optional, Type, Tuple, List, Dict
import os

import cv2

from uuid import uuid4

# Configure logger (optional)
logger = logging.getLogger(__name__)

def try_except(
    func: Optional[Callable] = None,
    *,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    fallback: Any = None,
    max_retries: int = 0,
    delay: float = 0,
    log_error: bool = True,
    raise_on_fail: bool = False,
    error_message: Optional[str] = None
):
    """
    A powerful decorator to wrap any function with try/except logic.

    Args:
        func: The function to wrap (when used as decorator)
        exceptions: Tuple of exceptions to catch (default: all)
        fallback: Value to return on failure
        max_retries: Number of retry attempts
        delay: Seconds to wait between retries
        log_error: Whether to log the exception
        raise_on_fail: Re-raise after retries
        error_message: Custom message for logs/raise

    Returns:
        Wrapped function or decorator
    """
    
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            attempt = 0
            last_exception = None

            while attempt <= max_retries:
                try:
                    return f(*args, **kwargs)
                
                except exceptions as e:
                    last_exception = e
                    attempt += 1

                    msg = error_message or f"Error in {f.__name__}"
                    full_msg = f"{msg}: {e}"

                    if log_error:
                        logger.error(full_msg, exc_info=True)

                    if attempt <= max_retries:
                        if delay > 0:
                            time.sleep(delay)
                        continue
                    else:
                        break

            # All retries failed
            if raise_on_fail and last_exception:
                raise last_exception

            return fallback

        return wrapper

    # Allow @try_except or @try_except(...)
    return decorator if func is None else decorator(func)

# # classifier output data structure example:
# {'image_name': 'd8a6912a-8e98-4619-8496-375bd55c1a02 - Ayan Sanki - ayansanki2004@gmail.com.jpg', 
#  'detections': [
#      {'class': 'D20_Alligator_Crack', 'confidence': 0.6158, 'bounding_box': {'x1': 0, 'y1': 17, 'x2': 549, 'y2': 341}, 'area_pixels': 178083}, 
#      {'class': 'D20_Alligator_Crack', 'confidence': 0.5608, 'bounding_box': {'x1': 0, 'y1': 37, 'x2': 160, 'y2': 164}, 'area_pixels': 20418}
#     ], 
#  'main_class': 'D20_Alligator_Crack', 
#  'main_confidence': 0.6158
# }

def extract_and_classify_frames(video_path: str,max_frames: int = 10) -> List[Dict]:
    """
    Extract up to `max_frames` evenly spaced frames from video
    and classify each one.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError(f"Cannot open video: {video_path}")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    duration = total_frames / fps if fps > 0 else 0

    # Choose frame indices evenly
    if total_frames <= max_frames:
        frame_indices = range(0, total_frames, max(1, total_frames // max_frames))
    else:
        step = total_frames // max_frames
        frame_indices = range(0, total_frames, step)

    results = []
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count in frame_indices:
            frame_path = f"{os.path.splitext(video_path)[0]}_frame_{frame_count}_{uuid4()}.jpg"
            cv2.imwrite(frame_path, frame)
            result = classifier(frame_path)
            results.append(result)

        frame_count += 1

        # Optional: stop early if we have enough
        if len(results) >= max_frames:
            break
    cap.release()

    os.remove(video_path)

    return results


@try_except
def data_classifier(instance: RoadAnomalyReport):
    if RoadAnomalyReport.objects.filter(pk = instance.pk):
        reports = []
        for f in instance.files:
            print(f)
            if f["file_type"] == "Image":
                media : MediaContent = MediaContent.objects.get(file_id = f['file_id'])
                file_path = f'road_anomaly_detection_model/temp/{media.file_id}.jpg'
                with open(file_path, 'wb') as file:
                    file.write(media.binary_data)

                result = classifier(file_path)
                print(result)

                if result['detections']:
                    reports.append({
                        'file_id': media.file_id,
                        'file_path': file_path,
                        'class': result['main_class'],
                        'confidence': result['main_confidence']
                    })
                
                else:
                    reports.append({
                        'file_id': media.file_id,
                        'file_path': file_path,
                        'class': None,
                        'confidence': 0.0
                    })

            elif f["file_type"] == "Video":
                media : MediaContent = MediaContent.objects.get(file_id = f['file_id'])
                file_path = f'road_anomaly_detection_model/temp/{media.file_id}.mp4'
                with open(file_path, 'wb') as file:
                    file.write(media.binary_data)

                results = extract_and_classify_frames(file_path, max_frames=10)
                print(results)
                for result in results:
                    if result['detections']:
                        reports.append({
                            'file_id': media.file_id,
                            'file_path': f'road_anomaly_detection_model/temp/{result["image_name"]}',
                            'class': result['main_class'],
                            'confidence': result['main_confidence']
                        })
                    else:
                        reports.append({
                            'file_id': media.file_id,
                            'file_path': f'road_anomaly_detection_model/temp/{result["image_name"]}',
                            'class': None,
                            'confidence': 0.0
                        })
            else:
                pass

        best = max(reports, key=lambda x: x['confidence']) 
        if best['confidence'] > 0:
            instance.anomalyType = best['class']
        else:
            instance.anomalyType = "No detections found"

        with open(best['file_path'], 'r+b') as file:
            instance.anomalyImage = file.read()

        instance.status = StatusTypeChoise.PENDING

        instance.save(update_fields=['status', 'anomalyType', 'anomalyImage'])

        for path in reports:
            os.remove(path['file_path'])


        


