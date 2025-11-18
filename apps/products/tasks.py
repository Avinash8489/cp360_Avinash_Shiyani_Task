import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_uploaded_video(self, product_video_id):
    from apps.products.models import ProductVideo

    try:
        pv = ProductVideo.objects.get(id=product_video_id)
        
        if not pv.file:
            logger.warning(f"ProductVideo {product_video_id} has no file attached")
            return {"status": "skipped", "reason": "no_file"}

        logger.info(f"Processing video {product_video_id} for product {pv.product.id}")
        
        file_path = pv.file.path if hasattr(pv.file, "path") else str(pv.file)
        file_size = pv.file.size if hasattr(pv.file, "size") else 0
        
        logger.info(f"Video file: {file_path}, size: {file_size} bytes")
        
        logger.info(f"Video {product_video_id} processed successfully")
        
        return {
            "status": "success",
            "product_video_id": product_video_id,
            "product_id": pv.product.id,
            "file_size": file_size,
        }
        
    except ProductVideo.DoesNotExist:
        logger.error(f"ProductVideo {product_video_id} not found")
        return {"status": "error", "reason": "not_found"}
        
    except Exception as exc:
        logger.error(f"Error processing video {product_video_id}: {str(exc)}")
        raise self.retry(exc=exc, countdown=60 * (self.request.retries + 1))
