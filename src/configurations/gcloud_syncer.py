import os, sys
from src.exception import CustomException

class GCloudSync:

    def sync_file_from_gcloud(self, gcp_bucket_url, filename, destination):
        try:
            command = f"gcloud storage cp gs://{gcp_bucket_url}/{filename} {destination}/"
            # print("GCP BUCKET URL: " + gcp_bucket_url)
            os.system(command)
        except Exception as e:
            raise CustomException(e, sys) from e

    def sync_file_to_gcloud(self, gcp_bucket_url, filepath):
        try:
            command = f"gcloud storage cp {filepath} gs://{gcp_bucket_url}/"
            os.system(command)
        except Exception as e:
            raise CustomException(e, sys) from e