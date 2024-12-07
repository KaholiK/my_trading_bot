import pytest
import pandas as pd
import numpy as np
from src.predictive_models import PredictiveModel

@pytest.fixture
def mock_data():
    """
    Create mock data for testing predictive models.
    """
    return pd.DataFrame({
        "feature1": np.random.rand(100),
        "feature2": np.random.rand(100),
        "target": np.random.randint(0, 2, 100),
    })

def test_model_training(mock_data):
    """
    Test if the predictive model can be trained successfully.
    """
    model = PredictiveModel()
    result = model.train(mock_data[["feature1", "feature2"]], mock_data["target"])
    
    assert result["status"] == "success", "Model training should return success"
    assert result["model"] is not None, "Trained model should not be None"

def test_model_prediction(mock_data):
    """
    Test if the predictive model makes predictions successfully.
    """
    model = PredictiveModel()
    model.train(mock_data[["feature1", "feature2"]], mock_data["target"])
    
    predictions = model.predict(mock_data[["feature1", "feature2"]])
    
    assert len(predictions) == len(mock_data), "Number of predictions should match number of inputs"
    assert all(pred in [0, 1] for pred in predictions), "Predictions should only contain valid classes"

def test_model_evaluation(mock_data):
    """
    Test if the model evaluation metrics are calculated correctly.
    """
    model = PredictiveModel()
    model.train(mock_data[["feature1", "feature2"]], mock_data["target"])
    
    metrics = model.evaluate(mock_data[["feature1", "feature2"]], mock_data["target"])
    
    assert "accuracy" in metrics, "Evaluation should return accuracy"
    assert 0 <= metrics["accuracy"] <= 1, "Accuracy should be between 0 and 1"
