# SQS
resource "aws_sqs_queue" "document_queue" {
  name = "document-processing-queue"
}

# Configure S3 to send event to SQS when a file is created
resource  "aws_s3_bucket_notification" "bucket_notification" {
    bucket = aws_s3_bucket.documents.id

    queue {
        queue_arn = aws_sqs_queue.document_queue.arn
        events = ["s3:ObjectCreated:*"]
    }
}