"use strict";
const translations = {
  fr: {
    skip:"Aller au contenu",workspace:"Atelier documentaire",searchTab:"Rechercher",reviewTab:"Classer et vérifier",summaryTab:"Faire le bilan",local:"Sur votre ordinateur",localNote:"Traitement CPU local. Aucun document envoyé à un service externe.",repo:"Code et méthodologie ↗",demoLabel:"Démonstration · Corpus public DILA",language:"Langue",preparing:"Préparation de votre atelier",preparingNote:"Le premier lancement crée les index. Les suivants les réutilisent.",step1:"01 / EXPLORER",searchTitle:"Retrouver l’information utile.",searchLead:"Posez une question. Retrouvez les passages pertinents dans 220 fiches administratives françaises.",queryLabel:"Votre question",placeholder:"Quels sont mes droits en tant que locataire ?",searchAction:"Rechercher",try:"Essayer :",example1:"Logement à louer",example2:"Licenciement",example3:"Déclaration de revenus",results:"Documents retrouvés",searchEmpty:"Une question, des passages à lire.",searchEmptyNote:"Les résultats présentent le texte d’origine et sa source, sans réponse générée.",searchLimit:"Le score mesure la similarité, pas la véracité ni une probabilité. Les fiches sont figées au 22 octobre 2026 et ne remplacent pas une source administrative à jour.",step2:"02 / DÉCIDER",reviewTitle:"Le modèle propose. Vous décidez.",reviewLead:"Vérifiez les propositions sur les 80 documents de test séparés de l’apprentissage et de la calibration.",filter:"Afficher",pending:"À examiner",abstained:"Abstentions à examiner",done:"Décisions enregistrées",all:"Tous les documents",reviewLimit:"Les scores ne sont pas des probabilités. Vos décisions sont conservées sur cet ordinateur ; elles ne réentraînent pas le modèle.",step3:"03 / MESURER",summaryTitle:"Un bilan que vous pouvez vérifier.",summaryLead:"Votre travail de revue et les limites du modèle, présentés séparément.",exportTitle:"Conserver les décisions",exportNote:"Un CSV avec les propositions initiales, les décisions humaines et leurs dates.",export:"Exporter les 80 lignes",modelResults:"Résultats du modèle avant revue humaine",modelResultsNote:"Mesurés sur les 80 documents de test publics. Les seuils proviennent uniquement des 80 documents de validation.",qualityLimit:"Petit corpus administratif, quatre thèmes connus. Ces résultats ne garantissent pas la qualité sur vos documents. La revue humaine reste nécessaire.",timingTitle:"Temps observés sur cet ordinateur",timingLimit:"Temps de cette démonstration, pas un benchmark comparatif. Ils ne mesurent ni un gain industriel ni une économie de coûts.",copyright:"© 2026 ENINCA CONSULTING — Tous droits réservés.",attribution:"Données DILA : Licence Ouverte. Modèle MiniLM : Apache 2.0.",close:"Fermer",starting:"Démarrage…",checking_corpus:"Vérification du corpus public",loading_model:"Chargement du modèle local",indexing_train:"Indexation ou chargement : apprentissage (60)",indexing_validation:"Indexation ou chargement : validation (80)",indexing_test:"Indexation ou chargement : test (80)",calibrating:"Calibration sur la validation uniquement",ready:"Prêt",seconds:"s",elapsed:"Temps écoulé",failure:"La préparation a échoué. Consultez le message dans le Terminal ; aucun résultat de démonstration n’est disponible.",networkError:"Le serveur local ne répond pas. Vérifiez que le Terminal est toujours ouvert, puis rechargez la page.",invalid_request_or_query:"Requête invalide. Pour une recherche, saisissez une question plus courte (126 tokens maximum).",stale_review:"Ce document a été modifié dans un autre onglet. Les décisions ont été rechargées ; vérifiez avant de sauvegarder.",server_error:"Une erreur est survenue. Consultez le Terminal et réessayez.",not_found:"Document introuvable.",not_ready:"L’index n’est pas encore prêt.",local_origin_required:"Session locale expirée. Rechargez la page à l’adresse indiquée dans le Terminal.",searching:"Recherche…",score:"Similarité",source:"Lire la source publique ↗",modelAccepted:"Proposition retenue par le modèle",modelAbstained:"Modèle en abstention",humanSaved:"Décision enregistrée",noRows:"Aucun document dans cette vue.",selectDocument:"Sélectionnez un document pour le lire et décider.",suggestion:"Thème suggéré",margin:"Écart entre les deux premiers thèmes",decision:"Votre décision",choose:"Choisir un thème ou hors périmètre…",save:"Enregistrer ma décision",undo:"Remettre à examiner",saved:"Décision enregistrée localement.",undone:"Document remis à examiner.",outside:"Hors des quatre thèmes",readDocument:"Lire le document complet",completed:"Décisions humaines",remaining:"Restent à examiner",changed:"Suggestions corrigées",outsideCount:"Classés hors périmètre",accepted:"Propositions acceptées automatiquement",precision:"Précision des propositions acceptées",interval:"Intervalle de Wilson à 95 %",abstentions:"Abstentions automatiques",falseAccept:"Documents hors périmètre acceptés à tort",thresholds:"Seuils de similarité / écart",prepareTime:"Préparation de cette session",indexTime:"Encodage initial des 220 documents",cache:"Index réutilisés au démarrage",queries:"Recherches effectuées dans cette session",queryTime:"Temps cumulé des recherches",undefined:"Non définie",frozen:"Ces chiffres ne sont pas recalculés à partir de vos corrections.",docCount:"document(s)",queryResultCount:"résultats",details:"Texte public d’origine",reviewSource:"Vous pouvez consulter la source avant de décider.",scope:"Identifiant de la configuration"
  },
  en: {
    skip:"Skip to content",workspace:"Document workspace",searchTab:"Search",reviewTab:"Classify and review",summaryTab:"Summary",local:"On your computer",localNote:"Local CPU processing. No document is sent to an external service.",repo:"Code and methodology ↗",demoLabel:"Demonstration · Public DILA corpus",language:"Language",preparing:"Preparing your workspace",preparingNote:"The first launch builds the indexes. Later launches reuse them.",step1:"01 / EXPLORE",searchTitle:"Find the information that matters.",searchLead:"Ask a question. Find relevant passages across 220 French administrative guidance documents.",queryLabel:"Your question",placeholder:"What are my rights as a tenant?",searchAction:"Search",try:"Try:",example1:"Rental housing",example2:"Dismissal",example3:"Income tax return",results:"Retrieved documents",searchEmpty:"A question. Passages to read.",searchEmptyNote:"Results show the original text and its source, without a generated answer.",searchLimit:"Scores measure similarity, not truth or probability. These documents were frozen on 22 October 2026 and do not replace current official guidance.",step2:"02 / DECIDE",reviewTitle:"The model suggests. You decide.",reviewLead:"Review suggestions for the 80 test documents held apart from training and calibration.",filter:"Show",pending:"Awaiting review",abstained:"Abstentions awaiting review",done:"Saved decisions",all:"All documents",reviewLimit:"Scores are not probabilities. Your decisions stay on this computer; they do not retrain the model.",step3:"03 / MEASURE",summaryTitle:"A summary you can check.",summaryLead:"Your review work and the model’s limitations, presented separately.",exportTitle:"Keep your decisions",exportNote:"A CSV containing the original suggestions, human decisions and their dates.",export:"Export all 80 rows",modelResults:"Model results before human review",modelResultsNote:"Measured on the 80 public test documents. Thresholds use only the 80 validation documents.",qualityLimit:"A small administrative corpus, four known topics. These results do not guarantee quality on your documents. Human review remains necessary.",timingTitle:"Observed times on this computer",timingLimit:"Times from this demonstration, not a comparative benchmark. They do not measure industrial gains or cost savings.",copyright:"© 2026 ENINCA CONSULTING — All rights reserved.",attribution:"DILA data: Open Licence. MiniLM model: Apache 2.0.",close:"Close",starting:"Starting…",checking_corpus:"Checking the public corpus",loading_model:"Loading the local model",indexing_train:"Indexing or loading: training (60)",indexing_validation:"Indexing or loading: validation (80)",indexing_test:"Indexing or loading: test (80)",calibrating:"Calibrating on validation only",ready:"Ready",seconds:"s",elapsed:"Elapsed time",failure:"Preparation failed. Read the message in the Terminal; no demonstration result is available.",networkError:"The local server is not responding. Check that the Terminal is still open, then reload the page.",invalid_request_or_query:"Invalid request. For a search, enter a shorter question (126 tokens maximum).",stale_review:"This document was changed in another tab. Decisions were reloaded; check before saving.",server_error:"An error occurred. Check the Terminal and try again.",not_found:"Document not found.",not_ready:"The index is not ready yet.",local_origin_required:"Local session expired. Reload the address printed in the Terminal.",searching:"Searching…",score:"Similarity",source:"Read the public source ↗",modelAccepted:"Suggestion accepted by model",modelAbstained:"Model abstained",humanSaved:"Decision saved",noRows:"No documents in this view.",selectDocument:"Select a document to read and decide.",suggestion:"Suggested topic",margin:"Gap between the top two topics",decision:"Your decision",choose:"Choose a topic or out of scope…",save:"Save my decision",undo:"Return to review",saved:"Decision saved locally.",undone:"Document returned to review.",outside:"Outside the four topics",readDocument:"Read the full document",completed:"Human decisions",remaining:"Awaiting review",changed:"Corrected suggestions",outsideCount:"Marked out of scope",accepted:"Automatically accepted suggestions",precision:"Precision of accepted suggestions",interval:"95% Wilson interval",abstentions:"Automatic abstentions",falseAccept:"Out-of-scope documents wrongly accepted",thresholds:"Similarity / gap thresholds",prepareTime:"Preparation for this session",indexTime:"Initial encoding of the 220 documents",cache:"Indexes reused at startup",queries:"Searches performed this session",queryTime:"Cumulative search time",undefined:"Undefined",frozen:"These figures are not recomputed from your corrections.",docCount:"document(s)",queryResultCount:"results",details:"Original public text",reviewSource:"You can read the source before deciding.",scope:"Configuration identifier"
  }
};
const categories = {fr:{N19803:"Argent · Impôts · Consommation",N19806:"Travail · Formation",N19808:"Logement",N19811:"Social · Santé"},en:{N19803:"Money · Tax · Consumer rights",N19806:"Work · Training",N19808:"Housing",N19811:"Social support · Health"}};
let lang = "fr";
try { lang = localStorage.getItem("eninca-language") === "en" ? "en" : "fr"; } catch {}
let state, token, selected, view="search", searchResult, status, busy=false, toastTimer;
const $ = (id) => document.getElementById(id);
const t = (key) => translations[lang][key] || key;
const label = (key) => key === "out_of_scope" ? t("outside") : (categories[lang][key] || key);
const number = (x, digits=1) => x.toLocaleString(lang, {maximumFractionDigits:digits,minimumFractionDigits:digits});
const percent = (x) => x == null ? t("undefined") : number(x*100) + " %";
function node(tag, text, cls) {const el=document.createElement(tag);if(text!==undefined)el.textContent=text;if(cls)el.className=cls;return el;}
function error(key) {$("error").dataset.message=key;$("error").textContent=t(key);$("error").hidden=false;}
function clearError() {$("error").hidden=true;}
async function api(path, data) {
  let response;
  try {response=await fetch(path, data===undefined ? {} : {method:"POST",headers:{"Content-Type":"application/json","X-Demo-Token":token},body:JSON.stringify(data)});} catch {throw new Error("networkError");}
  const value=await response.json();
  if(!response.ok)throw new Error(value.error || "server_error");
  return value;
}
function toast(key) {$("toast").dataset.message=key;$("toast").textContent=t(key);$("toast").hidden=false;clearTimeout(toastTimer);toastTimer=setTimeout(()=>$("toast").hidden=true,3500);}
function translate() {
  document.documentElement.lang=lang;$("language").value=lang;
  for(const id of ["error","toast"]){if($(id).dataset.message)$(id).textContent=t($(id).dataset.message);}
  document.querySelectorAll("[data-t]").forEach(el=>el.textContent=t(el.dataset.t));
  $("query").placeholder=t("placeholder");
  $("review-list").setAttribute("aria-label",lang==="fr"?"Documents à examiner":"Documents to review");
  if(status)renderStatus();
  if(searchResult)renderSearch();
  if(state){renderReview();renderSummary();}
}
function renderStatus() {
  const phases=["starting","checking_corpus","loading_model","indexing_train","indexing_validation","indexing_test","calibrating"];
  $("phase").textContent=t(status.phase);
  $("progress").value=Math.max(0,phases.indexOf(status.phase));
  $("elapsed").textContent=t("elapsed")+" : "+number(status.elapsed_seconds,0)+" s";
}
async function refresh() {state=await api("/api/state");renderReview();renderSummary();}
async function poll() {
  try {
    status=await api("/api/status");token=status.token;renderStatus();
    if(status.error){error("failure");$("progress").hidden=true;return;}
    if(status.ready){await refresh();$("loading").hidden=true;$("application").hidden=false;return;}
    setTimeout(poll,1200);
  } catch(exc) {error(exc.message);}
}
function sourceLink(doc) {
  const a=node("a",t("source"),"source-link");
  const url=new URL(doc.source_url);
  if(url.protocol==="https:" && url.hostname==="www.service-public.gouv.fr") {a.href=url.href;a.target="_blank";a.rel="noopener noreferrer";}
  return a;
}
async function openDocument(id) {
  clearError();
  try {const doc=await api("/api/document?id="+encodeURIComponent(id));$("document-title").textContent=doc.title;$("document-text").textContent=doc.text;$("document-source").replaceChildren(sourceLink(doc),node("span",doc.source_modified,"muted"));$("document-dialog").showModal();} catch(exc) {error(exc.message);}
}
function renderSearch() {
  const fragment=document.createDocumentFragment();
  searchResult.results.forEach((r,i)=>{
    const card=node("article",undefined,"result"),header=node("div",undefined,"result-header");
    const title=node("button",r.title);title.type="button";title.addEventListener("click",()=>openDocument(r.document_id));
    header.append(title,node("span",t("score")+" "+number(r.score,3),"result-score"));
    card.append(header,node("p",r.excerpt),node("div",String(i+1).padStart(2,"0")+" · DILA · "+r.document_id,"result-id"));fragment.append(card);
  });
  $("search-results").replaceChildren(fragment);
  $("search-timing").textContent=searchResult.results.length+" "+t("queryResultCount")+" · "+number(searchResult.seconds,2)+" s";
}
$("search-form").addEventListener("submit",async e=>{
  e.preventDefault();if(busy)return;busy=true;clearError();$("search-submit").disabled=true;$("search-submit").textContent=t("searching");
  try{searchResult=await api("/api/search",{query:$("query").value});renderSearch();await refresh();}catch(exc){error(exc.message);}finally{busy=false;$("search-submit").disabled=false;$("search-submit").textContent=t("searchAction");}
});
document.querySelectorAll("[data-query]").forEach(el=>el.addEventListener("click",()=>{$("query").value=el.dataset.query;$("search-form").requestSubmit();}));
function visibleRows() {
  const filter=$("review-filter").value;
  return state.rows.filter(r=>filter==="all" || (filter==="done"?r.review.label!==null:filter==="abstained"?r.review.label===null&&r.needs_review:r.review.label===null));
}
function renderReview() {
  const rows=visibleRows();
  $("review-count").textContent=rows.length+" "+t("docCount")+" · "+state.review_counts.completed+" / 80 "+t("done").toLowerCase();
  if(!rows.some(r=>r.document_id===selected))selected=rows[0]?.document_id;
  const fragment=document.createDocumentFragment();
  for(const row of rows){
    const button=node("button",undefined,"review-item"+(row.document_id===selected?" selected":""));button.type="button";
    button.setAttribute("aria-pressed",String(row.document_id===selected));
    const caption=row.review.label!==null?"humanSaved":row.needs_review?"modelAbstained":"modelAccepted";
    button.append(node("div",row.title),node("span",t(caption),"badge"+(row.needs_review&&row.review.label===null?" amber":"")));
    button.addEventListener("click",()=>{selected=row.document_id;renderReview();});fragment.append(button);
  }
  if(!rows.length)fragment.append(node("p",t("noRows"),"empty"));
  $("review-list").replaceChildren(fragment);
  renderDetail(rows.find(r=>r.document_id===selected));
}
function renderDetail(row) {
  const target=$("review-detail");
  if(!row){target.replaceChildren(node("p",t("selectDocument"),"muted"));return;}
  const title=node("h2",row.title),proposal=node("div",undefined,"proposal");
  proposal.append(node("span",t(row.needs_review?"modelAbstained":"modelAccepted"),"badge"+(row.needs_review?" amber":"")),node("p",t("suggestion")),node("strong",label(row.suggested_label)),node("p",t("score")+" : "+number(row.cosine_score,3)+" · "+t("margin")+" : "+number(row.margin,3)));
  const read=node("button",t("readDocument"),"quiet");read.type="button";read.addEventListener("click",()=>openDocument(row.document_id));
  const choose=node("select");choose.id="decision";const option=node("option",t("choose"));option.value="";choose.append(option);
  for(const key of [...state.labels,"out_of_scope"]){const o=node("option",label(key));o.value=key;choose.append(o);}
  choose.value=row.review.label || "";
  const caption=node("label",t("decision"));caption.htmlFor="decision";
  const save=node("button",t("save"),"primary");save.type="button";save.disabled=!choose.value;choose.addEventListener("change",()=>save.disabled=!choose.value);
  const actions=node("div",undefined,"review-actions");actions.append(save);
  const persist=async(value)=>{
    clearError();actions.querySelectorAll("button").forEach(b=>b.disabled=true);
    try{await api("/api/review",{document_id:row.document_id,label:value,revision:row.review.revision});await refresh();toast(value===null?"undone":"saved");}
    catch(exc){error(exc.message);try{await refresh();}catch{} }
  };
  save.addEventListener("click",()=>persist(choose.value));
  if(row.review.label!==null){const undo=node("button",t("undo"),"quiet");undo.type="button";undo.addEventListener("click",()=>persist(null));actions.append(undo);}
  target.replaceChildren(title,read,proposal,caption,choose,actions,node("p",t("reviewSource"),"fineprint"));
}
function metrics(target, pairs) {
  const dl=node("dl");pairs.forEach(([key,value])=>{const div=node("div",undefined,"metric");div.append(node("dt",t(key)),node("dd",String(value)));dl.append(div);});$(target).replaceChildren(dl);
}
function renderSummary() {
  const c=state.review_counts,m=state.metrics,tm=state.timings,p=state.policy;
  $("summary-cards").replaceChildren(...[["completed",c.completed],["remaining",c.remaining],["changed",c.changed_suggestion],["outsideCount",c.outside]].map(([key,value])=>{const el=node("div",undefined,"card");el.append(node("span",String(value),"number"),node("span",t(key),"caption"));return el;}));
  metrics("model-metrics",[["accepted",m.accepted+" / "+m.documents],["precision",percent(m.accepted_precision)+" ("+m.correct_accepted+" / "+m.accepted+")"],["interval",m.accepted_precision_wilson95?m.accepted_precision_wilson95.map(percent).join(" – "):t("undefined")],["abstentions",m.documents-m.accepted],["falseAccept",m.unknown_false_accepts+" / "+m.unknown_documents],["thresholds",p.mode==="thresholds"?number(p.min_score,2)+" / "+number(p.min_margin,2):t("modelAbstained")]]);
  metrics("timing-metrics",[["prepareTime",number(tm.preparation_seconds,2)+" s"],["indexTime",number(Object.values(tm.original_encoding_seconds).reduce((a,b)=>a+b,0),2)+" s"],["cache",Object.values(tm.cache_hits).filter(Boolean).length+" / 3"],["queries",tm.search_count],["queryTime",number(tm.search_seconds,2)+" s"]]);
}
$("review-filter").addEventListener("change",()=>{selected=null;renderReview();});
document.querySelectorAll("[data-view]").forEach(button=>button.addEventListener("click",async()=>{
  view=button.dataset.view;clearError();
  document.querySelectorAll("[data-view]").forEach(b=>{b.classList.toggle("active",b.dataset.view===view);if(b.dataset.view===view)b.setAttribute("aria-current","page");else b.removeAttribute("aria-current");});
  document.querySelectorAll(".view").forEach(v=>v.hidden=v.id!==view+"-view");
  if(state){try{await refresh();}catch(exc){error(exc.message);}}
}));
$("language").addEventListener("change",()=>{lang=$("language").value;try{localStorage.setItem("eninca-language",lang);}catch{}translate();});
$("close-dialog").addEventListener("click",()=>$("document-dialog").close());
translate();poll();
