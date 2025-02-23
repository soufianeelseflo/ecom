from transformers import pipeline
import logging

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentimentGrader:
    def __init__(self):
        """
        Initialize the sentiment grader with a pre-trained DistilBERT model.
        See: https://huggingface.co/docs/transformers/main_classes/pipelines
        """
        try:
            self.classifier = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english"
            )
            logger.info("Sentiment grader initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize sentiment grader: {e}")
            raise

    def grade(self, text: str) -> str:
        """
        Grade the sentiment of the input text.
        Returns: "POSITIVE", "NEGATIVE", or "NEUTRAL" on error.
        """
        try:
            result = self.classifier(text)[0]
            return result["label"]  # e.g., "POSITIVE" or "NEGATIVE"
        except Exception as e:
            logger.error(f"Sentiment grading failed: {e}")
            return "NEUTRAL"