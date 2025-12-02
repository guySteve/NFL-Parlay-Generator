#!/usr/bin/env python3
"""
Matchup Narrative Engine - Generate Human-Readable Analysis

Creates natural language descriptions of matchups based on EPA/DVOA metrics.
Explains what to expect in plain English with reasoning.
"""

from typing import Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class NarrativeAnalysis:
    """Container for narrative analysis results."""
    offensive_outlook: str
    defensive_outlook: str
    key_matchup: str
    game_script_prediction: str
    confidence_note: str
    full_narrative: str
    confidence_score: float
    derivation_explanation: str


class MatchupNarrator:
    """Generates narrative analysis of team matchups."""
    
    # Interpretation thresholds
    EPA_ELITE = -0.10
    EPA_GOOD = -0.04
    EPA_AVERAGE = 0.04
    EPA_POOR = 0.10
    
    DVOA_ELITE = -15.0
    DVOA_GOOD = -5.0
    DVOA_AVERAGE = 5.0
    DVOA_POOR = 15.0
    
    def __init__(self, ai_modifier: float = 1.0):
        """
        Initialize narrator.
        
        Args:
            ai_modifier: Adjustment factor for AI analysis (0.5 = conservative, 1.0 = standard, 1.5 = aggressive)
        """
        self.ai_modifier = ai_modifier
    
    def _interpret_def_epa(self, epa: float) -> Tuple[str, str]:
        """
        Interpret defensive EPA value.
        
        Returns:
            (quality_descriptor, explanation)
        """
        if epa <= self.EPA_ELITE:
            return "elite", "consistently preventing scoring opportunities"
        elif epa <= self.EPA_GOOD:
            return "strong", "limiting opponent efficiency"
        elif epa <= self.EPA_AVERAGE:
            return "average", "performing at league-average level"
        elif epa <= self.EPA_POOR:
            return "below average", "struggling to prevent scoring"
        else:
            return "weak", "allowing high-efficiency offense"
    
    def _interpret_dvoa(self, dvoa: float, metric_type: str = "pass") -> Tuple[str, str]:
        """
        Interpret DVOA value.
        
        Args:
            dvoa: DVOA percentage
            metric_type: "pass" or "run"
            
        Returns:
            (quality_descriptor, explanation)
        """
        action = "throwing" if metric_type == "pass" else "running"
        
        if dvoa <= self.DVOA_ELITE:
            return "elite", f"shutting down {action} attacks"
        elif dvoa <= self.DVOA_GOOD:
            return "solid", f"defending {action} plays well"
        elif dvoa <= self.DVOA_AVERAGE:
            return "average", f"average against the {metric_type}"
        elif dvoa <= self.DVOA_POOR:
            return "vulnerable", f"giving up yards via {action}"
        else:
            return "exploitable", f"major weakness against the {metric_type}"
    
    def _interpret_off_epa(self, epa: float) -> Tuple[str, str]:
        """
        Interpret offensive EPA (recent form).
        
        Returns:
            (form_descriptor, explanation)
        """
        if epa >= 0.15:
            return "hot", "clicking on all cylinders lately"
        elif epa >= 0.08:
            return "strong", "executing well in recent games"
        elif epa >= -0.05:
            return "average", "performing at typical level"
        elif epa >= -0.12:
            return "struggling", "having trouble moving the ball"
        else:
            return "cold", "offense has stalled recently"
    
    def generate_narrative(
        self,
        team_name: str,
        opponent_name: str,
        spread: float,
        opponent_def_epa: float,
        opponent_dvoa_pass: float,
        opponent_dvoa_run: float,
        team_offense_epa_l4: float
    ) -> NarrativeAnalysis:
        """
        Generate complete matchup narrative in Tony Romo's conversational style.
        
        Args:
            team_name: Team being analyzed
            opponent_name: Opponent team
            spread: Point spread (negative = favorite)
            opponent_def_epa: Opponent's defensive EPA
            opponent_dvoa_pass: Opponent's DVOA vs pass
            opponent_dvoa_run: Opponent's DVOA vs run
            team_offense_epa_l4: Team's offensive EPA (last 4 games)
            
        Returns:
            NarrativeAnalysis object with all narrative components
        """
        # Interpret metrics
        def_quality, def_explain = self._interpret_def_epa(opponent_def_epa)
        pass_quality, pass_explain = self._interpret_dvoa(opponent_dvoa_pass, "pass")
        run_quality, run_explain = self._interpret_dvoa(opponent_dvoa_run, "run")
        off_form, off_explain = self._interpret_off_epa(team_offense_epa_l4)
        
        # Calculate narrative confidence score
        confidence_factors = []
        
        # Factor 1: Data completeness (40% weight)
        if all([opponent_def_epa != 0, opponent_dvoa_pass != 0, 
                opponent_dvoa_run != 0, team_offense_epa_l4 != 0]):
            confidence_factors.append(40.0)
        else:
            missing = sum([1 for x in [opponent_def_epa, opponent_dvoa_pass, 
                                       opponent_dvoa_run, team_offense_epa_l4] if x == 0])
            confidence_factors.append(40.0 * (1 - missing/4))
        
        # Factor 2: Metric clarity (30% weight) - stronger signal = higher confidence
        signal_strength = abs(opponent_dvoa_pass - opponent_dvoa_run) / 20.0
        confidence_factors.append(min(30.0, 15.0 + signal_strength * 15.0))
        
        # Factor 3: Offensive form consistency (30% weight)
        if abs(team_offense_epa_l4) > 0.10:  # Strong signal either way
            confidence_factors.append(30.0)
        elif abs(team_offense_epa_l4) > 0.05:
            confidence_factors.append(22.0)
        else:
            confidence_factors.append(15.0)
        
        narrative_confidence = sum(confidence_factors)
        
        # Build derivation explanation
        derivation_parts = [
            "🎯 **HOW THIS NARRATIVE WAS CREATED:**\n",
            f"\n**1. Data Inputs Used ({confidence_factors[0]:.0f}/40 pts):**",
            f"   • Opponent Defensive EPA: {opponent_def_epa:+.3f} → Defense is {def_quality}",
            f"   • Opponent DVOA vs Pass: {opponent_dvoa_pass:+.1f}% → {pass_quality} pass defense",
            f"   • Opponent DVOA vs Run: {opponent_dvoa_run:+.1f}% → {run_quality} run defense",
            f"   • {team_name} Offense EPA (L4): {team_offense_epa_l4:+.3f} → Offense is {off_form}",
            f"\n**2. Matchup Clarity ({confidence_factors[1]:.0f}/30 pts):**",
            f"   • Pass vs Run DVOA Difference: {abs(opponent_dvoa_pass - opponent_dvoa_run):.1f}%",
            f"   • Larger difference = clearer exploitable weakness = higher confidence",
        ]
        
        if abs(opponent_dvoa_pass - opponent_dvoa_run) > 15:
            if opponent_dvoa_pass > opponent_dvoa_run:
                derivation_parts.append(f"   • ✅ CLEAR EDGE: Pass defense {opponent_dvoa_pass - opponent_dvoa_run:.1f}% worse than run")
            else:
                derivation_parts.append(f"   • ✅ CLEAR EDGE: Run defense {opponent_dvoa_run - opponent_dvoa_pass:.1f}% worse than pass")
        else:
            derivation_parts.append(f"   • ⚠️ NO CLEAR EDGE: Defense balanced, harder to exploit")
        
        derivation_parts.extend([
            f"\n**3. Offensive Form Signal ({confidence_factors[2]:.0f}/30 pts):**",
            f"   • Recent EPA: {team_offense_epa_l4:+.3f}",
        ])
        
        if team_offense_epa_l4 > 0.10:
            derivation_parts.append(f"   • ✅ STRONG SIGNAL: Hot offense (>0.10 EPA)")
        elif team_offense_epa_l4 < -0.10:
            derivation_parts.append(f"   • ✅ STRONG SIGNAL: Cold offense (<-0.10 EPA)")
        else:
            derivation_parts.append(f"   • ⚠️ WEAK SIGNAL: Average performance (mixed data)")
        
        derivation_parts.extend([
            f"\n**4. Game Script Context:**",
            f"   • Point Spread: {team_name} {spread:+.1f}",
        ])
        
        if abs(spread) > 7:
            derivation_parts.append(f"   • Large spread impacts expected play-calling (pass/run ratio)")
        else:
            derivation_parts.append(f"   • Tight spread = standard balanced offense expected")
        
        derivation_parts.append(f"\n**📊 FINAL CONFIDENCE: {narrative_confidence:.0f}%**")
        
        if narrative_confidence >= 80:
            derivation_parts.append("   ✅ HIGH - Strong data + clear edges")
        elif narrative_confidence >= 65:
            derivation_parts.append("   ⚠️ MODERATE - Some uncertainty in matchup")
        else:
            derivation_parts.append("   ⚠️ LOW - Limited data or unclear advantages")
        
        derivation_explanation = "\n".join(derivation_parts)
        
        # Determine game script (Tony Romo style - conversational and insightful)
        if spread < -7:
            game_script = f"Here's what I like about this one - {team_name} is a big favorite here. When you're up by two scores, you know what happens? You're gonna see them lean on that run game, control the clock, keep that defense fresh."
            script_impact = "Look for increased rushing volume if they get ahead early."
        elif spread > 7:
            game_script = f"Now {team_name}'s gonna be playing from behind as a big dog here. And Jim, when you're down like that, you gotta throw the football. You can't run your way back into this game."
            script_impact = "Passing volume's gonna spike, especially in that second half."
        elif spread < -3:
            game_script = f"So {team_name}'s favored by a field goal or so. That's interesting because they'll probably stick to their bread and butter - balanced attack, maybe lean run if they get a lead."
            script_impact = "Pretty standard game flow, balanced playcalling."
        elif spread > 3:
            game_script = f"You know what I'm seeing here? {team_name}'s getting points, so if they fall behind, watch for them to open up the passing game. They might need to be aggressive."
            script_impact = "Slight pass-heavy lean if they're trailing."
        else:
            game_script = f"I love these pick'em games, Jim! Both teams are just gonna go out there and run their offense. No game script pressure, just good football."
            script_impact = "Standard offensive distribution for both sides."
        
        # Offensive outlook (Romo style)
        if team_offense_epa_l4 > 0.10:
            offensive_outlook = f"Here's the thing about {team_name} right now - they are ROLLING. I'm talking {team_offense_epa_l4:+.2f} EPA per play, that's elite stuff. Everything's clicking - QB's seeing the field, they're hitting chunk plays, this offense is dangerous right now."
        elif team_offense_epa_l4 > 0.05:
            offensive_outlook = f"Look at {team_name}'s offense - they've been pretty solid lately, getting about {team_offense_epa_l4:+.2f} EPA per play. They're executing, moving the chains, doing what they need to do."
        elif team_offense_epa_l4 > -0.05:
            offensive_outlook = f"So {team_name}'s offense has been... okay. Not great, not terrible. They're sitting around {team_offense_epa_l4:+.2f} EPA - that's pretty average. They need something to get this thing going."
        else:
            offensive_outlook = f"Alright, real talk - {team_name}'s offense is struggling. {team_offense_epa_l4:+.2f} EPA, that's rough. They're not sustaining drives, not finishing in the red zone. This unit needs to figure it out quick."
        
        # Defensive outlook (opponent) - Romo style
        if opponent_def_epa < -0.08:
            defensive_outlook = f"Now {opponent_name}'s defense? They're legit. {opponent_def_epa:+.2f} EPA allowed - that's top tier. But here's what's interesting - they're {pass_quality} against the pass and {run_quality} against the run. "
        elif opponent_def_epa < 0:
            defensive_outlook = f"{opponent_name}'s got a solid defense, nothing spectacular but they get the job done. {opponent_def_epa:+.2f} EPA allowed. What I'm watching is how they defend differently - {pass_quality} vs the pass, {run_quality} vs the run. "
        else:
            defensive_outlook = f"I'm gonna be honest with you - {opponent_name}'s defense is not good. {opponent_def_epa:+.2f} EPA, that's bottom third of the league. They're {pass_quality} against the pass and {run_quality} against the run. "
        
        # Key matchup analysis (Romo-style excitement)
        pass_vs_run_diff = opponent_dvoa_pass - opponent_dvoa_run
        
        if abs(pass_vs_run_diff) > 15:
            if pass_vs_run_diff > 0:
                # Defense worse vs pass
                key_matchup = f"💡 **Jim, THIS is the matchup I'm watching!** {opponent_name}'s pass defense? {opponent_dvoa_pass:+.1f}% DVOA - that's {abs(pass_vs_run_diff):.0f} points worse than their run defense! "
                
                if team_offense_epa_l4 > 0:
                    key_matchup += f"And with {team_name}'s offense clicking right now? Oh man, this could get fun through the air. **I'm looking OVER on those QB and WR props all day.**"
                else:
                    key_matchup += f"Even though {team_name}'s offense has been struggling, THIS is where they attack. The passing game is the path back."
            else:
                # Defense worse vs run
                key_matchup = f"💡 **Okay, HERE's your money matchup right here!** {opponent_name} cannot stop the run - {opponent_dvoa_run:+.1f}% DVOA, that's {abs(pass_vs_run_diff):.0f} points worse than pass defense! "
                
                if spread < 0:
                    key_matchup += f"{team_name}'s favored, which means what? They're gonna pound the rock, control that clock. **RB props? I'm smashing those OVERS.**"
                else:
                    key_matchup += f"Even as underdogs, if {team_name} can establish this run game early, they control the tempo of this whole game."
        else:
            key_matchup = f"You know what's tough here? {opponent_name} defends pass and run pretty evenly - no real weakness to exploit. {team_name}'s gonna have to just execute, beat 'em straight up."
        
        # Full narrative (Tony Romo broadcast style)
        full_narrative = f"""
🏈 **ROMO'S TAKE: {team_name} vs {opponent_name}**

**Game Setup**:
{game_script}
{script_impact}

**What I'm Seeing from {team_name}'s Offense**:
{offensive_outlook}

**The {opponent_name} Defense**:
{defensive_outlook}

{key_matchup}

**The Bottom Line**:
"""
        
        # Generate bottom line (Romo-style confident take)
        if team_offense_epa_l4 > 0.10 and opponent_def_epa > 0.05:
            bottom_line = f"This is a GREAT spot for {team_name}. Hot offense, weak defense? **I'm going OVER on their team total, and I'm loading up on their skill position props.** This could get out of hand."
        elif team_offense_epa_l4 < -0.05 and opponent_def_epa < -0.08:
            bottom_line = f"Look, I'm not gonna sugarcoat it - struggling offense versus elite defense? **This screams UNDER. Temper those expectations** and look for the defense to make plays instead."
        elif pass_vs_run_diff > 15 and team_offense_epa_l4 > 0:
            bottom_line = f"The matchup is SCREAMING pass game here. **Target those QB completions, WR receptions, receiving yards - all OVER.** This is where the offense does damage."
        elif pass_vs_run_diff < -15 and spread < -3:
            bottom_line = f"Ground and pound game right here. Favorable run matchup, favored in the game? **Load up on RB carries and rushing yards OVERS.** They're gonna feed him all day."
        else:
            bottom_line = f"This is one of those games where you stick with your studs. No crazy edges here - **play it safe, target your top guys,** and don't get cute with speculative props."
        
        full_narrative += bottom_line + f"\n\n**📊 Confidence: {narrative_confidence:.0f}%** - "
        
        if narrative_confidence >= 80:
            full_narrative += "High confidence, strong data backing this read."
        elif narrative_confidence >= 65:
            full_narrative += "Moderate confidence, some uncertainty in the matchup."
        else:
            full_narrative += "Lower confidence, proceed with caution."
        
        return NarrativeAnalysis(
            offensive_outlook=offensive_outlook,
            defensive_outlook=defensive_outlook,
            key_matchup=key_matchup,
            game_script_prediction=f"{game_script} {script_impact}",
            confidence_note=f"Narrative Confidence: {narrative_confidence:.0f}%",
            full_narrative=full_narrative,
            confidence_score=narrative_confidence,
            derivation_explanation=derivation_explanation
        )


# Example usage
if __name__ == "__main__":
    narrator = MatchupNarrator(ai_modifier=1.0)
    
    # Example: Chiefs vs Broncos
    analysis = narrator.generate_narrative(
        team_name="Kansas City Chiefs",
        opponent_name="Denver Broncos",
        spread=-7.5,
        opponent_def_epa=-0.08,  # Good defense
        opponent_dvoa_pass=12.5,  # Weak vs pass
        opponent_dvoa_run=-8.2,   # Strong vs run
        team_offense_epa_l4=0.18  # Hot offense
    )
    
    print(analysis.full_narrative)
    print("\n" + "="*70 + "\n")
    
    # Example with AI modifier
    conservative_narrator = MatchupNarrator(ai_modifier=0.5)
    conservative_analysis = conservative_narrator.generate_narrative(
        team_name="Kansas City Chiefs",
        opponent_name="Denver Broncos",
        spread=-7.5,
        opponent_def_epa=-0.08,
        opponent_dvoa_pass=12.5,
        opponent_dvoa_run=-8.2,
        team_offense_epa_l4=0.18
    )
    
    print("CONSERVATIVE MODE:")
    print(conservative_analysis.confidence_note)
