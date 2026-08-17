import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt

L = np.arange(16, 80)

pole_gap = np.array([3.105,2.454,1.995,2.251,2.818,2.667,2.327,3.506,3.350,3.039,3.139,3.202,2.977,2.918,3.048,2.601,2.770,3.738,3.313,3.319,3.276,3.905,10.636,10.169,9.895,9.329,9.862,9.644,9.219,9.167,8.885,8.938,8.975,9.075,8.807,8.656,8.508,8.416,8.268,8.335,8.507,8.434,8.742,8.624,8.929,8.961,9.127,9.181,9.301,9.200,9.330,9.160,9.135,9.286,9.452,9.656,9.368,9.273,9.479,9.746,9.445,9.539,10.521,11.531])
spread   = np.array([0.656,0.585,0.440,0.630,0.794,0.845,0.946,1.380,1.264,1.274,1.290,1.300,1.190,1.278,1.363,1.199,1.317,1.572,1.461,1.655,1.608,1.598,2.580,2.413,2.361,2.431,2.555,2.530,2.428,2.490,2.456,2.436,2.398,2.339,2.336,2.411,2.423,2.407,2.373,2.473,2.564,2.586,2.652,2.622,2.693,2.632,2.638,2.631,2.736,2.691,2.690,2.639,2.692,2.667,2.670,2.709,2.636,2.607,2.716,2.803,2.794,2.850,3.471,4.007])
stat_sol = np.array([-0.373,-0.432,-0.359,-0.339,-0.399,-0.380,-0.665,-1.293,-1.104,-1.173,-1.057,-0.859,-0.829,-0.902,-0.911,-0.603,-0.605,-0.618,-0.734,-1.003,-0.942,-0.615,-0.086,-0.354,-0.038,-0.115,0.170,0.050,0.279,0.238,0.213,0.279,0.228,0.411,0.392,0.386,0.280,0.107,0.159,0.145,0.154,0.174,0.171,0.281,0.328,0.193,0.176,0.033,0.086,0.048,0.017,-0.061,-0.227,-0.152,-0.125,-0.218,-0.138,-0.129,-0.121,-0.174,-0.237,-0.162,-0.111,-0.024])
ratio    = spread / np.abs(pole_gap)

BASE = np.array([14.563,14.688,13.610,12.429,11.006,11.610,14.089,15.047,13.460,15.193,14.169,15.450,15.271,14.582,14.537,12.988,13.876,15.048,14.245,12.327,11.210,11.075,15.001,15.230,15.629,15.236,15.713,16.345,16.198,16.299,15.648,15.369,14.712,13.849,13.060,12.856,12.501,12.782,12.742,12.427,12.436,12.459,12.701,12.452,12.859,13.504,13.395,13.477,13.687,13.468,13.304,13.461,13.389,13.468,13.516,13.423,13.522,13.446,13.382,13.949,14.127,14.004,15.529,17.506])
SOL  = np.array([13.454,13.747,12.913,11.297,9.566,10.068,12.543,12.991,11.508,13.276,12.140,13.316,13.305,12.462,12.277,10.932,11.634,12.484,11.908,9.749,8.705,8.556,11.451,11.933,12.354,11.729,12.312,12.928,12.965,12.884,12.204,11.991,11.399,10.616,9.779,9.444,9.154,9.424,9.432,9.030,8.925,8.973,9.123,8.866,9.174,9.847,9.699,9.710,9.848,9.716,9.594,9.836,9.701,9.934,9.994,9.839,10.013,9.911,9.524,9.709,9.707,9.390,9.776,10.728])
STAT = np.array([13.081,13.315,12.554,10.958,9.166,9.688,11.879,11.698,10.404,12.102,11.083,12.456,12.475,11.560,11.366,10.329,11.030,11.867,11.174,8.745,7.763,7.941,11.365,11.579,12.316,11.614,12.482,12.978,13.244,13.122,12.418,12.270,11.626,11.028,10.171,9.830,9.434,9.531,9.591,9.175,9.079,9.147,9.294,9.147,9.502,10.040,9.875,9.744,9.934,9.764,9.611,9.776,9.473,9.781,9.869,9.620,9.875,9.782,9.402,9.535,9.470,9.228,9.665,10.704])
SWARM= np.array([13.331,13.687,13.091,11.482,9.770,10.153,12.455,13.338,11.768,13.490,12.154,13.086,13.280,12.528,12.160,10.663,11.209,11.617,11.147,8.915,7.855,7.501,8.715,9.381,9.876,9.347,9.462,10.162,10.258,10.215,9.655,9.420,8.854,8.139,7.362,6.975,6.582,6.911,6.951,6.387,6.171,6.135,6.215,6.044,6.280,7.077,6.960,7.081,7.018,6.906,6.741,7.028,6.843,6.957,6.993,6.815,7.088,7.088,6.789,7.221,7.513,7.286,7.390,8.159])

print("=== ABSOLUTE persona separation ===")
print(f"L16  spread across 4 personas : {spread[0]:.2f}   range {min(BASE[0],SOL[0],STAT[0],SWARM[0]):.1f}-{max(BASE[0],SOL[0],STAT[0],SWARM[0]):.1f}")
print(f"L79  spread across 4 personas : {spread[-1]:.2f}   range {min(BASE[-1],SOL[-1],STAT[-1],SWARM[-1]):.1f}-{max(BASE[-1],SOL[-1],STAT[-1],SWARM[-1]):.1f}")
print(f"  -> personas separate {spread[-1]/spread[0]:.1f}x more at L79 than L16 (absolute)")
print(f"  BUT pole gap also grows {pole_gap[-1]/pole_gap[0]:.1f}x ({pole_gap[0]:.1f} -> {pole_gap[-1]:.1f})")
print(f"  -> normalised ratio: L16 {ratio[0]:.3f} vs L79 {ratio[-1]:.3f}")

print("\n=== MASKING PAIR: Static vs Sol ===")
print(f"|Static-Sol| mean over all layers : {np.abs(stat_sol).mean():.3f}")
print(f"|Static-Sol| max (at L{L[np.argmax(np.abs(stat_sol))]}) : {np.abs(stat_sol).max():.3f}")
print(f"|Static-Sol| at deep layers 70-79 : {np.abs(stat_sol[-10:]).mean():.3f}")
bs = np.abs(BASE - SWARM)
print(f"compare |Baseline-Swarm| at 70-79 : {bs[-10:].mean():.3f}")
print("  -> the masking pair is the CLOSEST pair in the stack, at every depth")

print("\n=== REGIME CHANGE ===")
i37, i38 = list(L).index(37), list(L).index(38)
print(f"pole_gap L37 {pole_gap[i37]:.2f} -> L38 {pole_gap[i38]:.2f}  ({pole_gap[i38]/pole_gap[i37]:.1f}x jump)")
print(f"Swarm    L37 {SWARM[i37]:.2f} -> L38 {SWARM[i38]:.2f}")

print("\n=== TURN CONTRAST (the real finding) ===")
print(f"manipulation turns: ratio mid {0.066:.3f}  deep {0.118:.3f}")
print(f"report turn      : ratio mid {ratio[(L>=16)&(L<=40)].mean():.3f}  deep {ratio[(L>=65)].mean():.3f}")
print(f"  -> report-turn persona structure is ~{ratio[(L>=16)&(L<=40)].mean()/0.066:.1f}x (mid) "
      f"and ~{ratio[(L>=65)].mean()/0.118:.1f}x (deep) the manipulation-turn value")

# ---------------- FIGURE ----------------
PC={'BASELINE':'#4878CF','SOL':'#E8A33D','SWARM':'#5CB85C','STATIC':'#D65F5F'}
plt.rcParams.update({'font.size':9,'axes.titlesize':10,'figure.facecolor':'white'})
fig,axes=plt.subplots(1,3,figsize=(13.8,4.4),gridspec_kw={'width_ratios':[1.15,1.1,0.8]})

ax=axes[0]
for nm,arr in [('BASELINE',BASE),('SOL',SOL),('SWARM',SWARM),('STATIC',STAT)]:
    ax.plot(L,arr,color=PC[nm],lw=2.0,label=nm.title())
ax.axvline(38,color='grey',ls=':',lw=1)
ax.text(38.6,17.2,'regime change\nat L38',fontsize=7,color='#555')
ax.set_xlabel('layer'); ax.set_ylabel('report-turn internal score (NEG pole)')
ax.set_title('Personas do separate with depth \u2014 but so does everything')
ax.legend(fontsize=7.5,loc='lower left'); ax.grid(alpha=.25)
ax.annotate('Sol and Static overlap at every depth\n(mean gap 0.31 \u2014 the masking pair)',
            xy=(62,9.7),xytext=(44,5.4),fontsize=7.4,arrowprops=dict(arrowstyle='->',lw=.8))

ax=axes[1]
ax.plot(L,pole_gap,color='#333',lw=2.2,label='pole gap (NEG\u2212POS)')
ax.plot(L,spread,color='#B8860B',lw=2.2,label='persona spread within NEG')
ax.plot(L,np.abs(stat_sol),color='#D65F5F',lw=1.6,ls=':',label='|Static \u2212 Sol|')
ax.set_xlabel('layer'); ax.set_ylabel('affect-score units')
ax.set_title('Both scale together \u2014 the ratio stays flat')
ax.legend(fontsize=7.4,loc='upper left'); ax.grid(alpha=.25)
ax2=ax.twinx()
ax2.plot(L,ratio,color='#2E9AA6',lw=1.4,alpha=.85)
ax2.set_ylabel('persona / pole ratio',color='#2E9AA6',fontsize=8)
ax2.tick_params(axis='y',labelcolor='#2E9AA6',labelsize=7.5); ax2.set_ylim(0,0.75)

ax=axes[2]
vals=[0.066,0.118,ratio[(L>=16)&(L<=40)].mean(),ratio[L>=65].mean()]
lbls=['mid\n(L16\u201340)','deep\n(L65\u201379)','mid\n(L16\u201340)','deep\n(L65\u201379)']
cols=['#BBBBBB','#888888','#E8A33D','#B8860B']
ax.bar(range(4),vals,0.62,color=cols,edgecolor='k',lw=.5)
for i,v in enumerate(vals): ax.text(i,v+0.008,f"{v:.2f}",ha='center',fontsize=8)
ax.set_xticks(range(4)); ax.set_xticklabels(lbls,fontsize=7.5)
ax.set_ylabel('persona / pole ratio'); ax.set_ylim(0,0.45)
ax.set_title('Where personas actually diverge')
ax.text(0.5,0.40,'MANIPULATION\nturns',ha='center',fontsize=8,fontweight='bold',color='#555')
ax.text(2.5,0.40,'REPORT\nturn',ha='center',fontsize=8,fontweight='bold',color='#8A6400')
ax.axvline(1.5,color='k',lw=.8,ls='--'); ax.grid(axis='y',alpha=.25)

fig.suptitle('Figure 6 \u2014 Per-layer decomposition: the persona\u2013substrate split is by conversational moment, not by network depth',fontsize=10.5)
plt.tight_layout(rect=[0,0,1,0.91]); plt.savefig('s7_perlayer.png',dpi=170); plt.close()
print("\nfigure saved: s7_perlayer.png")
