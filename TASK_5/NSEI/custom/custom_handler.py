from qlib.data.dataset.handler import DataHandlerLP
from qlib.data.dataset.processor import DropnaProcessor, Fillna, CSZScoreNorm, DropnaLabel, ZScoreNorm

class CustomHandler(DataHandlerLP):
    def __init__(
        self,
        instruments,
        start_time,
        end_time,
        fit_start_time,  # Used for processor fitting period
        fit_end_time,    # Used for processor fitting period  
        feature_conf,
        infer_processors=None,
        learn_processors=None,
        **kwargs
    ):
        self.feature_conf = feature_conf
        
        # 1. Configure data loader (MUST HAVE)
        data_loader = {
            "class": "QlibDataLoader",
            "kwargs": {
                "config": {
                    "feature": self.get_feature_config(),
                    "label": self.get_label_config(),
                },
                "freq": "day",
            },
        }

        # 2. Set processors (CRUCIAL for data normalization)
        infer_processors = infer_processors or [
            # Fillna(),
            # ZScoreNorm(
            #     fit_start_time=fit_start_time,
            #     fit_end_time=fit_end_time
            # )
        ]
        
        learn_processors = learn_processors or [
            # DropnaLabel()
        ]
        
        # 3. Proper initialization (DO NOT pass fit_*_time to super())
        super().__init__(
            instruments=instruments,
            start_time=start_time,
            end_time=end_time,
            data_loader=data_loader,
            infer_processors=infer_processors,
            learn_processors=learn_processors,
            **kwargs
        )

    def get_feature_config(self):
        features = []
        names = []
        for group_name, group_config in self.feature_conf.items():
            for expr in group_config["feature"]:
                # Use pre-formatted expressions with $ prefixes
                features.append(expr)
                names.append(f"{group_name}_{expr[:15]}".replace(" ", "").replace("$", ""))
        
        print("Final feature expressions:", features)
        print("Feature names:", names)
        return (features, names)

    def get_label_config(self):
        # Return a tuple of (list of expressions, list of names)
        #TODO: add % return: #Ref($close, -1)/Ref($close) - 1: 
        #2d= 100, 1d=110, 0d=120: 
        #return = 100/110 - 1 = -0.09
        #return = 110/120 - 1 = -0.0833
        return (
            ["Ref($close, -1)"],
            ["NEXT_CLOSE"]
        )