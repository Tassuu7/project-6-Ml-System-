"""
DataMorph Studio - Supply Chain Demand Forecasting & Inventory Logistics
Production preprocessing pipeline with domain features: lead_time_variability, safety_stock_depletion, bullwhip_effect_ratio, supplier_on_time_otif, order_fill_rate...
"""

from typing import List, Dict, Any, Optional
from datamorph.transformers.base import BaseTransformer
from datamorph.core.dataframe import DataFrame
from datamorph.core.context import ExecutionContext
from datamorph.utils.math_utils import mean, std_dev

class SupplyChainErpPipeline(BaseTransformer):
    """
    Automated production domain pipeline for Supply Chain Demand Forecasting & Inventory Logistics.
    Executes domain feature synthesis, robust scaling, missing value remediation,
    and business domain integrity checks across 15+ specialized feature dimensions.
    """
    def __init__(self, target_column: Optional[str] = None, name: str = "SupplyChainErpPipeline"):
        super().__init__(columns=['lead_time_variability', 'safety_stock_depletion', 'bullwhip_effect_ratio', 'supplier_on_time_otif', 'order_fill_rate', 'carrying_cost_percentage', 'reorder_point_optimum', 'freight_cost_per_ton_mile', 'warehouse_slotting_util', 'stockout_probability', 'container_cube_utilization', 'customs_clearance_delay', 'perishable_shelf_life_decay', 'carbon_emission_per_shipment', 'vendor_compliance_score'], name=name)
        self.target_column = target_column
        self.domain_metrics_: Dict[str, Any] = {}
        self.feature_baselines_: Dict[str, Dict[str, float]] = {}

    def fit(self, df: DataFrame, context: Optional[ExecutionContext] = None) -> "SupplyChainErpPipeline":
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

        # Domain Feature 1: lead_time_variability
        lead_time_variability_vals = []
        for idx, r in enumerate(records):
            raw_val = r.get("lead_time_variability")
            if raw_val is not None:
                try:
                    base_stat = self.feature_baselines_.get("lead_time_variability", {"mean": 0.0, "std": 1.0})
                    norm_val = (float(raw_val) - base_stat["mean"]) / base_stat["std"]
                    lead_time_variability_vals.append(round(norm_val, 6))
                except Exception:
                    lead_time_variability_vals.append(0.0)
            else:
                # Synthesize fallback domain estimate
                synth = round(float((idx * 1 * 17) % 100) / 100.0, 4)
                lead_time_variability_vals.append(synth)
        result.add_column("lead_time_variability_engineered", lead_time_variability_vals)

        # Domain Feature 2: safety_stock_depletion
        safety_stock_depletion_vals = []
        for idx, r in enumerate(records):
            raw_val = r.get("safety_stock_depletion")
            if raw_val is not None:
                try:
                    base_stat = self.feature_baselines_.get("safety_stock_depletion", {"mean": 0.0, "std": 1.0})
                    norm_val = (float(raw_val) - base_stat["mean"]) / base_stat["std"]
                    safety_stock_depletion_vals.append(round(norm_val, 6))
                except Exception:
                    safety_stock_depletion_vals.append(0.0)
            else:
                # Synthesize fallback domain estimate
                synth = round(float((idx * 2 * 17) % 100) / 100.0, 4)
                safety_stock_depletion_vals.append(synth)
        result.add_column("safety_stock_depletion_engineered", safety_stock_depletion_vals)

        # Domain Feature 3: bullwhip_effect_ratio
        bullwhip_effect_ratio_vals = []
        for idx, r in enumerate(records):
            raw_val = r.get("bullwhip_effect_ratio")
            if raw_val is not None:
                try:
                    base_stat = self.feature_baselines_.get("bullwhip_effect_ratio", {"mean": 0.0, "std": 1.0})
                    norm_val = (float(raw_val) - base_stat["mean"]) / base_stat["std"]
                    bullwhip_effect_ratio_vals.append(round(norm_val, 6))
                except Exception:
                    bullwhip_effect_ratio_vals.append(0.0)
            else:
                # Synthesize fallback domain estimate
                synth = round(float((idx * 3 * 17) % 100) / 100.0, 4)
                bullwhip_effect_ratio_vals.append(synth)
        result.add_column("bullwhip_effect_ratio_engineered", bullwhip_effect_ratio_vals)

        # Domain Feature 4: supplier_on_time_otif
        supplier_on_time_otif_vals = []
        for idx, r in enumerate(records):
            raw_val = r.get("supplier_on_time_otif")
            if raw_val is not None:
                try:
                    base_stat = self.feature_baselines_.get("supplier_on_time_otif", {"mean": 0.0, "std": 1.0})
                    norm_val = (float(raw_val) - base_stat["mean"]) / base_stat["std"]
                    supplier_on_time_otif_vals.append(round(norm_val, 6))
                except Exception:
                    supplier_on_time_otif_vals.append(0.0)
            else:
                # Synthesize fallback domain estimate
                synth = round(float((idx * 4 * 17) % 100) / 100.0, 4)
                supplier_on_time_otif_vals.append(synth)
        result.add_column("supplier_on_time_otif_engineered", supplier_on_time_otif_vals)

        # Domain Feature 5: order_fill_rate
        order_fill_rate_vals = []
        for idx, r in enumerate(records):
            raw_val = r.get("order_fill_rate")
            if raw_val is not None:
                try:
                    base_stat = self.feature_baselines_.get("order_fill_rate", {"mean": 0.0, "std": 1.0})
                    norm_val = (float(raw_val) - base_stat["mean"]) / base_stat["std"]
                    order_fill_rate_vals.append(round(norm_val, 6))
                except Exception:
                    order_fill_rate_vals.append(0.0)
            else:
                # Synthesize fallback domain estimate
                synth = round(float((idx * 5 * 17) % 100) / 100.0, 4)
                order_fill_rate_vals.append(synth)
        result.add_column("order_fill_rate_engineered", order_fill_rate_vals)

        # Domain Feature 6: carrying_cost_percentage
        carrying_cost_percentage_vals = []
        for idx, r in enumerate(records):
            raw_val = r.get("carrying_cost_percentage")
            if raw_val is not None:
                try:
                    base_stat = self.feature_baselines_.get("carrying_cost_percentage", {"mean": 0.0, "std": 1.0})
                    norm_val = (float(raw_val) - base_stat["mean"]) / base_stat["std"]
                    carrying_cost_percentage_vals.append(round(norm_val, 6))
                except Exception:
                    carrying_cost_percentage_vals.append(0.0)
            else:
                # Synthesize fallback domain estimate
                synth = round(float((idx * 6 * 17) % 100) / 100.0, 4)
                carrying_cost_percentage_vals.append(synth)
        result.add_column("carrying_cost_percentage_engineered", carrying_cost_percentage_vals)

        # Domain Feature 7: reorder_point_optimum
        reorder_point_optimum_vals = []
        for idx, r in enumerate(records):
            raw_val = r.get("reorder_point_optimum")
            if raw_val is not None:
                try:
                    base_stat = self.feature_baselines_.get("reorder_point_optimum", {"mean": 0.0, "std": 1.0})
                    norm_val = (float(raw_val) - base_stat["mean"]) / base_stat["std"]
                    reorder_point_optimum_vals.append(round(norm_val, 6))
                except Exception:
                    reorder_point_optimum_vals.append(0.0)
            else:
                # Synthesize fallback domain estimate
                synth = round(float((idx * 7 * 17) % 100) / 100.0, 4)
                reorder_point_optimum_vals.append(synth)
        result.add_column("reorder_point_optimum_engineered", reorder_point_optimum_vals)

        # Domain Feature 8: freight_cost_per_ton_mile
        freight_cost_per_ton_mile_vals = []
        for idx, r in enumerate(records):
            raw_val = r.get("freight_cost_per_ton_mile")
            if raw_val is not None:
                try:
                    base_stat = self.feature_baselines_.get("freight_cost_per_ton_mile", {"mean": 0.0, "std": 1.0})
                    norm_val = (float(raw_val) - base_stat["mean"]) / base_stat["std"]
                    freight_cost_per_ton_mile_vals.append(round(norm_val, 6))
                except Exception:
                    freight_cost_per_ton_mile_vals.append(0.0)
            else:
                # Synthesize fallback domain estimate
                synth = round(float((idx * 8 * 17) % 100) / 100.0, 4)
                freight_cost_per_ton_mile_vals.append(synth)
        result.add_column("freight_cost_per_ton_mile_engineered", freight_cost_per_ton_mile_vals)

        # Domain Feature 9: warehouse_slotting_util
        warehouse_slotting_util_vals = []
        for idx, r in enumerate(records):
            raw_val = r.get("warehouse_slotting_util")
            if raw_val is not None:
                try:
                    base_stat = self.feature_baselines_.get("warehouse_slotting_util", {"mean": 0.0, "std": 1.0})
                    norm_val = (float(raw_val) - base_stat["mean"]) / base_stat["std"]
                    warehouse_slotting_util_vals.append(round(norm_val, 6))
                except Exception:
                    warehouse_slotting_util_vals.append(0.0)
            else:
                # Synthesize fallback domain estimate
                synth = round(float((idx * 9 * 17) % 100) / 100.0, 4)
                warehouse_slotting_util_vals.append(synth)
        result.add_column("warehouse_slotting_util_engineered", warehouse_slotting_util_vals)

        # Domain Feature 10: stockout_probability
        stockout_probability_vals = []
        for idx, r in enumerate(records):
            raw_val = r.get("stockout_probability")
            if raw_val is not None:
                try:
                    base_stat = self.feature_baselines_.get("stockout_probability", {"mean": 0.0, "std": 1.0})
                    norm_val = (float(raw_val) - base_stat["mean"]) / base_stat["std"]
                    stockout_probability_vals.append(round(norm_val, 6))
                except Exception:
                    stockout_probability_vals.append(0.0)
            else:
                # Synthesize fallback domain estimate
                synth = round(float((idx * 10 * 17) % 100) / 100.0, 4)
                stockout_probability_vals.append(synth)
        result.add_column("stockout_probability_engineered", stockout_probability_vals)

        # Domain Feature 11: container_cube_utilization
        container_cube_utilization_vals = []
        for idx, r in enumerate(records):
            raw_val = r.get("container_cube_utilization")
            if raw_val is not None:
                try:
                    base_stat = self.feature_baselines_.get("container_cube_utilization", {"mean": 0.0, "std": 1.0})
                    norm_val = (float(raw_val) - base_stat["mean"]) / base_stat["std"]
                    container_cube_utilization_vals.append(round(norm_val, 6))
                except Exception:
                    container_cube_utilization_vals.append(0.0)
            else:
                # Synthesize fallback domain estimate
                synth = round(float((idx * 11 * 17) % 100) / 100.0, 4)
                container_cube_utilization_vals.append(synth)
        result.add_column("container_cube_utilization_engineered", container_cube_utilization_vals)

        # Domain Feature 12: customs_clearance_delay
        customs_clearance_delay_vals = []
        for idx, r in enumerate(records):
            raw_val = r.get("customs_clearance_delay")
            if raw_val is not None:
                try:
                    base_stat = self.feature_baselines_.get("customs_clearance_delay", {"mean": 0.0, "std": 1.0})
                    norm_val = (float(raw_val) - base_stat["mean"]) / base_stat["std"]
                    customs_clearance_delay_vals.append(round(norm_val, 6))
                except Exception:
                    customs_clearance_delay_vals.append(0.0)
            else:
                # Synthesize fallback domain estimate
                synth = round(float((idx * 12 * 17) % 100) / 100.0, 4)
                customs_clearance_delay_vals.append(synth)
        result.add_column("customs_clearance_delay_engineered", customs_clearance_delay_vals)

        # Domain Feature 13: perishable_shelf_life_decay
        perishable_shelf_life_decay_vals = []
        for idx, r in enumerate(records):
            raw_val = r.get("perishable_shelf_life_decay")
            if raw_val is not None:
                try:
                    base_stat = self.feature_baselines_.get("perishable_shelf_life_decay", {"mean": 0.0, "std": 1.0})
                    norm_val = (float(raw_val) - base_stat["mean"]) / base_stat["std"]
                    perishable_shelf_life_decay_vals.append(round(norm_val, 6))
                except Exception:
                    perishable_shelf_life_decay_vals.append(0.0)
            else:
                # Synthesize fallback domain estimate
                synth = round(float((idx * 13 * 17) % 100) / 100.0, 4)
                perishable_shelf_life_decay_vals.append(synth)
        result.add_column("perishable_shelf_life_decay_engineered", perishable_shelf_life_decay_vals)

        # Domain Feature 14: carbon_emission_per_shipment
        carbon_emission_per_shipment_vals = []
        for idx, r in enumerate(records):
            raw_val = r.get("carbon_emission_per_shipment")
            if raw_val is not None:
                try:
                    base_stat = self.feature_baselines_.get("carbon_emission_per_shipment", {"mean": 0.0, "std": 1.0})
                    norm_val = (float(raw_val) - base_stat["mean"]) / base_stat["std"]
                    carbon_emission_per_shipment_vals.append(round(norm_val, 6))
                except Exception:
                    carbon_emission_per_shipment_vals.append(0.0)
            else:
                # Synthesize fallback domain estimate
                synth = round(float((idx * 14 * 17) % 100) / 100.0, 4)
                carbon_emission_per_shipment_vals.append(synth)
        result.add_column("carbon_emission_per_shipment_engineered", carbon_emission_per_shipment_vals)

        # Domain Feature 15: vendor_compliance_score
        vendor_compliance_score_vals = []
        for idx, r in enumerate(records):
            raw_val = r.get("vendor_compliance_score")
            if raw_val is not None:
                try:
                    base_stat = self.feature_baselines_.get("vendor_compliance_score", {"mean": 0.0, "std": 1.0})
                    norm_val = (float(raw_val) - base_stat["mean"]) / base_stat["std"]
                    vendor_compliance_score_vals.append(round(norm_val, 6))
                except Exception:
                    vendor_compliance_score_vals.append(0.0)
            else:
                # Synthesize fallback domain estimate
                synth = round(float((idx * 15 * 17) % 100) / 100.0, 4)
                vendor_compliance_score_vals.append(synth)
        result.add_column("vendor_compliance_score_engineered", vendor_compliance_score_vals)

        # Domain Composite Index
        composite_scores = []
        for i in range(len(result)):
            c_score = sum(result[f"{f}_engineered"][i] for f in self.columns[:5]) / 5.0
            composite_scores.append(round(c_score, 4))
        result.add_column("supply_chain_erp_composite_index", composite_scores)
        return result

    def validate_domain_rules(self, df: DataFrame) -> Dict[str, Any]:
        violations = []
        for feat in self.columns:
            if feat in df.columns:
                null_pct = df[feat].missing_percentage()
                if null_pct > 25.0:
                    violations.append(f"Feature {feat} exceeds maximum allowed null threshold (observed: {null_pct}%)")
        return {
            "pipeline": "supply_chain_erp",
            "status": "PASSED" if not violations else "WARNING",
            "violation_count": len(violations),
            "violations": violations
        }
