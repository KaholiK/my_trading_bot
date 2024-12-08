import torch
import torch.nn as nn
import numpy as np
import logging

logger = logging.getLogger(__name__)

class TimeSeriesPredictor(nn.Module):
    def __init__(self, input_dim=1, hidden_dim=64, num_layers=2, output_dim=1, bidirectional=False, proj_size=0):
        super(TimeSeriesPredictor, self).__init__()
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.bidirectional = bidirectional
        self.proj_size = proj_size

        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            bidirectional=bidirectional,
            batch_first=True
        )

        direction_factor = 2 if bidirectional else 1
        self.fc = nn.Linear(hidden_dim * direction_factor, output_dim)

    def forward(self, x):
        # x should be of shape (batch_size, sequence_length, input_dim)
        out, _ = self.lstm(x)  # out: (batch_size, sequence_length, hidden_dim * num_directions)
        # Take the last output
        out = out[:, -1, :]  # (batch_size, hidden_dim * num_directions)
        out = self.fc(out)    # (batch_size, output_dim)
        return out.detach().numpy()

    def predict(self, X):
        if X.dim() != 3:
            raise ValueError(f"Expected input tensor to be 3D, got {X.dim()}D instead.")
        with torch.no_grad():
            return self.forward(X)
