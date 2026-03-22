# create aws_s3_bucket
resource "aws_s3_bucket" "documents" {
    bucket = "document-upload-bucket"
}

# create DynamoDB table
resource "aws_dynamodb_table" "documents" {
    name         = "documents"
    billing_mode = "PAY_PER_REQUEST"
    hash_key     = "document_id"

    attribute {
        name = "document_id"
        type = "S"
    }
}