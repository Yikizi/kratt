# Statistical Uncertainty Reporting for Kratt Wake-Word Evaluation

## Executive summary

For this thesis, the cleanest and most defensible reporting policy is to treat clip-level recall and hard-negative false-positive rate as **binomial** quantities, and streaming false accepts per hour as a **count rate over exposure time**. In practice, that means: use a **95% Wilson score interval** for clip-level recall and hard-negative false-positive rate, report the **exact observed counts** alongside every percentage, and use an **exact Poisson/Garwood interval** for false accepts per hour with the number of observed events and the total negative-audio duration shown explicitly. This is consistent with the statistical literature on binomial intervals, with wake-word / keyword-spotting practice that evaluates miss-vs-false-alarm tradeoffs at fixed false alarms per hour, and with broader evaluation guidance that separates model selection from final testing. citeturn22view0turn16view0turn16view1turn10view1

The headline practical rules are straightforward. Do **not** write “perfect recall” for 48/48, 11/11, or 145/145; write “100% observed recall” and include a confidence interval. Do **not** write “FAPH = 0” as if the true risk were zero when 0 events were observed in 3.65 h or 5.4 h; write “0 observed false accepts in T hours” and include a 95% upper bound for the underlying rate. Keep diagnostic/regression sets visually separated from final held-out claims, and keep threshold sweeps out of final test claims unless the operating point was fixed before seeing the test data. citeturn12view1turn20search1turn10view1turn10view2

A confidence interval addresses **sampling uncertainty**, not **methodological validity**. A narrow interval does not repair leakage, speaker overlap, threshold tuning on the test set, or a diagnostic set that does not represent deployment. That distinction should be stated explicitly in the thesis. citeturn10view1turn33search0

**Open questions / limitations.** The main unresolved issue is not the interval formulas themselves, but whether some of the ambient logs and user-test data are clustered strongly enough by speaker, session, device, or room condition that simple iid-style uncertainty intervals will be optimistic. For a BSc thesis, the pragmatic remedy is to keep the exact analytic intervals as the main tables, then add speaker- or session-bootstrap sensitivity analyses where clustering is most likely to matter. citeturn12view1turn12view0turn31search0

## Binomial metrics

For positive wake-word clips and hard-negative clip sets, the natural model is binomial: if \(x\) successes are observed in \(n\) trials, the point estimate is \(\hat p = x/n\). The **ordinary normal/Wald interval** is the weakest option here; Brown, Cai, and DasGupta show that its coverage behaves poorly, especially when \(n\) is small or \(\hat p\) is near 0 or 1, and the NIST/SEMATECH handbook explicitly recommends Wilson or Jeffreys for small samples and near-boundary proportions. Clopper–Pearson is exact in the coverage sense but conservative, and Jeffreys has good frequentist behavior but requires a short Bayesian explanation. For a thesis table that needs a single default across many rows, **Wilson is the best default**: it is easy to compute, behaves well at boundaries, and is easy to explain to readers. citeturn22view0turn0search1turn24view0

Use the following definitions at nominal confidence level \(1-\alpha\), with \(z = \Phi^{-1}(1-\alpha/2)\).

\[
\hat p = \frac{x}{n}
\]

**Wilson score interval**
\[
\frac{\hat p + z^2/(2n)}{1+z^2/n}
\;\pm\;
\frac{z}{1+z^2/n}
\sqrt{\frac{\hat p(1-\hat p)}{n} + \frac{z^2}{4n^2}}
\]

**Clopper–Pearson exact interval**
\[
\left[
\mathrm{Beta}^{-1}\!\left(\alpha/2; x, n-x+1\right),
\mathrm{Beta}^{-1}\!\left(1-\alpha/2; x+1, n-x\right)
\right]
\]
with the usual boundary conventions \(L=0\) when \(x=0\) and \(U=1\) when \(x=n\).

**Jeffreys equal-tailed interval**
\[
\left[
\mathrm{Beta}^{-1}\!\left(\alpha/2; x+\tfrac12, n-x+\tfrac12\right),
\mathrm{Beta}^{-1}\!\left(1-\alpha/2; x+\tfrac12, n-x+\tfrac12\right)
\right]
\]
and, for boundary cases, the modified version recommended by Brown et al. sets the lower limit to 0 when \(x=0\) and the upper limit to 1 when \(x=n\).

**Normal/Wald interval**
\[
\hat p \pm z \sqrt{\frac{\hat p(1-\hat p)}{n}}
\]

The Wilson formula is closed-form; Clopper–Pearson and Jeffreys require Beta quantiles. These are standard formulas and are trivial to implement in Python with `scipy.stats.beta.ppf` and `scipy.stats.norm.ppf`. citeturn22view0turn3view0turn0search1

For this thesis, I recommend the following policy.

1. Use **Wilson 95% intervals** as the default for all clip-level binomial rows in the main tables.
2. Report the **raw count** with the denominator in every row, not just the percentage.
3. If a row is especially sensitive because it is all successes or all failures and very small \(n\), it is acceptable to add a footnote that Clopper–Pearson would be slightly more conservative, but do not switch methods row by row in the main table.
4. If you report **false reject rate** instead of recall, derive it from the same interval: if recall has CI \([L,U]\), then FRR has CI \([1-U,\,1-L]\). citeturn22view0turn24view0

For your all-success positive examples, Wilson 95% intervals make the uncertainty very visible. If a model achieves **48/48**, the interval is about **92.6%–100.0%**. If it achieves **11/11**, the interval is about **74.1%–100.0%**. If it achieves **145/145**, the interval is about **97.4%–100.0%**. Those rows are strong evidence, but they are not “perfect recall” in the inferential sense. Jeffreys is slightly less conservative at the boundary, and Clopper–Pearson is slightly more conservative, especially at \(n=11\); that difference is exactly why the interval must be shown. citeturn22view0turn20search2

For hard-negative clip sets, the same binomial logic applies, but the interpretation is narrower. If \(x\) false positives occur in \(n\) hard-negative clips, then \(x/n\) is a **clip-level false-positive rate on that curated set**, not a deployment false-accepts-per-hour claim. Wake-word practice in deployed settings emphasizes false alarms per hour precisely because the operational problem is continuous streaming audio, while curated adversarial negatives may oversample confusables. In the Howl paper, the authors explicitly note that their negative set contained adversarial examples that “misrepresent real-world usage,” so they did not treat that set as a full deployment proxy. citeturn16view0turn7view2

This matters a great deal for your sample sizes. With a Wilson 95% interval, **0/15** false positives still implies an upper bound of about **20.4%** on that clip-level FPR. **0/60** implies about **6.0%**. **0/186** implies about **2.0%**. **0/600** still implies about **0.64%**. For the planned user-test hard negatives, **0/100** corresponds to an upper bound of about **3.7%**, and **0/150** to about **2.5%**. Those are useful regression diagnostics, but the small rows, especially \(n=15\) and \(n=60\), are far too uncertain to carry a strong standalone claim. If even **1/15** hard negatives fires, the Wilson interval is still extremely wide, about **1.2%–29.8%**. citeturn22view0turn24view0

The conservative thesis wording should therefore be: hard-negative sets diagnose **prefix, confusable, and phrase-order failure modes**; they do **not** directly estimate ambient deployment FAPH. They complement the streaming long-form negative-audio evaluation rather than replacing it. citeturn16view0turn7view2

## Poisson rate metrics

Streaming false accepts per hour are best treated as **event counts over exposure time**. If \(k\) false-accept events are observed over \(T\) hours of negative audio, the natural point estimate is
\[
\hat\lambda = \frac{k}{T}
\]
in events per hour. This matches wake-word / keyword-spotting practice, where the miss-vs-false-alarm tradeoff is commonly reported at a fixed false alarms per hour operating point because false alarms are particularly costly in real-world voice-assistant deployment. citeturn16view0turn16view1turn16view2turn16view3

A Poisson model is reasonable when false accepts are rare, exposure time is known, and events can be approximated as arising from an approximately stationary process with independent increments. But it becomes questionable when events cluster in time, when the same speaker or acoustic session dominates parts of the exposure, or when the system itself introduces dependence through score smoothing and a cooldown / refractory period. Those complications matter here: a cooldown mechanically suppresses near-duplicate events, while correlated audio and repeated session structure make independence less plausible. NIST’s uncertainty work on ROC analysis and later speech-bootstrap work both warn that analytic uncertainty formulas can underestimate uncertainty when observations are dependent. citeturn18view0turn18view1turn12view1turn12view0

The standard exact interval for a Poisson rate is the **Garwood interval** applied to the count and then divided by exposure time. For a two-sided \(100(1-\alpha)\%\) interval:
\[
\lambda_L = \frac{1}{2T}\chi^2_{2k,\alpha/2}, \qquad
\lambda_U = \frac{1}{2T}\chi^2_{2(k+1),1-\alpha/2}
\]
with \(\lambda_L = 0\) when \(k=0\). A one-sided upper \(100(1-\alpha)\%\) bound is
\[
\lambda_U^{(1\text{-sided})} = \frac{1}{2T}\chi^2_{2(k+1),1-\alpha}.
\]
For \(k=0\), this simplifies to
\[
\lambda_U^{(1\text{-sided})} = -\frac{\ln(\alpha)}{T},
\]
so the one-sided 95% upper bound is approximately \(2.996/T\) and the two-sided 95% upper limit is approximately \(3.689/T\). citeturn20search1turn7view0turn23search12

This is exactly how to report “0 observed false accepts.” The point estimate \(\hat\lambda\) is indeed 0, but the interval is not. For your example durations, the two-sided exact 95% upper bounds at \(k=0\) are:

- **3.65 h:** upper bound about **1.01/h**
- **5.4 h:** upper bound about **0.68/h**
- **3.3 h:** upper bound about **1.12/h**
- **99 h:** upper bound about **0.037/h**

If you prefer a one-sided 95% upper bound for zero-event rows, the corresponding values are about **0.82/h**, **0.55/h**, **0.91/h**, and **0.030/h**, respectively. So 0 observed events in 3.3–5.4 h only rules out fairly high false-accept rates; by contrast, 0 events in 99 h gives substantively stronger evidence of a low underlying rate. citeturn20search1turn7view0turn23search12

This is why short ambient runs should be described conservatively. If a model shows 0 observed false accepts in 3.65 h on Estonian speech, the correct thesis claim is not “the model has zero FAPH,” but rather “0 observed false accepts in 3.65 h; exact 95% upper bound 1.01 FA/h.” For a stringent low-FAPH claim, exposure duration matters almost as much as the observed count. citeturn20search1turn12view1

When Poisson assumptions are doubtful, the practical BSc-thesis answer is not to abandon the analytic interval, but to qualify it. Report the exact Poisson/Garwood interval as the main result because it is simple, standard, and easy to reproduce, then add a sentence that dependence from cooldown, session clustering, or correlated audio may make the interval optimistic. If you have natural high-level units such as file, session, or device run, a **cluster bootstrap over files/sessions** is a good sensitivity analysis for FAPH. citeturn12view1turn12view0turn31search0

## User-test clustered data

The planned user study with roughly 20–30 participants creates a different statistical problem: multiple utterances from the same participant are not independent trials. In speech evaluation, utterances from the same speaker can be correlated, and clustered binary data are precisely the setting where simple iid formulas become too optimistic unless the clustering is addressed. Mixed-effects logistic regression and cluster/block bootstrap methods were developed for exactly this situation. citeturn12view0turn12view3turn31search0

For a BSc thesis, the most pragmatic approach is:

- **Primary summary:** report the ordinary utterance-level recall and hard-negative FPR under the frozen threshold, because that directly corresponds to how many attempted interactions succeeded or failed.
- **Cluster-aware companion summary:** compute a per-participant recall \(r_i = x_i/n_i\) and a per-participant hard-negative FPR \(f_i = y_i/m_i\), then report the number of participants plus the mean or median across participants.
- **Primary uncertainty method for the user test:** perform a **participant bootstrap**. Resample participants with replacement, keep all of each resampled participant’s utterances together, recompute the chosen metric, and take the percentile 95% interval from the bootstrap distribution. This preserves the within-speaker dependence structure rather than pretending each utterance is independent. citeturn31search0turn12view0turn12view1

This split serves two goals. The utterance-level number tells the practical story of interaction success. The participant-level summary prevents talkative participants from dominating the estimate. For instance, if one participant contributes 30 positives and another contributes 6, pooled utterance-level recall weights them very differently, whereas participant-level averaging gives equal speaker weight. In a user study, both views are informative. citeturn12view0turn31search0

A **random-intercept logistic regression** is acceptable as an optional secondary analysis, especially if you want a model-based participant-adjusted overall recall estimate. Conceptually, this is a model of the form
\[
\Pr(y_{ij}=1 \mid u_j) = \operatorname{logit}^{-1}(\beta_0 + u_j),
\]
where \(u_j\) is a participant-level random effect. That is statistically principled, but for a near-submission BSc thesis it is more machinery than you need unless you are already comfortable with it. The participant bootstrap is simpler, easier to explain, and easier to reproduce quickly in Python. citeturn12view3turn32search10

The practical recommendation, therefore, is: **main table = utterance-level frozen-threshold results; supporting table = per-speaker summary; uncertainty = cluster bootstrap by participant**. If time is short, this is the best tradeoff between rigor and implementation cost. citeturn31search0turn12view0

## Reporting templates and combining test sets

The thesis tables should make the evidence size visible immediately. For every clip-level metric, show the count and denominator. For every rate metric, show the event count and total exposure hours. Percentages and rates without counts make it much harder to judge precision, especially when some rows are \(n=11\), \(n=15\), or only a few hours long. citeturn12view1turn22view0turn20search1

A good main-table style is:

| Metric type | Recommended table text |
|---|---|
| Positive recall | `100.0% (48/48; Wilson 95% CI 92.6–100.0%)` |
| Positive FRR | `0.0% (0/48 misses; 95% CI 0.0–7.4%)` |
| Hard-negative FPR | `0.0% (0/60; Wilson 95% CI 0.0–6.0%)` |
| Streaming FAPH | `0.00/h (0 events / 3.65 h; exact 95% upper bound 1.01/h)` |

This format is compact, transparent, and conservative. It also prevents the common mistake of presenting a point estimate as if precision were obvious from context. citeturn22view0turn20search1turn12view1

For decimals, keep them modest. A good rule is **one decimal place for percentages** in the main table, because values like 100.0%, 97.4%, and 74.1% are interpretable without false precision. For FA/h, use **two decimals when the rate is at least 0.1/h**, and **three decimals below 0.1/h** so that long-run evidence such as 0.037/h is not collapsed to 0.04/h or 0.0/h. For exposure duration, two decimals is usually enough for concatenated corpora. Excess decimals make weak datasets look stronger than they are.

Threshold sweeps should be split into two categories. **Validation/dev sweeps** are appropriate for choosing the operating point. **Test-set sweeps** are exploratory only unless they were pre-specified in advance. The final test tables should therefore contain **only frozen-threshold results**, with the chosen threshold identified in the text or caption. If you show a test sweep figure, label it as exploratory and keep it out of the headline claim. This is standard protection against selection bias: once the threshold is optimized on the test evidence, the nominal interval no longer reflects the full uncertainty. citeturn10view1turn10view2

For heterogeneous test sets, the statistically defensible default is **stratification first, pooling second if clearly justified**.

For **FAPH**, report Common Voice ET, LibriSpeech, DiPCo, and device/background logs as **separate rows** in the main table, because they differ in language, acoustics, speaker/session structure, and sometimes device conditions. You may add one pooled row **only if** the threshold, device class, counting logic, and post-processing rule are identical across the pooled sources and you define the estimand clearly as the rate for the **hours-weighted mixture of those corpora**. If you do pool, pool by **summing counts and summing exposure hours**:
\[
\hat\lambda_{\text{pooled}} = \frac{\sum_i k_i}{\sum_i T_i}.
\]
Do **not** average the per-hour rates arithmetically. But even when mathematically pooled, the pooled row should be supplementary rather than the main claim if the component sets are heterogeneous. citeturn16view0turn16view1turn10view1

For **recall**, keep XTTS synthetic, small real-speaker anchors, stronger real-speaker warning sets, and final user-test speakers as **separate rows**. Pool only when the pooled row corresponds to a meaningful target population. For example, pooling all final user-test positives under one frozen threshold is coherent. Pooling synthetic XTTS positives together with real-user positives into one headline recall is much less coherent and can hide the domain distinction the thesis is supposed to acknowledge. A confidence interval on a pooled convenience mixture does not solve that validity problem. citeturn10view1turn33search0

A conservative structure for the thesis is therefore:

- **Main claim tables:** final frozen-threshold, held-out or final user-test results, stratified by domain.
- **Diagnostic/regression tables:** prefix-only, confusables, reversed phrases, tiny hard-negative sets, same-device logs, threshold-sweep analyses.
- **Optional pooled rows:** clearly labeled as descriptive mixtures, never as the only headline result.

That matches both the statistical uncertainty story and the methodological-validity story the thesis needs to tell. citeturn10view1turn7view2

## Estonian thesis-ready wording

**Metoodika peatükki**

Lisaks punktihinnangutele esitame 95% usaldusvahemikud, sest mitmed wake-word’i testikomplektid on väikesed ning ainult protsendi esitamine jätaks põhjendamatult kindla mulje. Usaldusvahemik kirjeldab valimist tulenevat statistilist ebakindlust, kuid ei kõrvalda metoodilisi piiranguid, nagu võimalik mitteiseseisvus, domeeninihe või diagnostiliste andmestike piiratud esinduslikkus. Positiivsete ja kõvade negatiivsete klippide puhul kasutame Wilsoni 95% usaldusvahemikku; voogedastuse valepositiivseid sündmusi tunnis esitame sündmuste arvu ja negatiivse heli kogukestuse põhjal täpse Poissoni määra usalduspiiridega. citeturn22view0turn20search1turn10view1

**Tulemuste peatükki**

Tulemust 48/48 või 11/11 ei tõlgendata käesolevas töös kui “täiuslikku tuvastust”, vaid kui 100% vaadeldud tagasikutsumist koos vastava usaldusvahemikuga. Samuti ei tähenda 0 täheldatud valepositiivset sündmust näiteks 3,65 tunni jooksul, et tegelik FA/h oleks null; korrektne tõlgendus on “0 täheldatud sündmust T tunni jooksul”, millele lisandub 95% ülemine usalduspiir tegelikule määrale. Väikese N-iga diagnostilised komplektid on kasulikud regressioonitestid, kuid neist ei tehta üksinda tugevaid üldistusväiteid süsteemi tootmiskõlblikkuse kohta. citeturn20search1turn12view1turn7view2

## Citation list with BibTeX

For the thesis bibliography, the core sources worth citing are the original interval papers, the Brown–Cai–DasGupta review, Garwood/Ulm for Poisson rates, Cawley–Talbot for selection bias, one or two uncertainty references for dependent speech data, and a small set of KWS / wake-word papers that explicitly evaluate at fixed false alarms per hour. citeturn19search0turn20search2turn20search0turn20search1turn7view0turn10view1turn12view1turn31search0turn16view0turn29search0turn28search2turn34search10

```bibtex
@article{wilson1927probable,
  author  = {Wilson, Edwin B.},
  title   = {Probable Inference, the Law of Succession, and Statistical Inference},
  journal = {Journal of the American Statistical Association},
  volume  = {22},
  number  = {158},
  pages   = {209--212},
  year    = {1927},
  doi     = {10.1080/01621459.1927.10502953}
}

@article{clopper1934confidence,
  author  = {Clopper, C. J. and Pearson, E. S.},
  title   = {The Use of Confidence or Fiducial Limits Illustrated in the Case of the Binomial},
  journal = {Biometrika},
  volume  = {26},
  number  = {4},
  pages   = {404--413},
  year    = {1934},
  doi     = {10.1093/biomet/26.4.404}
}

@article{agresti1998approximate,
  author  = {Agresti, Alan and Coull, Brent A.},
  title   = {Approximate Is Better than ``Exact'' for Interval Estimation of Binomial Proportions},
  journal = {The American Statistician},
  volume  = {52},
  number  = {2},
  pages   = {119--126},
  year    = {1998},
  doi     = {10.1080/00031305.1998.10480550}
}

@article{brown2001interval,
  author  = {Brown, Lawrence D. and Cai, T. Tony and DasGupta, Anirban},
  title   = {Interval Estimation for a Binomial Proportion},
  journal = {Statistical Science},
  volume  = {16},
  number  = {2},
  pages   = {101--133},
  year    = {2001},
  doi     = {10.1214/ss/1009213286}
}

@article{garwood1936fiducial,
  author  = {Garwood, F.},
  title   = {(i) Fiducial Limits for the Poisson Distribution},
  journal = {Biometrika},
  volume  = {28},
  number  = {3--4},
  pages   = {437--442},
  year    = {1936},
  doi     = {10.1093/biomet/28.3-4.437}
}

@article{ulm1990smr,
  author  = {Ulm, Kurt},
  title   = {A Simple Method to Calculate the Confidence Interval of a Standardized Mortality Ratio},
  journal = {American Journal of Epidemiology},
  volume  = {131},
  number  = {2},
  pages   = {373--375},
  year    = {1990},
  doi     = {10.1093/oxfordjournals.aje.a115507}
}

@book{efron1994bootstrap,
  author    = {Efron, Bradley and Tibshirani, Robert J.},
  title     = {An Introduction to the Bootstrap},
  publisher = {Chapman and Hall/CRC},
  address   = {New York, NY},
  year      = {1994}
}

@article{cawley2010overfitting,
  author  = {Cawley, Gavin C. and Talbot, Nicola L. C.},
  title   = {On Over-fitting in Model Selection and Subsequent Selection Bias in Performance Evaluation},
  journal = {Journal of Machine Learning Research},
  volume  = {11},
  pages   = {2079--2107},
  year    = {2010}
}

@techreport{wu2018nistroc,
  author      = {Wu, Jin Chu and Martin, Alvin F. and Sanders, Gregory A. and Kacker, Raghu N.},
  title       = {Bootstrap Method versus Analytical Approach for Estimating Uncertainties of Measures in ROC Analysis on Large Datasets},
  institution = {National Institute of Standards and Technology},
  number      = {NISTIR 8218},
  year        = {2018},
  doi         = {10.6028/NIST.IR.8218}
}

@article{cheng2013clusterbootstrap,
  author  = {Cheng, Guang and Yu, Zhuqing and Huang, Jianhua Z.},
  title   = {The Cluster Bootstrap Consistency in Generalized Estimating Equations},
  journal = {Journal of Multivariate Analysis},
  volume  = {115},
  pages   = {33--47},
  year    = {2013},
  doi     = {10.1016/j.jmva.2012.09.003}
}

@article{liu2019blockwisebootstrap,
  author  = {Liu, Zhe and Peng, Fuchun},
  title   = {Statistical Testing on ASR Performance via Blockwise Bootstrap},
  journal = {arXiv preprint arXiv:1912.09508},
  year    = {2019}
}

@article{lopez2022overview,
  author  = {L{\'o}pez-Espejo, Iv{\'a}n and Tan, Zheng-Hua and Hansen, John H. L. and Jensen, Jesper},
  title   = {Deep Spoken Keyword Spotting: An Overview},
  journal = {IEEE Access},
  volume  = {10},
  pages   = {4169--4199},
  year    = {2022},
  doi     = {10.1109/ACCESS.2021.3139508}
}

@inproceedings{sainath2015cnnkws,
  author    = {Sainath, Tara N. and Parada, Carolina},
  title     = {Convolutional Neural Networks for Small-Footprint Keyword Spotting},
  booktitle = {Proceedings of Interspeech 2015},
  pages     = {1478--1482},
  year      = {2015},
  doi       = {10.21437/Interspeech.2015-352}
}

@inproceedings{tang2020howl,
  author    = {Tang, Raphael and Lee, Jaejun and Razi, Afsaneh and Cambre, Julia and Bicking, Ian and Kaye, Jofish and Lin, Jimmy},
  title     = {Howl: A Deployed, Open-Source Wake Word Detection System},
  booktitle = {Proceedings of the Second Workshop for NLP Open Source Software (NLP-OSS)},
  pages     = {61--65},
  year      = {2020}
}

@inproceedings{ghosh2022lowresource,
  author    = {Ghosh, Arindam and Fuhs, Mark and Bagchi, Deblin and Farahani, Bahman and Woszczyna, Monika},
  title     = {Low-Resource Low-Footprint Wake-Word Detection Using Knowledge Distillation},
  booktitle = {Proceedings of Interspeech 2022},
  pages     = {3739--3743},
  year      = {2022},
  doi       = {10.21437/Interspeech.2022-529}
}
```

## Checklist for implementing this in Python

Use this as the thesis implementation checklist.

- Store the following for every evaluation row: `dataset_name`, `dataset_role` (`dev`, `diagnostic`, `final_holdout`, `user_test`), `threshold_id`, `x`, `n`, `k`, `T_hours`, and whether the threshold was frozen before this run.

- For **clip-level recall / FRR / hard-negative FPR**, compute Wilson 95% intervals once and reuse them everywhere:
  - `p_hat = x / n`
  - `z = norm.ppf(0.975)`
  - Wilson lower/upper from the closed-form formula above.
  - If you need FRR, transform the recall interval as `[1 - upper_recall, 1 - lower_recall]`. citeturn22view0

- For sensitivity checks or appendix tables, optionally compute:
  - Clopper–Pearson with `beta.ppf(alpha/2, x, n-x+1)` and `beta.ppf(1-alpha/2, x+1, n-x)`.
  - Jeffreys with `beta.ppf(alpha/2, x+0.5, n-x+0.5)` and `beta.ppf(1-alpha/2, x+0.5, n-x+0.5)`, using the modified boundary convention for `x=0` or `x=n`. citeturn3view0turn22view0

- For **FAPH / FA/h**, compute:
  - `rate = k / T_hours`
  - two-sided exact Poisson/Garwood bounds using chi-square quantiles
  - for `k == 0`, also compute the one-sided 95% upper bound `-log(0.05) / T_hours`. citeturn20search1turn23search12

- For **user-test clustering**, create a participant-level dataframe and run a **bootstrap by participant**:
  1. sample participants with replacement,
  2. keep all utterances from each sampled participant,
  3. recompute the chosen metric,
  4. repeat at least 2,000 times,
  5. take the 2.5th and 97.5th percentiles. citeturn31search0turn12view0

- Keep **main tables** and **diagnostic tables** separate:
  - main tables: frozen-threshold held-out or final user-test results,
  - diagnostic tables: confusables, prefixes, reversed phrases, small regression sets, same-device logs, exploratory sweeps. citeturn10view1turn7view2

- In every final table row, show counts and exposure explicitly:
  - `Recall 100.0% (48/48; Wilson 95% CI 92.6–100.0%)`
  - `FAPH 0.00/h (0 events / 3.65 h; exact 95% upper bound 1.01/h)`.

- Do not pool heterogeneous sets by default. If you create an extra pooled FAPH row, pool by `sum(k) / sum(T)` only when threshold, device, and counting rules are identical, and label the row as a descriptive mixture, not as the only headline result. citeturn10view1turn16view0

- Add one sentence near every final-results table reminding the reader that the confidence interval quantifies sampling uncertainty **within that evaluation protocol** and does not repair leakage, dependence, or domain mismatch. citeturn10view1turn33search0