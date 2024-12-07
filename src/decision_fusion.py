# File: src/decision_fusion.py
# Part 6: Decision Fusion & Meta-Controller
#
# This module takes:
# - Predictive model signals (e.g., predicted price moves or probabilities of upward/downward trends)
# - RL agent's recommended action (buy, sell, hold)
# - LLM-derived sentiment or fundamental signals
#
# It then fuses these inputs into a final decision. Initially, the logic here will be simple:
# a weighted average or a rule-based system. In later parts, we will refine this to be more dynamic.

from typing import Dict, Any, Optional
import numpy as np

class MetaController:
    """
    The MetaController integrates outputs from:
    1. Predictive models (forecasted returns or probabilities)
    2. RL agent recommended action
    3. LLM sentiment signals (e.g., bullish/bearish score)
    
    It uses these inputs to decide final trading actions and parameters (e.g., position size).
    """
    def __init__(self,
                 predictive_weight: float = 0.4,
                 rl_weight: float = 0.4,
                 sentiment_weight: float = 0.2):
        # These weights sum to 1.0 (ideally).
        self.predictive_weight = predictive_weight
        self.rl_weight = rl_weight
        self.sentiment_weight = sentiment_weight

    def fuse_signals(self,
                     predictive_signal: float,
                     rl_action: int,
                     sentiment_score: float) -> Dict[str, Any]:
        """
        Fuse signals into a final decision.
        
        predictive_signal: A value from predictive models (e.g., expected return next period).
            Positive = bullish, negative = bearish, magnitude indicates confidence.
        rl_action: An integer representing RL agent's suggested action: 0=sell, 1=hold, 2=buy
        sentiment_score: A value from LLM sentiment analysis, say in range [-1, 1].
            Positive = bullish, negative = bearish.

        We'll combine these heuristically:
        - Convert rl_action into a numeric signal: buy=+1, sell=-1, hold=0
        - Weighted sum of three signals (predictive, rl, sentiment) to produce final direction.
        """
        rl_numeric = 0.0
        if rl_action == 2:  # buy
            rl_numeric = 1.0
        elif rl_action == 0: # sell
            rl_numeric = -1.0
        # hold = 0.0 by default

        # Weighted sum
        combined_signal = (self.predictive_weight * predictive_signal) + \
                          (self.rl_weight * rl_numeric) + \
                          (self.sentiment_weight * sentiment_score)

        # Final action decision:
        # If combined_signal > 0.1 => buy
        # If combined_signal < -0.1 => sell
        # Otherwise, hold
        if combined_signal > 0.1:
            final_action = "buy"
        elif combined_signal < -0.1:
            final_action = "sell"
        else:
            final_action = "hold"

        # For demonstration, we just return a dict.
        return {
            "final_action": final_action,
            "combined_signal": combined_signal,
            "predictive_signal": predictive_signal,
            "rl_action": rl_action,
            "sentiment_score": sentiment_score
        }

if __name__ == "__main__":
    # Quick test:
    meta = MetaController()
    # Suppose the predictive model is slightly bullish (0.2),
    # RL suggests buy (2),
    # Sentiment is neutral (0.0)
    result = meta.fuse_signals(predictive_signal=0.2, rl_action=2, sentiment_score=0.0)
    print("Decision:", result)
    
    # Another scenario: predictive is bearish (-0.3), RL says hold (1), sentiment is bearish (-0.5)
    result2 = meta.fuse_signals(predictive_signal=-0.3, rl_action=1, sentiment_score=-0.5)
    print("Decision:", result2)
