# =====================================================================
# CELL 11 — PER-LAYER DECOMPOSITION
# Where does the persona diverge, and where is the reaction shared?
#
# Paste after CELL 8. Requires: df, hidden_store, project(), 
# state_at_turn(), N_LAYERS, BEST_LAYERS  (i.e. run the notebook first).
#
# The hypothesis under test:
#   - mid-network (~L16): all personas react alike  -> persona spread LOW
#   - near output (~L70-73): personas diverge       -> persona spread HIGH
# If true, persona_ratio rises with depth. If flat, the split is not
# localized to depth and the paper's claim stays a hypothesis.
# =====================================================================

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

MIN_LAYER = 16   # same a-priori cut as CELL 6 (below this = lexical echo)

# ---------------------------------------------------------------------
# 1. Per-layer state score at the REPORT turn — one row per run per layer
# ---------------------------------------------------------------------
rows = []
for _, r in df[df.parse_ok].iterrows():
    st = state_at_turn(r.run_id, r.report_turn)
    if st is None:
        continue
    sc = project(st)                       # [L]
    for L in range(N_LAYERS):
        rows.append({"run_id": r.run_id, "persona": r.persona, "test": r.test,
                     "context_tag": r.context_tag, "rating": r.rating,
                     "layer": L, "state": float(sc[L])})
per_layer = pd.DataFrame(rows)
print(f"per_layer: {len(per_layer)} rows  "
      f"({per_layer.run_id.nunique()} runs x {N_LAYERS} layers)")

# ---------------------------------------------------------------------
# 2. Two quantities per layer:
#    (a) pole_gap        = does this layer separate NEG from POS at all?
#    (b) persona_spread  = do the personas differ WITHIN the NEG pole?
# ---------------------------------------------------------------------
pole = per_layer.groupby(["layer", "context_tag"])["state"].mean().unstack()
pole_gap = (pole["NEG"] - pole["POS"]).rename("pole_gap")

neg = per_layer[per_layer.context_tag == "NEG"]
persona_means = neg.groupby(["layer", "persona"])["state"].mean().unstack()
persona_spread = persona_means.std(axis=1).rename("persona_spread_NEG")

# The pre-registered masking contrast: STATIC (+1 report) vs SOL (-1 report)
# Same situation, opposite reports. Where in the stack do they differ?
static_sol = (persona_means["STATIC"] - persona_means["SOL"]).rename("static_minus_sol")

summary = pd.concat([pole_gap, persona_spread, static_sol], axis=1)
# Normalised: persona structure relative to context structure at that layer
summary["persona_ratio"] = (summary.persona_spread_NEG /
                            summary.pole_gap.abs().replace(0, np.nan))

sm = summary.loc[MIN_LAYER:]
print("\n--- Report-turn, layers >= 16 ---")
print(sm.round(3).to_string())

print("\nBEST_LAYERS detail:")
print(summary.loc[BEST_LAYERS].round(3).to_string())

# ---------------------------------------------------------------------
# 3. THE DECISIVE COMPARISON
# ---------------------------------------------------------------------
shallow = sm.loc[16:40, "persona_ratio"].mean()
deep    = sm.loc[65:79, "persona_ratio"].mean()
print(f"\nmean persona_ratio  L16-40 (mid) : {shallow:.3f}")
print(f"mean persona_ratio  L65-79 (deep): {deep:.3f}")
if deep > shallow * 1.5:
    print(">>> SUPPORTS the hypothesis: persona structure grows toward the output.")
elif shallow > deep * 1.5:
    print(">>> CONTRADICTS it: persona structure is larger mid-network.")
else:
    print(">>> FLAT: no depth localization. Report it as a null.")

# ---------------------------------------------------------------------
# 4. Same question at the MANIPULATION turns (the trajectory claim,
#    which was only ever checked at layer 16)
# ---------------------------------------------------------------------
mrows = []
for rid, hs in hidden_store.items():
    meta = df.loc[df.run_id == rid].iloc[0]
    sc = project(z(hs["hidden"]))          # [T, L]
    for i, t in enumerate(hs["turns"]):
        if t < 4 or t > 6:                 # manipulation + immediate aftermath
            continue
        for L in range(N_LAYERS):
            mrows.append({"persona": meta.persona, "context_tag": meta.context_tag,
                          "turn": t, "layer": L, "state": float(sc[i, L])})
manip = pd.DataFrame(mrows)
mneg = manip[manip.context_tag == "NEG"]
manip_pm = mneg.groupby(["layer", "persona"])["state"].mean().unstack()
manip_spread = manip_pm.std(axis=1)
manip_pole = manip.groupby(["layer", "context_tag"])["state"].mean().unstack()
manip_gap = (manip_pole["NEG"] - manip_pole["POS"])
manip_ratio = (manip_spread / manip_gap.abs().replace(0, np.nan))

print(f"\n--- Manipulation turns (4-6) ---")
print(f"persona_ratio L16-40 : {manip_ratio.loc[16:40].mean():.3f}")
print(f"persona_ratio L65-79 : {manip_ratio.loc[65:79].mean():.3f}")
print("(If this is flat but the REPORT turn is not, that is the cleanest")
print(" version of the finding: shared reaction, persona-specific report.)")

# ---------------------------------------------------------------------
# 5. Plots
# ---------------------------------------------------------------------
fig = go.Figure()
fig.add_trace(go.Scatter(x=sm.index, y=sm.pole_gap, name="pole gap (NEG-POS)",
                         line=dict(width=3)))
fig.add_trace(go.Scatter(x=sm.index, y=sm.persona_spread_NEG,
                         name="persona spread within NEG", line=dict(width=3)))
fig.add_trace(go.Scatter(x=sm.index, y=sm.static_minus_sol.abs(),
                         name="|Static - Sol| (masking pair)",
                         line=dict(width=2, dash="dot")))
fig.update_layout(title="Report turn: context structure vs persona structure, by layer",
                  xaxis_title="layer", yaxis_title="affect-score units")
fig.show()

fig2 = px.line(sm.reset_index(), x="layer", y="persona_ratio",
               title="Persona structure relative to context structure, by layer"
                     "<br><sup>rising = personas diverge toward the output</sup>")
fig2.show()

fig3 = px.line(persona_means.loc[MIN_LAYER:].reset_index().melt(
                   id_vars="layer", var_name="persona", value_name="state"),
               x="layer", y="state", color="persona",
               title="Report-turn state by persona and layer (NEG pole only)"
                     "<br><sup>if lines converge mid-network and fan out deep,"
                     " the hypothesis holds</sup>")
fig3.show()

summary.to_csv("per_layer_summary.csv")
per_layer.to_csv("per_layer_report_turn.csv", index=False)
print("\nSaved: per_layer_summary.csv, per_layer_report_turn.csv")
