# Zipping lambda code
data "archive_file" "lambda_zip" {
    type = "zip"
    source_file = "index.py"
    output_path = "lambda_function.zip"
}

resource "aws_lambda_function" "upload_handler" {
    filename = "lambda_function.zip"
    function_name = "upload_metadata_handler"
    role = aws_iam_role.lambda_role.arn
    handler = "index.handler"
    runtime = "python3.9"

    source_code_hash = data.archive_file.lambda_zip.output_base64sha256

    environment {
        variables = {
            BUCKET_NAME = aws_s3_bucket.documents.id
        }
    }
}