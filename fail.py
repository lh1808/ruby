[rubin] React 18.2.0 geladen, Babel kompiliert.
8501/:332  You are using the in-browser Babel transformer. Be sure to precompile your scripts for production - https://babeljs.io/docs/setup/
(anonymous) @ 8501/:332
8501/:332  Uncaught SyntaxError: /Inline Babel script: Identifier 'spFmt' has already been declared. (2282:9)

  2280 |     return () => { mounted = false; clearInterval(iv); };
  2281 |   }, []);
> 2282 |   const [spFmt,setSpFmt] = useState({lgbm:{},catboost:{}});
       |          ^
  2283 |   const [dp,setDp] = useState({files:[""],evalFiles:[],featurePath:"",target:"Y",treatment:"T",scoreName:"",multiOpt:"merge",controlFileIndex:0,fillNa:"(keine)",binaryTarget:false,dedup:false,dedupCol:"",scoreAsFeature:false,outputPath:"data/processed",delimiter:",",detectedCols:null,featureSelection:{},treatValues:[],treatMap:{},colTypes:{},targetValues:[],chunksize:300000,sasEncoding:"utf-8",dpMlflow:false,dpMlflowExp:""});
  2284 |   const [cfg,set] = useState({
  2285 |     expName:"rubin",seed:42,x_file:"",t_file:"",y_file:"",s_file:"",treatmentType:"binary",refGroup:0,hasNaN:false,nanCols:[],validateOn:"cross",cvSplits:5,testSize:0.2,downsample:false,dfFrac:0.1,reduceMem:true,fsEnabled:false,fsMethods:["lgbm_importance"],fsTopPct:15,fsCorrThresh:0.9,outputDir:"",savePreds:false,predsFormat:"csv",models:["NonParamDML","DRLearner","SLearner","TLearner"],baseLearner:"lgbm",tuningEnabled:true,tuningTrials:30,tuningSingleFold:false,tuningMetric:"roc_auc",tuningPerRole:false,tuningPerLearner:false,fmtEnabled:false,fmtModels:[],fmtSingleFold:false,fmtTrials:20,fmtMaxRows:200000,cfTune:false,cfTuneMaxRows:0,selMetric:"qini",higherBetter:true,refitChamp:true,manualChamp:null,surrEnabled:false,surrMinLeaf:50,surrLeaves:31,surrDepth:0,bundleEnabled:false,bundleDir:"bundles",bundleChallengers:true,bundleMlflow:true,explEnabled:true,explMethod:"shap",explSampleSize:10000,explTopN:20,shapModels:[],shapBins:10,segEnabled:true,segQuantiles:10,segTopFeatures:8,segMaxBins:6,segMaxCats:15,histScoreName:"historical_score",histScoreCol:"S",histScoreHigher:true,fsMaxFeatures:0,maxPredRows:0,tuningTimeout:0,tuningMaxRows:200000,fmtTimeout:0,blFixed:{},fmtFixed:{},cfFixed:{},fracSL:1,fracTL:1,fracXL:1,fracDML:1,fracDR:1,
    at e (8501/:332:427854)
    at r.raise (8501/:332:465828)
    at t.checkRedeclarationInScope (8501/:332:438397)
    at t.declareName (8501/:332:437761)
    at r.declareName (8501/:332:440569)
    at r.declareNameFromIdentifier (8501/:332:495889)
    at r.checkIdentifier (8501/:332:495804)
    at r.checkLVal (8501/:332:495398)
    at r.checkLVal (8501/:332:495213)
    at r.parseVarId (8501/:332:681540)
    at r.parseVarId (8501/:332:555835)
    at r.parseVar (8501/:332:680971)
    at r.parseVarStatement (8501/:332:677326)
    at r.parseStatementContent (8501/:332:668999)
    at r.parseStatementLike (8501/:332:667179)
    at r.parseStatementLike (8501/:332:542997)
    at r.parseStatementListItem (8501/:332:666755)
    at r.parseBlockOrModuleBlockBody (8501/:332:679464)
    at r.parseBlockBody (8501/:332:679274)
    at r.parseBlock (8501/:332:678972)
    at r.parseFunctionBody (8501/:332:655968)
    at r.parseFunctionBody (8501/:332:542304)
    at r.parseFunctionBodyAndFinish (8501/:332:655596)
    at r.parseFunctionBodyAndFinish (8501/:332:542631)
    at 8501/:332:682237
    at r.withSmartMixTopicForbiddingContext (8501/:332:661363)
    at r.parseFunction (8501/:332:682188)
    at r.parseFunctionStatement (8501/:332:674953)
    at r.parseStatementContent (8501/:332:667757)
    at r.parseStatementLike (8501/:332:667179)
    at r.parseStatementLike (8501/:332:542997)
    at r.parseModuleItem (8501/:332:666674)
    at r.parseBlockOrModuleBlockBody (8501/:332:679441)
    at r.parseBlockBody (8501/:332:679274)
    at r.parseProgram (8501/:332:664657)
    at r.parseTopLevel (8501/:332:663380)
    at r.parseTopLevel (8501/:332:561443)
    at r.parse (8501/:332:704066)
    at hE (8501/:332:704257)
    at 8501/:332:1130775
    at p (8501/:332:2224)
    at Generator.<anonymous> (8501/:332:3574)
    at Generator.next (8501/:332:2653)
    at p (8501/:332:2224)
    at A (8501/:332:4004)
    at Generator.<anonymous> (8501/:332:3351)
    at Generator.next (8501/:332:2653)
    at p (8501/:332:2224)
    at A (8501/:332:4004)
    at Generator.<anonymous> (8501/:332:3351)
