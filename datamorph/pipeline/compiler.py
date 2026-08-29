"""
DataMorph Studio - Pipeline Code Generator & Compiler
Exports visual DAG pipeline recipes into standalone Python scripts and scikit-learn code.
"""

from typing import Dict, Any
from datamorph.pipeline.dag import PipelineDAG


class PipelineCompiler:
    """Compiles DAG pipeline recipes into standalone Python deployment scripts."""
    
    @classmethod
    def to_python_script(cls, dag: PipelineDAG) -> str:
        ordered_steps = dag.topological_sort()
        lines = [
            '"""',
            f'DataMorph Studio Auto-Generated Preprocessing Pipeline: {dag.name}',
            '"""',
            'import pandas as pd',
            'import numpy as np',
            '',
            'def preprocess(df: pd.DataFrame) -> pd.DataFrame:',
            '    df = df.copy()',
            '    print(f"Initial shape: {df.shape}")',
            ''
        ]

        for step in ordered_steps:
            lines.append(f'    # Step: {step.name} ({step.transformer.__class__.__name__})')
            t_type = step.transformer.__class__.__name__
            cols = step.transformer.columns
            col_repr = repr(cols) if cols else "df.select_dtypes(include=[np.number]).columns.tolist()"

            if "StandardScaler" in t_type:
                lines.append(f'    for col in {col_repr}:')
                lines.append('        if col in df.columns:')
                lines.append('            m, s = df[col].mean(), df[col].std()')
                lines.append('            df[col] = (df[col] - m) / (s if s > 0 else 1.0)')
            elif "MinMaxScaler" in t_type:
                lines.append(f'    for col in {col_repr}:')
                lines.append('        if col in df.columns:')
                lines.append('            c_min, c_max = df[col].min(), df[col].max()')
                lines.append('            df[col] = (df[col] - c_min) / ((c_max - c_min) if (c_max - c_min) > 0 else 1.0)')
            elif "SimpleImputer" in t_type:
                lines.append(f'    for col in {col_repr}:')
                lines.append('        if col in df.columns:')
                lines.append('            df[col] = df[col].fillna(df[col].mean() if pd.api.types.is_numeric_dtype(df[col]) else df[col].mode()[0])')
            elif "OneHotEncoder" in t_type:
                lines.append(f'    df = pd.get_dummies(df, columns={col_repr}, drop_first=False)')
            elif "VarianceThreshold" in t_type:
                lines.append(f'    numeric_cols = df.select_dtypes(include=[np.number]).columns')
                lines.append('    variances = df[numeric_cols].var()')
                lines.append('    valid_cols = variances[variances > 0.01].index.tolist()')
                lines.append('    df = df[valid_cols]')
            else:
                lines.append(f'    # Custom transformer logic for {t_type}')
                lines.append(f'    pass')
            lines.append('')

        lines.append('    print(f"Transformed shape: {df.shape}")')
        lines.append('    return df')
        lines.append('')
        lines.append('if __name__ == "__main__":')
        lines.append('    import sys')
        lines.append('    if len(sys.argv) > 1:')
        lines.append('        data = pd.read_csv(sys.argv[1])')
        lines.append('        transformed = preprocess(data)')
        lines.append('        transformed.to_csv("transformed_output.csv", index=False)')
        lines.append('        print("Transformed data saved to transformed_output.csv")')
        return "\n".join(lines)
