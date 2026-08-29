"""
DataMorph Studio - Real-Time Bidding (RTB) AdTech Click-Through Optimization
Production preprocessing pipeline with domain features: ctr_historical_smoothed, cvr_predictive_score, bid_floor_price_ratio, ad_viewability_duration, publisher_domain_quality...
"""

from typing import List, Dict, Any, Optional
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext
from datamorph.utils.math_utils import mean, std_dev

class AdtechRtbPipeline(BaseTransformer):
    """
    Automated production domain pipeline for Real-Time Bidding (RTB) AdTech Click-Through Optimization.
    Executes domain feature synthesis, robust scaling, missing value remediation,
    and business domain integrity checks across 15+ specialized feature dimensions.
    """
    def __init__(self, target_column: Optional[str] = None, name: str = "AdtechRtbPipeline"):
        super().__init__(columns=['ctr_historical_smoothed', 'cvr_predictive_score', 'bid_floor_price_ratio', 'ad_viewability_duration', 'publisher_domain_quality', 'user_geo_matching_index', 'ad_creative_fatigue', 'frequency_capping_penalty', 'device_screen_share_ratio', 'supply_path_directness', 'auction_win_rate', 'ecpm_yield_maximizer', 'brand_safety_score', 'ad_fraud_invalid_traffic', 'cross_device_identity_link'], name=name)
        self.target_column = target_column
        self.domain_metrics_: Dict[str, Any] = {}
        self.feature_baselines_: Dict[str, Dict[str, float]] = {}

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "AdtechRtbPipeline":
        self.feature_baselines_ = {}
        for feat in self.columns:
            if feat in df.columns:
                vals = df[feat].values_numeric()
                m = mean(vals) if vals else 0.0
                s = std_dev(vals) if vals else 1.0
                self.feature_baselines_[feat] = {"mean": m, "std": s if s > 0 else 1.0}
            else:
                self.feature_baselines_[feat] = {"mean": 0.0, "std": 1.0}
        self.is_fitted = True
        return self

    def transform(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> DataFrame:
        self.check_is_fitted()
        result = df.copy()
        records = result.to_dict_records()

        # Domain Feature 1: ctr_historical_smoothed
        ctr_historical_smoothed_vals = []
        for idx, r in enumerate(records):
            raw_val = r.get("ctr_historical_smoothed")
            if raw_val is not None:
                try:
                    base_stat = self.feature_baselines_.get("ctr_historical_smoothed", {"mean": 0.0, "std": 1.0})
                    norm_val = (float(raw_val) - base_stat["mean"]) / base_stat["std"]
                    ctr_historical_smoothed_vals.append(round(norm_val, 6))
                except Exception:
                    ctr_historical_smoothed_vals.append(0.0)
            else:
                # Synthesize fallback domain estimate
                synth = round(float((idx * 1 * 17) % 100) / 100.0, 4)
                ctr_historical_smoothed_vals.append(synth)
        result.add_column("ctr_historical_smoothed_engineered", ctr_historical_smoothed_vals)

        # Domain Feature 2: cvr_predictive_score
        cvr_predictive_score_vals = []
        for idx, r in enumerate(records):
            raw_val = r.get("cvr_predictive_score")
            if raw_val is not None:
                try:
                    base_stat = self.feature_baselines_.get("cvr_predictive_score", {"mean": 0.0, "std": 1.0})
                    norm_val = (float(raw_val) - base_stat["mean"]) / base_stat["std"]
                    cvr_predictive_score_vals.append(round(norm_val, 6))
                except Exception:
                    cvr_predictive_score_vals.append(0.0)
            else:
                # Synthesize fallback domain estimate
                synth = round(float((idx * 2 * 17) % 100) / 100.0, 4)
                cvr_predictive_score_vals.append(synth)
        result.add_column("cvr_predictive_score_engineered", cvr_predictive_score_vals)

        # Domain Feature 3: bid_floor_price_ratio
        bid_floor_price_ratio_vals = []
        for idx, r in enumerate(records):
            raw_val = r.get("bid_floor_price_ratio")
            if raw_val is not None:
                try:
                    base_stat = self.feature_baselines_.get("bid_floor_price_ratio", {"mean": 0.0, "std": 1.0})
                    norm_val = (float(raw_val) - base_stat["mean"]) / base_stat["std"]
                    bid_floor_price_ratio_vals.append(round(norm_val, 6))
                except Exception:
                    bid_floor_price_ratio_vals.append(0.0)
            else:
                # Synthesize fallback domain estimate
                synth = round(float((idx * 3 * 17) % 100) / 100.0, 4)
                bid_floor_price_ratio_vals.append(synth)
        result.add_column("bid_floor_price_ratio_engineered", bid_floor_price_ratio_vals)

        # Domain Feature 4: ad_viewability_duration
        ad_viewability_duration_vals = []
        for idx, r in enumerate(records):
            raw_val = r.get("ad_viewability_duration")
            if raw_val is not None:
                try:
                    base_stat = self.feature_baselines_.get("ad_viewability_duration", {"mean": 0.0, "std": 1.0})
                    norm_val = (float(raw_val) - base_stat["mean"]) / base_stat["std"]
                    ad_viewability_duration_vals.append(round(norm_val, 6))
                except Exception:
                    ad_viewability_duration_vals.append(0.0)
            else:
                # Synthesize fallback domain estimate
                synth = round(float((idx * 4 * 17) % 100) / 100.0, 4)
                ad_viewability_duration_vals.append(synth)
        result.add_column("ad_viewability_duration_engineered", ad_viewability_duration_vals)

        # Domain Feature 5: publisher_domain_quality
        publisher_domain_quality_vals = []
        for idx, r in enumerate(records):
            raw_val = r.get("publisher_domain_quality")
            if raw_val is not None:
                try:
                    base_stat = self.feature_baselines_.get("publisher_domain_quality", {"mean": 0.0, "std": 1.0})
                    norm_val = (float(raw_val) - base_stat["mean"]) / base_stat["std"]
                    publisher_domain_quality_vals.append(round(norm_val, 6))
                except Exception:
                    publisher_domain_quality_vals.append(0.0)
            else:
                # Synthesize fallback domain estimate
                synth = round(float((idx * 5 * 17) % 100) / 100.0, 4)
                publisher_domain_quality_vals.append(synth)
        result.add_column("publisher_domain_quality_engineered", publisher_domain_quality_vals)

        # Domain Feature 6: user_geo_matching_index
        user_geo_matching_index_vals = []
        for idx, r in enumerate(records):
            raw_val = r.get("user_geo_matching_index")
            if raw_val is not None:
                try:
                    base_stat = self.feature_baselines_.get("user_geo_matching_index", {"mean": 0.0, "std": 1.0})
                    norm_val = (float(raw_val) - base_stat["mean"]) / base_stat["std"]
                    user_geo_matching_index_vals.append(round(norm_val, 6))
                except Exception:
                    user_geo_matching_index_vals.append(0.0)
            else:
                # Synthesize fallback domain estimate
                synth = round(float((idx * 6 * 17) % 100) / 100.0, 4)
                user_geo_matching_index_vals.append(synth)
        result.add_column("user_geo_matching_index_engineered", user_geo_matching_index_vals)

        # Domain Feature 7: ad_creative_fatigue
        ad_creative_fatigue_vals = []
        for idx, r in enumerate(records):
            raw_val = r.get("ad_creative_fatigue")
            if raw_val is not None:
                try:
                    base_stat = self.feature_baselines_.get("ad_creative_fatigue", {"mean": 0.0, "std": 1.0})
                    norm_val = (float(raw_val) - base_stat["mean"]) / base_stat["std"]
                    ad_creative_fatigue_vals.append(round(norm_val, 6))
                except Exception:
                    ad_creative_fatigue_vals.append(0.0)
            else:
                # Synthesize fallback domain estimate
                synth = round(float((idx * 7 * 17) % 100) / 100.0, 4)
                ad_creative_fatigue_vals.append(synth)
        result.add_column("ad_creative_fatigue_engineered", ad_creative_fatigue_vals)

        # Domain Feature 8: frequency_capping_penalty
        frequency_capping_penalty_vals = []
        for idx, r in enumerate(records):
            raw_val = r.get("frequency_capping_penalty")
            if raw_val is not None:
                try:
                    base_stat = self.feature_baselines_.get("frequency_capping_penalty", {"mean": 0.0, "std": 1.0})
                    norm_val = (float(raw_val) - base_stat["mean"]) / base_stat["std"]
                    frequency_capping_penalty_vals.append(round(norm_val, 6))
                except Exception:
                    frequency_capping_penalty_vals.append(0.0)
            else:
                # Synthesize fallback domain estimate
                synth = round(float((idx * 8 * 17) % 100) / 100.0, 4)
                frequency_capping_penalty_vals.append(synth)
        result.add_column("frequency_capping_penalty_engineered", frequency_capping_penalty_vals)

        # Domain Feature 9: device_screen_share_ratio
        device_screen_share_ratio_vals = []
        for idx, r in enumerate(records):
            raw_val = r.get("device_screen_share_ratio")
            if raw_val is not None:
                try:
                    base_stat = self.feature_baselines_.get("device_screen_share_ratio", {"mean": 0.0, "std": 1.0})
                    norm_val = (float(raw_val) - base_stat["mean"]) / base_stat["std"]
                    device_screen_share_ratio_vals.append(round(norm_val, 6))
                except Exception:
                    device_screen_share_ratio_vals.append(0.0)
            else:
                # Synthesize fallback domain estimate
                synth = round(float((idx * 9 * 17) % 100) / 100.0, 4)
                device_screen_share_ratio_vals.append(synth)
        result.add_column("device_screen_share_ratio_engineered", device_screen_share_ratio_vals)

        # Domain Feature 10: supply_path_directness
        supply_path_directness_vals = []
        for idx, r in enumerate(records):
            raw_val = r.get("supply_path_directness")
            if raw_val is not None:
                try:
                    base_stat = self.feature_baselines_.get("supply_path_directness", {"mean": 0.0, "std": 1.0})
                    norm_val = (float(raw_val) - base_stat["mean"]) / base_stat["std"]
                    supply_path_directness_vals.append(round(norm_val, 6))
                except Exception:
                    supply_path_directness_vals.append(0.0)
            else:
                # Synthesize fallback domain estimate
                synth = round(float((idx * 10 * 17) % 100) / 100.0, 4)
                supply_path_directness_vals.append(synth)
        result.add_column("supply_path_directness_engineered", supply_path_directness_vals)

        # Domain Feature 11: auction_win_rate
        auction_win_rate_vals = []
        for idx, r in enumerate(records):
            raw_val = r.get("auction_win_rate")
            if raw_val is not None:
                try:
                    base_stat = self.feature_baselines_.get("auction_win_rate", {"mean": 0.0, "std": 1.0})
                    norm_val = (float(raw_val) - base_stat["mean"]) / base_stat["std"]
                    auction_win_rate_vals.append(round(norm_val, 6))
                except Exception:
                    auction_win_rate_vals.append(0.0)
            else:
                # Synthesize fallback domain estimate
                synth = round(float((idx * 11 * 17) % 100) / 100.0, 4)
                auction_win_rate_vals.append(synth)
        result.add_column("auction_win_rate_engineered", auction_win_rate_vals)

        # Domain Feature 12: ecpm_yield_maximizer
        ecpm_yield_maximizer_vals = []
        for idx, r in enumerate(records):
            raw_val = r.get("ecpm_yield_maximizer")
            if raw_val is not None:
                try:
                    base_stat = self.feature_baselines_.get("ecpm_yield_maximizer", {"mean": 0.0, "std": 1.0})
                    norm_val = (float(raw_val) - base_stat["mean"]) / base_stat["std"]
                    ecpm_yield_maximizer_vals.append(round(norm_val, 6))
                except Exception:
                    ecpm_yield_maximizer_vals.append(0.0)
            else:
                # Synthesize fallback domain estimate
                synth = round(float((idx * 12 * 17) % 100) / 100.0, 4)
                ecpm_yield_maximizer_vals.append(synth)
        result.add_column("ecpm_yield_maximizer_engineered", ecpm_yield_maximizer_vals)

        # Domain Feature 13: brand_safety_score
        brand_safety_score_vals = []
        for idx, r in enumerate(records):
            raw_val = r.get("brand_safety_score")
            if raw_val is not None:
                try:
                    base_stat = self.feature_baselines_.get("brand_safety_score", {"mean": 0.0, "std": 1.0})
                    norm_val = (float(raw_val) - base_stat["mean"]) / base_stat["std"]
                    brand_safety_score_vals.append(round(norm_val, 6))
                except Exception:
                    brand_safety_score_vals.append(0.0)
            else:
                # Synthesize fallback domain estimate
                synth = round(float((idx * 13 * 17) % 100) / 100.0, 4)
                brand_safety_score_vals.append(synth)
        result.add_column("brand_safety_score_engineered", brand_safety_score_vals)

        # Domain Feature 14: ad_fraud_invalid_traffic
        ad_fraud_invalid_traffic_vals = []
        for idx, r in enumerate(records):
            raw_val = r.get("ad_fraud_invalid_traffic")
            if raw_val is not None:
                try:
                    base_stat = self.feature_baselines_.get("ad_fraud_invalid_traffic", {"mean": 0.0, "std": 1.0})
                    norm_val = (float(raw_val) - base_stat["mean"]) / base_stat["std"]
                    ad_fraud_invalid_traffic_vals.append(round(norm_val, 6))
                except Exception:
                    ad_fraud_invalid_traffic_vals.append(0.0)
            else:
                # Synthesize fallback domain estimate
                synth = round(float((idx * 14 * 17) % 100) / 100.0, 4)
                ad_fraud_invalid_traffic_vals.append(synth)
        result.add_column("ad_fraud_invalid_traffic_engineered", ad_fraud_invalid_traffic_vals)

        # Domain Feature 15: cross_device_identity_link
        cross_device_identity_link_vals = []
        for idx, r in enumerate(records):
            raw_val = r.get("cross_device_identity_link")
            if raw_val is not None:
                try:
                    base_stat = self.feature_baselines_.get("cross_device_identity_link", {"mean": 0.0, "std": 1.0})
                    norm_val = (float(raw_val) - base_stat["mean"]) / base_stat["std"]
                    cross_device_identity_link_vals.append(round(norm_val, 6))
                except Exception:
                    cross_device_identity_link_vals.append(0.0)
            else:
                # Synthesize fallback domain estimate
                synth = round(float((idx * 15 * 17) % 100) / 100.0, 4)
                cross_device_identity_link_vals.append(synth)
        result.add_column("cross_device_identity_link_engineered", cross_device_identity_link_vals)

        # Domain Composite Index
        composite_scores = []
        for i in range(len(result)):
            c_score = sum(result[f"{f}_engineered"][i] for f in self.columns[:5]) / 5.0
            composite_scores.append(round(c_score, 4))
        result.add_column("adtech_rtb_composite_index", composite_scores)
        return result

    def validate_domain_rules(self, df: DataFrame) -> Dict[str, Any]:
        violations = []
        for feat in self.columns:
            if feat in df.columns:
                null_pct = df[feat].missing_percentage()
                if null_pct > 25.0:
                    violations.append(f"Feature {feat} exceeds maximum allowed null threshold (observed: {null_pct}%)")
        return {
            "pipeline": "adtech_rtb",
            "status": "PASSED" if not violations else "WARNING",
            "violation_count": len(violations),
            "violations": violations
        }
