import cv2
import numpy as np

from contrastlens.config import ContrastLensConfig


class ContrastLens:
    @staticmethod
    def rgb_to_luminance(image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY).astype(np.float32)
        return gray / 255.0

    @staticmethod
    def adaptive_contrast(gray, strength):
        """
        Contrast expansion centered around midtones.
        strength > 1.0  -> stronger contrast
        strength < 1.0  -> softer contrast
        """
        gray = np.clip(gray, 1e-6, 1.0)
        mid = 0.5
        return np.clip(mid + (gray - mid) * strength, 0.0, 1.0)

    @staticmethod
    def tone_to_probability(gray, params):
        # Adaptive contrast (single dominant control)
        gray = ContrastLens.adaptive_contrast(gray, params["contrast_gain"])

        # Shadow emphasis only (no highlight punishment)
        p = 1.0 - gray

        # Gentle shaping
        p = np.power(p, params["probability_gamma"])

        # Clean whites: hard clamp
        p[gray > 0.95] = 0.0

        return np.clip(p, 0.0, 1.0)

    @staticmethod
    def stochastic_sampling(probability):
        rnd = np.random.rand(*probability.shape)
        return (rnd < probability).astype(np.uint8)

    @staticmethod
    def process(image, contrast, mode):
        params = ContrastLensConfig.get_parameters(contrast, mode)

        gray = ContrastLens.rgb_to_luminance(image)

        probability = ContrastLens.tone_to_probability(gray, params)

        mask = ContrastLens.stochastic_sampling(probability)

        return np.where(mask == 1, 0, 255).astype(np.uint8)
