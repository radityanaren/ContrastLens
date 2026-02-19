class ContrastLensConfig:
    @staticmethod
    def get_parameters(contrast, mode):
        if mode == "high":
            return {
                "contrast_gain": 1.0 + contrast * 4.0,
                "probability_gamma": 0.6
            }
        else:
            return {
                "contrast_gain": 1.0 + contrast * 1.5,
                "probability_gamma": 1.0
            }
