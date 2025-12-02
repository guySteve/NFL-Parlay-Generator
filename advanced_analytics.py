#!/usr/bin/env python3
"""
Advanced NFL Analytics Engine
Senior Quantitative Analyst Implementation

Implements rigorous statistical methods for NFL prop betting:
- Historical Covariance Matrix for prop correlations
- Monte Carlo simulations for uncertainty quantification
- Kelly Criterion for bankroll management
- Adversarial validation for model robustness
- Brier Score & Log Loss metrics

Author: Quantitative Analytics Team
Version: 2.0.0
Python: 3.12+
"""

import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import minimize_scalar
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score, brier_score_loss, log_loss
from typing import Optional, Tuple, Dict, List
from dataclasses import dataclass
import warnings
warnings.filterwarnings('ignore')


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class PropProjection:
    """Single prop projection with uncertainty."""
    player_name: str
    stat_type: str
    mean: float
    std: float
    line: float
    confidence_interval: Tuple[float, float]
    p_over: float
    brier_score: Optional[float] = None


@dataclass
class CorrelatedPair:
    """Pair of correlated props."""
    prop1: str
    prop2: str
    correlation: float
    covariance: float
    p_value: float
    sample_size: int


# =============================================================================
# 1. CORRELATION & COVARIANCE ANALYSIS
# =============================================================================

class PropCorrelationEngine:
    """
    Calculates historical covariance matrices between player props.
    
    Uses actual game-by-game data to identify statistically significant
    correlations for Same Game Parlay (SGP) construction.
    """
    
    def __init__(self, min_sample_size: int = 30, significance_level: float = 0.05):
        """
        Initialize correlation engine.
        
        Args:
            min_sample_size: Minimum games required for correlation calculation
            significance_level: P-value threshold for significance (default 0.05)
        """
        self.min_sample_size = min_sample_size
        self.significance_level = significance_level
        self.correlation_matrix: Optional[pd.DataFrame] = None
        self.covariance_matrix: Optional[pd.DataFrame] = None
    
    def calculate_prop_correlations(
        self,
        historical_data: pd.DataFrame,
        props: List[str]
    ) -> pd.DataFrame:
        """
        Calculate correlation matrix for specified props.
        
        Args:
            historical_data: DataFrame with columns for each prop (game-by-game)
            props: List of prop column names to analyze
            
        Returns:
            Correlation matrix with statistical significance
        """
        # Filter to props that exist
        available_props = [p for p in props if p in historical_data.columns]
        
        if len(available_props) < 2:
            raise ValueError("Need at least 2 props to calculate correlations")
        
        # Check sample size
        n_samples = len(historical_data)
        if n_samples < self.min_sample_size:
            warnings.warn(
                f"Sample size {n_samples} below minimum {self.min_sample_size}. "
                "Correlations may be unreliable."
            )
        
        # Calculate Pearson correlations
        self.correlation_matrix = historical_data[available_props].corr(method='pearson')
        
        # Calculate covariance
        self.covariance_matrix = historical_data[available_props].cov()
        
        return self.correlation_matrix
    
    def find_significant_pairs(
        self,
        correlation_matrix: Optional[pd.DataFrame] = None,
        min_correlation: float = 0.3
    ) -> List[CorrelatedPair]:
        """
        Find statistically significant correlated prop pairs.
        
        Args:
            correlation_matrix: Precomputed correlation matrix (uses stored if None)
            min_correlation: Minimum absolute correlation threshold
            
        Returns:
            List of CorrelatedPair objects with significance tests
        """
        if correlation_matrix is None:
            if self.correlation_matrix is None:
                raise ValueError("No correlation matrix available. Run calculate_prop_correlations first.")
            correlation_matrix = self.correlation_matrix
        
        significant_pairs = []
        props = correlation_matrix.columns
        
        for i, prop1 in enumerate(props):
            for prop2 in props[i+1:]:
                corr = correlation_matrix.loc[prop1, prop2]
                
                # Skip weak correlations
                if abs(corr) < min_correlation:
                    continue
                
                # Calculate statistical significance
                # Use Fisher transformation for correlation significance test
                n = self.min_sample_size  # Conservative estimate
                z = 0.5 * np.log((1 + corr) / (1 - corr))
                se = 1 / np.sqrt(n - 3)
                p_value = 2 * (1 - stats.norm.cdf(abs(z) / se))
                
                if p_value < self.significance_level:
                    cov = self.covariance_matrix.loc[prop1, prop2] if self.covariance_matrix is not None else 0.0
                    
                    significant_pairs.append(CorrelatedPair(
                        prop1=prop1,
                        prop2=prop2,
                        correlation=corr,
                        covariance=cov,
                        p_value=p_value,
                        sample_size=n
                    ))
        
        # Sort by absolute correlation strength
        significant_pairs.sort(key=lambda x: abs(x.correlation), reverse=True)
        
        return significant_pairs
    
    def game_script_correlation(
        self,
        team_a_score_diff: np.ndarray,
        team_b_pass_attempts: np.ndarray
    ) -> Tuple[float, float]:
        """
        Calculate correlation between Team A score differential and Team B passing volume.
        
        This is the key metric for cross-team SGP construction.
        
        Args:
            team_a_score_diff: Array of Team A score differentials
            team_b_pass_attempts: Array of Team B pass attempts in same games
            
        Returns:
            Tuple of (correlation coefficient, p-value)
        """
        if len(team_a_score_diff) != len(team_b_pass_attempts):
            raise ValueError("Arrays must be same length")
        
        if len(team_a_score_diff) < self.min_sample_size:
            warnings.warn(f"Sample size {len(team_a_score_diff)} below minimum")
        
        # Pearson correlation
        corr, p_value = stats.pearsonr(team_a_score_diff, team_b_pass_attempts)
        
        return corr, p_value


# =============================================================================
# 2. MONTE CARLO SIMULATION ENGINE
# =============================================================================

class MonteCarloSimulator:
    """
    Monte Carlo simulation engine for uncertainty quantification.
    
    Runs thousands of game simulations to generate probability distributions
    for player props instead of point estimates.
    """
    
    def __init__(self, n_simulations: int = 10000, random_seed: Optional[int] = 42):
        """
        Initialize Monte Carlo simulator.
        
        Args:
            n_simulations: Number of simulations to run (default 10,000)
            random_seed: Random seed for reproducibility
        """
        self.n_simulations = n_simulations
        self.rng = np.random.default_rng(random_seed)
    
    def simulate_prop_distribution(
        self,
        mean: float,
        std: float,
        distribution: str = 'normal'
    ) -> np.ndarray:
        """
        Simulate prop value distribution.
        
        Args:
            mean: Expected value (projection)
            std: Standard deviation (uncertainty)
            distribution: Distribution type ('normal', 'lognormal', 'gamma')
            
        Returns:
            Array of simulated values
        """
        if distribution == 'normal':
            samples = self.rng.normal(mean, std, self.n_simulations)
        elif distribution == 'lognormal':
            # For naturally positive values (yards, points)
            sigma = np.sqrt(np.log(1 + (std / mean) ** 2))
            mu = np.log(mean) - 0.5 * sigma ** 2
            samples = self.rng.lognormal(mu, sigma, self.n_simulations)
        elif distribution == 'gamma':
            # For count data (attempts, receptions)
            shape = (mean / std) ** 2
            scale = std ** 2 / mean
            samples = self.rng.gamma(shape, scale, self.n_simulations)
        else:
            raise ValueError(f"Unknown distribution: {distribution}")
        
        # Clip negative values for physical stats
        samples = np.maximum(samples, 0)
        
        return samples
    
    def calculate_probability_over(
        self,
        simulated_values: np.ndarray,
        line: float
    ) -> float:
        """
        Calculate probability that prop goes over the line.
        
        Args:
            simulated_values: Array of Monte Carlo simulations
            line: Vegas line to compare against
            
        Returns:
            Probability of over (0 to 1)
        """
        return np.mean(simulated_values > line)
    
    def calculate_confidence_interval(
        self,
        simulated_values: np.ndarray,
        confidence_level: float = 0.90
    ) -> Tuple[float, float]:
        """
        Calculate confidence interval from simulations.
        
        Args:
            simulated_values: Array of Monte Carlo simulations
            confidence_level: Confidence level (default 90%)
            
        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        alpha = 1 - confidence_level
        lower = np.percentile(simulated_values, 100 * alpha / 2)
        upper = np.percentile(simulated_values, 100 * (1 - alpha / 2))
        
        return lower, upper
    
    def simulate_correlated_props(
        self,
        means: np.ndarray,
        stds: np.ndarray,
        correlation_matrix: np.ndarray
    ) -> np.ndarray:
        """
        Simulate multiple correlated props simultaneously.
        
        Uses Cholesky decomposition to preserve correlation structure.
        
        Args:
            means: Array of mean values for each prop
            stds: Array of standard deviations for each prop
            correlation_matrix: Correlation matrix between props
            
        Returns:
            Array of shape (n_simulations, n_props) with correlated samples
        """
        n_props = len(means)
        
        # Generate uncorrelated standard normal samples
        uncorrelated = self.rng.standard_normal((self.n_simulations, n_props))
        
        # Cholesky decomposition for correlation
        try:
            L = np.linalg.cholesky(correlation_matrix)
        except np.linalg.LinAlgError:
            # If matrix not positive definite, use eigendecomposition
            eigenvalues, eigenvectors = np.linalg.eigh(correlation_matrix)
            eigenvalues = np.maximum(eigenvalues, 1e-10)  # Ensure positive
            L = eigenvectors @ np.diag(np.sqrt(eigenvalues))
        
        # Apply correlation structure
        correlated = uncorrelated @ L.T
        
        # Scale and shift to match means and stds
        scaled = correlated * stds + means
        
        # Ensure non-negative for physical stats
        scaled = np.maximum(scaled, 0)
        
        return scaled
    
    def simulate_parlay(
        self,
        props: List[PropProjection],
        correlation_matrix: Optional[np.ndarray] = None
    ) -> Dict[str, float]:
        """
        Simulate entire parlay to calculate true probability.
        
        Args:
            props: List of PropProjection objects
            correlation_matrix: Correlation matrix (identity if None)
            
        Returns:
            Dictionary with parlay statistics
        """
        n_props = len(props)
        
        if correlation_matrix is None:
            correlation_matrix = np.eye(n_props)
        
        # Extract parameters
        means = np.array([p.mean for p in props])
        stds = np.array([p.std for p in props])
        lines = np.array([p.line for p in props])
        
        # Simulate correlated outcomes
        simulated = self.simulate_correlated_props(means, stds, correlation_matrix)
        
        # Check how often ALL legs hit
        all_legs_hit = np.all(simulated > lines, axis=1)
        parlay_probability = np.mean(all_legs_hit)
        
        # Individual leg probabilities
        individual_probs = np.mean(simulated > lines, axis=0)
        
        # Independence assumption probability (for comparison)
        independent_prob = np.prod(individual_probs)
        
        return {
            'true_probability': parlay_probability,
            'independent_probability': independent_prob,
            'correlation_advantage': parlay_probability - independent_prob,
            'individual_probabilities': individual_probs.tolist()
        }


# =============================================================================
# 3. KELLY CRITERION & BANKROLL MANAGEMENT
# =============================================================================

class KellyCriterion:
    """
    Kelly Criterion implementation for optimal bet sizing.
    
    Calculates mathematically optimal stake sizes based on edge and confidence.
    """
    
    @staticmethod
    def calculate_kelly_fraction(
        true_probability: float,
        decimal_odds: float,
        fractional_kelly: float = 0.25
    ) -> float:
        """
        Calculate Kelly Criterion bet fraction.
        
        Formula: f* = (bp - q) / b
        where b = decimal_odds - 1, p = true_probability, q = 1 - p
        
        Args:
            true_probability: Model's estimated probability (0 to 1)
            decimal_odds: Decimal odds offered (e.g., 2.0 for even money)
            fractional_kelly: Fraction of Kelly to use (0.25 = Quarter Kelly)
            
        Returns:
            Fraction of bankroll to wager (0 to 1)
        """
        if not 0 < true_probability < 1:
            raise ValueError("Probability must be between 0 and 1")
        
        if decimal_odds <= 1.0:
            raise ValueError("Decimal odds must be > 1.0")
        
        b = decimal_odds - 1  # Net odds
        p = true_probability
        q = 1 - p
        
        # Full Kelly
        kelly_full = (b * p - q) / b
        
        # Don't bet if no edge
        if kelly_full <= 0:
            return 0.0
        
        # Apply fractional Kelly for risk management
        kelly_fraction = kelly_full * fractional_kelly
        
        # Cap at reasonable maximum (20% of bankroll)
        return min(kelly_fraction, 0.20)
    
    @staticmethod
    def american_to_decimal(american_odds: int) -> float:
        """
        Convert American odds to decimal odds.
        
        Args:
            american_odds: American odds (e.g., -110, +150)
            
        Returns:
            Decimal odds
        """
        if american_odds > 0:
            return 1 + (american_odds / 100)
        else:
            return 1 + (100 / abs(american_odds))
    
    @staticmethod
    def calculate_expected_value(
        true_probability: float,
        decimal_odds: float,
        stake: float = 1.0
    ) -> float:
        """
        Calculate expected value of a bet.
        
        Args:
            true_probability: Model's probability estimate
            decimal_odds: Decimal odds offered
            stake: Bet amount (default 1 unit)
            
        Returns:
            Expected value in same units as stake
        """
        win_amount = stake * decimal_odds
        loss_amount = stake
        
        ev = (true_probability * win_amount) - ((1 - true_probability) * loss_amount)
        
        return ev
    
    @staticmethod
    def minimum_edge_required(
        decimal_odds: float,
        confidence_std: float = 0.05
    ) -> float:
        """
        Calculate minimum edge required to overcome uncertainty.
        
        Args:
            decimal_odds: Decimal odds offered
            confidence_std: Standard deviation in probability estimate
            
        Returns:
            Minimum edge required (as probability difference)
        """
        # Need edge > 2 * standard error to be statistically significant
        implied_prob = 1 / decimal_odds
        min_edge = 2 * confidence_std
        
        return min_edge


# =============================================================================
# 4. ADVERSARIAL VALIDATION
# =============================================================================

class AdversarialValidator:
    """
    Adversarial validation to detect covariate shift.
    
    Tests whether model can distinguish between training and test data.
    High discriminability indicates distribution shift (overfitting risk).
    """
    
    def __init__(self, n_folds: int = 5, random_state: int = 42):
        """
        Initialize validator.
        
        Args:
            n_folds: Number of cross-validation folds
            random_state: Random seed
        """
        self.n_folds = n_folds
        self.random_state = random_state
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=5,
            random_state=random_state,
            n_jobs=-1
        )
    
    def validate(
        self,
        train_features: pd.DataFrame,
        test_features: pd.DataFrame
    ) -> Dict[str, float]:
        """
        Run adversarial validation.
        
        Args:
            train_features: Training data features
            test_features: Test data features (upcoming game)
            
        Returns:
            Dictionary with validation metrics
        """
        # Combine and label datasets
        train_features['is_test'] = 0
        test_features['is_test'] = 1
        
        combined = pd.concat([train_features, test_features], ignore_index=True)
        
        X = combined.drop('is_test', axis=1)
        y = combined['is_test']
        
        # Cross-validated AUC
        cv = StratifiedKFold(n_splits=self.n_folds, shuffle=True, random_state=self.random_state)
        aucs = []
        
        for train_idx, val_idx in cv.split(X, y):
            X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
            y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
            
            self.model.fit(X_train, y_train)
            y_pred = self.model.predict_proba(X_val)[:, 1]
            
            auc = roc_auc_score(y_val, y_pred)
            aucs.append(auc)
        
        mean_auc = np.mean(aucs)
        std_auc = np.std(aucs)
        
        # Interpretation
        if mean_auc > 0.7:
            warning = "HIGH RISK: Significant covariate shift detected. Model may not generalize."
        elif mean_auc > 0.6:
            warning = "MODERATE RISK: Some distribution shift present. Use caution."
        else:
            warning = "LOW RISK: Train and test distributions are similar."
        
        return {
            'mean_auc': mean_auc,
            'std_auc': std_auc,
            'warning': warning,
            'passed': mean_auc < 0.7
        }


# =============================================================================
# 5. MODEL EVALUATION METRICS
# =============================================================================

class ModelEvaluator:
    """
    Rigorous model evaluation using proper scoring rules.
    """
    
    @staticmethod
    def brier_score(
        true_outcomes: np.ndarray,
        predicted_probs: np.ndarray
    ) -> float:
        """
        Calculate Brier Score (lower is better).
        
        Brier Score measures calibration: (forecast - outcome)²
        
        Args:
            true_outcomes: Binary outcomes (0 or 1)
            predicted_probs: Predicted probabilities (0 to 1)
            
        Returns:
            Brier score (0 to 1, lower is better)
        """
        return brier_score_loss(true_outcomes, predicted_probs)
    
    @staticmethod
    def log_loss_score(
        true_outcomes: np.ndarray,
        predicted_probs: np.ndarray
    ) -> float:
        """
        Calculate Log Loss (lower is better).
        
        Log Loss heavily penalizes confident wrong predictions.
        
        Args:
            true_outcomes: Binary outcomes (0 or 1)
            predicted_probs: Predicted probabilities (0 to 1)
            
        Returns:
            Log loss (0 to infinity, lower is better)
        """
        return log_loss(true_outcomes, predicted_probs)
    
    @staticmethod
    def calibration_curve(
        true_outcomes: np.ndarray,
        predicted_probs: np.ndarray,
        n_bins: int = 10
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate calibration curve for probability predictions.
        
        Args:
            true_outcomes: Binary outcomes
            predicted_probs: Predicted probabilities
            n_bins: Number of probability bins
            
        Returns:
            Tuple of (bin_means, true_frequencies)
        """
        bins = np.linspace(0, 1, n_bins + 1)
        bin_indices = np.digitize(predicted_probs, bins) - 1
        
        bin_means = []
        true_freqs = []
        
        for i in range(n_bins):
            mask = bin_indices == i
            if mask.sum() > 0:
                bin_means.append(predicted_probs[mask].mean())
                true_freqs.append(true_outcomes[mask].mean())
        
        return np.array(bin_means), np.array(true_freqs)
    
    @staticmethod
    def expected_calibration_error(
        true_outcomes: np.ndarray,
        predicted_probs: np.ndarray,
        n_bins: int = 10
    ) -> float:
        """
        Calculate Expected Calibration Error (ECE).
        
        ECE measures how well predicted probabilities match actual frequencies.
        
        Args:
            true_outcomes: Binary outcomes
            predicted_probs: Predicted probabilities
            n_bins: Number of bins
            
        Returns:
            ECE score (0 to 1, lower is better)
        """
        bins = np.linspace(0, 1, n_bins + 1)
        bin_indices = np.digitize(predicted_probs, bins) - 1
        
        ece = 0.0
        n_total = len(predicted_probs)
        
        for i in range(n_bins):
            mask = bin_indices == i
            n_bin = mask.sum()
            
            if n_bin > 0:
                bin_acc = true_outcomes[mask].mean()
                bin_conf = predicted_probs[mask].mean()
                ece += (n_bin / n_total) * abs(bin_acc - bin_conf)
        
        return ece


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

def example_usage():
    """Demonstrate usage of advanced analytics modules."""
    
    print("=" * 70)
    print("ADVANCED NFL ANALYTICS - QUANTITATIVE DEMONSTRATION")
    print("=" * 70)
    print()
    
    # 1. Correlation Analysis
    print("1. PROP CORRELATION ANALYSIS")
    print("-" * 70)
    
    # Simulated historical data
    np.random.seed(42)
    n_games = 50
    
    qb_pass_yards = np.random.normal(250, 50, n_games)
    wr1_rec_yards = qb_pass_yards * 0.35 + np.random.normal(0, 15, n_games)
    rb_rush_yards = -qb_pass_yards * 0.15 + np.random.normal(70, 20, n_games)
    
    hist_data = pd.DataFrame({
        'QB_Pass_Yards': qb_pass_yards,
        'WR1_Rec_Yards': wr1_rec_yards,
        'RB_Rush_Yards': rb_rush_yards
    })
    
    corr_engine = PropCorrelationEngine(min_sample_size=30)
    corr_matrix = corr_engine.calculate_prop_correlations(hist_data, hist_data.columns.tolist())
    
    print("Correlation Matrix:")
    print(corr_matrix.round(3))
    print()
    
    pairs = corr_engine.find_significant_pairs(min_correlation=0.3)
    print(f"Found {len(pairs)} significant correlations:")
    for pair in pairs:
        print(f"  {pair.prop1} ↔ {pair.prop2}: r={pair.correlation:.3f}, p={pair.p_value:.4f}")
    print()
    
    # 2. Monte Carlo Simulation
    print("2. MONTE CARLO SIMULATION")
    print("-" * 70)
    
    mc_sim = MonteCarloSimulator(n_simulations=10000)
    
    # Simulate QB passing yards
    qb_mean, qb_std, qb_line = 252.5, 45.0, 245.5
    qb_samples = mc_sim.simulate_prop_distribution(qb_mean, qb_std, distribution='normal')
    
    p_over = mc_sim.calculate_probability_over(qb_samples, qb_line)
    ci_lower, ci_upper = mc_sim.calculate_confidence_interval(qb_samples, confidence_level=0.90)
    
    print(f"QB Passing Yards Projection:")
    print(f"  Mean: {qb_mean:.1f}")
    print(f"  Line: {qb_line:.1f}")
    print(f"  P(Over): {p_over:.1%}")
    print(f"  90% CI: [{ci_lower:.1f}, {ci_upper:.1f}]")
    print()
    
    # 3. Kelly Criterion
    print("3. KELLY CRITERION BET SIZING")
    print("-" * 70)
    
    kelly = KellyCriterion()
    
    true_prob = p_over
    american_odds = -110
    decimal_odds = kelly.american_to_decimal(american_odds)
    
    kelly_fraction = kelly.calculate_kelly_fraction(true_prob, decimal_odds, fractional_kelly=0.25)
    ev = kelly.calculate_expected_value(true_prob, decimal_odds, stake=100)
    
    print(f"Bet Analysis (QB Pass Yards Over {qb_line}):")
    print(f"  True Probability: {true_prob:.1%}")
    print(f"  Odds: {american_odds} ({decimal_odds:.2f} decimal)")
    print(f"  Expected Value: ${ev:.2f} per $100 bet")
    print(f"  Quarter-Kelly Stake: {kelly_fraction:.1%} of bankroll")
    print(f"  → On $1000 bankroll: Bet ${kelly_fraction * 1000:.2f}")
    print()
    
    # 4. Adversarial Validation
    print("4. ADVERSARIAL VALIDATION")
    print("-" * 70)
    
    # Simulated train/test features
    train_features = pd.DataFrame(np.random.normal(0, 1, (100, 5)))
    test_features = pd.DataFrame(np.random.normal(0.2, 1, (20, 5)))  # Slight shift
    
    validator = AdversarialValidator()
    validation_results = validator.validate(train_features.copy(), test_features.copy())
    
    print(f"Adversarial Validation Results:")
    print(f"  Mean AUC: {validation_results['mean_auc']:.3f}")
    print(f"  Std AUC: {validation_results['std_auc']:.3f}")
    print(f"  Status: {validation_results['warning']}")
    print(f"  Passed: {'✓' if validation_results['passed'] else '✗'}")
    print()
    
    # 5. Model Evaluation
    print("5. MODEL EVALUATION METRICS")
    print("-" * 70)
    
    # Simulated predictions vs outcomes
    true_outcomes = np.random.binomial(1, 0.55, 100)
    predicted_probs = np.random.beta(5.5, 4.5, 100)  # Centered around 0.55
    
    evaluator = ModelEvaluator()
    
    brier = evaluator.brier_score(true_outcomes, predicted_probs)
    logloss = evaluator.log_loss_score(true_outcomes, predicted_probs)
    ece = evaluator.expected_calibration_error(true_outcomes, predicted_probs)
    
    print(f"Model Performance:")
    print(f"  Brier Score: {brier:.4f} (lower is better, 0.25 = random)")
    print(f"  Log Loss: {logloss:.4f} (lower is better)")
    print(f"  Expected Calibration Error: {ece:.4f} (lower is better)")
    print()
    
    print("=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    example_usage()
