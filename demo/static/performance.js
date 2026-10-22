"use strict";
Object.assign(translations.fr, {
  performanceTab:"Comparer les performances",performanceEyebrow:"ÉVALUATION COMPARATIVE · CPU",
  performanceTitle:"Mesurer le temps et contrôler la qualité.",performanceLead:"Comparez la création d’un index documentaire avec et sans regroupement par longueur. Même modèle, mêmes textes, mêmes ressources.",
  scopeTitle:"Ce qui est comparé",scopeDescription:"Deux configurations de notre encodeur MiniLM / ONNX sur CPU : ordre d’entrée et regroupement par longueur. Ce n’est pas une comparaison avec votre outil métier, ni un essai TPU.",
  benchmarkStart:"Lancer un nouvel essai",benchmarkCancel:"Arrêter après le passage en cours",protocolShort:"48 textes · 7 paires · lots de 4 · 2 threads",
  runNote:"Prévoir plusieurs minutes. Les deux versions sont préchauffées ; leur ordre est alterné et mélangé. Les autres fonctions attendent pendant la mesure.",
  noComparison:"Pas encore de comparaison terminée.",noComparisonNote:"Lancez l’essai pour obtenir deux mesures vérifiées et les résultats bruts.",
  tableCaption:"Création complète de l’index après préchauffage",measure:"Mesure",reference:"Référence · ordre d’entrée",optimized:"Regroupement par longueur",
  qualityGate:"Le résultat fonctionnel est-il préservé ?",qualityGateNote:"Des sorties proches et des décisions identiques ne rendent pas le modèle plus juste. Les erreurs existantes restent comptées. Pertinence de recherche et temps de revue humaine ne sont pas mesurés ici.",
  costTitle:"Chiffrer une hypothèse de coût",costLead:"Saisissez votre tarif de machine. Aucun prix fournisseur n’est supposé.",hourlyRate:"Coût machine en €/heure",volume:"Nombre de textes",
  costLimit:"Extrapolation linéaire du petit lot mesuré, pour des textes et une charge comparables. Hors chargement du modèle, OCR, stockage distant, intégration et corrections humaines. Ni devis ni économie de production démontrée.",
  evidenceTitle:"Vérifier les chiffres",evidenceNote:"Protocole figé, temps bruts, prédictions et empreintes des sources.",downloadTimings:"Temps CSV",downloadEvidence:"Dossier de preuves",
  nextPilotTitle:"Ce qu’une équipe peut décider avec cet essai",nextPilotText:"Le regroupement mérite-t-il d’être retenu dans cette configuration ? Pour comparer à un outil existant, il faut ensuite un même lot représentatif, des réponses attendues et les temps de votre processus. Le classement accepté doit rester assez précis, et le coût de la revue humaine doit être inclus.",
  benchmark_busy:"Un essai comparatif est en cours. Les autres fonctions reprendront à la fin pour ne pas perturber les mesures.",
  bench_idle:"Prêt à mesurer",bench_starting:"Préparation de l’essai",bench_checking_data:"Vérification des données",bench_quality_train:"Encodage des exemples d’apprentissage",bench_quality_validation:"Calibration sur la validation",bench_quality_reference:"Contrôle des 80 tests : référence",bench_quality_optimized:"Contrôle des 80 tests : regroupement",bench_quality_pass:"Conformité des décisions vérifiée",bench_warmup:"Préchauffage",bench_warmup_done:"Préchauffage terminé",bench_measurement:"Mesure en cours",bench_measurement_done:"Mesure vérifiée",bench_complete:"Essai terminé",bench_cancelled:"Essai arrêté. Le dernier résultat terminé est conservé.",bench_failed:"Échec de l’essai. Aucun nouveau gain n’est validé ; consulter le journal du serveur.",
  cancelling:"Arrêt demandé : attente de la fin du passage en cours.",archivedRecord:"Mesure archivée livrée avec le code",localRecord:"Dernier essai terminé sur cet hôte",measuredHost:"Machine mesurée",observed_gain:"Un gain observé sur cet essai",observed_regression:"Un ralentissement observé sur cet essai",inconclusive:"Avantage non établi sur cet essai",
  gainDetail:"La borne basse de l’intervalle descriptif du rapport de vitesse dépasse 1. À confirmer sur d’autres charges et conditions.",regressionDetail:"L’intervalle descriptif du rapport de vitesse reste sous 1 : le regroupement est plus lent sur cet essai.",inconclusiveDetail:"L’intervalle descriptif du rapport de vitesse contient 1. Les mesures ne permettent pas de retenir un avantage stable.",
  medianIndex:"Durée médiane du lot complet",medianEncoding:"Dont encodage (médiane)",medianExport:"Dont export (médiane)",throughputDocs:"Textes par seconde",throughputChunks:"Fenêtres par seconde",padding:"Proportion de padding",timeRange:"Durées minimale – maximale",pairedReduction:"Réduction médiane de durée par paire",pairedSpeedup:"Rapport de vitesse apparié",pairedInterval:"Intervalle descriptif à 95 %",fasterPairs:"Paires où le regroupement est plus rapide",pairedLimit:"La médiane des rapports appariés diffère du rapport des médianes du tableau. Sept répétitions du même lot ne sont pas sept corpus indépendants. Une machine partagée peut varier.",
  equalDecisions:"Décisions de classement identiques",qualityPrecision:"Précision parmi les propositions retenues",qualityCoverage:"Propositions retenues sur le test",qualityErrors:"Propositions retenues mais erronées",qualityAbstentions:"Abstentions du modèle",qualityUnknown:"Hors périmètre acceptés à tort",numericError:"Écart maximal entre embeddings",notEvaluated:"Qualité métier non évaluée",costPrompt:"Saisissez un tarif valide pour calculer cette hypothèse.",estimatedReference:"Coût de calcul estimé · référence",estimatedOptimized:"Coût de calcul estimé · regroupement",estimatedDifference:"Écart estimé (référence − regroupement)",recordInvalid:"Un dossier de résultats invalide a été ignoré. Les temps affichés proviennent du dernier dossier vérifié.",
  reviewLimit:"Les scores ne sont pas des probabilités. Vos décisions sont conservées sur l’hôte du serveur ; elles ne réentraînent pas le modèle.",timingTitle:"Temps observés sur l’hôte du serveur",local:"Sur l’hôte de calcul",localNote:"Calcul CPU sur le Mac ou le VPS qui héberge l’application. Aucun appel à une IA externe."
});
Object.assign(translations.en, {
  performanceTab:"Compare performance",performanceEyebrow:"COMPARATIVE EVALUATION · CPU",performanceTitle:"Measure time and check quality.",performanceLead:"Compare document indexing with and without length grouping. Same model, same texts, same resources.",
  scopeTitle:"What is compared",scopeDescription:"Two configurations of our MiniLM / ONNX CPU encoder: input order and length grouping. This is not a comparison with your business tool or a TPU experiment.",
  benchmarkStart:"Run a new comparison",benchmarkCancel:"Stop after the current pass",protocolShort:"48 texts · 7 pairs · batch size 4 · 2 threads",runNote:"Allow several minutes. Both versions are warmed up; their order alternates and is shuffled. Other functions wait while measurements run.",noComparison:"No completed comparison yet.",noComparisonNote:"Run the comparison to obtain two checked measurements and raw evidence.",
  tableCaption:"Complete warm index creation",measure:"Measure",reference:"Reference · input order",optimized:"Length grouping",qualityGate:"Are functional results preserved?",qualityGateNote:"Close outputs and identical decisions do not make the model more accurate. Existing errors still count. Retrieval relevance and human-review time are not measured here.",
  costTitle:"Calculate a cost assumption",costLead:"Enter your machine rate. No provider price is assumed.",hourlyRate:"Machine cost in €/hour",volume:"Number of texts",costLimit:"Linear extrapolation from the small measured batch, assuming comparable text lengths and workload. Excludes model loading, OCR, remote storage, integration and human corrections. Neither a quote nor demonstrated production savings.",
  evidenceTitle:"Check the figures",evidenceNote:"Fixed protocol, raw times, predictions and source checksums.",downloadTimings:"Timing CSV",downloadEvidence:"Evidence archive",nextPilotTitle:"What a team can decide from this test",nextPilotText:"Is length grouping worth retaining in this configuration? Comparing with an existing tool then requires the same representative sample, expected answers and timings from your process. Accepted classifications must remain accurate enough, and human-review cost must be included.",
  benchmark_busy:"A comparison is running. Other functions will resume afterwards to avoid disturbing measurements.",bench_idle:"Ready to measure",bench_starting:"Preparing the comparison",bench_checking_data:"Checking data",bench_quality_train:"Encoding training examples",bench_quality_validation:"Calibrating on validation",bench_quality_reference:"Checking 80 tests: reference",bench_quality_optimized:"Checking 80 tests: length grouping",bench_quality_pass:"Decision agreement checked",bench_warmup:"Warmup",bench_warmup_done:"Warmup complete",bench_measurement:"Measurement running",bench_measurement_done:"Measurement checked",bench_complete:"Comparison complete",bench_cancelled:"Comparison stopped. The last completed result is retained.",bench_failed:"Comparison failed. No new gain is validated; check the server log.",cancelling:"Stop requested: waiting for the current pass to finish.",
  archivedRecord:"Archived measurement shipped with the code",localRecord:"Last comparison completed on this host",measuredHost:"Measured machine",observed_gain:"A gain observed in this run",observed_regression:"A slowdown observed in this run",inconclusive:"An advantage is not established in this run",gainDetail:"The lower bound of the descriptive speed ratio interval exceeds 1. Confirmation on other workloads and conditions is needed.",regressionDetail:"The descriptive speed ratio interval stays below 1: grouping is slower in this run.",inconclusiveDetail:"The descriptive speed ratio interval includes 1. These measurements do not establish a stable advantage.",
  medianIndex:"Median complete batch time",medianEncoding:"Encoding component (median)",medianExport:"Export component (median)",throughputDocs:"Texts per second",throughputChunks:"Chunks per second",padding:"Padding fraction",timeRange:"Minimum – maximum time",pairedReduction:"Median time reduction per pair",pairedSpeedup:"Paired speed ratio",pairedInterval:"Descriptive 95% interval",fasterPairs:"Pairs where grouping is faster",pairedLimit:"The median paired ratio differs from the ratio of the table medians. Seven repeats of the same batch are not seven independent corpora. Shared-machine conditions can vary.",
  equalDecisions:"Identical classification decisions",qualityPrecision:"Precision of accepted suggestions",qualityCoverage:"Accepted suggestions on the test set",qualityErrors:"Accepted but incorrect suggestions",qualityAbstentions:"Model abstentions",qualityUnknown:"Out-of-scope false accepts",numericError:"Maximum embedding difference",notEvaluated:"Business quality not evaluated",costPrompt:"Enter a valid rate to calculate this assumption.",estimatedReference:"Estimated compute cost · reference",estimatedOptimized:"Estimated compute cost · grouping",estimatedDifference:"Estimated difference (reference − grouping)",recordInvalid:"An invalid result directory was skipped. Displayed timings come from the last verified record.",
  reviewLimit:"Scores are not probabilities. Your decisions stay on the server host; they do not retrain the model.",timingTitle:"Times observed on the server host",local:"On the compute host",localNote:"CPU processing on the Mac or VPS hosting the application. No external AI call."
});
let comparisonState, comparisonPoll;
function money(value){return value.toLocaleString(lang,{style:"currency",currency:"EUR",minimumFractionDigits:4,maximumFractionDigits:4});}
function renderCost(){
  if(!comparisonState?.report)return;
  const rate=Number($("hourly-rate").value),volume=Number($("cost-volume").value),report=comparisonState.report;
  if(!$("hourly-rate").value.trim()||!Number.isFinite(rate)||rate<0||rate>1000000||!Number.isInteger(volume)||volume<1||volume>10000000){$("cost-output").replaceChildren(node("p",t("costPrompt"),"muted"));return;}
  const ref=report.variants.reference.median_index_seconds/report.documents*volume/3600*rate;
  const opt=report.variants.length_grouped.median_index_seconds/report.documents*volume/3600*rate;
  metrics("cost-output",[["estimatedReference",money(ref)],["estimatedOptimized",money(opt)],["estimatedDifference",money(ref-opt)]]);
}
function renderComparison(){
  if(!comparisonState)return;
  const s=comparisonState,r=s.report,p=s.progress;
  $("benchmark-start").disabled=s.running||!status?.ready;
  $("benchmark-cancel").hidden=!s.running;$("benchmark-cancel").disabled=s.cancel_requested;
  document.querySelectorAll("[data-view]").forEach(b=>b.disabled=s.running&&b.dataset.view!=="performance");
  $("benchmark-progress-box").hidden=!s.running;
  $("benchmark-progress").max=p.total||20;$("benchmark-progress").value=p.completed||0;
  $("benchmark-progress-text").textContent=s.cancel_requested?t("cancelling"):t("bench_"+p.phase)+" · "+(p.completed||0)+" / "+(p.total||20)+(p.pair?" · "+p.pair+" / "+p.pairs:"");
  $("benchmark-error").hidden=!s.load_error&&!(["failed","cancelled"].includes(p.phase));
  $("benchmark-error").textContent=s.load_error?t("recordInvalid"):t("bench_"+p.phase);
  $("benchmark-empty").hidden=!!r;$("benchmark-result").hidden=!r;
  if(!r)return;
  $("benchmark-origin").textContent=t(s.source==="archived"?"archivedRecord":"localRecord")+" · "+new Date(r.plan.created_utc).toLocaleString(lang)+" · "+t("measuredHost")+" : "+r.environment.platform+" / "+r.environment.machine+" / "+(r.environment.cpu_model||"CPU");
  const c=r.comparison;
  $("verdict-heading").textContent=t(c.verdict);
  $("verdict-detail").textContent=t(c.verdict==="observed_gain"?"gainDetail":c.verdict==="observed_regression"?"regressionDetail":"inconclusiveDetail");
  $("benchmark-verdict").className="benchmark-verdict "+c.verdict;
  const rows=[["medianIndex",v=>number(v.median_index_seconds,3)+" s"],["medianEncoding",v=>number(v.median_encode_seconds,3)+" s"],["medianExport",v=>number(v.median_export_seconds,3)+" s"],["throughputDocs",v=>number(v.documents_per_second,3)],["throughputChunks",v=>number(v.chunks_per_second,3)],["padding",v=>percent(v.padding_fraction)],["timeRange",v=>number(v.min_index_seconds,3)+" – "+number(v.max_index_seconds,3)+" s"]];
  $("comparison-values").replaceChildren(...rows.map(([key,format])=>{const tr=node("tr");const th=node("th",t(key));th.scope="row";tr.append(th,node("td",format(r.variants.reference)),node("td",format(r.variants.length_grouped)));return tr;}));
  metrics("paired-detail",[["pairedReduction",number(c.median_paired_time_reduction_pct,2)+" %"],["pairedSpeedup","× "+number(c.median_paired_speedup,3)],["pairedInterval",c.paired_speedup_bootstrap95.map(x=>number(x,3)).join(" – ")],["fasterPairs",c.faster_pairs+" / "+c.pairs]]);
  $("paired-detail").append(node("p",t("pairedLimit"),"fineprint"));
  const q=r.quality;
  if(q.status==="pass"){
    const m=q.reference;
    metrics("comparison-quality",[["equalDecisions",q.matching_decisions+" / "+q.documents],["qualityPrecision",percent(m.accepted_precision)+" ("+m.correct_accepted+" / "+m.accepted+")"],["qualityCoverage",m.accepted+" / "+m.documents],["qualityErrors",m.incorrect_accepted],["qualityAbstentions",m.documents-m.accepted],["qualityUnknown",m.unknown_false_accepts+" / "+m.unknown_documents],["numericError",q.max_abs_embedding_difference.toExponential(2)+" (atol=rtol=3e−5)"]]);
  }else{$("comparison-quality").replaceChildren(node("p",t("notEvaluated")));}
  renderCost();
}
async function pollComparison(){
  try{comparisonState=await api("/api/benchmark/status");renderComparison();}catch(exc){$("benchmark-error").hidden=false;$("benchmark-error").textContent=t(exc.message);}
  comparisonPoll=setTimeout(pollComparison,comparisonState?.running?2000:8000);
}
$("benchmark-start").addEventListener("click",async()=>{
  $("benchmark-start").disabled=true;clearError();
  try{comparisonState=await api("/api/benchmark/start",{});renderComparison();clearTimeout(comparisonPoll);comparisonPoll=setTimeout(pollComparison,1000);}catch(exc){error(exc.message);$("benchmark-start").disabled=false;}
});
$("benchmark-cancel").addEventListener("click",async()=>{try{comparisonState=await api("/api/benchmark/cancel",{});renderComparison();}catch(exc){error(exc.message);}});
$("hourly-rate").addEventListener("input",renderCost);$("cost-volume").addEventListener("input",renderCost);
translate();pollComparison();
