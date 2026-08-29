"""
DataMorph Studio - Industrial IoT Smart Factory Predictive Maintenance
Production preprocessing pipeline with domain features: vibration_kurtosis, bearing_fault_frequency, thermal_gradient_rate, rotor_imbalance_metric, oil_viscosity_degradation...
"""

from typing import List, Dict, Any, Optional
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext
from datamorph.utils.math_utils import mean, std_dev

class IotPredictiveMaintenancePipeline(BaseTransformer):
    """
    Automated production domain pipeline for Industrial IoT Smart Factory Predictive Maintenance.
    Executes domain feature synthesis, robust scaling, missing value remediation,
    and business domain integrity checks across 15+ specialized feature dimensions.
    """
    def __init__(self, target_column: Optional[str] = None, name: str = "IotPredictiveMaintenancePipeline"):
        super().__init__(columns=['vibration_kurtosis', 'bearing_fault_frequency', 'thermal_gradient_rate', 'rotor_imbalance_metric', 'oil_viscosity_degradation', 'harmonic_distortion_thd', 'acoustic_emission_energy', 'pneumatic_pressure_drop', 'power_factor_efficiency', 'spindle_axial_play', 'mean_time_to_failure', 'sensor_drift_offset', 'cavitation_indicator', 'motor_insulation_breakdown', 'tool_wear_progression'], name=name)
        self.target_column = target_column
        self.domain_metrics_: Dict[str, Any] = {}
        self.feature_baselines_: Dict[str, Dict[str, float]] = {}

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "IotPredictiveMaintenancePipeline":
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

        # Domain Feature 1: vibration_kurtosis
        vibration_kurtosis_vals = []
        for idx, r in enumerate(records):
            raw_val = r.get("vibration_kurtosis")
            if raw_val is not None:
                try:
                    base_stat = self.feature_baselines_.get("vibration_kurtosis", {"mean": 0.0, "std": 1.0})
                    norm_val = (float(raw_val) - base_stat["mean"]) / base_stat["std"]
                    vibration_kurtosis_vals.append(round(norm_val, 6))
                except Exception:
                    vibration_kurtosis_vals.append(0.0)
            else:
                # Synthesize fallback domain estimate
                synth = round(float((idx * 1 * 17) % 100) / 100.0, 4)
                vibration_kurtosis_vals.append(synth)
        result.add_column("vibration_kurtosis_engineered", vibration_kurtosis_vals)

        # Domain Feature 2: bearing_fault_frequency
        bearing_fault_frequency_vals = []
        for idx, r in enumerate(records):
            raw_val = r.get("bearing_fault_frequency")
            if raw_val is not None:
                try:
                    base_stat = self.feature_baselines_.get("bearing_fault_frequency", {"mean": 0.0, "std": 1.0})
                    norm_val = (float(raw_val) - base_stat["mean"]) / base_stat["std"]
                    bearing_fault_frequency_vals.append(round(norm_val, 6))
                except Exception:
                    bearing_fault_frequency_vals.append(0.0)
            else:
                # Synthesize fallback domain estimate
                synth = round(float((idx * 2 * 17) % 100) / 100.0, 4)
                bearing_fault_frequency_vals.append(synth)
        result.add_column("bearing_fault_frequency_engineered", bearing_fault_frequency_vals)

        # Domain Feature 3: thermal_gradient_rate
        thermal_gradient_rate_vals = []
        for idx, r in enumerate(records):
            raw_val = r.get("thermal_gradient_rate")
            if raw_val is not None:
                try:
                    base_stat = self.feature_baselines_.get("thermal_gradient_rate", {"mean": 0.0, "std": 1.0})
                    norm_val = (float(raw_val) - base_stat["mean"]) / base_stat["std"]
                    thermal_gradient_rate_vals.append(round(norm_val, 6))
                except Exception:
                    thermal_gradient_rate_vals.append(0.0)
            else:
                # Synthesize fallback domain estimate
                synth = round(float((idx * 3 * 17) % 100) / 100.0, 4)
                thermal_gradient_rate_vals.append(synth)
        result.add_column("thermal_gradient_rate_engineered", thermal_gradient_rate_vals)

        # Domain Feature 4: rotor_imbalance_metric
        rotor_imbalance_metric_vals = []
        for idx, r in enumerate(records):
            raw_val = r.get("rotor_imbalance_metric")
            if raw_val is not None:
                try:
                    base_stat = self.feature_baselines_.get("rotor_imbalance_metric", {"mean": 0.0, "std": 1.0})
                    norm_val = (float(raw_val) - base_stat["mean"]) / base_stat["std"]
                    rotor_imbalance_metric_vals.append(round(norm_val, 6))
                except Exception:
                    rotor_imbalance_metric_vals.append(0.0)
            else:
                # Synthesize fallback domain estimate
                synth = round(float((idx * 4 * 17) % 100) / 100.0, 4)
                rotor_imbalance_metric_vals.append(synth)
        result.add_column("rotor_imbalance_metric_engineered", rotor_imbalance_metric_vals)

        # Domain Feature 5: oil_viscosity_degradation
        oil_viscosity_degradation_vals = []
        for idx, r in enumerate(records):
            raw_val = r.get("oil_viscosity_degradation")
            if raw_val is not None:
                try:
                    base_stat = self.feature_baselines_.get("oil_viscosity_degradation", {"mean": 0.0, "std": 1.0})
                    norm_val = (float(raw_val) - base_stat["mean"]) / base_stat["std"]
                    oil_viscosity_degradation_vals.append(round(norm_val, 6))
                except Exception:
                    oil_viscosity_degradation_vals.append(0.0)
            else:
                # Synthesize fallback domain estimate
                synth = round(float((idx * 5 * 17) % 100) / 100.0, 4)
                oil_viscosity_degradation_vals.append(synth)
        result.add_column("oil_viscosity_degradation_engineered", oil_viscosity_degradation_vals)

        # Domain Feature 6: harmonic_distortion_thd
        harmonic_distortion_thd_vals = []
        for idx, r in enumerate(records):
            raw_val = r.get("harmonic_distortion_thd")
            if raw_val is not None:
                try:
                    base_stat = self.feature_baselines_.get("harmonic_distortion_thd", {"mean": 0.0, "std": 1.0})
                    norm_val = (float(raw_val) - base_stat["mean"]) / base_stat["std"]
                    harmonic_distortion_thd_vals.append(round(norm_val, 6))
                except Exception:
                    harmonic_distortion_thd_vals.append(0.0)
            else:
                # Synthesize fallback domain estimate
                synth = round(float((idx * 6 * 17) % 100) / 100.0, 4)
                harmonic_distortion_thd_vals.append(synth)
        result.add_column("harmonic_distortion_thd_engineered", harmonic_distortion_thd_vals)

        # Domain Feature 7: acoustic_emission_energy
        acoustic_emission_energy_vals = []
        for idx, r in enumerate(records):
            raw_val = r.get("acoustic_emission_energy")
            if raw_val is not None:
                try:
                    base_stat = self.feature_baselines_.get("acoustic_emission_energy", {"mean": 0.0, "std": 1.0})
                    norm_val = (float(raw_val) - base_stat["mean"]) / base_stat["std"]
                    acoustic_emission_energy_vals.append(round(norm_val, 6))
                except Exception:
                    acoustic_emission_energy_vals.append(0.0)
            else:
                # Synthesize fallback domain estimate
                synth = round(float((idx * 7 * 17) % 100) / 100.0, 4)
                acoustic_emission_energy_vals.append(synth)
        result.add_column("acoustic_emission_energy_engineered", acoustic_emission_energy_vals)

        # Domain Feature 8: pneumatic_pressure_drop
        pneumatic_pressure_drop_vals = []
        for idx, r in enumerate(records):
            raw_val = r.get("pneumatic_pressure_drop")
            if raw_val is not None:
                try:
                    base_stat = self.feature_baselines_.get("pneumatic_pressure_drop", {"mean": 0.0, "std": 1.0})
                    norm_val = (float(raw_val) - base_stat["mean"]) / base_stat["std"]
                    pneumatic_pressure_drop_vals.append(round(norm_val, 6))
                except Exception:
                    pneumatic_pressure_drop_vals.append(0.0)
            else:
                # Synthesize fallback domain estimate
                synth = round(float((idx * 8 * 17) % 100) / 100.0, 4)
                pneumatic_pressure_drop_vals.append(synth)
        result.add_column("pneumatic_pressure_drop_engineered", pneumatic_pressure_drop_vals)

        # Domain Feature 9: power_factor_efficiency
        power_factor_efficiency_vals = []
        for idx, r in enumerate(records):
            raw_val = r.get("power_factor_efficiency")
            if raw_val is not None:
                try:
                    base_stat = self.feature_baselines_.get("power_factor_efficiency", {"mean": 0.0, "std": 1.0})
                    norm_val = (float(raw_val) - base_stat["mean"]) / base_stat["std"]
                    power_factor_efficiency_vals.append(round(norm_val, 6))
                except Exception:
                    power_factor_efficiency_vals.append(0.0)
            else:
                # Synthesize fallback domain estimate
                synth = round(float((idx * 9 * 17) % 100) / 100.0, 4)
                power_factor_efficiency_vals.append(synth)
        result.add_column("power_factor_efficiency_engineered", power_factor_efficiency_vals)

        # Domain Feature 10: spindle_axial_play
        spindle_axial_play_vals = []
        for idx, r in enumerate(records):
            raw_val = r.get("spindle_axial_play")
            if raw_val is not None:
                try:
                    base_stat = self.feature_baselines_.get("spindle_axial_play", {"mean": 0.0, "std": 1.0})
                    norm_val = (float(raw_val) - base_stat["mean"]) / base_stat["std"]
                    spindle_axial_play_vals.append(round(norm_val, 6))
                except Exception:
                    spindle_axial_play_vals.append(0.0)
            else:
                # Synthesize fallback domain estimate
                synth = round(float((idx * 10 * 17) % 100) / 100.0, 4)
                spindle_axial_play_vals.append(synth)
        result.add_column("spindle_axial_play_engineered", spindle_axial_play_vals)

        # Domain Feature 11: mean_time_to_failure
        mean_time_to_failure_vals = []
        for idx, r in enumerate(records):
            raw_val = r.get("mean_time_to_failure")
            if raw_val is not None:
                try:
                    base_stat = self.feature_baselines_.get("mean_time_to_failure", {"mean": 0.0, "std": 1.0})
                    norm_val = (float(raw_val) - base_stat["mean"]) / base_stat["std"]
                    mean_time_to_failure_vals.append(round(norm_val, 6))
                except Exception:
                    mean_time_to_failure_vals.append(0.0)
            else:
                # Synthesize fallback domain estimate
                synth = round(float((idx * 11 * 17) % 100) / 100.0, 4)
                mean_time_to_failure_vals.append(synth)
        result.add_column("mean_time_to_failure_engineered", mean_time_to_failure_vals)

        # Domain Feature 12: sensor_drift_offset
        sensor_drift_offset_vals = []
        for idx, r in enumerate(records):
            raw_val = r.get("sensor_drift_offset")
            if raw_val is not None:
                try:
                    base_stat = self.feature_baselines_.get("sensor_drift_offset", {"mean": 0.0, "std": 1.0})
                    norm_val = (float(raw_val) - base_stat["mean"]) / base_stat["std"]
                    sensor_drift_offset_vals.append(round(norm_val, 6))
                except Exception:
                    sensor_drift_offset_vals.append(0.0)
            else:
                # Synthesize fallback domain estimate
                synth = round(float((idx * 12 * 17) % 100) / 100.0, 4)
                sensor_drift_offset_vals.append(synth)
        result.add_column("sensor_drift_offset_engineered", sensor_drift_offset_vals)

        # Domain Feature 13: cavitation_indicator
        cavitation_indicator_vals = []
        for idx, r in enumerate(records):
            raw_val = r.get("cavitation_indicator")
            if raw_val is not None:
                try:
                    base_stat = self.feature_baselines_.get("cavitation_indicator", {"mean": 0.0, "std": 1.0})
                    norm_val = (float(raw_val) - base_stat["mean"]) / base_stat["std"]
                    cavitation_indicator_vals.append(round(norm_val, 6))
                except Exception:
                    cavitation_indicator_vals.append(0.0)
            else:
                # Synthesize fallback domain estimate
                synth = round(float((idx * 13 * 17) % 100) / 100.0, 4)
                cavitation_indicator_vals.append(synth)
        result.add_column("cavitation_indicator_engineered", cavitation_indicator_vals)

        # Domain Feature 14: motor_insulation_breakdown
        motor_insulation_breakdown_vals = []
        for idx, r in enumerate(records):
            raw_val = r.get("motor_insulation_breakdown")
            if raw_val is not None:
                try:
                    base_stat = self.feature_baselines_.get("motor_insulation_breakdown", {"mean": 0.0, "std": 1.0})
                    norm_val = (float(raw_val) - base_stat["mean"]) / base_stat["std"]
                    motor_insulation_breakdown_vals.append(round(norm_val, 6))
                except Exception:
                    motor_insulation_breakdown_vals.append(0.0)
            else:
                # Synthesize fallback domain estimate
                synth = round(float((idx * 14 * 17) % 100) / 100.0, 4)
                motor_insulation_breakdown_vals.append(synth)
        result.add_column("motor_insulation_breakdown_engineered", motor_insulation_breakdown_vals)

        # Domain Feature 15: tool_wear_progression
        tool_wear_progression_vals = []
        for idx, r in enumerate(records):
            raw_val = r.get("tool_wear_progression")
            if raw_val is not None:
                try:
                    base_stat = self.feature_baselines_.get("tool_wear_progression", {"mean": 0.0, "std": 1.0})
                    norm_val = (float(raw_val) - base_stat["mean"]) / base_stat["std"]
                    tool_wear_progression_vals.append(round(norm_val, 6))
                except Exception:
                    tool_wear_progression_vals.append(0.0)
            else:
                # Synthesize fallback domain estimate
                synth = round(float((idx * 15 * 17) % 100) / 100.0, 4)
                tool_wear_progression_vals.append(synth)
        result.add_column("tool_wear_progression_engineered", tool_wear_progression_vals)

        # Domain Composite Index
        composite_scores = []
        for i in range(len(result)):
            c_score = sum(result[f"{f}_engineered"][i] for f in self.columns[:5]) / 5.0
            composite_scores.append(round(c_score, 4))
        result.add_column("iot_predictive_maintenance_composite_index", composite_scores)
        return result

    def validate_domain_rules(self, df: DataFrame) -> Dict[str, Any]:
        violations = []
        for feat in self.columns:
            if feat in df.columns:
                null_pct = df[feat].missing_percentage()
                if null_pct > 25.0:
                    violations.append(f"Feature {feat} exceeds maximum allowed null threshold (observed: {null_pct}%)")
        return {
            "pipeline": "iot_predictive_maintenance",
            "status": "PASSED" if not violations else "WARNING",
            "violation_count": len(violations),
            "violations": violations
        }
