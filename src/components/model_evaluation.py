import os
import sys
import torch
from tqdm import tqdm
from src.logger import logging
from src.constants import DEVICE
from torch.utils.data import DataLoader
from src.exception import CustomException
from src.utils.main_utils import load_object
from src.configurations.gcloud_syncer import GCloudSync
from src.entity.config_entity import ModelEvaluationConfig
from src.entity.artifcat_entity import ModelTrainerArtifacts, DataTransformationArtifacts, ModelEvaluationArtifacts



class ModelEvaluation:
    def __init__(self, model_evaluation_config: ModelEvaluationConfig, model_trainer_artifacts: ModelTrainerArtifacts, data_transformation_artifacts: DataTransformationArtifacts):
        self.model_evaluation_config = model_evaluation_config
        self.model_trainer_artifacts = model_trainer_artifacts
        self.data_transformation_artifacts = data_transformation_artifacts
        self.gcloud = GCloudSync()

    def get_best_model_from_gcloud(self) -> str:
        try:
            logging.info("Entered the get_best_model_from_gcloud function of Model Evaluation class")
            os.makedirs(self.model_evaluation_config.BEST_MODEL_DIR, exist_ok=True)
            self.gcloud.sync_file_from_gcloud(self.model_evaluation_config.BUCKET_NAME,
                                              self.model_evaluation_config.MODEL_NAME,
                                              self.model_evaluation_config.BEST_MODEL_DIR)
            best_model_path = os.path.join(self.model_evaluation_config.BEST_MODEL_DIR,
                                           self.model_evaluation_config.MODEL_NAME)
            logging.info("Exited the get_best_model_from_gcloud function of Model Evaluation class")
            return best_model_path
        except Exception as e:
            raise CustomException(e, sys) from e

    def evaluate(self, model, criterion, test_dataloader):
        try:
            total_test_lost = 0
            model.eval()
            with tqdm(test_dataloader, unit='batch', leave=False) as pbar:
                pbar.set_description(f'testing')
                for images, idxs in pbar:
                    images = images.to(DEVICE, non_blocking=True)
                    idxs = idxs.to(DEVICE, non_blocking=True)

                    outputs = model(images)
                    loss = criterion(outputs, idxs)
                    total_test_lost += loss.item()
            test_loss = total_test_lost / len(self.data_transformation_artifacts.test_transformed_object)
            print(f'Test loss: {test_loss:.4f}')
            return test_loss
        except Exception as e:
            raise CustomException(e, sys) from e

    def initiate_model_evaluation(self) -> ModelEvaluationArtifacts:
        logging.info("Entered the Initiate_model_evaluation function of Model Evaluation class")
        try:
            logging.info("Loading validation data for model evaluation")
            test_dataset = load_object(self.data_transformation_artifacts.test_transformed_object)
            test_loader = DataLoader(test_dataset, shuffle=False,
                                     batch_size=self.model_evaluation_config.BATCH_SIZE,
                                     num_workers=self.model_evaluation_config.NUM_WORKERS)
            criterion = torch.nn.CrossEntropyLoss()

            logging.info("Loading currently trained model")
            model = torch.load(self.model_trainer_artifacts.trained_model_path, map_location=DEVICE)
            model.eval()

            trained_model_loss = self.evaluate(model, criterion, test_loader)

            logging.info("Fetch best model from gcloud storage")
            best_model_path = self.get_best_model_from_gcloud()

            logging.info("Check is best model present in the gcloud storage or not?")
            if os.path.isfile(best_model_path) is False:
                is_model_accepted = True
                logging.info("gcloud storage model is false and currently trained model accepted is true")
            else:
                logging.info("Load best model from gcloud storage")
                model =torch.load(best_model_path, map_location=DEVICE)
                model.eval()
                best_model_loss = self.evaluate(model, criterion, test_loader)
                logging.info("Comparing loss between best_model_loss and trained_model_loss ?")
                if best_model_loss > trained_model_loss:
                    is_model_accepted = True
                    logging.info("Trained model not accepted")
                else:
                    is_model_accepted = False
                    logging.info("Trained model accepted")

            model_evaluation_artifacts = ModelEvaluationArtifacts(is_model_accepted=is_model_accepted)
            return model_evaluation_artifacts
        except Exception as e:
            raise CustomException(e, sys) from e

