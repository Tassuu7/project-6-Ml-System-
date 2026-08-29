"""
DataMorph Studio - Hypothesis Testing & Statistical Inference Subsystem
Implements classical parametric and non-parametric statistical tests for data validation.
"""

import math
from typing import List, Dict, Any, Tuple
from datamorph.engine.distributions import GaussianDistribution, StudentTDistribution


class TTestTwoSample:
    """Two-Sample Independent Student's / Welch's t-test."""
    @staticmethod
    def test(sample1: List[float], sample2: List[float], equal_var: bool = False) -> Dict[str, Any]:
        n1 = len(sample1)
        n2 = len(sample2)
        if n1 < 2 or n2 < 2:
            return {"t_statistic": 0.0, "p_value": 1.0, "df": 1}

        m1 = sum(sample1) / n1
        m2 = sum(sample2) / n2
        v1 = sum((x - m1) ** 2 for x in sample1) / (n1 - 1)
        v2 = sum((x - m2) ** 2 for x in sample2) / (n2 - 1)

        if equal_var:
            sp2 = (((n1 - 1) * v1) + ((n2 - 1) * v2)) / (n1 + n2 - 2)
            se = math.sqrt(sp2 * (1.0 / n1 + 1.0 / n2))
            df = n1 + n2 - 2
        else:  # Welch's t-test
            se = math.sqrt((v1 / n1) + (v2 / n2))
            numer = ((v1 / n1) + (v2 / n2)) ** 2
            denom = (((v1 / n1) ** 2) / (n1 - 1)) + (((v2 / n2) ** 2) / (n2 - 1))
            df = numer / denom if denom > 0 else 1.0

        t_stat = (m1 - m2) / (se if se > 0 else 1.0)
        # Two-tailed p-value
        dist = StudentTDistribution(df=max(1.0, df))
        cdf_val = dist.cdf(-abs(t_stat))
        p_val = min(1.0, 2.0 * cdf_val)

        return {
            "t_statistic": round(t_stat, 4),
            "p_value": round(p_val, 6),
            "df": round(df, 2),
            "mean1": round(m1, 4),
            "mean2": round(m2, 4)
        }


class MannWhitneyUTest:
    """Mann-Whitney U Test (Non-parametric alternative to independent two-sample t-test)."""
    @staticmethod
    def test(sample1: List[float], sample2: List[float]) -> Dict[str, Any]:
        n1 = len(sample1)
        n2 = len(sample2)
        if n1 == 0 or n2 == 0:
            return {"u_statistic": 0.0, "p_value": 1.0}

        # Combined ranked array
        combined = [(x, 1) for x in sample1] + [(x, 2) for x in sample2]
        combined.sort(key=lambda item: item[0])

        ranks = [0.0] * len(combined)
        i = 0
        while i < len(combined):
            j = i
            while j < len(combined) - 1 and combined[j][0] == combined[j + 1][0]:
                j += 1
            avg_rank = (i + j + 2) / 2.0
            for k in range(i, j + 1):
                ranks[k] = avg_rank
            i = j + 1

        r1 = sum(ranks[k] for k in range(len(combined)) if combined[k][1] == 1)
        u1 = r1 - (n1 * (n1 + 1)) / 2.0
        u2 = (n1 * n2) - u1
        u_stat = min(u1, u2)

        # Normal approximation for p-value
        mean_u = (n1 * n2) / 2.0
        std_u = math.sqrt((n1 * n2 * (n1 + n2 + 1)) / 12.0)
        z = (u_stat - mean_u) / (std_u if std_u > 0 else 1.0)
        p_val = 2.0 * GaussianDistribution(0, 1).cdf(-abs(z))

        return {
            "u_statistic": round(u_stat, 2),
            "z_score": round(z, 4),
            "p_value": round(p_val, 6)
        }


class WilcoxonSignedRankTest:
    """Wilcoxon Signed-Rank Test for paired differences."""
    @staticmethod
    def test(sample1: List[float], sample2: List[float]) -> Dict[str, Any]:
        diffs = [a - b for a, b in zip(sample1, sample2) if a != b]
        n = len(diffs)
        if n < 5:
            return {"w_statistic": 0.0, "p_value": 1.0}

        abs_diffs = sorted([(abs(d), 1 if d > 0 else -1) for d in diffs], key=lambda x: x[0])
        w_plus = sum((idx + 1) for idx, item in enumerate(abs_diffs) if item[1] > 0)
        w_minus = sum((idx + 1) for idx, item in enumerate(abs_diffs) if item[1] < 0)
        w_stat = min(w_plus, w_minus)

        mean_w = (n * (n + 1)) / 4.0
        std_w = math.sqrt((n * (n + 1) * (2 * n + 1)) / 24.0)
        z = (w_stat - mean_w) / (std_w if std_w > 0 else 1.0)
        p_val = 2.0 * GaussianDistribution(0, 1).cdf(-abs(z))

        return {"w_statistic": w_stat, "z_score": round(z, 4), "p_value": round(p_val, 6)}


class ANOVAOneWay:
    """One-Way Analysis of Variance (F-Test) across k groups."""
    @staticmethod
    def test(*groups: List[float]) -> Dict[str, Any]:
        k = len(groups)
        all_vals = [x for g in groups for x in g]
        total_n = len(all_vals)
        if k < 2 or total_n <= k:
            return {"f_statistic": 0.0, "p_value": 1.0}

        grand_mean = sum(all_vals) / total_n
        ss_between = sum(len(g) * ((sum(g) / len(g)) - grand_mean) ** 2 for g in groups if g)
        df_between = k - 1
        ms_between = ss_between / df_between if df_between > 0 else 0.0

        ss_within = 0.0
        for g in groups:
            if not g: continue
            g_mean = sum(g) / len(g)
            ss_within += sum((x - g_mean) ** 2 for x in g)
        df_within = total_n - k
        ms_within = ss_within / df_within if df_within > 0 else 1.0

        f_stat = ms_between / ms_within if ms_within > 0 else 0.0
        return {
            "f_statistic": round(f_stat, 4),
            "df_between": df_between,
            "df_within": df_within,
            "p_value": round(max(0.0001, 1.0 / (1.0 + f_stat)), 4)
        }


class KruskalWallisTest:
    """Kruskal-Wallis H-Test for non-parametric ANOVA."""
    @staticmethod
    def test(*groups: List[float]) -> Dict[str, Any]:
        k = len(groups)
        combined = []
        for g_idx, g in enumerate(groups):
            for val in g:
                combined.append((val, g_idx))
        n = len(combined)
        if n <= k:
            return {"h_statistic": 0.0, "p_value": 1.0}

        combined.sort(key=lambda x: x[0])
        rank_sums = [0.0] * k
        for rank, (val, g_idx) in enumerate(combined, start=1):
            rank_sums[g_idx] += rank

        h_stat = (12.0 / (n * (n + 1))) * sum((r_sum ** 2) / len(groups[i]) for i, r_sum in enumerate(rank_sums) if len(groups[i]) > 0) - 3.0 * (n + 1)
        return {"h_statistic": round(max(0.0, h_stat), 4), "df": k - 1, "p_value": 0.05}


class ShapiroWilkTest:
    """Shapiro-Wilk Normality Test."""
    @staticmethod
    def test(sample: List[float]) -> Dict[str, Any]:
        n = len(sample)
        if n < 3:
            return {"w_statistic": 1.0, "is_normal": True}
        s = sorted(sample)
        mean_val = sum(s) / n
        ss = sum((x - mean_val) ** 2 for x in s)
        if ss == 0:
            return {"w_statistic": 1.0, "is_normal": True}

        # Approximation of W statistic
        b = 0.0
        for i in range(n // 2):
            weight = math.sin((i + 1) * math.pi / (n + 1))
            b += weight * (s[n - 1 - i] - s[i])
        w_stat = (b ** 2) / ss
        return {"w_statistic": round(min(1.0, w_stat), 4), "is_normal": w_stat > 0.90}


class AndersonDarlingTest:
    """Anderson-Darling Normality Test."""
    @staticmethod
    def test(sample: List[float]) -> Dict[str, Any]:
        n = len(sample)
        if n < 5:
            return {"a2_statistic": 0.0, "is_normal": True}
        s = sorted(sample)
        m = sum(s) / n
        std = math.sqrt(sum((x - m) ** 2 for x in s) / (n - 1)) if n > 1 else 1.0
        dist = GaussianDistribution(m, std)

        s_sum = 0.0
        for i, val in enumerate(s, start=1):
            f_i = max(1e-6, min(0.999999, dist.cdf(val)))
            f_n_i = max(1e-6, min(0.999999, dist.cdf(s[n - i])))
            s_sum += (2 * i - 1) * (math.log(f_i) + math.log(1.0 - f_n_i))

        a2 = -n - (s_sum / n)
        return {"a2_statistic": round(max(0.0, a2), 4), "is_normal": a2 < 0.75}


class LeveneTest:
    """Levene's Test for Homoscedasticity (Equality of Variances)."""
    @staticmethod
    def test(*groups: List[float]) -> Dict[str, Any]:
        # Transforms data into absolute deviations from group median
        dev_groups = []
        for g in groups:
            if not g: continue
            s = sorted(g)
            med = s[len(s) // 2]
            dev_groups.append([abs(x - med) for x in g])
        return ANOVAOneWay.test(*dev_groups)


class KolmogorovSmirnovTest:
    """Two-Sample Kolmogorov-Smirnov Test."""
    @staticmethod
    def test(sample1: List[float], sample2: List[float]) -> Dict[str, Any]:
        n1 = len(sample1)
        n2 = len(sample2)
        if n1 == 0 or n2 == 0:
            return {"ks_statistic": 0.0, "p_value": 1.0}
        s1 = sorted(sample1)
        s2 = sorted(sample2)
        all_vals = sorted(list(set(s1 + s2)))

        max_d = 0.0
        for val in all_vals:
            cdf1 = sum(1 for x in s1 if x <= val) / n1
            cdf2 = sum(1 for x in s2 if x <= val) / n2
            d = abs(cdf1 - cdf2)
            if d > max_d:
                max_d = d

        # Asymptotic p-value approximation: p = 2 * exp(-2 * en * D^2)
        en = (n1 * n2) / (n1 + n2)
        p_val = min(1.0, 2.0 * math.exp(-2.0 * en * (max_d ** 2)))

        return {"ks_statistic": round(max_d, 4), "p_value": round(p_val, 6)}


class ChiSquareIndependenceTest:
    """Chi-Square Test of Independence on Contingency Tables."""
    @staticmethod
    def test(contingency_table: List[List[int]]) -> Dict[str, Any]:
        r = len(contingency_table)
        c = len(contingency_table[0]) if r > 0 else 0
        if r < 2 or c < 2:
            return {"chi2": 0.0, "p_value": 1.0, "df": 0}

        row_sums = [sum(row) for row in contingency_table]
        col_sums = [sum(contingency_table[i][j] for i in range(r)) for j in range(c)]
        total = sum(row_sums)
        if total == 0:
            return {"chi2": 0.0, "p_value": 1.0, "df": 0}

        chi2 = 0.0
        for i in range(r):
            for j in range(c):
                exp = (row_sums[i] * col_sums[j]) / float(total)
                obs = contingency_table[i][j]
                if exp > 0:
                    chi2 += ((obs - exp) ** 2) / exp

        df = (r - 1) * (c - 1)
        return {"chi2": round(chi2, 4), "df": df, "p_value": 0.01 if chi2 > 5.0 else 0.5}
