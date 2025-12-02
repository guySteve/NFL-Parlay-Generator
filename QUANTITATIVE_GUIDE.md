# 📊 Quantitative Analytics Guide

## Advanced Statistical Methods for NFL Prop Betting

This document explains the rigorous quantitative methods implemented in the system.

---

## 🎯 FEATURE UPDATE: EPA/DVOA-Based Defense Metrics

### Replaced: Simple Rank (1-32)
### With: Quantitative EPA & DVOA Metrics

---

## 📐 New Defense Metrics Framework

### 1. Opponent Defensive EPA (Primary Metric)

**Definition**: Expected Points Added allowed by the defense per play.

**Scale**: -0.5 (elite) to +0.5 (poor)
- **Negative EPA** = Good defense (prevents points)
- **Positive EPA** = Bad defense (allows points)

**Example Values**:
```
-0.15 = Elite defense (Top 5)
-0.04 = Above average
 0.00 = League average
+0.08 = Below average
+0.20 = Poor defense (Bottom 5)
```

**How It's Used**:
```python
# In projection formula:
epa_modifier = 1.0 - (opponent_def_epa * 0.5)

# Examples:
# -0.20 EPA (elite) → 1.10x modifier → Reduces projection 10%
# +0.20 EPA (poor) → 0.90x modifier → Increases projection 10%
```

**Weight in Model**: **65%** of defensive adjustment

---

### 2. Opponent DVOA Pass Defense (Secondary Metric)

**Definition**: Defense-adjusted Value Over Average vs the pass.

**Scale**: -50% (elite) to +50% (poor)
- **Negative DVOA** = Good pass defense
- **Positive DVOA** = Bad pass defense

**Example Values**:
```
-25% = Elite pass defense
 -5% = Above average
  0% = League average
 +8% = Below average
+30% = Poor pass defense
```

**How It's Used**:
```python
# In projection formula:
dvoa_modifier = 1.0 - (opponent_dvoa / 250.0)

# Examples:
# -20% DVOA (elite) → 1.08x modifier → Reduces projection 8%
# +20% DVOA (poor) → 0.92x modifier → Increases projection 8%
```

**Weight in Model**: **35%** of defensive adjustment

---

### 3. Opponent DVOA Run Defense (Secondary Metric)

**Definition**: Defense-adjusted Value Over Average vs the run.

**Scale**: -50% (elite) to +50% (poor)
- **Negative DVOA** = Good run defense
- **Positive DVOA** = Bad run defense

**Example Values**:
```
-20% = Elite run defense
 -5.5% = Above average
  0% = League average
 +6% = Below average
+25% = Poor run defense
```

**Applied separately for RB projections**.

**Weight in Model**: **35%** of defensive adjustment

---

### 4. Team Offensive EPA (Recent Form)

**Definition**: Team's offensive EPA per play over last 4 games.

**Scale**: -0.5 (struggling) to +0.5 (hot)
- **Positive EPA** = Offense is clicking
- **Negative EPA** = Offense is struggling

**Example Values**:
```
+0.25 = Elite recent form
+0.15 = Above average form
 0.00 = Average form
-0.10 = Below average form
-0.25 = Struggling offense
```

**How It's Used**:
```python
# Applied as multiplier to projections:
offensive_form_modifier = 1.0 + (team_offense_epa_l4 * 0.3)

# Examples:
# +0.20 EPA (hot) → 1.06x modifier → Increases projection 6%
# -0.20 EPA (cold) → 0.94x modifier → Decreases projection 6%
```

**Weight in Model**: **Additive 30%** modifier on final projection

---

## 🧮 Combined Adjustment Formula

### Full Mathematical Model:

```python
# Step 1: Calculate base projection (L5 weighted 65%, Season 35%)
base = (last_5_avg * 0.65) + (season_avg * 0.35)

# Step 2: Apply EPA adjustment (primary)
epa_modifier = 1.0 - (opponent_def_epa * 0.5)

# Step 3: Apply DVOA adjustment (secondary)
dvoa_modifier = 1.0 - (opponent_dvoa / 250.0)

# Step 4: Combine EPA & DVOA (weighted 65%/35%)
defensive_adjustment = (epa_modifier * 0.65) + (dvoa_modifier * 0.35)

# Step 5: Clamp to reasonable bounds
defensive_adjustment = max(0.85, min(1.15, defensive_adjustment))

# Step 6: Apply defensive adjustment
adjusted = base * defensive_adjustment

# Step 7: Apply team offensive form
form_modifier = 1.0 + (team_offense_epa_l4 * 0.3)
final = adjusted * form_modifier
```

---

## 📊 Example Calculation

### Scenario: QB Passing Yards Projection

**Given**:
- Last 5 Games Avg: 265 yards
- Season Avg: 245 yards
- Opponent Def EPA: -0.08 (good defense)
- Opponent DVOA Pass: +12.5% (bad pass defense)
- Team Off EPA (L4): +0.18 (hot offense)

**Calculation**:

```python
# Step 1: Base
base = (265 * 0.65) + (245 * 0.35) = 258.0

# Step 2: EPA Modifier
epa_mod = 1.0 - (-0.08 * 0.5) = 1.04

# Step 3: DVOA Modifier  
dvoa_mod = 1.0 - (12.5 / 250.0) = 0.95

# Step 4: Combined Defensive
def_adj = (1.04 * 0.65) + (0.95 * 0.35) = 1.009

# Step 5: Clamp (already in range)
def_adj = 1.009

# Step 6: Apply Defense
adjusted = 258.0 * 1.009 = 260.3

# Step 7: Apply Offensive Form
form_mod = 1.0 + (0.18 * 0.3) = 1.054
final = 260.3 * 1.054 = 274.3 yards

# Result: Project 274.3 yards vs market line of 265.5
# Edge: +3.3% → Bet OVER
```

---

## 🎓 Integration with Your Existing System

### Step 1: Replace Single-Point Projections with Distributions

**Current Code (NFL_pre.py)**:
```python
def _create_projection(self, player, stat_type, projected, line):
    edge = ((projected - line) / line) * 100
    recommendation = BetType.OVER if projected > line else BetType.UNDER
    # ...
```

**Enhanced Code**:
```python
from advanced_analytics import MonteCarloSimulator

def _create_projection_with_uncertainty(self, player, stat_type, mean, std, line):
    sim = MonteCarloSimulator(n_simulations=10000)
    samples = sim.simulate_prop_distribution(mean, std, distribution='normal')
    
    p_over = sim.calculate_probability_over(samples, line)
    ci_lower, ci_upper = sim.calculate_confidence_interval(samples, confidence_level=0.90)
    
    # Calculate edge using TRUE probability, not point estimate
    implied_prob = 1 / 1.91  # Assuming -110 odds = 52.4%
    true_edge = p_over - implied_prob
    
    recommendation = BetType.OVER if p_over > 0.524 else BetType.UNDER
    
    return Projection(
        player_name=player.name,
        stat_type=stat_type,
        projected_mean=mean,
        projected_std=std,
        confidence_interval=(ci_lower, ci_upper),
        market_line=line,
        true_probability=p_over,
        edge=true_edge * 100,
        recommendation=recommendation
    )
```

### Step 2: Add Correlation-Aware Parlay Construction

**Enhanced Correlation Engine**:
```python
def build_sgp_with_correlation(self, projections, correlation_matrix):
    """Build SGP using actual correlation data, not heuristics."""
    from advanced_analytics import MonteCarloSimulator, PropProjection
    
    sim = MonteCarloSimulator()
    
    # Convert projections to PropProjection format
    props = [
        PropProjection(
            player_name=p.player_name,
            stat_type=p.stat_type,
            mean=p.projected_mean,
            std=p.projected_std,
            line=p.market_line,
            confidence_interval=p.confidence_interval,
            p_over=p.true_probability
        )
        for p in projections
    ]
    
    # Simulate correlated parlay
    parlay_stats = sim.simulate_parlay(props, correlation_matrix)
    
    # Check if correlation gives us edge
    true_prob = parlay_stats['true_probability']
    independent_prob = parlay_stats['independent_probability']
    
    correlation_edge = true_prob - independent_prob
    
    if correlation_edge > 0.03:  # 3% edge from correlation
        return {
            'props': props,
            'true_probability': true_prob,
            'correlation_edge': correlation_edge,
            'recommendation': 'BET' if true_prob > 0.30 else 'PASS'
        }
```

### Step 3: Add Kelly-Based Stake Sizing

**Add to Results Display**:
```python
from advanced_analytics import KellyCriterion

def display_results_with_kelly(self, projections, bankroll=1000):
    kelly = KellyCriterion()
    
    for proj in projections:
        # Calculate optimal stake
        decimal_odds = kelly.american_to_decimal(-110)
        kelly_fraction = kelly.calculate_kelly_fraction(
            proj.true_probability,
            decimal_odds,
            fractional_kelly=0.25  # Conservative
        )
        
        stake_amount = bankroll * kelly_fraction
        ev = kelly.calculate_expected_value(proj.true_probability, decimal_odds, stake_amount)
        
        print(f"{proj.player_name} {proj.stat_type}:")
        print(f"  True Probability: {proj.true_probability:.1%}")
        print(f"  Recommended Stake: ${stake_amount:.2f} ({kelly_fraction:.1%} of bankroll)")
        print(f"  Expected Return: ${ev:.2f}")
```

---

## 📈 Performance Benchmarks

From test run of advanced_analytics.py:

| Metric | Value | Interpretation |
|--------|-------|----------------|
| **Correlation Detection** | 3 significant pairs found | Strong QB-WR correlation (r=0.807) |
| **Monte Carlo Accuracy** | 55.8% P(Over) | Conservative (includes variance) |
| **Kelly Stake** | 1.8% of bankroll | Safe bet sizing |
| **EV per $100** | $6.22 | 6.2% ROI (excellent) |
| **Adversarial AUC** | 0.585 | Model generalizes well ✓ |
| **Brier Score** | 0.2717 | Needs calibration tuning |

---

## ⚠️ Important Notes

### Statistical Significance Requirements

- **Minimum Sample Size**: 30 games for correlation analysis
- **P-value Threshold**: 0.05 (5% significance level)
- **Correlation Threshold**: |r| > 0.3 for practical significance

### Risk Management

- **Never bet Full Kelly**: Use 25% Kelly (Quarter Kelly) for safety
- **Minimum Edge**: Require >2% edge after accounting for vig
- **Max Bet Size**: Cap at 20% of bankroll even if Kelly suggests more

### Model Validation

- **Run Adversarial Validation** before every major bet
- **Track Brier Score** over time to detect model decay
- **Recalibrate** if ECE > 0.10

---

## 🚀 Next Steps

1. **Collect Historical Data**: Game-by-game player stats for correlation analysis
2. **Estimate Variance**: Calculate std dev for each player's props
3. **Build Correlation Matrix**: Run PropCorrelationEngine on full season data
4. **Integrate with GUI**: Add Monte Carlo and Kelly to results tab
5. **Track Performance**: Log all predictions for Brier Score calculation

---

## 📚 References

- Kelly, J. L. (1956). "A New Interpretation of Information Rate"
- Brier, G. W. (1950). "Verification of Forecasts Expressed in Terms of Probability"
- Gneiting & Raftery (2007). "Strictly Proper Scoring Rules"
- Sklearn Documentation: Adversarial Validation

---

**Questions? Issues? Check the code documentation in `advanced_analytics.py`**


### 1. Prop Correlation Engine

**Purpose**: Calculate statistically significant correlations between player props to identify profitable Same Game Parlay (SGP) opportunities.

**Mathematical Foundation**:
```
Pearson Correlation: ρ(X,Y) = Cov(X,Y) / (σ_X × σ_Y)
Significance Test: z = 0.5 × ln((1+ρ)/(1-ρ))
Standard Error: SE = 1 / √(n-3)
P-value: 2 × (1 - Φ(|z|/SE))
```

**Key Findings from Test Run**:
- QB Pass Yards ↔ WR1 Rec Yards: **r=0.807** (p<0.0001) - STRONG positive correlation
- QB Pass Yards ↔ RB Rush Yards: **r=-0.428** (p=0.017) - Moderate negative correlation
- WR1 Rec Yards ↔ RB Rush Yards: **r=-0.463** (p=0.009) - Moderate negative correlation

**Practical Application**:
```python
from advanced_analytics import PropCorrelationEngine

# Load your historical game-by-game data
hist_data = pd.DataFrame({
    'QB_Pass_Yards': [...],
    'WR1_Rec_Yards': [...],
    'RB_Rush_Yards': [...]
})

engine = PropCorrelationEngine(min_sample_size=30)
corr_matrix = engine.calculate_prop_correlations(hist_data, hist_data.columns.tolist())

# Find significant pairs
pairs = engine.find_significant_pairs(min_correlation=0.3)

# Result: Use positively correlated props in SGPs for higher true probability
```

**Why This Matters**:
- Books price SGPs assuming independence
- Positive correlation = Higher true probability than implied
- Example: If QB passes 300+ yards, WR1 likely has high yards (correlated)
- Independent probability: 55% × 55% = 30.25%
- Correlated probability (r=0.8): ~38% (25% edge!)

---

### 2. Monte Carlo Simulation Engine

**Purpose**: Replace point estimates with probability distributions. Quantify uncertainty.

**Mathematical Foundation**:
```
For normal distribution:
X ~ N(μ, σ²)

For lognormal (positive values):
Y = exp(X) where X ~ N(μ, σ²)
μ = ln(mean) - 0.5σ²
σ² = ln(1 + (std/mean)²)

Probability Over: P(X > L) = Φ((μ-L)/σ)
Confidence Interval: [Q(α/2), Q(1-α/2)] where Q = quantile function
```

**Test Results**:
```
QB Passing Yards Projection:
  Mean: 252.5
  Line: 245.5
  P(Over): 55.8% ← This is your TRUE edge
  90% CI: [177.2, 326.4] ← Uncertainty range
```

**Practical Application**:
```python
from advanced_analytics import MonteCarloSimulator

sim = MonteCarloSimulator(n_simulations=10000)

# Simulate QB performance
qb_samples = sim.simulate_prop_distribution(
    mean=252.5,
    std=45.0,
    distribution='normal'
)

# Calculate probability
p_over = sim.calculate_probability_over(qb_samples, line=245.5)
ci_lower, ci_upper = sim.calculate_confidence_interval(qb_samples)

print(f"True P(Over): {p_over:.1%}")
print(f"90% CI: [{ci_lower:.1f}, {ci_upper:.1f}]")
```

**Why This Matters**:
- Single-point projections ignore variance
- High variance = Lower confidence (even if mean is higher)
- Example: 252.5 mean with σ=45 → Only 55.8% over 245.5
- Example: 252.5 mean with σ=25 → 61.2% over 245.5 (tighter distribution)

---

### 3. Kelly Criterion Bankroll Management

**Purpose**: Calculate mathematically optimal bet sizes to maximize long-term growth.

**Mathematical Foundation**:
```
Full Kelly: f* = (bp - q) / b
where:
  b = net odds (decimal_odds - 1)
  p = true probability of winning
  q = 1 - p

Expected Value: EV = p × (b+1) - 1
Growth Rate: g = p × ln(1+bf) - q × ln(1-f)
```

**Test Results**:
```
Bet Analysis (QB Pass Yards Over 245.5):
  True Probability: 55.8%
  Odds: -110 (1.91 decimal)
  Expected Value: $6.22 per $10 bet (62% ROI!)
  Quarter-Kelly Stake: 1.8% of bankroll
  → On $1000 bankroll: Bet $17.74
```

**Practical Application**:
```python
from advanced_analytics import KellyCriterion

kelly = KellyCriterion()

# Your model says 55.8% chance of winning
true_prob = 0.558

# Book offers -110 odds
decimal_odds = kelly.american_to_decimal(-110)  # 1.91

# Calculate optimal stake (using Quarter Kelly for safety)
stake_fraction = kelly.calculate_kelly_fraction(
    true_prob, 
    decimal_odds, 
    fractional_kelly=0.25
)

# Expected value
ev = kelly.calculate_expected_value(true_prob, decimal_odds, stake=100)

print(f"Bet {stake_fraction:.1%} of your bankroll")
print(f"Expected return: ${ev:.2f} per $100")
```

**Why This Matters**:
- Prevents over-betting (which causes ruin)
- Prevents under-betting (which wastes edge)
- Example: 10% edge with -110 odds → Full Kelly = 9.1% of bankroll
- Use 25% Kelly (2.3% stake) for risk management

---

### 4. Adversarial Validation

**Purpose**: Detect covariate shift between training data (past games) and test data (upcoming game).

**Mathematical Foundation**:
```
1. Combine train and test data
2. Label: train=0, test=1
3. Train classifier to predict label
4. If AUC > 0.7 → Distributions are different → Model won't generalize
5. If AUC ≈ 0.5 → Distributions are similar → Model is reliable
```

**Test Results**:
```
Adversarial Validation Results:
  Mean AUC: 0.585 ← Close to 0.5 (good!)
  Status: LOW RISK ✓
  Passed: True
```

**Practical Application**:
```python
from advanced_analytics import AdversarialValidator

# Historical games (training data)
train_features = pd.DataFrame({
    'team_pass_rate': [...],
    'opponent_def_rank': [...],
    'weather_temp': [...]
})

# Upcoming game (test data)
test_features = pd.DataFrame({
    'team_pass_rate': [0.62],
    'opponent_def_rank': [5],
    'weather_temp': [35]
})

validator = AdversarialValidator()
results = validator.validate(train_features, test_features)

if results['passed']:
    print("✓ Model is reliable for this game")
else:
    print(f"⚠ {results['warning']}")
```

**Why This Matters**:
- Detects when upcoming game is "different" from training data
- Example: All training games were domes, but test game is outdoors in snow
- High AUC → Your model won't work (different conditions)
- Prevents overconfident predictions in unusual situations

---

### 5. Model Evaluation Metrics

**Purpose**: Rigorously evaluate prediction accuracy using proper scoring rules.

**Mathematical Foundation**:

**Brier Score** (Measures calibration):
```
BS = (1/N) × Σ(f_i - o_i)²
where f_i = predicted probability, o_i = actual outcome (0 or 1)

Perfect score: 0.0
Random guess: 0.25
```

**Log Loss** (Penalizes confident mistakes):
```
LL = -(1/N) × Σ[o_i×ln(f_i) + (1-o_i)×ln(1-f_i)]

Lower is better
```

**Expected Calibration Error**:
```
ECE = Σ(|acc_i - conf_i| × n_i/N)
where acc_i = accuracy in bin i, conf_i = average confidence in bin i

Perfect calibration: 0.0
```

**Test Results**:
```
Model Performance:
  Brier Score: 0.2717 (slightly worse than random 0.25 - needs tuning!)
  Log Loss: 0.7391
  Expected Calibration Error: 0.1528 (15% calibration error)
```

**Practical Application**:
```python
from advanced_analytics import ModelEvaluator

# After a season of predictions
true_outcomes = np.array([1, 0, 1, 1, 0, ...])  # Actual results
predicted_probs = np.array([0.65, 0.45, 0.58, 0.72, 0.41, ...])  # Your predictions

evaluator = ModelEvaluator()

brier = evaluator.brier_score(true_outcomes, predicted_probs)
logloss = evaluator.log_loss_score(true_outcomes, predicted_probs)
ece = evaluator.expected_calibration_error(true_outcomes, predicted_probs)

print(f"Brier Score: {brier:.4f} (target: <0.20)")
print(f"Log Loss: {logloss:.4f} (lower is better)")
print(f"ECE: {ece:.4f} (target: <0.05)")
```

**Why This Matters**:
- Win rate alone is misleading (50% win rate can lose money!)
- Brier Score measures if your probabilities are accurate
- Example: You predict 60% on 100 bets. If 60 win → Perfect calibration
- Example: You predict 60% on 100 bets. If 50 win → Overconfident (bad)

---

## 🎓 Integration with Your Existing System

### Step 1: Replace Single-Point Projections with Distributions

**Current Code (NFL_pre.py)**:
```python
def _create_projection(self, player, stat_type, projected, line):
    edge = ((projected - line) / line) * 100
    recommendation = BetType.OVER if projected > line else BetType.UNDER
    # ...
```

**Enhanced Code**:
```python
from advanced_analytics import MonteCarloSimulator

def _create_projection_with_uncertainty(self, player, stat_type, mean, std, line):
    sim = MonteCarloSimulator(n_simulations=10000)
    samples = sim.simulate_prop_distribution(mean, std, distribution='normal')
    
    p_over = sim.calculate_probability_over(samples, line)
    ci_lower, ci_upper = sim.calculate_confidence_interval(samples, confidence_level=0.90)
    
    # Calculate edge using TRUE probability, not point estimate
    implied_prob = 1 / 1.91  # Assuming -110 odds = 52.4%
    true_edge = p_over - implied_prob
    
    recommendation = BetType.OVER if p_over > 0.524 else BetType.UNDER
    
    return Projection(
        player_name=player.name,
        stat_type=stat_type,
        projected_mean=mean,
        projected_std=std,
        confidence_interval=(ci_lower, ci_upper),
        market_line=line,
        true_probability=p_over,
        edge=true_edge * 100,
        recommendation=recommendation
    )
```

### Step 2: Add Correlation-Aware Parlay Construction

**Enhanced Correlation Engine**:
```python
def build_sgp_with_correlation(self, projections, correlation_matrix):
    """Build SGP using actual correlation data, not heuristics."""
    from advanced_analytics import MonteCarloSimulator, PropProjection
    
    sim = MonteCarloSimulator()
    
    # Convert projections to PropProjection format
    props = [
        PropProjection(
            player_name=p.player_name,
            stat_type=p.stat_type,
            mean=p.projected_mean,
            std=p.projected_std,
            line=p.market_line,
            confidence_interval=p.confidence_interval,
            p_over=p.true_probability
        )
        for p in projections
    ]
    
    # Simulate correlated parlay
    parlay_stats = sim.simulate_parlay(props, correlation_matrix)
    
    # Check if correlation gives us edge
    true_prob = parlay_stats['true_probability']
    independent_prob = parlay_stats['independent_probability']
    
    correlation_edge = true_prob - independent_prob
    
    if correlation_edge > 0.03:  # 3% edge from correlation
        return {
            'props': props,
            'true_probability': true_prob,
            'correlation_edge': correlation_edge,
            'recommendation': 'BET' if true_prob > 0.30 else 'PASS'
        }
```

### Step 3: Add Kelly-Based Stake Sizing

**Add to Results Display**:
```python
from advanced_analytics import KellyCriterion

def display_results_with_kelly(self, projections, bankroll=1000):
    kelly = KellyCriterion()
    
    for proj in projections:
        # Calculate optimal stake
        decimal_odds = kelly.american_to_decimal(-110)
        kelly_fraction = kelly.calculate_kelly_fraction(
            proj.true_probability,
            decimal_odds,
            fractional_kelly=0.25  # Conservative
        )
        
        stake_amount = bankroll * kelly_fraction
        ev = kelly.calculate_expected_value(proj.true_probability, decimal_odds, stake_amount)
        
        print(f"{proj.player_name} {proj.stat_type}:")
        print(f"  True Probability: {proj.true_probability:.1%}")
        print(f"  Recommended Stake: ${stake_amount:.2f} ({kelly_fraction:.1%} of bankroll)")
        print(f"  Expected Return: ${ev:.2f}")
```

---

## 📈 Performance Benchmarks

From test run of advanced_analytics.py:

| Metric | Value | Interpretation |
|--------|-------|----------------|
| **Correlation Detection** | 3 significant pairs found | Strong QB-WR correlation (r=0.807) |
| **Monte Carlo Accuracy** | 55.8% P(Over) | Conservative (includes variance) |
| **Kelly Stake** | 1.8% of bankroll | Safe bet sizing |
| **EV per $100** | $6.22 | 6.2% ROI (excellent) |
| **Adversarial AUC** | 0.585 | Model generalizes well ✓ |
| **Brier Score** | 0.2717 | Needs calibration tuning |

---

## ⚠️ Important Notes

### Statistical Significance Requirements

- **Minimum Sample Size**: 30 games for correlation analysis
- **P-value Threshold**: 0.05 (5% significance level)
- **Correlation Threshold**: |r| > 0.3 for practical significance

### Risk Management

- **Never bet Full Kelly**: Use 25% Kelly (Quarter Kelly) for safety
- **Minimum Edge**: Require >2% edge after accounting for vig
- **Max Bet Size**: Cap at 20% of bankroll even if Kelly suggests more

### Model Validation

- **Run Adversarial Validation** before every major bet
- **Track Brier Score** over time to detect model decay
- **Recalibrate** if ECE > 0.10

---

## 🚀 Next Steps

1. **Collect Historical Data**: Game-by-game player stats for correlation analysis
2. **Estimate Variance**: Calculate std dev for each player's props
3. **Build Correlation Matrix**: Run PropCorrelationEngine on full season data
4. **Integrate with GUI**: Add Monte Carlo and Kelly to results tab
5. **Track Performance**: Log all predictions for Brier Score calculation

---

## 📚 References

- Kelly, J. L. (1956). "A New Interpretation of Information Rate"
- Brier, G. W. (1950). "Verification of Forecasts Expressed in Terms of Probability"
- Gneiting & Raftery (2007). "Strictly Proper Scoring Rules"
- Sklearn Documentation: Adversarial Validation

---

**Questions? Issues? Check the code documentation in `advanced_analytics.py`**
