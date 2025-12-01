//Code from
	function traduz (texto,sendines) {

		var testo;

        testo =texto;

		//duas seguidas
		var re = new RegExp(" ", "g");
		testo = testo.replace(re, "  ");

		var simblos = "([^a-zA-Z0-9áàâãäÁÀÂÃÄéèêëÉÈÊËíìîïÍÌÎÏòóôõöÓÒÔÕÖùúûüÚÙÛÜçÇ ])";

		var re = new RegExp(simblos, "g");
		testo = testo.replace(re, " $1 ");


	//normalmente ampeços de palabras
	var upperCase = new Array(
		//tratar links
		//"www . ([.]*)+[ ]* (. com|. html|. htm|. org)+", "deuwww.$1$2",
		"bem - vind(a|o)(s)? ", "bienbenid$1$2 ",

		"com  o ", "cul ",
		"com  a ", "cula ",
		"de  um ", "dun ",
		"de  uns ", "duns ",

		"com  os ", "culs ",
		"com  as ", "culas ",
		"para  o(s)? ", "pa l$1 ",
		"para  a(s)? ", "pa la$1 ",

		//traduções de verbos
		//SER
		"és ", "sós ",
		"é ", "ye ",
		"sois ", "sodes ",

		"eramos ", "éramos ",
		"erais ", "érades ",
		"eram ", "éran ",

		"serão " ,"seran ",

		"foi ", "fui ",
		"foste ", "fuste ",
		"fomos ", "fumos ",
		"foram ", "fúrun ",

		"fosse ", "fusse ",
		"fosses ", "fusses ",
		"fossemos ", "fússemos ",
		"fosseis ", "fússedes ",
		"fossem ", "fússen ",

		"for ", "fur ",
		"fores ", "fures ",
		"formos ", "furmos ",
		"foreis ", "furdes ",
		"forem ", "fúren ",

		"fora ", "fura ",
		"foras ", "furas ",
		"foramos ", "fúramos ",
		"foreis ", "fúrades ",
		"forem ", "fúran ",

		"seja ", "seia ",
		"sejas ", "seias ",
		"sejamos ", "séiamos ",
		"sejais ", "séiades ",
		"sejam ", "séian ",

		"sereis ", "serdes ",
		"serem ", "séren ",

		"seria ", "serie ",
		"serias ", "series ",
		"seriamos ", "seriemos ",
		"serieis ", "seriedes ",
		"seriam ", "serien ",

		"sê ", "sei ",

		//STAR
		"estou ","stou ",
		"estás ","stás ",
		"está ","stá ",
		"estamos ","stamos ",
		"estais ","stais ",
		"estão ","stan ",

		"estava ","staba ",
		"estavas ","stabas ",
		"estávamos ","stábamos ",
		"estáveis ","stábades ",
		"estavam ","stában ",

		"estive ","stube ",
		"estiveste ","stubiste ",
		"esteve ","stubo ",
		"estivemos ","stubimos ",
		"estivestes ","stubistes ",
		"estiveram ","stubírun ",

		"estivera ","stubira ",
		"estiveras ","stubiras ",
		"estivéramos ","stubíramos ",
		"estivéreis ","stubírades ",
		"estiveram ","stubíran ",

		"estarei ","starei ",
		"estarás ","starás ",
		"estará ","stará ",
		"estaremos ","staremos ",
		"estareis ","stareis ",
		"estarão ","staran ",

		"estaria ","starie ",
		"estarias ","staries ",
		"estaríamos ","stariemos ",
		"estaríeis ","stariedes ",
		"estariam ","starien ",

		"esteja ","steia ",
		"estejas ","steias ",
		"estejamos ","stéiamos ",
		"estejais ","stéiades ",
		"estejam ","stéian ",

		"estivesse ","stubisse ",
		"estivesses ","stubisses ",
		"estivéssemos ","stubíssemos ",
		"estivésseis ","stubíssedes ",
		"estivessem ","stubíssen ",

		"estiver ","stubir ",
		"estiveres ","stubires ",
		"estivermos ","stubirmos ",
		"estiverdes ","stubirdes ",
		"estiverem ","stubíren ",

		"estares ","stares ",
		"estarmos ","starmos ",
		"estarem ","stáren ",

		"esteja ","steia ",
		"estejas ","steias ",
		"estejamos ","stéiamos ",
		"estai ","stéiades ",
		"estejam ","stéian ",

		//TENER
		"tenho ", "tengo ",
		"temos ", "tenemos ",
		"tendes ", "teneis ",
		"têm ", "ténen ",

		"tinha ", "tenie ",
		"tinhas ", "tenies ",
		"tinhamos ", "teniemos ",
		"tinhais ", "teniedes ",
		"tinham ", "tenien ",

		"tive ", "tube ",
		"tiveste ", "tubiste ",
		"teve ", "tubo ",
		"tivemos ", "tubimos ",
		"tivesteis ", "tubistes ",
		"tiveram ", "tubírun ",

		"tivera ","tubira ",
		"tiveras ","tubiras ",
		"tiveramos ","tubiramos ",
		"tivereis ","tubirades ",
		//"tiveram ","tubíran ",

		"tenha ", "tenga ",
		"tenhas ", "tengas ",
		"tenhamos ", "téngamos ",
		"tenhais ", "téngades ",
		"tenham ", "téngan ",

		"tivesse ","tubisse ",
		"tivesses ","tubisses ",
		"tivessemos ","tubíssemos ",
		"tivesseis ","tubíssedes ",
		"tivessem ","tubíssen ",

		"tiver ","tubir ",
		"tiveres ","tubires ",
		"tivermos ","tubirmos ",
		"tivereis ","tubirdes ",
		"tiverem ","tubíren ",

		"ter ","tener ",
		"teres ","teneres ",
		"termos ","tenermos ",
		"terdes ","tenerdes ",
		"terem ","tenéren ",

		"teria ","tenerie ",
		"terias ","teneries ",
		"teriamos ","teneriemos ",
		"terieis ","teneriedes ",
		"teriam ","tenerien ",

		"tendo ", "tenendo ",
		"tid(a|o)+(s)?", "tenid$1$2",
		//FAZER
		"faço ","fago ",

		"fazem ","fázen ",

		"fizeste ","faziste ",
		"fez ", "fizo ",
		"fizemos ","fazimos ",
		"fizestes ", "fazistes ",
		"fizeram ","fazirun ",

		"fazia ","fazie ",
		"fazias ","fazies ",
		"fazíamos ","faziemos ",
		"fazíeis ","faziedes ",
		"faziam ","fazien ",

		"fizera ","fazira ",
		"fizeras ","faziras ",
		"fizéramos ","faziramos ",
		"fizéreis ","fazirades ",
		"fizeram ","faziran ",

		"farei ","fazerei ",
		"farás ","fazerás ",
		"fará ","fazerá ",
		"faremos ","fazeremos ",
		"fareis ","fazereis ",
		"farão ","fazeran ",

		"faria ","fazerie ",
		"farias ","fazeries ",
		"faríamos ","fazeriemos ",
		"faríeis ","fazerides ",
		"fariam ","fazerien ",

		"faça ","faga ",
		"faças ","fagas ",
		"façamos ","fágamos ",
		"façais ","fágades ",
		"façam ","fágan ",

		"fizesse ","fazisse ",
		"fizesses ","fazisses ",
		"fizéssemos ","fazissemos ",
		"fizésseis ","fazissedes ",
		"fizessem ","fazissen ",

		"fizer ","fazir ",
		"fizeres ","fazires ",
		"fizermos ","fazirmos ",
		"fizerdes ","fazirdes ",
		"fizerem ","faziren ",

		"faça ","faga ",
		"façamos ","fagamos ",
		"façam ","fagan ",

		//PONER
		"ponho ","pongo ",
		"pões ","pones ",
		"põe ","pon ",
		"pomos ","ponemos ",
		"pondes ","puneis ",
		"põem ","pónen ",

		"puseste ","puniste ",
		"pôs ","puso ",
		"pusemos ","punimos ",
		"pusestes ","punistes ",
		"puseram ","punirun ",

		"punha ","punie ",
		"punhas ","punies ",
		"púnhamos ","puniemos ",
		"púnheis ","puniedes ",
		"punham ","punien ",

		"pusera ","punira ",
		"puseras ","puniras ",
		"puséramos ","puniramos ",
		"puséreis ","punirades ",
		"puseram ","puniran ",

		"porei ","ponerei ",
		"porás ","ponerás ",
		"porá ","ponerá ",
		"poremos ","poneremos ",
		"poreis ","ponereis ",
		"porão ","poneran ",

		"poria ","ponerie ",
		"porias ","poneries ",
		"poríamos ","poneriemos ",
		"poríeis ","poneriedes ",
		"poriam ","ponerien ",

		"ponha ","ponga ",
		"ponhas ","pongas ",
		"ponhamos ","pongamos ",
		"ponhais ","pongades ",
		"ponham ","pongan ",

		"pusesse ","punisse ",
		"pusesses ","punisses ",
		"puséssemos ","punissemos ",
		"pusésseis ","punissedes ",
		"pusessem ","punissen ",

		"puser ","punir ",
		"puseres ","punires ",
		"pusermos ","punirmos ",
		"puserdes ","punirdes ",
		"puserem ","puniren ",

		"pôr ","poner ",
		"pores ","poneres ",
		"pormos ","ponermos ",
		"pordes ","ponerdes ",
		//"porem ","poneren ",

		"põe ","pon ",
		"ponha ","ponga ",
		"ponhamos ","pongamos ",
		"ponde ","ponei ",
		"ponham ","pongan ",

		"pondo ","ponendo ",
		"posto ","puosto ",

		//HABER

		"hão ","han ",

		"houve ","houbo ",
		"houveste ","houbiste ",
		"houvemos ","houbimos ",
		"houvestes ","houbistes ",
		"houveram ","houbírun ",

		"havia ","habie ",
		"havias ","habies ",
		"havíamos ","habiemos ",
		"havíeis ","habiedes ",
		"haviam ","habien ",

		"houvera ","houbira ",
		"houveras ","houbiras ",
		"houvéramos ","houbíramos ",
		"houvéreis ","houbírades ",
		"houveram ","houbíran ",

		"haverão ","haberan ",

		"haveria ","haberie ",
		"haverias ","haberies ",
		"haveríamos ","haberiemos ",
		"haveríeis ","haberiedes ",
		"haveriam ","haberien ",

		"haja ","haba ",
		"hajas ","habas ",
		"hajamos ","hábamos ",
		"hajais ","hábades ",
		"hajam ","hában ",

		"houvesses ","houbisses ",
		"houvesse ","houbisse ",
		"houvéssemos ","houbíssemos ",
		"houvésseis ","houbíssedes ",
		"houvessem ","houbíssen ",

		"houver ","houbir ",
		"houveres ","houbires ",
		"houvermos ","houbirmos ",
		"houverdes ","houbirdes ",
		"houverem ","houbíren ",

		"haverem ","habéren ",
		"há ","hai ",
		"haja ","haba ",
		"havei ","habei ",

		//BENIR
		"venho ","bengo ",
		"vens ","benes ",
		"vem ","ben ",
		"vimos ","benimos ",
		"vindes ","benis ",
		"vêm ","bénen ",

		"vim ","bin ",
		"vieste ","beniste ",
		"veio ","bieno ",
		"viemos ","benimos ",
		"viestes ","benistes ",
		"vieram ","benirun ",

		"vinha ","benie ",
		"vinhas ","benies ",
		"vínhamos ","beniemos ",
		"vínheis ","beniedes ",
		"vinham ","benien ",

		"viera ","benira ",
		"vieras ","beniras ",
		"viéramos ","beniramos ",
		"viéreis ","benirades ",
		"vieram ","beniran ",

		"virei ","benerei ",
		"virás ","benerás ",
		"virá ","benerá ",
		"viremos ","beneremos ",
		"vireis ","benereis ",
		"virão ","beneran ",

		"viria ","benerie ",
		"virias ","beneries ",
		"viríamos ","beneriemos ",
		"viríeis ","beneriedes ",
		"viriam ","benerien ",

		"venha ","benga ",
		"venhas ","bengas ",
		"venhamos ","béngamos ",
		"venhais ","béngades ",
		"venham ","béngan ",

		"viesse ","benisse ",
		"viesses ","benisses ",
		"viéssemos ","benissemos ",
		"viésseis ","benissedes ",
		"viessem ","benissen ",

		"vier ","benir ",
		"vieres ","benires ",
		"viermos ","benirmos ",
		"vierdes ","benirdes ",
		"vierem ","beniren ",

		"vir ","benir ",
		"vires ","benires ",
		"virmos ","benirmos ",
		"virdes ","benirdes ",
		"virem ","beniren ",

		"vem ","ben ",
		"vinde ","beni ",

		"vindo ","benido ",

		//QUERER
		"quero ","quiero ",
		"queres ","quieres ",
		"quer ","quier ",
		"queremos ","queremos ",
		"quereis ","queredes ",
		"querem ","quieren ",

		"quis ","quijo ",
		"quiseste ","quejiste ",
		"quisemos ","quejimos ",
		"quisestes ","quejistes ",
		"quiseram ","quejirun ",

		"queria ","querie ",
		"querias ","queries ",
		"queríamos ","queriemos ",
		"queríeis ","queriedes ",
		"queriam ","querien ",

		"quisera ","quejira ",
		"quiseras ","quejiras ",
		"quiséramos ","quejiramos ",
		"quiséreis ","quejirades ",
		"quiseram ","quejiran ",

		"quererão ","quereran ",

		"quereria ","quererie ",
		"quererias ","quereries ",
		"quereríamos ","quereriemos ",
		"quereríeis ","quereriedes ",
		"quereriam ","quererien ",

		"queira ","querga ",
		"queiras ","quergas ",
		"queiramos ","quérgamos ",
		"queirais ","quérgades ",
		"queiram ","quérgan ",

		"quisesse ","quejisse ",
		"quisesses ","quejisses ",
		"quiséssemos ","quejissemos ",
		"quisésseis ","quejissedes ",
		"quisessem ","quejissen ",

		"quiser ","quejir ",
		"quiseres ","quejires ",
		"quisermos ","quejirmos ",
		"quiserdes ","quejirdes ",
		"quiserem ","quejiren ",

		"quererem ","quereren ",

		"quer ","quier ",
		"queira ","querga ",

		// IR
		"vou	","bou ",
		"vais ","bás ",
		"vai ","bai ",
		"vamos ","bamos ",
		"ides ","ides ",
		"vão ","ban ",

		"foste ","fuste ",
		"foi ","fui ",
		"fomos ","fumos ",
		"fostes ","fustes ",
		"foram ","furun ",

		"ia ","iba ",
		"ias ","ibas ",
		"íamos ","ibamos ",
		"íeis ","ibades ",
		"iam ","iban ",

		"foras ","furas ",
		"fôramos ","furamos ",
		"fôreis ","furades ",
		"foram ","furan ",

		"irei ","eirei ",
		"irás ","eirás ",
		"irá ","eirá ",
		"iremos ","eiremos ",
		"ireis ","eireis ",
		"irão ","eiran ",

		"iria ","eirie ",
		"irias ","eiries ",
		"iríamos ","eiriemos ",
		"iríeis ","eiriedes ",
		"iriam ","eirien ",

		"vá ","baia ",
		"vás ","baias ",
		"vades ","báiades ",
		//"vão ","báian ",

		"fosse ","fusse ",
		"fosses ","fusses ",
		"fôssemos ","fussemos ",
		"fôsseis ","fussedes ",
		"fossem ","fussen ",

		"for ","fur ",
		"fores ","fures ",
		"formos ","furmos ",
		"fordes ","furdes ",
		"forem ","furen ",

		"vá ","baia ",

		// DEZIR
		"dizemos ","dezimos ",
		"dizeis ","dezis ",
		"dizem ","dízen ",

		"disse ","dixe ",
		"disseste ","deziste ",
		"dissemos ","deximos ",
		"dissestes ","dezistes ",
		"disseram ","dezírun ",

		"dizia ","dezie ",
		"dizias ","dezies ",
		"dizíamos ","deziemos ",
		"dizíeis ","deziedes ",
		"diziam ","dezien ",

		"dissera ","dezira ",
		"disseras ","deziras ",
		"disséramos ","dezíramos ",
		"disséreis ","dezírades ",
		"disseram ","dezíran ",

		"direi ","dezirei ",
		"dirás ","dezirás ",
		"dirá ","dezirá ",
		"diremos ","deziremos ",
		"direis ","dezireis ",
		"dirão ","deziran ",

		"diria ","dirie ",
		"dirias ","diries ",
		"diríamos ","diriemos ",
		"diríeis ","diriedes ",
		"diriam ","dirien ",

		"digamos ","dígamos ",
		"digais ","dígades ",
		"digam ","dígan ",

		"dissesse ","dezisse ",
		"dissesses ","dezisses ",
		"disséssemos ","dezíssemos ",
		"dissésseis ","dezíssedes ",
		"dissessem ","dezíssen ",

		"disser ","dezir ",
		"disseres ","dezires ",
		"dissermos ","dezirmos ",
		"disserdes ","dezirdes ",
		"disserem ","dezíren ",

		"dizer ","dezir ",
		"dizeres ","dezires ",
		"dizermos ","dezirmos ",
		"dizerdes ","dezirdes ",
		"dizerem ","dezíren ",

		"dizei ","dezi ",

		"dizendo ","dezindo ",

		"dito ","dezido ",

		// RECEBIR
		"recebo ","recibo ",
		"recebes ","recibes ",
		"recebe ","recibe ",
		"recebemos ","recebimos ",
		"recebeis ","recebis ",
		"recebem ","recíben ",

		"recebi ","recebi ",
		"recebeste ","recebiste ",
		"recebeu ","recebiu ",
		"recebemos ","recebimos ",
		"recebestes ","recebistes ",
		"receberam ","recebírun ",

		"recebia ","recebie ",
		"recebias ","recebies ",
		"recebíamos ","recebiemos ",
		"recebíeis ","recebiedes ",
		"recebiam ","recebien ",

		"recebera ","recebira ",
		"receberas ","recebiras ",
		"recebêramos ","recebíramos ",
		"recebêreis ","recebírades ",
		"receberam ","recebíran ",

		"receberei ","recebirei ",
		"receberás ","recebirás ",
		"receberá ","recebirá ",
		"receberemos ","recebiremos ",
		"recebereis ","recebireis ",
		"receberão ","recebiran ",

		"receberia ","recebirie ",
		"receberias ","recebiries ",
		"receberíamos ","recebiriemos ",
		"receberíeis ","recebiriedes ",
		"receberiam ","recebirien ",

		"receba ","reciba ",
		"recebas ","recibas ",
		"recebamos ","recíbamos ",
		"recebais ","recíbades ",
		"recebam ","recíban ",

		"recebesse ","recebisse ",
		"recebesses ","recebisses ",
		"recebêssemos ","recebíssemos ",
		"recebêsseis ","recebíssedes ",
		"recebessem ","recebíssen ",

		"receber ","recebir ",
		"receberes ","recebires ",
		"recebermos ","recebirmos ",
		"receberdes ","recebirdes ",
		"receberem ","recebíren ",

		"recebe ","recibe ",
		"receba ","reciba ",
		"recebei ","recebi ",

		"recebendo ","recebindo ",

		//PODER
		"posso ","puodo ",
		"podes ","puodes ",
		"pode ","puode ",
		"podemos ","podemos ",
		"podeis ","podeis ",
		"podem ","puoden ",

		"pude ","pude ",
		"pudeste ","podiste ",
		"pôde ","pudo ",
		"pudemos ","podimos ",
		"pudestes ","podistes ",
		"puderam ","podírun ",

		//"podia ","podie ",
		//"podias ","podies ",
		"podíamos ","podiemos ",
		"podíeis ","podiedes ",
		"podiam ","podien ",

		"pudera ","podira ",
		"puderas ","podiras ",
		"pudéramos ","podíramos ",
		"pudéreis ","podírades ",
		"puderam ","podíran ",

		"poderão ","poderán ",

		"poderia ","poderie ",
		"poderias ","poderies ",
		"poderíamos ","poderiemos ",
		"poderíeis ","poderiedes ",
		"poderiam ","poderien ",

		"possa ","puoda ",
		"possas ","puodas ",
		"possamos ","puodamos ",
		"possais ","puodades ",
		"possam ","puodan ",

		"pudesse ","podisse ",
		"pudesses ","podisses ",
		"pudéssemos ","podissemos ",
		"pudésseis ","podíssades ",
		"pudessem ","podíssen ",

		"puder ","podir ",
		"puderes ","podires ",
		"pudermos ","podirmos ",
		"puderdes ","podirdes ",
		"puderem ","podíren ",

		"poderem ","podéren ",

		"pode ","puode ",
		"possa ","puoda ",

		//SABER
		"soubemos ","soubimos ",
		//"soubestes ","soubistes ",
		//"souberam ","soubírun ",

		"sabíamos ","sabiemos ",
		"sabíeis ","sabiedes ",
		"sabiam ","sabien ",

		"soubera ","soubira ",
		"souberas ","soubiras ",
		"soubéramos ","soubiramos ",
		"soubéreis ","soubirades ",
		"souberam ","soubiran ",

		"saberão ","saberan ",

		"saberíeis ","saberiedes ",

		"saberiam ","saberien ",

		"saiba ","saba ",
		"saibas ","sabas ",
		"saibamos ","sábamos ",
		"saibais ","sábades ",
		"saibam ","sában ",

		"soubéssemos ","soubissemos ",
		"soubésseis ","soubissedes ",
		"soubessem ","soubissen ",

		"souber ","soubir ",
		"souberes ","soubires ",
		"soubermos ","soubirmos ",
		"souberdes ","soubirdes ",
		"souberem ","soubiren ",

		"saberem ","saberen ",

		"saiba ","saba ",
		"sabei ","sabei ",

		//DAR
		"deu ","dou ",
		"deram ","dórun ",

		//"dáveis ","dábadesd ",
		"davam ","dában ",

		"dera ","dira ",
		"deras ","diras ",
		"déramos ","díramos ",
		"déreis ","dírades ",
		"deram ","díran ",

		"daríamos ","dariemos ",
		"daríeis ","dariedes ",
		"dariam ","darien ",

		"dê ","deia ",
		"dês ","deias ",
		"dêmos ","déiamos ",
		"deis ","déiades ",
		"dêem ","déian ",

		"desse ","disse ",
		"desses ","disses ",
		"déssemos ","díssemos ",
		"désseis ","díssedes ",
		"dessem ","díssen ",

		"der ","dar ",
		"deres ","dares ",
		"dermos ","darmos ",
		"derdes ","dardes ",
		"derem ","dáren ",

		"darem ","dáren ",

		"dê ","deia ",

		//OUNIR
		"unimos ","ounimos ",
		"unis ","ounis ",
		"unem ","únen ",

		"uni ","ouni ",
		"unistes ","ouniste ",
		"uniu ","ouniu ",
		"unimos ","ounimos ",
		"uniste ","ounistes ",
		"uniram ","ounírun ",

		"unia ","ounie ",
		"unias ","ounies ",
		"uníamos ","ouniemos ",
		"uníeis ","ounides ",
		"uniam ","ounien ",

		"unira ","ounira ",
		"uniras ","ouniras ",
		"uníramos ","ouníramos ",
		"uníreis ","ounírades ",
		"uniram ","ouníran ",

		"unirei ","ounirei ",
		"unirás ","ounirás ",
		"unirá ","ounirá ",
		"uniremos ","ouniremos ",
		"unireis ","ounireis ",
		"unirão ","ouniran ",

		"uniria ","ounirie ",
		"unirias ","ouniries ",
		"uniríamos ","ouniriemos ",
		"uniríeis ","ouniriedes ",
		"uniriam	","ounirien ",

		"unais ","unades ",
		"unam ","únan ",

		"unisse ","ounisse ",
		"unisses ","ounisses ",
		"uníssemos ","ouníssemos ",
		"unísseis ","ouníssedes ",
		"unissem ","ouníssen ",

		"unir ","ounir ",
		"unires ","ounires ",
		"unirmos ","ounirmos ",
		"unirdes ","ounirdes ",
		"unirem ","ouníren ",

		"unindo ","ounindo ",

		"unid(o|a)+(s)? ","ounid$1$2 ",


		//RESTRO BERBOS
		"usar", "ousar", //ousar
		"determina", "detremina", //detremina
		"usad(a|o)+(s)?", "ousad$1$2", //ousado
		"alter", "altar", //altarar
		"emi", "eimi", //eimissora, eimitir
		"ocorreu", "acunteciu",
		"termin", "tremin",
		"represent", "repersent",
		"consider", "cunsidr",
		"pede(s)? ", "piede$1 ",
		"mente(s)? ", "minte$1 ",
		"acham ", "áchan ",
		"aconteceu", "acunteciu",
		"acred", "acrad",
		"adivinh", "adebin",
		"andei ", "andube ",
		"apont", "apunt", //apuntar
		"aprend", "daprend", //daprender
		"apres([^s]+)", "apers$1", //apersentar
		"aquec", "calec",
		"arranc", "arrinc",
		"arrast", "arrastr",  //arrastrar
		"aument", "oument", //aumentar
		"bail([^e |^es ]+)", "beil$1", //beilar
		"bail", "beil",
		"beber", "buber",
		"bebi", "bubi",
		"caiar", "ancaliar",
		"cair ", "caer ",
		"cala ", "calha ",
		"calai ", "calhai ",
		"calar ", "calhar ",
		"calei ", "calhei ",
		"caminh", "camin",
		"classif", "classef", //classificar
		"começ", "ampeç",
		"comeu", "comiu",
		"comparar", "acumparar",
		"cresc", "crec",
		"dan([ç|c]+)", "beil$1", //beilei", beile", dança -> beila
		"dão ", "dan ",
		"denomina", "chama",
		"desapareceu","zapareciu",
		"descreve", "çcribe",
		"descreveu ", "çcrebiu ",
		"desej", "desei", //deseio
		"designar ", "chamar ",
		"divid", "debed", //debeddir
		"dizem ","dízen ",
		"dizer", "dezir",
		"efei", "eifei", //eifeito
		"emb", "amb", //ambarcar", "ambubidos"
		"encaix", "ancaix",
		"encontro", "ancuontro",
		"encontr", "ancontr",
		"entend", "antend",
		"entr([^a |^as ]+)", "antr$1", //antrar
		"escreve ", "scribe ",
		"escreveu ", "screbiu ",
		"escuta", "scuita",
		"estrumar", "stercar",
		"cor(es)? ","quelor$1 ",
		"experiment", "spurment",
		"experiênc", "spriénc",
		"fica","queda",
		"ficou ", "quedou ",
		"fiqu", "qued", //quedei
		"inclui", "anclui",
		"insatisf", "ansastif",
		"inspir", "anspir",
		"olha", "mira",
		"oriund", "ouriund",
		"ouço ","oubo ",
		"pergunt", "pregunt",  //preguntar
		"possui", "ten",
		"prob([a-z]+)", "porb$1",  //porbar ...ber melhor
		"procur", "percur", //percura
		"resist ", "rejist",
		"respond", "respund", //respunder
		"sai ", "sal ",
		"saí ", "sali ",
		"sair", "salir",
		"saiu ", "saliu ",
		"serve ", "sirbe ",
		"vale ", "bal ",
		"viver", "bibir",
		"voar ", "bolar ", //bolar
		"colocar ", "poner ",
		"perante ", "delantre ",
		"inimigo", "einimigo",
		"rainha", "reina",
		"mecânic", "macánic",
		"academia", "academie",
		"parcialmente", "an parte",
		"divisão", "debison",

		//OUTRAS TRADUÇONES AMPORTA ORDE
		// AMPORTA ORDE

		"um  idioma", "ua léngua",
		"verões", "beranos",
		"nos  ([a-z]*)r ", "mos $1r ",
		"nos  ([a-z]*)rmos ", "mos $1rmos ",
		"- as ","- las ",
		"- nos ","- mos ",
		"- o ","- lo ",
		"- os ","- los ",
		"a(s)?  criança", "l$1  nino",
		"criança", "nino",

		"mort(a|o)+(s)? ", "muort$1$2 ",

		"desconto(s)?", "çcunto$1",

		"mantinham ", "mantenien ",

		"portátel ", "portátele ",
		"portáteis ", "portáteles ",

		"proposta(s)?", "perpuosta$1",

		"acolhe", "acuolhe",

		"provocar", "porbocar",

		"sudão","sudan",

		"ruído(s)?", "rugido$1",

		"considera ", "cunsidra ",

		"devia ", "debie ",
		"fora ","fuora ",

		"urban", "ourban",

		"oitavo(s)?", "uitabo$1",
		"esboço", "rabisco",
		"nua(s)? ", "znuda$1 ",
		"nu(s)? ", "znudo$1 ",
		"conteúdo", "cuntenido",
		"joão ", "juan ",
		"carneiro  de  cobrição", "maron",
		"carneiros  de  cobrição", "marones",
		"ponta(s)?  do(s)?  dedo(s)?", "carapota$1",
		"depois  de  amanhã", "passado manhana",
		"às  riscas ", "reixado ",

		"solo", "tierra",
		"só ", "solo ",
		"este  ano", "astanho",
		"à  volta", "al redror",
		"se  situa ", "queda ",
		"situa - se ", "queda ",

		"com  ela(s)? ", "culha$1 ",
		"com  ele(s)? ", "cul$1 ",
		"de  uma(s)? ", "dua$1 ",

		"pelo(s)? ","pul$1 ",
		"in.ciativa(s)? ", "einiciatiba$1 ",

		"inicial ", "einicial ",
		"iniciais ", "einiciales ",
		"in.ci", "ampeç", //iniciar
		"à  frente", "delantre",

		"no  entanto ", "inda assi ",
		"porém ", "mas ",

		"água  -  pé ", "gaçpoia ",
		"testo", "coberteira",
		"terra  gelada", "cúscaro",
		"um  calor", "ua calor",
		"uns  calor", "uas calor",
		"num  calor", "nua calor",
		"de  um  calor", "dua calor",

		"um  fim", "ua fin",
		"com  um  fim", "cun ua fin",
		"com  o  fim", "cula fin",
		"o  fim", "la fin",
		"de  um  fim", "dua fin",


		"meio - dia(s)? ", "meidie$1 ",
		"meia(s)? - noite(s)? ", "meia$1 nuite$2 ",

		"a(s)? ","la$1 ",
		"à(s)? ","a la$1 ",
		"ao(s)? ","al$1 ",

		"banco  de  pedra", "puial",
		"bancos  de  pedra", "puiales",

		"em  baixo ", "ambaixo ",
		"em  cima ", "arriba ",

		"grão  de  bico ", "garbanço ",
		"grãos  de  bico ", "garbanços ",
		"feijão  frade ", "chícharo ",
		"feijões  frade ", "chícharos ",
		"passar  uma  rasteira", "armar ua çancadielha",
		"cabelo  encaracolado", "pelo grifo",
		"espinal  medula", "spinaço",
		"queda  de  água", "cachon",
		"quedas  de  água", "cachones",
		"papa - figos", "perpiendula",
		"cozer  pão", "amassar",

		"vaca(s)?  com  cio ", "baca$1 touronda ",
		"meio  dia ", "meidie ",
		"instestino  grosso ", "tripa gorda ",
		"instestino  delgado ", "tripa fina ",
		"cabra(s)?  com  cio ", "cabra$1 bechonda ",
		"cadela(s)?  com  cio ", "perra$1 cachonda ",
		"ovelha(s)?  com  cio ", "oubeilha$1 maronda ",
		"porca(s)?  com  cio ", "cochina$1 berronda ",
		"com  cio ", "salida ",
		"caspa  do  cabelo", "falhiçca",
		"nevoeiro(s)? gelado(s)? ", "cenceinho$1 ",
		"dente(s)?  canino(s)? ", "caneiro$1 ",
		"e - mail(s)?", "correio$1 eiletrónico",
		"mail", "carta eiletrónica",
		"alguma  coisa", "algo",
		"ao  contrário", "alrobés ",
		"em vão ", "ambalde ",
		"à volta ", "al redror",
		"muito  ([a-zA-Záéíóúàèìòùâêîôûãiõ]+)([a-zA-Záéíóúàèìòùâêîôûãiõ]+)","mui $1$2",
		"de  um ","dun ",
		"de  uma ","dua ",
		"coluna(s)?  vertebral ", "spina$1 ",
		"localiza - se ", "queda ",
		"apesar  de ", "anque ",
		"apesar ", "anque ",

		//Nuobas
		"soberania(s) ", "soberanie$1 ",
		"acordo", "acuordo",
		"acordo", "acuordo",
		"leva", "lieba",
		"mecanismo", "macanismo",
		"economia", "eiquenomie",
		"governo", "gobierno",
		"minoria", "minorie",
		"d ' a","de la",
		"visita","bejita",
		"resistir","rejistir",
		"produto", "perduto",
		"volta", "buolta",
		"imposto", "ampuosto",
		"soberania", "soberanie",
		"dificul","deficul",
		"devem ","dében ",
		"têm ","ténen ",
		"tomam ","tóman ",
		"usam ","úsan ",
		"etimologia", "eitimologie",
		"redor ", "redror ",
		"produ", "pordu",
		"austrália", "oustrália",
		"turquia", "turquie",
		"israel", "eisrael",
		"isl", "eisl", //eislamica
		"depressa", "depriessa",
		"melhoria", "melhorie",
		"horário", "hourário",
		"inaug","einoug",
		"preto", "negro",
		"qualidade", "culidade",
		"quantidade", "cantidade",
		"areal", "arenal",
		"dilúvio", "delúbio",
		"pomar", "maçanal",


		//NUOBAS PROPOSTAS
		"signif", "senef",//senefica
		"preocupad", "preacupad",
		"reconhecer ", "recoincer ", //FutureSpy
		"oficial ", "oufecial ", //FutureSpy
		"oficiais ", "oufeciales ", //FutureSpy
		"ortográfic(o|a)+(s)? ", "ourtográfic$1$2 ", //FutureSpy
		"esperar", "asperar", //FutureSpy
		"devagarzinho(s)? ","devagarico$1 ",
		"devagarinho(s)? ","debagarico$1 ", //FutureSpy
		"vontade(s)? ", "buntade$1 ", //FutureSpy
		"valente(s)? ","baliente$1 ",
		"planície(s)? ","prainada$1 ",
		"barulho(s)? ", "bruído ",
		"gelad(a|o)+(s)? ", "gilad$1$2 ",
		"adormecid(a|o)+(s)? ","drumid$1$2 ",
		"viúv(a|o)+(s)? ", "biúd$1$2 ",
		"plan(a|o)+(s)? ","prain$1$2 ",

		"inferno", "anfierno",
		"gabriela", "grabiela",
		"cox(a|o)+(s)? ", "coix$1$2 ",
		"rox(a|o)+(s)? ", "roix$1$2 ",
		"soar ", "sonar ",
		"bragança ", "bergáncia ",
		"milhares ","miles ",
		"pilar ","pedamiego ",
		"pilares ","pedamiegos ",
		"espanhóis ","spanholes ",
		"vice - versa ","al alrobés ",
		"hotéis ","houteles ",
		"corrente", "corriente",
		"decorrente", "decorriente",
		"restaurante(s)? ","restourante$1 ",
		"hoteleir(a|o)+(s)? ","houteleir$1$2 ",
		"hotelaria(s)? ","houtelarie$1 ",
		"concentração ","cuncentraçon ",
		"concentrações ","cuncentraçones ",
		"esconjurar ","scunjurar ",
		"exé","eisé", //"exército ","eisército ",
		"rar(a|o)+(s)? ","ral$1$2" ,
		"dign(a|o)+(s)? ","din$1$2 ",
		"fabris ","fabriles ",
		"tasc(a|o)+(s)? ","taberna$2 ",
		"atenor ","atanor ",
		"cara(c)?terizad(a|o)+(s)? ","caratelizad$2$3 ",
		"orla ","borda ",
		"et ","eit ",
		//"etnográfico ","eitnográfico ",
		//"etnografia ","eitnografie ",
		"voltar ","tornar ",
		"loja(s)? ","loija$1 ",
		"camponês ","camposino ",
		"camponêses ","camposinos ",
		"camponesa(s)? ","camposina$1 ",
		"alumiar ","alumbrar ",
		"eólic(a|o)+(s)? ","eiólic$1$2 ",
		"marão ","maron ",
		"inverter ","ambertir ",
		"urban(a|o)+(s)? ","ourban$1$2 ",
		"urbanismo(s)? ","ourbanismo$1 ",

		//esto son alguns de ls erros que tamien fui caçando pula Biquipédia :-).

		"equ","eiqu",//eiquaçon, eiquitaçon
		"volta(s)? ","buolta$1 ",
		"rapidamente ","debrebe ",
		"resolver ","resulber ",
		"aneis ","anielhos ",
		"medicina(s)? ","medecina$1 ",
		"importância ","amportança ",
		"participante(s)? ","partecipante$1 ",
		"pupil(a|o)+(s)? ","alun$1$2 ",
		"marinh(a|o)+(s)? ","marin$1$2 ",
		"dece(p)?cionad(a|o)+(s)? ","zeiludid$2$3 ",
		"divin(a|o)+(s)? ","debin$1$2 ",
		"conselho ","cunseilho ",
		"preparação ","perparaçon ",
		"preparações ","perparaçones ",
		"aguarela(s)? ","augarielha$1 ",
		"colon(a|o)+(s)? ","quelon$1$2 ",
		"enorme(s)? ","einorme$1 ",
		"cara(c)?terístic(a|o)+(s)? ","caratelístic$2$3 ",
		"gradualmente ","als poucos ",
		"posteriormente ","mais tarde ",
		"anteriormente ","antes ",
		"extint(a|o)+(s)? ","zaparecid$1$2 ",
		"separad(a|o)+(s)? ","apartad$1$2 ",
		"salpicão ","chouriço ",
		"salpicões ","chouriços ",
		"tartaruga(s)? ","tartarua$1 ",
		"evidéncia(s)? ","eibidéncia$1 ",
		"selvagem ","salbaige ",
		"selvagens ","salbaiges ",
		"em  um ","nun ",
		"em  uns ","nuns ",
		"em  uma ","nua ",
		"em  umas ","nuas ",
		"distante ","loinge ",
		"cuidadosamente ","cun cuidado ",
		"transformaçon ","streformaçon ",
		"justificar ","justeficar ",
		"apesar  de ","anque ",
		"corrigir ","corregir ",
		"secretári(a|o)+(s)? ","secretair$1$2 ",
		"novamente ","outra beç ",
		"fortuna", "fertuna",
		"imposto", "ampuosto",
		"contrariando ","cuntreriando ",
		"raciocínio ","pensar ",
		"process(a|o)+(s)? ","porcesso$1$2 ",
		"sinais ","senhales ",
		"sinal ","senhal ",
		"matrimónio(s)? ","casamiento$1 ",
		"temor ","miedo ",
		"temores ","miedos ",
		"religios(a|o)+(s)? ","relegios$1$2 ",
		"consequentemente ","por bias desso ",
		"resposta(s)? ","repuosta$1 ",
		"grabidez ","prenheç ",
		"grávida(s)? ","prenha$1 ",
		"porêm ","mas ",
		"utensílio(s)? ","ferramienta$1 ",
		"coes(a|o)+(s)? ","fuorte$2 ",
		"capa(s)? ","cápia$1 ",
		"semente(s)? ","semiente$1 ",
		"pomb(a|o)+(s)? ","palomb$1$2 ",
		"minhoc(a|o)+(s)? ","bich$1$2 ",
		"ortodox(a|o)+(s)? ","ourtodox$1$2 ",
		"crença(s)? ","fé$1 ",
		"cristianismo ","cristandade ",
		"herança(s)? ","hardança$1 ",
		"instrumento(s)? ","strumiento$1 ",
		//"propriedade(s)? ","propiadade$1 ",
		"proprie","propia",
		"documentad(a|o)+(s)? ","decumentad$1$2 ",
		"anfinidade(s)? ","anfenidade$1 ",
		"infinit(a|o)+(s)? ","anfenit$1$2 ",
		"criatividade(s)? ","criatebidade$1 ",
		"atividade(s)? ","atebidade$1 ",
		"experi ","spri",
		"espiritual ","spritual ",
		"espirituais ","sprituales ",
		"adversári(a|o)+(s)? ","adbersair$1$2 ",
		"desportiv(a|o)+(s)? ","çportib$1$2 ",
		"descobert(a|o)+(s)? ", "çcubiert$1$2 ",

		//BRASILEIRO
		"acessad(a|o)+(s)? ","besitad$1$2 ",
		"trem ","camboio ",
		"trens ","camboios ",
		"abridor  de  latas ","abre-latas ",
		"aeromoça ","spedeira ",
		"água - viva ","alforreca ",
		"medusa ","alforreca ",
		"AIDS ","SIDA ",
		"alho  poró ","alho-porro ",
		"aterrissagem ","aterraige ",
		"aterrissagens ","aterraiges ",
		"banheiro ","casa de banho ",
		"toalete ","casa de banho ",
		"lavabo ","casa de banho ",
		"sanitário ","casa de banho ",
		"freio ","trabon ",
		"freios ","trabones ",
		"café  da  manhã ","zayuno ",
		"caminhonete ","carrinha ",
		"câncer ","cáncaro ",
		"carona ","boleia ",
		"carteira  de  habilitação ","carta de cunduzir ",
		"carteira  de  motorista ","carta de cunduzir ",
		"carteira  de  identidade ","belhete d'eidentidade ",
		"telefone  celular ","telemoble ",
		"telefone", "telifone", //amporta orde
		"celular ","telemoble ",
		"celulares ","telemobles ",
		"telemóvel ","telemoble ",
		"telemóveis ","telemobles ",
		"canadense(s)? ","canadiano$1 ",
		"caqui ","dióspiro ",
		"cingapura ","singapura ",
		"dublagem ","dobraige ",
		"time(s)? ","eiquipa$1 ",
		"equipe(s)? ","eiquipa$1 ",
		"favela(s)? ","bairro$1 de lata ",
		"estrada(s)?  de  ferro ","camino$1 de fierro ",
		"ferrovia(s)? ","camino$1 de fierro ",
		"gol(s)? ","golo$1 ",
		"irã ","eiran ",
		"irão ","eiran ",
		"islã ","eislan ",
		"islão ","eislan ",
		"israelense(s)? ","eisraelita ",
		"maiô(s)? ","fato de banho ",
		"mamadeira(s)? ","chupeta$1 ",
		"metrô(s)? ","metro$1 ",
		"metropolitano(s)? ","metro$1 ",
		"moscou ","moscobo ",
		"ônibus ","carreira ",
		"autocarro(s)? ","carreira$1 ",
		"polonês ","polaco ",
		"tcheco ","checo ",
		"trem ","camboio ",
		"vietnã ","bietname ",
		"usina ","central núclear ",
		"usinas ","centrais núclear ",
		"aquarela(s)? ","augarielha$1 ",

		//BERBOS pa fazer quando tubir tiempo
		/*
		BERBO:"descobrir"

		BERBO:"separar ","apartar ",

		BERBO:"ocorrer ","acuntecer ",

		BERBO:"trazer"

		BERBO:"sofrer"

		BERBO:"jantar ","cenar"

		BERBO :"punir ","cartigar ",

		BERBO:"decepcionado ","zeiludir ",

		BERBO:"raciocinar ","pensar ",

		BERBO:"auxiliar ","ajudar ",

		BERBO:"gerar ","criar ",

		BERBO:"falecer ","morrir ",

		cunsiderar
		*/


		//PROPOSTAS
		"limit", "lemit",
		"audição ", "oudiçon ",
		"audições ", "oudiçones ",
		"sequer ", "sequiera ",
		"troussesse ", "traísse ",
		"dívida(s)? ", "díbeda$1 ",
		"logo ", "lougo ",
		"surdez ", "xordeira ",
		"surdezes ", "xordeiras ",
		"ramo(s)? ", "galho$1 ",
		"quilha(s)? ", "peitua$1 ",

		"escabel ", "scanho ",
		"escabeis ", "scanhos ",
		"ruminar ", "remenar ",
		"catavento(s)? ", "beleta$1 ",

		"análise(s)? ","análeze$1 ",
		"garganta(s)? ","gorja$1 ",
		"mártir ","mártere ",
		"mártires ","márteres ",
		"doença(s)? ", "malina$1 ",
		"divertir ", "adbertir ",
		"lapiseira(s)? ", "lapezeira$1 ",
		"canalizador(es|as)? ", "ancanhador$1 ",
		"canalizar ", "ancanhar ",
		"canalização ", "ancanhamiento ",
		"canalizações ", "ancanhamientos ",
		"canalizad(o|a)?(s)? ", "ancanhad$1$2 ",
		"amarelad(o|a)?(s)? ", "amarelhad$1$2 ",
		"pavor ", "grima ",
		"pavores ", "grimas ",
		"apavorad(o|a)?(s)? ", "grimado ",
		"tecla ", "boton ",
		"teclas ", "botones ",
		"teclado(s)? ", "botoneira$1 ",
		"abecedário(s)? ", "abecé$1 ",
		"pevide(s)? ", "pediba$1 ",
		"caroço(s)? ", "carunha$1 ",
		"bentos(a|o)?(s)? ", "airoso$1$2 ",
		"nó ", "nuolo ",
		"corda(s)? grossa(s)? ", "lúria$1 ",
		"tesourar ", "tejeirar ",
		"centena(s)? ", "ciento$1 ",
		"fezes ", "merda ",
		"paveia(s)? ", "gabielha$1 ",
		"defecar ", "cagar ",
		"avental ", "mandil ",
		"aventais ", "mandiles ",
		"ruga(s)? ", "angúrria$1 ",
		"enrugad(a|o)?(s)? ", "angurriad$1$2 ",
		"enrugar ", "angurriar ",
		"esforço(s)? ", "sfuorço$1 ",
		"bigode(s)? ", "bigote$1 ",
		"esfoladela(s)? ", "çfolhadela$1 ",
		"negrilho(s)? ", "uolmo$1 ",
		"bigorna(s)? ", "çafra$1 ",
		"relojoeir(a|o)?(s)? ", "relojeir$1$2 ",

		"padrinho(s)? ", "padrino$1 ",
		"apadrinhar ", "apadrinar ",
		"madrinha(s)? ", "madrina$1 ",
		"entrar ", "antrar ",
		"encher ", "anchir ",
		"pâncreas ", "paxarina ",

		"côdea(s)? ", "costra$1 ",
		"crosta(s)? ", "costra$1 ",
		"pulverinho(s)? ", "pelubrino$1 ",
		"cortiça(s)? ", "corcha$1 ",
		"cortiço(s)? ", "corcho$1 ",
		"azinheira(s)? ", "carrasco$1 ",
		"bolota(s)? ", "belhotra$1 ",
		"oculista(s)? ", "ouclista$1 ",
		"cornalheira(s)? ", "fedieira$1 ",
		"sumagreira(s)? ", "cemaqueira$1 ",

		"arco  íris ","cinta de la bielha ",
		"arco - íris ","cinta de la bielha ",
		"javali ","cochino muntés ",
		"cravagem  do  centeio ","carniçuolos ",
		"bom(s)?  dia(s)? ","buonos dies ",

		"via ","bie ",
		"martelar ","martelhar ",

		"farmácia(s)? ","framácia$1 ",
		"comprimido(s)? ","cumpremido$1 ",
		"urgência(s)? ","ourgença$1 ",
		"operação ","ouparaçon ",
		"operações ","ouparaçones ",
		"opera", "oupera",
		"toro(s)? ","tuoro$1 ",
		"enterro(s)? ","antierro$1 ",
		"costela(s)? ","costielha$1 ",
		"ditongar ","ditungar ",
		"crescente(s)? ","creciente$1 ",
		"latejar ","ceçar ",
		"civilização ","ceblizaçon ",
		"civilizações ","ceblizaçones ",
		"cebolinho(s)? ","cebolhino$1 ",
		"cebolada(s)? ","cebolhada$1 ",
		"raio(s)? ","centeilha$1 ",
		"cirurgião ","cerjano ",
		"cirurgiões ","cerjanos ",
		"surrubeco(s)? ","cerrubeque$1 ",
		"topónimo(s)? ","chamadeiro$1 ",
		"rojão ","cherrelhon ",
		"rojões ","cherrelhones ",
		//"queda(s)? ","chimpa$1 ",
		"tombo(s)? ","chimpa$1 ",
		"sugar ","chochar ",
		"chumbo(s)? ","chombo$1 ",
		"bastão ","choupa ",
		"bastões ","choupas ",
		"muleta(s)? ","mulata$1 ",
		"subida(s)? ","chubida$1 ",
		"choco(s)? ","chuoco$1 ",
		"cidadão(s)? ","cidadano$1 ",

		"melga(s)? ","cínfano$1 ",
		"mosquito(s)? ","mosco$1 ",
		"mosquiteira(s)? ","mosqueira$1 ",
		"compacto(s)? ","cirne$1 ",
		"coagular ","coalhar ",
		"coágulo(s)? ","coalho$1 ",
		"([^a])  partir ","$1  cobrar ",
		"coadeira(s)? ","coladeira$1 ",
		"coador(es)? ","colador$1 ",
		"coar ","colar ",
		"suspender ","colgar ",
		"testículo ","colhon ",
		"testículos ","colhones ",
		"colmo(s)? ","cuolmo$1 ",
		"côngrua(s)? ","cóngara$1 ",
		"côngro(s)? ","cóngaro$1 ",
		"taça(s)? ","copa$1 ",
		"sardinhada(s)? ","sardinada$1 ",
		"colmeia(s)? ","colmena$1 ",
		"colmeal ","colmenal ",
		"colmeais ","colmenales ",

		"coroa(s)? ","corona ",
		"coroad(a|o)+(s)? ","coronad$1$2 ",
		"sutiã(s)? ","corpete$1 ",
		"cortesão(s)? ","cortesano$1 ",
		"cortesões ","cortesanos ",
		"risca(s)? do cabelo ","crencha$1 ",
		"encaracolad(a|o)+(s)? ","cresp$1$2 ",
		"cristão(s)? ","crestiano$1 ",
		"mexeriqueir(a|o)+(s)? ","criqueir$1$2 ",
		"crucificar ","curceficar ",
		"crucifixo(s)? ","curcefício$1 ",
		"crucificad(a|o)+(s)? ","curceficad$1$2 ",
		"crucifixão ","curceficion ",
		"poupa(s)? ","coculho$1 ",
		"cuspir ","cuçpir ",
		"cuspidela(s)? ","cuçpidela$1 ",
		"saliva(s)? ","cuçpinha$1 ",
		"cuspe(s)? ","cuçpinha$1 ",
		"cócega(s)? ","cuçquinha$1 ",
		"estaferm(a|o)+(s)?  ","cuiron ",
		"cueiro(s)? ","culeir$1 ",
		"ânus ","culo ",
		"aludir ","amentar ",
		"convénio ","cumben ",
		"compôr ","cumponer ",
		"compost(a|o)+(s)? ","cumpuost$1$2 ",
		"consciencios(a|o)+(s)? ","cuncencios$1$2 ",

		"vestígio(s)? ", "feitiço$1 ",
		"sonho(s)? ", "suonho$1 ",
		"soneira(s)? ", "sonheira$1 ",
		"bel(a|o)+(s)? ", "guap$1$2 ",
		"transparente(s)? ", "traspariente$1 ",
		"lasso(s)? ", "froixo$1 ",
		"surgir ", "aparecer ",

		"adoecer ", "quedar malo ",
		"outrem ", "outra pessona ",
		"outrens ", "outras pessonas ",
		"adoecid(a|o)+(s)? ", "quedad$1$2 malo ",
		"incómodo(s)? ", "moléstia$1 ",
		"injustificável ", "anjusteficable ",
		"justificável ", "justeficable ",
		"intimidade(s)? ", "antemidade$1 ",

		//PARECER
		"parecem ", "parécen ",
		"visit", "besit",
		"divid", "dibed",//dibedir
		"divib", "debin",//debina
		//"visitaram ", "besitórun ",


		"sertãs ","sartian ",
		"sertã(s)? ","sartianes ",

		//bocabulário SAL
		"morreu ","morriu ",
		"sofreu ","sofriu ",
		"dinastia(s)? ","dinastie$1 ",
		"maioria(s)? ", "maiorie$1 ",
		"zamora ","çamora ",
		"sacana(s)? ", "çacana$1 ",
		"carrapato(s)? ", "sancha$1 ",
		"sarandear ", "çarandar ",
		"abecedário(s) ", "alfabeto$1 ",
		"abelha(s) ", "abeilha$1 ",
		"ventur", "bintur", //abintura
		"aventur", "abintur", //abintura
		"hàbil ", "able ",
		"adbogad(a|o)?(s)? ", "abogad$1$2 ",
		"abotoad(a|o)?(s)? ", "abotonad$1$2 ",
		"aninhad(a|o)?(s)? ", "amarrad$1$2 ",
		"acaso ", "acauso ",
		"aceno", "aceinho",
		"acenar ", "acenhar ",
		"timidez ", "acanhamiento ",
		"estragar ", "açagar ",
		"açucarad(a|o)?(s)? ", "açucrad$1$2 ",
		"diberti", "adberti",
		"adiantar ", "adelantrar ",
		"administr", "admenistr",
		"naufrágio", "afogamiento",
		"louvor ", "agabon ",
		"aguentar", "aguantar",
		"sustentar", "aguantar",
		"amolador", "aguçador",
		"ventania(s)? ", "airaçada$1 ",
		"alentejan(a|o)?(s)? ", "alantejan$1$2 ",
		"alentejo(s)? ", "alantejo$2 ",
		"aliviad(a|o)?(s)? ","albiad$1$2 ",
		"tumulto", "albrote",
		"alcanices", "alcanhiças",
		"sobretudo ", "subretodo ",
		"aldeão ", "aldeano ",
		"aldeões ", "aldeanos ",
		"perna(s)? ", "pierna$1 ",
		"algibeira(s)? ", "bolso$1 ",
		"alabastro(s)? ", "alhabastro$1 ",
		"alagar ", "alhargar ",
		"alheio(s)? ", "alheno$1 ",
		"amendoeira(s)? ", "almendreira$1 ",
		"amável ", "anable ",
		"american(a|o)?(s)? ", "amarican$1$2 ",
		"americanice(s)? ", "amaricanice$1 ",
		"aleluia(s)? ", "alaluia$1 ",
		"aqueduto", "alcadute",
		"alcorão", "alcoran",
		"alfândega", "alfándiga",
		"rabaça", "alrabaça",
		"agachad(a|o)?(s)? ", "amarrad$1$2 ",
		"volume", "belume",
		"suavizar", "amerosar",
		"mostrar", "amostrar",
		"princípio", "percípio",
		"largura ", "anchura ",
		"larg(a|o)?(s)? ", "anch$1$2 ",
		"incert(a|o)?(s)? ", "anciert$1$2 ",
		"incobert(a|o)?(s)? ", "ancubiert$1$2 ",
		"gengiba(s)? ", "angina$1 ",
		"henrique ", "Anrique",
		"enriquecer ", "anriquecer ",
		"entead(a|o)?(s)? ", "antead$1$2 ",
		"entrevista(s|r)? ", "anterbista$1 ",
		"entrevista(s|r)? ", "anterbista$1 ",
		"enterr", "anterr", //anterrador
		"internet", "anterneta",
		"funeral ", "anterro ",
		"entrudo(s)? ", "antruido$1 ",
		"carnaval ", "antruido ",
		"carnavais ", "antruidos ",
		"aparelho(s)? ", "apareilho$1 ",
		"separar ", "apartar ",
		"propôr ", "aperponer ",
		"adopção ", "aporfilhaçon ",
		"adopções ", "aporfilhaçones ",
		"adoptar ", "aporfilhar ",
		"adoptad(a|o)?(s)? ", "aporfilhad$1$2 ",
		"ardente", "ardiente",
		"ásper(a|o)?(s)? ", "áspar$1$2 ",
		"etern(a|o)?(s)? ", "eitern$1$2 ",
		"eternidade", "eiternidade",

		"oxigenad(a|o)?(s)? ", "ouxigenad$1$2 ",
		"jejuar ", "ayunar ",
		"desejejuar ", "zayunar ",
		"jejum ", "ayuno ",
		"bancári(a|o)?(s)? ", "bancair$1$2 ",
		"bárbara ", "bárbela ",
		"vassour(a|o)+(s)? ", "bardeiro$2 ",
		"variedade", "variadade",
		"batalha(s)? ", "batailha$1 ",
		"veado", "benado",
		"bemposta", "bempuosta",
		"bindima", "bendima",
		"besta", "béstia",
		"bentre(s)? ", "bientre$1 ",
		"sorte(s)? ", "suorte$1 ",
		"morte(s)? ", "muorte$1 ",
		"vesg(a|o)+(s)? ", "biruolh$1$2 ",
		"estrábic(a|o)+(s)? ","biruolh$1$2 ",
		"viola(s)? ", "biuola$1 ",
		"belisc", "belhiçc",//belhiçcar
		"bolo(s)? ", "bolho$1 ",
		"beldroega(s)? ", "bordelaga$1 ",
		"berço(s)? ", "brício$1 ",
		"verme(s)? ", "brugo$1 ",
		"feitiço(s)? ", "bruxedo$1 ",
		"feitiçaria(s)? ", "bruxedo$1 ",
		"feiticeir(a|o)+(s)? ", "brux$1$2 ",
		"bosta(s)? ", "buosta$1 ",
		"vermelh(a|o)+(s)? ", "burmeilh$1$2 ",

		"egipto", "Eigito",
		"renasce", "renace",
		"renascim", "renacim",
		"significa ", "quier dezir ",
		"catalão ", "catalan",
		"adicionalmente ", "para alhá desso",
		"afeganistão ", "Afeganistan ",
		"islámica", "eislámica",
		"islámica", "eislámica",
		"principado ", "prencipado ",
		"azerbeijão ", "Azerbeijan ",
		"casaquiston ", "Cazaquistan ",
		"chipre", "Xipre",
		"quinchasa", "Quinxasa",
		"quinchasa", "Quinxasa",
		"costa", "cuosta",
		"italian(a|o)+(s)? ", "eitalian$1$2 ",
		"eritreia", "Eiritreia",
		"holand", "houland",

		//TRADUÇONES
		"onde ", "adonde ",
		"domingo(s)? ", "demingo$1 ",
		"cidadania(s)? ", "cidadanie$1 ",
		"sangue(s)? ", "sangre$1 ",

		"joelh", "zinolh",
		"ajoelh", "azinolh",
		" org", " ourg", //organismo, organização
		"abaixo", "ambaixo",
		"abdómen", "abdóme",
		"abentur", "abintur",
		"abert", "abiert", //repetido
		"abóbada(s)? ", "bóbeda$1 ",
		"abóbora(s)? ", "bóbeda$1 ",
		"abort", "amóbit",
		"abutre(s)? ", "cuorbo$1 ",
		"acarrejar", "acarrear",
		"acima ", "arriba ",
		"açougue$1 ", "talho(s)? ",
		"açucar ","açucre ",
		"açucares ","açucres ",
		"adiante ", "adelantre ",
		"adro(s)? ", "sagrado$1 ",
		"água(s)? ", "auga$1 ",
		"aguaceiro(s)? ", "scarabanada$1 ",
		"aguardente(s)? ", "augardiente$1 ",
		"agueira(s)? ", "augadeira$1 ",
		"águia(s)? ", "águila$1 ",
		"aí ", "ende ",
		"ainda ", "inda ",
		"idioma", "léngua",
		"alcatroar", "alcatronar",
		"aldeia(s)? ", "aldé$1 ",
		"alegria(s)? ", "alegrie$1 ",
		"além ", "para alhá ",
		"alemães ", "almanes ",
		"alemanha ", "almanha ",
		"alemão ", "alman ",
		"alemã ","almana ",
		"alfor(g|j)+e[s]?", "alforjas",
		"alforje", "alforjas",
		"alga(s)? ", "ouca$1 ",
		"alguém ", "alguien ",
		"algum ","algun ",
		"alguma(s)? ","algua$1 ",
		"alheira(s)? ", "tabafeia$1 ",
		"ali ", "eilhi ",
		"alicerce(s)? ", "aliçace$1 ",
		"almoç", "almuorç",
		"alperce(s)? ", "albricoque$1 ",
		"am.ndoa", "almendra",
		"amanhã ", "manhana ",
		"amarel(o|a)?(s)? ", "amarielh$1$2 ",
		"ameaç", "amenaç",
		"ameixa(s)? ", "alméixina$1 ",
		"amendoim ", "cascaboi ",
		"amendoins ", "cascabois ",
		"amizade(s)? ", "amisade$1 ", //amisade
		"amora(s)? ", "mora$1 " ,
		"amoreira", "moreira",
		"anão ", "nano ",
		"ancinho(s)? ", "rastro$1 ",
		"andorinh", "andorin",
		"anel", "anielho",
		"anelar ", "anelhar ",
		"anex", "aneix", //anexo
		"anfiteatro([s]?)", "anfitriato$1",
		"animais ", "animales ",  // la tradução "ais" stá a scluir la letra [m]... pa manter mais
		"ano(s)? ", "anho$1 ",
		"anões ", "nanos ",
		"anoitec", "anuitec",
		"anteontem ", "trasdonte ",
		"anteproje[c]?t", "anteporjet",
		"apalp", "ampalp", //ampalpadelas, ampalpou
		"apenas ", "solo ",
		"aprofun", "aperfun", //aperfundar
		"aquela(s)? ","aqueilha$1 ",
		"aquele ", "aquel ",
		"aqueles ", "aqueilhes ",
		"aqui ", "eiqui ",
		"aquilo ","aqueilho ",
		"ar ", "aire ",
		"aranha ", "aranhon ",
		"área(s)? ", "ária$1 ",
		"areia(s)? ", "arena$1 ",
		"ares ", "aires ",
		"armário(s)? ", "almairo$1 ",
		"arredor(es)? ", "alredor$1 ",
		"árvore(s)? ", "arble$1 ",
		"arvoredo(s)? ", "arboledo$1 ",
		"assembleia(s)? ", "assemblé$1 ",
		"assim ", "assi ",
		"assoar ", "fungar ",
		"atordoar", "atrelundar",
		"através ", "atrabeç ",
		"automóveis ", "altemobles ",
		"automóvel ", "altemoble ",
		"autónom","outónom",
		"autor(es)? ", "outor$1 ",
		"avali", "abalu", //abaluação
		"aveia(s)? ", "bena$1 ",
		"azeitona(s)? ", "azeituna$1 ",
		"azuis ", "azules ",
		"bagado", "granado",
		"balança ", "baláncia ",
		"balde(s)? ", "baldo$1 ",
		"batata(s)? ", "patata$1 ",
		"batatais ", "patatales ",
		"batatal ", "patatal ",
		"batateir(a|o)+(s)? ", "patateir$1$2 ",
		"beij", "beis",
		"bem ", "bien ",
		"benvind(a|o)+(s)? ", "bienbenid$1$2 ",
		"beterraba(s)? ", "raba$1 ",
		"bilha(s)? ", "barrila$1 ",
		"bilhet", "belhet",
		"blaser ", "chambra ",
		"blaseres ", "chambras ",
		"blus(a|o)+(s)? ", "chambre$2 ",
		"boa(s)? ", "buona$1 ",
		"bocadinho(s)? ", "cachico$1 ",
		"bocado(s)? ", "cacho$1 ",
		"bode(s)? ", "beche$1 ",
		"boi(s)? ", "bui$1 ",
		"boina(s)? ", "gorra$1 " ,
		"bolacha(s)? ", "bolaixa$1 ",
		"bombard", "bumbard",
		"bombeir", "bumbeir",
		"boné(s)? ", "gorro$1 ",
		"boneco(s)? ", "caramono$1 ",
		"bonit(a|o)+(s)? ","guap$1$2 ", //guapo
		"borboleta(s)? ", "paixarina$1 ",
		"borracha(s)? ", "borraixa$1 ",
		"bugalho(s)? ", "bulhaca$1 ",
		"cá ", "acá ",
		"cabana ","cabanha ",
		"cabanais ", "cabanhales ",
		"cabanal ", "cabanhal ",
		"cabrito(s)? ", "chibo$1 ",
		"cachecois ", "cascoles ",
		"cachecol ", "cascol ",
		"cadela(s)? ", "perra$1 ",
		"cães ", "perros ",
		"caixilh", "queixilh",
		"calad(o|a)+(s)? ", "calhad$1$2 ",
		"calcanhar(es)? ", "carcanhal$1 ",
		"calo(s)? ", "calho$1 ",
		"camomila(s)? ", "maçanielha$1 ",
		"campainha(s)? ", "squila$1 ",
		"can(a|o)+(s)? ", "canh$1$2 ",
		"canais ", "canhales ",
		"canal ", "canhal ",
		"canaviais ", "canheiros ",
		"canavial ", "canheiro ",
		"cancro ", "cáncaro ",
		"candeeiro", "candieiro",
		"canela(s)? ", "canielha$1 ",
		"caniça(s)? ", "canhiça$1 ",
		"cão ", "perro ",
		"capela(s)? ","capielha$1 ",
		"capitão", "capitan",
		"caracois ", "caracoles ",
		"carangueijo(s)? ", "cangareijo$1 ",
		"carne(s)? ", "chicha$1 ",
		"carreiro", "carreiron",
		"casaca(s)? ", "çamarra$1 ",
		"casaco(s)? ", "jiqueta$1 ",
		"caso([s]?) ", "causo$1 ",
		"castel(a|o)+(s)? ", "castielh$1$2 ", //castielho/a
		"catarata ", "cachon ",
		"cataratas ", "cachones ",
		"categoria(s)? ", "catadorie$1 ",
		"cautel", "coutel",
		"caval([^h]+)", "cabalh$1", //cabalhitas, cabalho, cavalheiro manten-se
		"cavanais ", "cabanhales ",
		"cavanal ", "cabanhal ",
		"cebola(s)? ", "cebolha$1 ",
		"ceg(a|o)+(s)? ", "cieg$1$2 ",
		"cegonh(a|o)+(s)? ", "ciguonh$1$2 ", //ciguonha, ciguonho
		"ceia", "cena",
		"celest", "celhestr", //celhestial
		"cem ", "cien ",
		"cemitério(s)? ", "semitério$1 ",
		"centeio(s)? ", "centeno$1 ",
		"cento(s)? ", "ciento$1 ",
		"ceroulas ", "ciroulas ",
		"cert(a|o)+([s]?)", "ciert$1$2 ",
		"céu(s)? ", "cielo$1 ",
		"chá(s)? ", "xá$1 ",
		"chaminé ", "chupon ",
		"chaminés ", "chupones ",
		"champa[gn|nh]+e(s)? ", "xampanhe$1 ",
		"chão ", "suolo ",
		"charm([e|o]+)", "xarm$1",
		"chat", "xat", //xato, xateia, tira chatarra
		"chávena(s)? ", "chícara$1 ",
		"checo(s)? ", "xeco$1 ",
		"chefe(s)? ", "xefe$1 ",
		"chefi", "xefi", //xefiar
		"chei(a|o)+(s)? ", "chen$1$2 ", //cheio, cheia
		"cheiro ", "oulor ",
		"cheiros ", "oulores ",
		"cheque(s)? ", "xeque$1 ",
		"chique(s)? ", "xique$1 ",
		"chispa(s)? ", "chiçpa$1 ",
		"chocolat","choclat", //chocolate, chocolatado
		"chove ", "chuobe ",
		"chuvos(a|o)+(s)? ", "chubios$1$2 ",
		"cigarra(s)? ", "checharra$1 ",
		"civil ", "cebil ",
		"civis ", "cebiles ",
		"cobert(a|o)+(s)? ", "cubiert$1$2 ",
		"cobra(s)? ", "queluobra$1 ",
		"códea(s)? ", "costra$1 ",
		"coelh(a|o)+(s)? ", "coneilh$1$2 ",
		"coelheira(s)? ", "conelheira$1 ",
		"cogumelo(s)? ", "roque$1 ",
		"coisa(s)? ", "cousa$1 ",
		"colégio(s)? ", "coleijo$1 ",
		"colete ","jaleco ",
		"colher ", "cuchara ",
		"colheres ", "cucharas ",
		"colorid(a|o)+(s)? ","quelorid$1$2 ",
		"com ","cun ",
		"comboio(s)? ", "camboio$1 ",
		"comentário(s)? ", "comentairo$1 ",
		"comida(s)?  ", "quemido$1 ",
		"comigo ", "cumigo ",
		"como ","cumo ",
		"companhia(s)? ", "cumpanha$1 ",
		"comu", "quemu", // quemunitária, quemum
		"concelho(s)? ", "cunceilho$1 ",
		"conforto(s)? ", "cunfuorto$1 ",
		"conhecer ", "coincer ",
		"conhecid", "coincid",
		"conhecimento", "coincimiento",
		"connosco", "cun nós",
		"consciência", "cuncéncia",
		"consciente(s)? ", "cunciente$1 ",
		"inconsciente(s)? ", "ancunciente$1 ",
		"conso", "cunsu", //consume
		"contigo ", "cuntigo ",
		"continent","cuntinent",
		"contínuo", "cuntino",
		"continu", "cuntin",
		"convosco", "cun bós",
		"cor(es)? ", "quelor$1 ",
		"corad(a|o)+(s)? ", "quelorad$1$2 ",
		"corda(s)? ", "cuorda$1 ",
		"corpo(s)? ", "cuorpo$1 ",
		"costum", "questum",
		"cotovelada(s)? ", "quetobelhada$1 ",
		"cotovelo(s)? ", "quetobielho$1 ",
		"couval ", "berçal ",
		"couve", "berça",
		"cova(s)? ", "fóia$1 ",
		"cozinh", "cozin", //cozina, cozine
		"cristã(s)? ", "crestiana$1 ",
		"cristão ", "crestian ",
		"cristãos ", "crestianos ",
		"cristóvão ", "cristófe ",
		"cru(s)? ", "crudo$1 ",
		"crua(s)? ", "cruda$1 ",
		"cú(s)? ","culo$1 ",
		"cueca(s)? ", "braga$1 ",
		"curios(a|o)+(s)? ","curjidos$1$2 ",
		"curiosidade(s)? ", "curjidade$1 ",
		"curt(a|o)+", "cúrti$1",
		"curva(s)? ", "rebuolta$1 ",
		"da(s)? ","de la$1 ",
		"daí ", "dende ",
		"dali ", "deilhi ",
		"debaixo", "ambaixo",
		"dela(s)? ", "deilha$1 ",
		"dele ", "del ",
		"deles ", "deilhes ",
		"demons", "demuns", //demunstraçon
		"dente(s)? ", "diente$1 ",
		"dentro ", "drento ",
		"depois ", "depuis ",
		"desde ", "zde ",
		"desenh(a|e|ou)+", "zenh$1", //desenhar, nun traduç zeinho
		"desenho(s)? ", "zeinho$1 ",
		"deus(es)? ", "dius$1 ",
		"dez "," dieç ",
		"dezembro ","dezembre ",
		"dia(s)? ", "die$1 ",
		"diante ", "delantre ",
		"diferen", "defren",
		"difíceis ", "defíceles ",
		"difícil", "defícel",
		"dinheiro(s)? ", "denheiro$1 ",
		"direit", "dreit",
		"disposto", "çpuosto",
		"tradici", "tradeci", //tradecionales
		"óleo", "ólio",
		"petróleo", "petrólio",
		"disso ","desso ",
		"disto ","desto ",
		"do(s)? ","de l$1 ",
		"documento(s)? ", "decumiento$1 ",
		"ficheiro","fexeiro",
		"dois "," dous ",
		"domingo ", "demingo ",
		"doninha(s)? ", "renozielha$1 ",
		"dono(s)? ", "duonho$1 ",
		"dor(es)? ", "delor$1 ",
		"doze "," duoze ",
		"duas "," dues ",
		"dum ","dun ",
		"duma ","dua ",
		"dúvida(s)? ", "dúbeda$1 ",
		"duzentos ", "duzientos ",
		"e ","i ",
		"é ","ye ",
		"eco(s)? ", "retombo$1 ",
		"ecoar ", "ressonar ",
		"economia(s)? ", "eiquenomie$1 ",
		"edi", "eidi",
		"educa", "eiduca", //educação
		"efecti", "afeta", //afetiba
		"eg", "eig",
		"eira(s)? ", "eiras ",
		"eixo(s)? ", "eixe$1 ",
		"ela(s)? ", "eilha$1 ",
		"ele ", "el ",
		"elefante", "alifante",
		"elei", "eilei", //eileito, eileiçon
		"elemento", "eilemiento",
		"eles ", "eilhes ",
		"em ","an ",
		"embora", "ambora",
		"empre", "ampre", //amprego
		"encara", "ancara",
		"encosta", "costielha",
		"enfim ", "anfin ",
		"engan", "anganh",
		"engenharia", "angenharie",
		"engenheir", "angenheir",
		"engenho(s)? ", "angeinho$1 ",
		"englob", "anglob",
		"engolir", "angulhir",
		"enquanto ", "anquanto ",
		"enregelad", "atrecid",
		"ensaboar ", "anxabonar ",
		"ensin", "ansin",
		"entanto", "antanto",
		"então ", "anton ",
		"entidade(s)? ", "antidade$1 ",
		"entrada(s)? ","antrada$1 ",
		"entre ", "antre ",
		"entretanto ", "antretanto ",
		"entrete", "antrete", //eantretenimento
		"enxada(s)? ", "sacho$1 ",
		"enxadão ", "açadon ",
		"enxadões ", "açadones ",
		"enxofre", "alxofre",
		"equi", "eiqui", //eiquilíbrio, eiquibaléncia
		"erva(s)? ", "yerba$1 ",
		"escada(s)? ", "scaleira$1 ",
		"escano(s)? ", "scanho$1 ",
		"escola(s)? ", "scuola$1 ",
		"escorpião ", "alicran",
		"escorpiões ", "alicranes ",
		"esfolar ", "çfolhar ",
		"esfome", "sfame",
		"espaço(s)? ", "spácio$1 ",
		"espalhadoura", "biendo",
		"espelho(s)? ", "speilho$1 ",
		"espinha(s)? ", "spina$1 ",
		"espírit", "sprit", //sprito
		"esquerda", "squierda",
		"essenci", "eissenci",
		"essênci","eissenci",
		"esteva(s)? ", "xara$1 ",
		"estômago(s)? ", "stómado$1 ",
		"estrela(s)? ", "streilha$1 ",
		"estrelad", "strelhad",
		"estrume", "stierco",
		"eu ", "you ",
		"euro", "ouro",
		"evento(s)? ", "eibento$1 ",
		"evit", "eibit", //eibitar
		"evol", "eibol", //eiboluçon
		"excepto", "fuora",
		"explodir", "spludir",
		"explosão ", "spluson ",
		"explosões ", "splusones ",
		"fáceis ", "fáceles ",
		"fácil", "fácele",
		"faísca", "chiçpa",
		"falência", "falhéncia ",
		"fechad(a|o)+(s)? ", "cerrad$1$2 ",
		"fechar ", "ancerrar ",
		"feijão ", "freijon ",
		"feijões ", "frajones ",
		"férias ", "bacanças ",
		"fermento(s)? ", "furmiento$1 ",
		"ferramenta(s)? ", "ferramienta$1 ",
		"ferro(s)? ","fierro$1 ",
		"festa(s)? ", "fiesta$1 ",
		"fevereiro", "febreiro",
		"fiandeira", "filadeira" ,
		"fiar", "filar",
		"filosofia(s)? ", "filosofie$1 ",
		"fio(s)? ", "filo$1 ",
		"flauta(s)? ", "fraita$1 ",
		"focinhada(s)? ", "çofinada$1 ",
		"focinho(s)? ", "çofino$1 ",
		"fogo(s)? ", "fuogo$1 ",
		"foice", "fouce",
		"foicinha ", "foucin ",
		"folha(s)? ", "fuolha$1 ",
		"fome(s)? ", "fame$1 ",
		"fonte", "fuonte",
		"fontinha", "funtica",
		"fora ", "fuora ",
		"força([^r]+)", "fuorça$1",
		"forja", "frauga",
		"forte", "fuorte",
		"fósforo(s)? ","cerilha$1 ",
		"fotógraf[a|o]+(s)? ", "retratista$2 ",
		"fotografa(r)? ", "retrata$1 ",
		"fotografia", "retrato",
		"frágil ", "andeble ",
		"frança ", "fráncia ",
		"freix", "frezn", //frezno, frezneira
		"fria(s)? ", "frie$1 ",
		"frio(s)? ", "friu$1 ",
		"front", "frunt", //frunteira
		"frut", "fruit",
		"funcho ", "finolho ",
		"funda(s)? ", "atiradeira$1 ",
		"fundo", "fondo",
		"futur", "fetur",
		"gado(s)? ", "ganado$1 ",
		"galin", "galhin", // galhináceo
		"galinh", "galhin", //galhina
		"galo(s)? ", "galho$1 ",
		"gás ", "gáç ",
		"gávea ", "gábia ",
		"gavião ", "gabilan ",
		"gelado","ancarambiando",
		"gelo(s)? ", "carambelo$1 " ,
		"gêmeo(s)? ", "mielgo$1 ",
		"gente(s)? ", "giente$1 ",
		"geral", "giral",
		"gesto(s)? ", "géstio$1 ",
		"giesta(s|l)? ", "scoba$1 ",
		"gole(s)? ", "bucho$1 ",
		"gomo(s)? ", "gromo$1 ",
		"gost", "gust",
		"gota(s)? ", "pinga$1 ",
		"goteira(s)? ", "boteira$1 ",
		"graça(s)? ", "grácia$1 ",
		"grainha(s)? ", "granina$1 ",
		"grão(s)? ", "grano$1 ",
		"greg", "grieg", //griego
		"grifo(s)? ", "alcaforro$1 ",
		"grossa(s)? ", "gruossa$1 ",
		"guizo ", "cascabel ",
		"guizos ", "cascabeles ",
		"habili", "halbeli",
		"hall(s)? ", "preça$1 de casa ",
		"herança ", "hardáncia ",
		"hip", "heip", //heipotese
		"his", "s",
		"hoje ", "hoije ",
		"homem ", "home ",
		"homens ", "homes ",// AMPORTA ORDE
		"homilia(s)? ", "prática$1 ",
		"honest", "hounest", //hounesto
		"horizonte(s)? ", "hourizonte$1 ",
		"hospi", "spi",
		"human", "houman",
		"humi", "houmi", //houmilde
		"ibéric", "eibéric",
		"id([é|e]+)ia(s)? ", "eideia$2 ",
		"idade(s)? ", "eidade$1 ",
		"identi","eidanti", //eidantidade
		"ifanes ", "infainç ",
		"iguais ", "eiguales ",
		"igual ", "eigual ",
		"impossível ", "ampossible ",
		"incluem ", "ancluen ",
		"independente", "andependiente",
		"indivíd", "andibíd",
		"inevit", "einebit", //einebitable
		"infinito(s)? ", "anfenito$1 ",
		"inform", "anform",
		"informa", "anforma",
		"íngreme ", "egre ",
		"institui", "anstitui",
		"instru", "anstru", //instruir"", "instrumento"
		"intelig", "antelig",
		"intere", "antre",
		"íntimo", "íntemo",
		"inúme", "einúma",
		"inúteis ", "einúteles ",
		"inverno(s)? ", "ambierno$1 ",
		"iraque ", "eiraque ",
		"iraquian(a|o)+(s)? ", "eiraquian$1$2 ",
		"irmã(s)? ", "armana$1 ",
		"irmão(s)? ", "armano$1 ",
		"isqueiro(s)? ", "chiçqueiro$1 ",
		"isso ","esso ",
		"isto ","esto ",
		"itália ", "eitália ",
		"já ","yá ",
		"janela(s)? ","jinela$1 ",
		"jerusalem ","jarusalen ",
		"jesus ", "jasus ",
		"jordão ", "jordan ",
		"jovem ", "moço ",
		"jovens ", "moços ",
		"judeu", "judiu",
		"julho ","júlio ",
		"junho ","júnio ",
		"justiça", "justícia",
		"juventude(s)? ", "mocidade$1 ",
		"lá ", "alhá ",
		"lagoa(s)? ", "lagona$1 ",
		"lâmpada(s)? ", "bumbilha$1 ",
		"lápis ", "lápeç ",
		"lareira(s)? ", "lume$1 ",
		"lavrar", "arar",
		"leão ", "lion ",
		"lebre(s)? ", "liebre$1 ",
		"leões ", "liones ",
		"lesma(s)? ", "lezma$1 ",
		"lind(a|o)+(s)? ","guap$1$2 ", //guapo
		"língu", "léngu", // léngua, línguista
		"lingu", "lengu", // linguagem
		"linhaça", "linaça",
		"linho(s)? ", "lino$1 ",
		"líquen", "patrielha",
		"lisboa", "lisboua",
		"lol ", "alt (Arreganha La Tacha) ",
		"LOL ", "ALT (Arreganha La Tacha) ",
		"longe ", "loinge ",
		"lua(s)? ", "luna$1 ",
		"luar(es)?  ", "lunar$1 ",
		"luta(s)? ", "luita$1 ",
		"má(s)? ", "mala$1 ",
		"macieira(s)? ", "maçaneira$1 ",
		"mãe(s)? ","mai$1 ",
		"major", "manjor",
		"malagueta(s)? ", "guindilha$1 ",
		"malandro(s)? ","almanecha$1 ",
		"manhã ", "manhana ",
		"mão(s)? ","mano$1 ",
		"março ","márcio ",
		"margem ", "borda ",
		"margens ", "bordas ",
		"marmeleiro(s)?  ", "burmelheiro$1 ",
		"marmelo(s)?  ", "burmielho$1 ",
		"martelo", "martielho",
		"mau(s)? ", "malo$1 ",
		"máx", "máss",
		"melancia(s)? ", "balancie$1 ",
		"melro(s)? ", "mielro$1 ",
		"membr", "nembr",
		"memória(s)? ", "mimória$1 ",
		"menin(a|o)+(s)? ", "nin$1$2 ",
		"menstruação ", "pinganielho ",
		"mentira(s)?", "mintira$1 ",
		"merujas ", "regaho ",
		//"mesm(a|o)+(s)? ", "miesm$1$2 ",
		"meu(s)? ", "miu$1 ",
		"mezinha", "malzina",
		"migalha(s)? ", "forfalha$1 ",
		"mijar ", "mejar ",
		"mim ", "mi ",
		"minha ", "mie ",
		"nuvem ", "nubre ",
		"nuvens ", "nubres ",

		"minist", "menist", //menistério, menistra, menistro
		"mó(s)? ", "muola$1 ",
		"moela(s)? ", "cachuola$1 ",
		"moinho(s)? ", "molino$1 ",
		"mole(s)? ", "dóndio$1 ",
		"morango(s)? ", "morangano$1 ",
		"morcego(s)? ", "morciegano$1 ",
		"mordomo(s)? ", "mardomo$1 ",
		"mulher", "mulhier",
		"mulherio(s)? ", "mulheriu$1 ",
		"músico(s)?  ", "musiqueiro$1 ",
		"nação ", "nacion ",
		"nações ", "naciones ",
		"naquela(s)? ","naqueilha$1 ",
		"naquele ","naquel ",
		"naqueles ","naqueilhes ",
		"naquilo ","naqueilho ",
		"nasc", "nac",
		"nasç", "naç",
		"apôs ", "passado ",
		"após ", "passado ",
		"neblina(s)? ", "nubrina$1 ",
		"necessári", "neçair",
		"necessidade", "necidade",
		"nela(s)? ", "neilha$1 ",
		"nele ", "nel ",
		"neles ", "neilhes ",
		"nem ","nin ",
		"nenhum ", "nanhun ",
		"nenhuma(s)? ", "nanhue$1 ",
		"nenhuns ", "nanhuns ",
		"net(a|o)+(s)? ", "niet$1$2 ", //nieto,nieta
		"neve(s)? ", "niebe$1 ",
		"nevoeiro(s)? ", "nubrina$1 ",
		"ninguém ", "naide ",
		"ninhada(s)? ", "niada$1 ",
		"ninho(s)? ", "niu$1 ",
		"nisso  ","nesso ",
		"nisto ", "nesto ",
		"no(s)? ","ne l$1 ",
		"nogueira(s)? ", "nueira$1 ",
		"noite(s)? ", "nuite$1 ",
		"noss(a|o)+(s)? ", "nuoss$1$2 ",
		"notícia(s)? ","ambora$1 ",
		"nov(a|o)+(s)? ", "nuob$1$2 ",
		"nove ", "nuobe ",
		"novecentos ", "nuobecientos ",
		"novembro ","nobembre ",
		"noz ", "nuoç ",
		"nozes ", "nuozes ",
		"nú(s)? ", "amplache$1 ",
		"nublado ", "nubrado ",
		"num ","nun ",
		"numa ","nua ",
		"número(s)? ", "númaro$1 ",
		"nuvem ", "nube ",
		"nuvens ", "nubes ",
		"o ","l ",
		"oceano", "ouceano",
		"ocident", "oucident",
		"óculo(s)? ", "oclo$1 ",
		"ocupa", "acupa", //acupar, acupado
		"ódio(s)? ", "rábia$1 ",
		"odre(s)? ", "boto$1 ",
		"of([a-zí]+)", "ouf$1",
		"ofensiv", "oufensib",
		"oiro(s)? ", "ouro$1 ",
		"oitenta ", "uitenta ",
		"oito ", "uito ", //uito, uitenta
		"oitocentos ", "uitecientos ",
		"olá ", "oulá ",
		"olho(s)? ", "uolho$1 ",
		"olmo(s)? ", "uolmo$1 ",
		"onda(s)? ", "óndia$1 ",
		"ontem ", "onte ",
		"ora", "oura", //oração
		"orç([a-z]+)", "ourç$1",
		"ord([a-z]+)", "ourd$1",
		"orelha(s)? ", "oureilha$1 ",
		"órg", "uorg",
		"orgulho(s)? ", "proua$1 ",
		"origem ","ourige ",
		"origens ","ouriges ",
		"orvalhado(s)? ", "ourbalhado$1 ",
		"orvalho(s)? ", "ourbalheira$1 ",
		"os ","ls ",
		"osso(s)? ", "uosso$1 ",
		"ou ", "ó ",
		"oubra(s)? ", "obra$1 ",
		"ourdem ", "orde ",
		"ourdens ", "ordes ",
		"ouriço(s)? ", "pelhiço$1 ",
		"outon", "outonh",
		"outubro ","outubre ",
		"ovelha(s)? ", "canhona$1 ",
		"ovo(s)? ", "uobo$1 ",
		"oxigénio(s)? ", "ouxigénio$1 ",
		"ozono(s)? ", "ouzono$1 ",
		"pá(s)? ", "pala$1 " ,
		"paciência", "pacéncia",
		"padaria(s)? ", "panadarie$1 ",
		"padeir", "panadeir", //panadeiro
		"página(s)? ", "páigina$1 ",
		"país ", "paíç ",
		"paixão ", "peixon ",
		"paixões ", "peixones ",
		"palestra(s)? ", "palhestra$1 ",
		"palestrante(s)? ", "palhestrante$1 ",
		"pano(s)? ", "panho$1 ",
		"pão ", "pan ",
		"parabéns ","parabienes ",
		"parceria(s)? ", "parcerie$1 ",
		"parente(s)? ", "pariente$1 ",
		"passarinh(a|o)+(s)? ","paxaric$1$2 ",
		"pássaro(s)? ", "páixaro$1 ",
		"pato(s)? ", "parro$1 ",
		"pau(s)? ", "palo$1 ",
		"pé(s)? ","pie$1 ",
		"pedra(s)? ", "piedra$1 ",
		"pedrinha(s)? ", "china$1 ",
		"pela(s)? ","pula$1 ",
		"pele(s)? ","piel$1 ",
		"peneira(s)? ", "penheira$1 ",
		"peneirar", "penheirar",
		"penha(s)? ", "peinha$1 ",
		"pénis ", "gaita ",
		"pente(s)? ", "peine$1 ",
		"pentead(a|o)+(s)? ", "peinad$1$2 ",
		"pentear([e]?)(s)? ", "peinar$1$2 ",
		"pentei", "pein",
		"pequen(a|o)+(s)? ", "pequeinh$1$2 ",
		"percevejo", "chizme",
		"perfeit", "purfeit",
		"perigo", "peligro", //peligro, peligrosa
		"pero(s)? ", "cermeinho$1 ",
		"perto ", "acerca ",
		"perto ", "acerca ",
		"pescoço(s)? ", "cachaço$1 ",
		"pessoa", "pessona",
		"pestana(s)? ", "ceilha$1 ",
		"piano(s)? ", "pianho$1 ",
		"pilriteiro(s)? ", "spineiro$1 ",
		"piment(a|o)+(s)? ", "pumient$1$2 ",
		"pimenteira(s)? ", "pumenteira$1 ",
		"pingo(s)? ", "unto$1 ",
		"piscar ", "piçcar ",
		"planalto(s)? ", "praino$1 ",
		"pluma(s)? ", "pruma$1 ",
		"pois ", "pus ",
		"pólvora(s)? ", "pólbara$1 ",
		"pomba(s)? ", "palomba$1 ",
		"pombais ", "palumbares ",
		"pombal ", "palumbar ",
		"pombinha", "palumbica",
		"pont(a|o)+(s)? ", "punt$1$2 ",
		"ponta(s)?  ", "punta$1 ",
		"ponte(s)? ", "puonte$1 ",
		"ponteira(s)? ", "punteira$1 ",
		"pontinha(s)? ", "puntica$1 ",
		"pontões ", "puntones ",
		"porco(s)? ", "cochino$1 ",
		"porquê", "porquei",
		"porta(s)? ", "puorta$1 ",
		"portada", "portalada",
		"portugal ", "pertual ",
		"portugu", "pertu",
		"poss[í|i]+vel", "possible", //possível, possivelmente
		"possíveis ", "possibles ",
		"pr([o|ó]+)pri", "pr$1pi",
		"pr([o|ó]+)x", "pr$1ss",
		"precipício ", "faia ",
		"precipício(s)? ", "faia$1 ",
		"precis", "percis", //perciso
		"preço(s)? ", "précio$1 ",
		"prego(s)? ", "crabo$1 ",
		"presiden", "persiden",
		"presidên", "persidén",
		"pressa(s)? ", "priessa$1 ",
		"presunto(s)? ", "persunto$1 ",
		"primár", "purmár",
		"primeir", "purmeir",
		"principais ", "percipales ",
		"principal ", "percipal ",
		"principalmente ", "percipalmente ",
		"simultaneamente ", "a la par",
		"auxílio", "ajuda",
		"príncipe", "príncepe",
		"província", "porbíncia",
		"município", "munecípio",
		"liberdade", "libardade",
		"problema(s)? ", "porblema$1 ",
		"professor(es|a|as)? ", "porsor$1 ",
		"profun", "perfun", //profunda
		"program", "porgram",
		"proje(c)?t", "porjet", //porjecto
		"quaisquer ","qualesquiera ",
		"qualquer ","qualquiera ",
		"quase ","quaije ",
		"quatrocentos ", "quatrocientos ",
		"quebradiço", "salagre",
		"queij", "queis",
		"quem ","quien ",
		"quente(s)? ", "caliente$1 ",
		"quiet", "quet",
		"quinhentos ", "quenhientos ",
		"rabiça(s)? ", "rabadielha$1 ",
		"raiva(s)? ", "rábia$1 ",
		"ranho(s)? ", "moncas ",
		"rapariga(s)? ", "rapaza$1 ",
		"rasteira(s)? ", "çancadielha$1 ",
		"razão ", "rezon ",
		"razões ", "rezones ",
		"real", "rial",
		"rebanho(s)? ", "ganado$1 ",
		"referência(s)? ","refréncia$1 ",
		"relha(s)? ", "reilha$1 ",
		"relógio(s)? ", "reloijo$1 ",
		"remoinho", "remolino",
		"resposta(s)? ", "respuosta$1 ",
		"ressuscit", "ressucit",
		"réstea(s)? ", "raça$1 ",
		"ribeir(a|o)+(s)? ", "rieir$1$2 ",
		"rio(s)? ", "riu$1 ",
		"roca(s)? ", "ruoca$1 ",
		"rocha", "peinha",
		"roda(s)? ", "ruoda$1 ",
		"rosmaninho(s)? ", "tomilho$1 ",
		"rosto(s)? ","rostro$1 ",
		"rua(s)? ", "rue$1 ",
		"sabão ", "xabon ",
		"sabedoria", "sabedorie",
		"sabões", "xabones",
		"sabonete", "xabonete",
		"saída(s)? ", "salida$1 ",
		"sapat", "çapat", //çapato, çapatilha
		"sapataria(s)? ", "çapatarie$1 ",
		"sapateir(o|a)+(s)? ", "çapateiro$1$2 ",
		"sarda", "xarda",
		"sardento", "xardoso",
		"sardinha(s)? ", "sardina$1 ",
		"sargento", "cergento",
		"satisf", "sastif",  //sastifeito
		"saudade(s)? ","suidade$1 ",
		"saúde(s)? ","salude$1 ",
		"sebastião ", "sabastian ",
		"século(s)? ", "seclo$1 ",
		"segurança(s)? ", "sigurança$1 ",
		"segur(o|a)+(s)? ", "sigur$1$2 ",
		"seio(s)? ", "teta$1 ",
		"seiscentos ", "seicientos ",
		"seixada(s)? ", "xeixada$1 ",
		"seixo(s)? ", "xeixo$1 ",
		"sem ","sin ",
		"semana(s)? ", "sumana$1 ",
		"seme([a|e|i|o|u]+)", "sembr$1", //semear -> sembrar
		"sempre ", "siempre ",
		"senão ","senó ",
		"serviço(s)? ", "serbício$1 ",
		"sete "," siete ",
		"setecentos ", "sietecientos",
		"setembro ","setembre ",
		"seu(s)? ", "sou$1 ",
		"sext(a|o)+(s)? ", "sest$1$2 ",
		"sforço(s)? ", "sfuorço$1 ",
		"sim ","si ",
		"sineta(s)?  ", "campanina$1 ",
		"sino", "campana",
		"soalho(s)? ", "sobrado$1 ",
		"soar ", "sonar ",
		"sobrancelha(s)? ", "subreceilha$1 ",
		"sobre ", "subre ",
		"sobrinh(a|o)+(s)? ", "sobrin$1$2 ",
		"sociedade", "sociadade",
		"soco(s)? ", "çupapo$1 ",
		"som ", "sonido ",
		"sombra(s)? ", "selombra$1 ",
		"somente ", "solamente ",
		"sons ", "sonidos ",
		"sopa(s)? ", "caldo$1 ",
		"sozinh(a|o)+(s)? ", "solic$1$2 ",
		"sua(s)? ", "sue$1 ",
		"sumagre(s)? ", "cemaque$1 ",
		"surd(a|o)+(s)? ", "xord$1$2 ",  //xordo
		"também ", "tamien ",
		"tampa(s)? ", "tapadeira$1 ",
		"tão ", "tan ",
		"tear", "telar",
		"teatro(s)? ", "triato$1 ",
		"teia(s)?  de  aranha ", "aranheira$1 ",
		"teimos(a|o)+(s)? ", "maluc$1$2 ",
		"telha(s)? ", "teilha$1 ",
		"tempo(s)? ", "tiempo$1 ",
		"tenaz(es)? ", "tanazes ",
		"teoria(s)? ", "teorie$1 ",
		"terra(s)? ", "tierra$1 ",
		"tesoura(s)? ", "tejeira$1 ",
		"testa(s)? ", "tiesta$1 ",
		"teu(s)? ", "tou$1 ",
		"texto", "testo",
		"golfinho(s)?", "golfino$1",
		"texug(a|o)+(s)? ", "teixug$1$2 ",
		"tingido", "tenhido",
		"tingir", "tenhir",
		"título(s)? ", "títalo$1 ",
		"catítulo(s)? ", "catítalo$1 ",
		"toda ", "to ",
		"todo ", "to ",
		"toucinho ", "quenhon ",
		"toucinhos ", "quenhones ",
		"trabalhador(o|a)+(s)?  ", "trabalhadeir$1$2 ",
		"transmon", "strasmun", //stransmuntano
		"travessa(s)? ", "trabiessa$1 ",
		"tremer", "tembrar",
		"tremoceir(a|o)+(s)? ", "antramoceir$1$2 ",
		"tremoço(s)? ", "antramoço$1 ",
		"trezentos ", "trezientos ",
		"tudo ", "todo ",
		"últim", "redadeir", //redadeiro, redadeira...
		"um ","un ",
		"uma(s)? ","ua$1 ",
		"umbigo", "ambelhigo",
		"união ", "ounion ",
		"unid", "ounid",
		"uniões ", "ouniones ",
		"univ", "ounib", //ouniberso
		"urinar ", "mejar ",
		"úteis ", "úteles ",
		"útil ","útele ",
		"utili", "outili",
		"vadiar ","çarandar ",
		"vagaros(o|a)+(s)? ", "debagaros$1$2 ",
		"vagem ", "baina ",
		"vagens ", "bainas ",
		"vagina(s)? ", "parracha$1 ",
		"valentia ", "balentie ",
		"vapor(es)? ", "oupor$1 ",
		"veia(s)? ", "bena$1 ",
		"velh(a|o)+(s)? ", "bielh$1$2 ",
		"velhice(s)? ", "belheç$1 ",
		"verão", "berano",
		"vind(a|o)+(s)? ", "benid$1$2 ",
		"vinho(s)? ", "bino$1 ",
		"vizinh(a|o)+(s)? ", "bezin$1$2 ",
		"vocês ", "bós ",
		"voss(a|o)+(s)? ", "buoss$1$2 ",
		"vulva(s)? ", "parracha$1 ",
		"xisto(s)? ", "piçarra$1 ",
		"zangad", "anrabiad",
		"zangar", "anrabiar",
		"presen", "persen",


		"stadunidense", "amaricano",
		"milit", "melit", //melitar
		"esposa", "mulhier",
		"montanh", "muntanh", //muntanha
		"disci", "deci", //deciplina

		//erros Biquipédia
		"stado-ounidense", "amaricano",
		"cristianismo", "crestianismo",
		"indivíd", "andebíd",
		"soldado", "suldado",
		"portanto", "antoce",
		"cunteúdo", "cuntenido",

		// AMPORTA LA ORDE
		"contudo ","assi i todo ",
		"homen", "houmen", //houmenaige,  houmano
		"ig", "eig",  // AMPORTA ORDE
		"ob([a-z]+)", "oub$1",
		"oubra(s)? ", "obra$1 ",
		"dorm", "drum",
		"adorm", "adrum",
		"([a-z]+)áveis ", "$1ables ",
		"([a-z]+)ável ", "$1able ",//agradable
		"([a-z]+)ível ", "$1ible ",//"audible
		"([a-z]+)íveis ", "$1ibles ",
		"([a-z]+)óvel ", "$1oble ",
		"([a-z]+)óveis ", "$1obles ",

		"([a-z]+)óis ", "$1oles ",
		"([a-z]+)ónio(s)? ", "$1onho$2 ",



		"([a-z]+)ário(s)? ", "$1airo$2 ", //armairo

		"[\-]+ no "," nel ",
		"oria(s)? ", "orie$1 ", //minorie
		"mili", "meli", //melitar
		"mais ", "más ",

		//"ceg", "cieg",
		"conf", "cunf",
		"conv", "cumb", //cumbençon
		"desem", "zam",
		"desen", "zam",
		"trans", "tras",
		"produt", "pordut",
		"energ", "einerg", //einergico, einergie
		"emerg", "eimerg", //eimergir
		"emed", "eimed", //eimediato

		"respon", "respun",

		"ep", "eip",
		"op", "oup",//ouposiçon, ouportunidade
		"ev", "eib",

		"dese", "ze",
		"desa", "za",
		"desi", "zei",
		"desv", "zb", //"zbantagige ",
		"desb", "zb", //"desbater "??
		"desn", "zn", //"znutrida "??

		"não  ([^\\.|^;|^,|^:]+)","nun $1",
		"não ","nó ",

		"aconp", "acump",
		"acon", "acun", //acunteciu
		"comp", "cump", //cumputador
		"comb", "cumb", //cumbate

		"ide", "eide", //eideia
		"env", "amb", //ambiar, ambolber
		"emv", "amb",
		"eng", "ang",
		"emp", "amp",
		"enc", "anc",
		"end", "and",
		//AMPORTA ORDE
		"ande ", "ende ",
		"enf", "anf",
		"ens", "ans",//ansinar
		"enr", "anr",//ansinar
		"enx", "anx", //anxame
		"erg", "arg",

		"ofe", "oufe", //oferta,  ofende
		"oli", "ouli", //oulibeira
		"olí", "oulí", //oulibeira
		"opi", "oupi", //oupinião
		"otimi", "outimi", //outimismo
		"([ó|o])rf", "uorf", //uorfano
		"ori", "ouri", //ourige
		"ocup", "acup", //acupação

		"restaur", "restour",
		"const", "cust",
		"con([^eaiou]+)","cun$1",
		"descon([^eaiou]+)","çcun$1",
		"símbolo", "simblo",
		"etimologia","etimologie",
		"colónia", "quelónia",
		"triángulo", "trianglo",
		"Hungria", "Hungrie",
		"Turquia", "Turquie",


		"econ","eiquen",//eiquenomie
		"imp", "amp", //amportante
		"im", "eim",  //eimaculado
		"irm", "arm", //armandade
		"inf", "anf", //anferior, anfierno
		"inv", "amb", //ambierno //todo
		"he([^i]+)", "hei$1",

		"dis", "ç",	  // AMPORTA LA ORDE
		"çs", "diss",	  // AMPORTA LA ORDE
		"çto", "disto",	  // AMPORTA LA ORDE
		"descob", "çcub",
		"des([^a|^e|^i|^o|^u|^s])", "ç$1",	  // AMPORTA LA ORDE

		"aut", "out", //auto, autu, autó
		"el([a-zé]+)", "eil$1", //eilegante
		"irr([a-z]+)","eirr$1", //eirredutor
		"im([a]+)g","eim$1g", //eimaginable
		"im([q|w|r|t|p|s|f|g|h|j|k|l|ç|z|x|c|n]+)","am$1", //ambasão
		"inb"," amb", //ambasão
		"in([q|w|r|t|p|s|f|g|h|j|k|l|ç|z|x|c|n]+)","an$1", //ambasão
		"ind([^a]+)","and$1", //andicar  //tira inda
		"il([^h]+)", "eil$1", //eiludir
		"exam", "eisam", //eisame
		"exem","eisem", //eisemplo
		"exec","eisec", //eisecutar
		"exib", "eisib", //eisibir
		"excel", "eicel", //eicelente
		"exis","eisis", //eisistir
		"exig", "eisig", //eisigir
		"exij", "eisij", //eisijo
		"exer", "eiser", //eisercer
		"exot", "eisot", //eisotico
		"exíl", "eisíl", //eisílio
		"oxid", "ouxid",
		"equa", "eiqua", //eiquador; eiquaçon...
		"exp", "sp",  //spriéncia
		"iso", "eiso",  //eisolar
		"inalt", "einalt",

		"ex","s",
		"es([^s]+)", "s$1",
		"s - ","ex-", //ex-purmeiro

		"cabelo","pelo",  // solo apuis de pelo->pul    AMPORTA LA ORDE

		"bons  ([a-zAz]+)([a-zAz]*)([o|e|z|ç]+)(s)? ", "buns $1$2$3$4 ",    // AMPORTA LA ORDE
		"bons ", "buonos ",    // AMPORTA LA ORDE
		"bom  ([a-zAz]+)([a-zAz]*)([o]+)(s)? ", "bun $1$2$3$4 ",    // AMPORTA LA ORDE
		"bom ", "buono ",    // AMPORTA LA ORDE


		"-  l(a|o)+(s)?","-l$1$2", //para mantener "-la"   // AMPORTA LA ORDE
		"-  a ","-la ",

		// ANGANHOS

		"la  ([a-z]*r) ","a $1 ", //corecção  a , verbo a partir, a saber   AMPORTA LA ORDE
		"la  nun  ([a-z]*r) ","a nun $1 ", // "a nun saber"
		"la  ([a-z]*es) ","a $1 ", //corecção  a , "a preocupaçones"
		"la  ([a-z]*o) ","a $1 ", //corecção  a  "a camino", "a burro"
		"la  ([a-z]*os) ","a $1 ", //corecção  a  "a caminos"
		"l  calor", "la calor",
		"la  naide","a naide", //corecção  a queda a   AMPORTA LA ORDE
		"la  cerca", "a cerca",//corecção  a queda a   AMPORTA LA ORDE

		"la  esse", "a esse",//corecção  a queda a   AMPORTA LA ORDE
		"la  essa", "a essa",//corecção  a queda a   AMPORTA LA ORDE

		"la  un", "a un",//corecção  a queda a   AMPORTA LA ORDE
		"la  ua", "a ua",//corecção  a queda a   AMPORTA LA ORDE

		"la  ti", "a ti",//corecção  a queda a   AMPORTA LA ORDE
		"la  mi", "a mi",//corecção  a queda a   AMPORTA LA ORDE
		"la  el", "a el",//corecção  a queda a   AMPORTA LA ORDE
		"la  eilha", "a eilha",//corecção  a queda a   AMPORTA LA ORDE
		"la  nós", "a nós",//corecção  a queda a   AMPORTA LA ORDE
		"la  bós", "a bós",//corecção  a queda a   AMPORTA LA ORDE
		"la  eilhes", "a eilhes",//corecção  a queda a   AMPORTA LA ORDE
		"la  eilhas", "a eilhas",//corecção  a queda a   AMPORTA LA ORDE

		"la  to", "a to", //corecção  a queda a   AMPORTA LA ORDE
		"la  todo", "a todo", //corecção  a queda a   AMPORTA LA ORDE
		"la  ([0-9]+)","a $1",


		//repor de novo o "E"
		"sto ", "esto ",    // AMPORTA LA ORDE

		"ste ", "este ",    // AMPORTA LA ORDE
		"stes ", "estes ",    // AMPORTA LA ORDE

		"sta ", "esta ",	  // AMPORTA LA ORDE
		"stas ", "estas ",  // AMPORTA LA ORDE
		"çte ","deste ",     // AMPORTA LA ORDE
		"çtes ","destes ",    // AMPORTA LA ORDE

		"çta ","desta ",    // AMPORTA LA ORDE
		"çtas ","destas "     // AMPORTA LA ORDE

		//fim de repor de novo o "E"

		);

		//para garantir que ampeça i acaba cun spácio
		testo = " "+ testo +" ";


		for(i=0;i<upperCase.length;i=i+2)
		{
			var testo1= " "+upperCase[i].substr(0, 1).toUpperCase()+upperCase[i].substr(1);
			var testo2= " "+upperCase[i+1].substr(0, 1).toUpperCase()+upperCase[i+1].substr(1);
			var re = new RegExp(testo1, "gm");
			testo = testo.replace(re, testo2);
		}

		for(i=0;i<upperCase.length;i=i+2)
		{
			var testo1= " " + upperCase[i].substr(0, 1).toLowerCase() + upperCase[i].substr(1);
			var testo2= " " + upperCase[i+1].substr(0, 1).toLowerCase() + upperCase[i+1].substr(1);
			var re = new RegExp(testo1, "gm");
			testo = testo.replace(re, testo2);
		}

		//normalmente letras pequeinhas, treminaçones
		var lowerCase=new Array(
			//berbos
			//ar regular beilar
			"([a-zA-Zç]+)arão ", "$1aran ",
			"([a-zA-Zç]+)aram ", "$1órun ",
			//"([a-zA-Zç]+)aram ", "$1áran ",
			"([a-zA-Zç]+)arem ", "$1áren ",

			//er regular - Comer
			//"([a-zA-Zç]+)erão ", "$1eran ",
			//"([a-zA-Zç]+)eram ", "$1íran ",
			"([a-zA-Zç]+)erem ", "$1íren",
			//"([a-zA-Zç]+)erem ", "$1éren ",
			"([a-zA-Zç]+)eram ", "$1írun ",

			//ir regular - bibir
			"([a-zA-Zç]+)erão ", "$1iran ",
			//"([a-zA-Zç]+)eram ", "$1íran ",
			//"([a-zA-Zç]+)erem ", "$1íren",
			//"([a-zA-Zç]+)erem ", "$1íren ",
			//"([a-zA-Zç]+)eram ", "$1írun ",

			"([a-zA-Zç]+)deu ", "$1diu ",
			"([a-zA-Zç]+)meu ", "$1miu ",
			"([a-zA-Zç]+)beu ", "$1biu ",
			"íssim(a|o)", "íssem$1",

			"([a-zA-Zç]+)abia(s)? ", "$1abie$2 ",
			"([a-zA-Zç]+)avia(s)? ", "$1abie$2 ",
			"([a-zA-Zç]+)ecia(s)? ", "$1ecie$2 ",

			"([a-zA-Zç]+)aleu ", "$1aliu ",
			"([a-zA-Zç]+)aceu ", "$1aciu ",
			"([a-zA-Zç]+)eceu ", "$1eciu ",
			"([a-zA-Zç]+)eveu ", "$1ebiu ",
			"([a-zA-Zç]+)oveu ", "$1obiu ",
			"([a-zA-Zç]+)lveu ", "$1lbiu ",

			"([a-zA-Zç]+)avam ", "$1ában ",
			"([^s]+)tia(s)? ", "$1tie$2 ",
			"([a-zA-Zç]+)aria(s)? ", "$1arie$2 ",
			"([a-zA-Zç]+)eria(s)? ", "$1erie$2 ",
			"([a-zA-Zç]+)iria(s)? ", "$1irie$2 ",

			"([a-zA-Zç]+)azia(s)? ", "$1azie$2 ", //fazia -> fazie

			"([a-zA-Zç]+)êm ","$1énen ", //ténen
			"([a-zA-Zç]+)êem ","$1énen ", //bénen

			//FIXME
			"([a-zA-Zç]+)enhamos ","$1éngamos ", //tenhamos
			//"([a-zA-Zç]+)enham ", "$1engan ", //tenham
			//"([a-zA-Zç]+)enha ", "$1enga ", //tenham
			//"([a-zA-Zç]+)enho ", "$1engo ", //tenho

			"([a-zA-Zç]+)teu ", "$1tiu ", //bateu
			"([a-zç]+)([a-z]+)esse ", "$1$2isse ", //aparecesse -> aparecisse nesses
			"antrisse(s)? ", "antresse$1 ", //correcção
			"([a-zç]+)([a-z]+)esses ", "$1$2isses ", //aparecesses -> aparecisses //desses tira n, d
			"([a-zA-Zç]+)iveste ", "$1ubiste ", //estiveste
			"([a-zA-Zç]+)([a-z]+)este(s)? ", "$1$2iste$3 ", //estiveste
			//FIXME
			"nordiste(s)? ", "nordeste$1 ",
			"sudiste(s)? ", "sudeste$1 ",
			"sudoiste(s)? ", "sudoeste$1 ",
			"liste(s)? ", "leste$1 ",
			"São ","San ",
			"çaste ", "ceste ",
			"([a-zA-Z]+)aste ", "$1este ",
			" lhe(s)? ", " le$1 ",
			"cuntra ", "contra ",
			"cunde ", "conde ",

			"dizer", "dezir",

			//FIXME
			"çcriber", "çcrebir",
			"çcribiu", "çcrebiu",
			"screver", "screbir",

			"ej([o|a]+)", "eij$1", //aleije, azuleijo
			//"([^m|^i]+)elh", "$1eilh", //orelhas-> oureilhas //melhor n dá

			"ais ","ales ",
			" stales ", " stais ",
			" stables ", " stabais ",
			"ãos ","ones ",
			"ão ","on ",
			"ões ","ones ",
			"õe", "one", //??
			"ães ", "anes ",
			"ãe ", "ane ", //??

			"esia(s)? ", "esie$1 ",  //freguesia
			"([a-z]+)vel ", "$1ble ",
			"([a-z]+)mento(s)? ", "$1miento$2 ",
			"([a-z]+)veis ", "$1bles ",
			"([a-z]+)agens ", "$1aiges ",
			"([^a^e^i^o^u]+)gens ", "$1ges ",
			"([^a^e^i^o^u]+)gem ", "$1ge ",
			"([a-z]+)agem ", "$1aige ",

			"([^u]+)ns ", "$1nes ", //fins
			"([^né]+)dia ", "$1die ",	//óndia
			"([^n]+)dias ", "$1dies ",

			"([a-z]+)ogia(s)? ", "$1ogie$2 ", // biologie
			"([a-z]+)acia(s)? ", "$1acie$2 ", // democracie
			"([a-z]+)gia(s)? ", "$1gie$2 ",
			"([a-z]+)afia(s)? ", "$1afie$2 ",
			"([a-z]+)apia(s)? ", "$1apie$2 ",
			"([a-z]+)omia(s)? ", "$1omie$2 ",
			"([a-z]+)etria(s)? ", "$1etrie$2 ",
			"([a-z]+)ície(s)? ", "$1ice$2 ",
			"([a-z]+)écie(s)? ", "$1ece$2 ",

			//"([a-zA-Z]+)ox(a|o)+(s)? ", "$1oix$2$3 ", //coixo, roixo, roixa


			//repetidos, meio de las palabra
			"cresce", "crece",
			"cento", "ciento",
			"sobre", "subre",
			"rodapé", "rodapie",
			//"ter ", "tener ",
			"tinha ", "tenie ",
			"comp", "cump",
			"coisa", "cousa",
			"oiro", "ouro",

			"energia", "einergie",
			"abert", "abiert",
			"propri", "propi",
			"própri", "própi",

			"prox", "pross",
			"próx", "próss",
			"máx", "máss",

			"exis","eisis",
			"exem","eisem",

			"texto", "testo",
			"viver", "bibir",
			"inclui", "anclui",
			"coberta", "cobierta",
			// fim repetidos

			"([a-z]+)ini", "$1eni", //oupenion
			"([a-z]+)ivi", "$1ebi", //cebil
			"([^e]+)isi", "$1esi", //besible
			"([a-z]+)ili", "$1eli", //besible

			"hidr", "heidr", //heidratos

			"V","B",
			"v","b",
			"ü", "u",
			"Ü", "U",

			"â","á",
			"ô","ó",
			"ê","é",
			"ü","u",

			"Â","Á",
			"Ô","Ó",
			"Ê","É",
			"Ü","U",

			"ã(s)? ", "ana$1 ", //maçana

			//"in", "ein", ??

			"([a-z]+)bili", "$1bli", // porbalidade
			"([a-z]+)bele", "$1ble", //stablecer

			"deus", "dius",

			"tinho(s)? ", "tico$1 ",
			"tinha(s)? ", "tica$1 ",

			//melhoria
			"fere ", "fire ",
			"edade", "adade",
			"áculo(s)? ","aclo$1 ",
			"éculo(s)? ","eclo$1 ",
			"séc .", "sec.",
			"ículo(s)? ","iclo$1 ",
			"óculo(s)? ","oclo$1 ",
			"culo(s)? ","clo$1 ",

			" clo "," culo ",
			" clos "," culos ",

			" Clo "," Culo ",
			" Clos "," Culos ",

			"oo","o",
			"cç", "ç",
			"z ","ç ",
			"ubs", "us",
			"ct", "t",
			"cc", "c",
			"ee", "e",
			"pt", "t",
			"m ", "n ",

			//melhoria

			" la  ([a|e|i|o|u|h]+)", " l'$1",
			" l  ([a|e|i|o|u|h]+)", " l'$1",
			" que  ([a|e|i|o|u|h]+)", " qu'$1",
			" de  ([a|e|i|o|u|h]+)", " d'$1",
			" te  ([a|e|i|o|u|h]+)", " t'$1",

			" La  ([a|e|i|o|u|h]+)", " L'$1",
			" L  ([a|e|i|o|u|h]+)", " L'$1",
			" Que  ([a|e|i|o|u|h]+)", " Qu'$1",
			" De  ([a|e|i|o|u|h]+)", " D'$1",
			" Te  ([a|e|i|o|u|h]+)", " T'$1",

			//brasileirada
			/*
			"([a-z]*)ando ", "a $1ar ",
			"([a-z]*)endo ", "a $1er ",
			"([a-z]*)indo ", "a $1ir ",

			"([a-zA-Z]*)ando ", "A $1ar ",
			"([a-zA-Z]*)endo ", "A $1er ",
			"([a-zA-Z]*)indo ", "A $1ir ",
			*/

			"qu'a ", "que a ",
			"para  la ", "pa la ",
			"para  las ", "pa las ",
			"para  l ", "pa l ",
			"para  ls ", "pa ls ",
			"cunhe", "conhe",
			" pales ", " pais ",
			" (A|a)ssi  i  to ", " $1ssi i todo",
			" dables ", " dábades ",
			" dales ", " dais ",

			" Pales ", " Pais ",

			"Unes ", "Uns",
			"unes ", "uns",

			" Dables ", " Dábades ",
			" Dales ", " Dais ",

			" Más ", " Mais ",
			" más ", " mais ",

			"A maior", "La maior",
			" a maior", " la maior",

			//Biquipédia
			//" {  { ", "{{Wp/mwl/",
			" \\[  \\[ Categoria", "[[Catadorie",
			" \\[  \\[ Category", "[[Catadorie",
			" \\[  \\[ Eimaige", "[[Fexeiro",
			" \\[  \\[ File", "[[Fexeiro",
			" \\[  \\[ Eimage", "[[Fexeiro",
			//" \\[  \\[ ", "[[../",
			//" \\]  \\] ", "/]]",
			" \\| ([a-zA-Z0-9áàâãäÁÀÂÃÄéèêëÉÈÊËíìîïÍÌÎÏòóôõöÓÒÔÕÖùúûüÚÙÛÜçÇ ]*)\\/\\]\\] ", "|$1]]",
			//correcções wiki
			"(g|G)+eórgie", "Geórgia",
			"\\. cun", ".com",
			"\\. t", ".pt",
			"seclo(s)? ([^B]*)?B([^B])?","seclo$1 $2V$3",
			"la . C", "a.C",
			" < refrences /  >", "<references/>",
			"L(h)?igaçones (s|S)+ternas", "Lhigaçones Sternas",
			"balign", "valign",
			"lheft", "left",
			"centener", "center",
			"setion", "section",
			"refre", "diç",
			"Dabid", "David",
			"Disse", "Desse",
			" disse", " desse",

			//Correçones
			"éia(s)? ", "eia$1 ",
			"Mídie", "Média",
			" mídie", " média",

			"Bair(a|o)+(s)? ", " bári$1$2 ",
			" bair(a|o)+(s)? ", " bári$1$2 ",

			" n ", " m ",

			" kn(²)? ", " Km$1 ",
			" Kn(²)? ", " Km$1 ",


			"Binhales", "Binhais",
			"Bimioso", "Bumioso",
			"Urrós", "Ruolos",
			"commones", "commons",
			"Ampeçalmente", "Einicialmente",
			" ampeçalmente", " einicialmente",
			"Leonardo  de  la  Binci", "Leonardo da Vinci",
			"Israel ", "Eisrael ",
			"Jerusalén ", "Jarusalen ",
			"Binhales ", "Binhais ",
			"Afonso", "Fonso",
			"Juan", "João",
			"Bieira", "Viera",
			"Queiroç", "Queiroz",
			"Queiroç", "Queiroz",
			"Freport", "Freeport",
			"bok", "book",
			"Bok", "Book",
			"Ounibersity", "University",
			"ounibersity", "university",

			"freport", "freeport",
			"Freport", "Freeport",
			"Lhisboua ","Lisboua ",
			"Guimaranes", "Guimarães",
			"Camones", "Camões",
			"Richtener","Richter",
			"Amadiu", "Amadeu",
			"amadiu", "amadeu",
			"Cristófe", "Cristóvão",
			"Passos  Coneilho", "Passos Coelho",
			"Jorge  Coneilho", "Jorge Coelho",
			"Banessa", "Vanessa",
			"Beatriç", "Beatriz",
			"Willian ", "William ",
			"Gogle", "Google",
			"Oubama", "Obama"
			);

		for(i=0;i<lowerCase.length;i=i+2)
		{
			var testo1= lowerCase[i];
			var testo2= lowerCase[i+1];
			var re = new RegExp(testo1, "gm");
			testo = testo.replace(re, testo2);
		}

		//Mirandês

		if(sendines)
			{
				var re = new RegExp(" l([a|á|à|e|é|è|i|í|ì|o|ó|ò|u|ú|ù]+)([a-z]+)", "gm");
				testo = testo.replace(re," lh$1$2");
				var re = new RegExp(" L([a|á|à|e|é|è|i|í|ì|o|ó|ò|u|ú|ù]+)([a-z]+)", "gm");
				testo = testo.replace(re," Lh$1$2");

				//correcçao, manter la, las, les, le, lo
				var re = new RegExp(" lh(a|i|e|o|u)([s]??) ", "gm");
				testo = testo.replace(re," l$1$2 ");


				var re = new RegExp(" Lh(a|i|e|o|u)([s]??) ", "gm");
				testo = testo.replace(re," L$1$2 ");
			}


		//por causa  da garantia que ampeça cun spácios
		var length = testo.length-2;
		testo = testo.substr(1, length);

		simblos = " " + simblos + " ";
		var re = new RegExp(simblos, "g");
		testo = testo.replace(re, "$1");

		//duas seguidas
		var re = new RegExp("  ( )?", "g");
		testo = testo.replace(re, " ");

		//document.getElementById('resultado').innerHTML=testVar;
		return testo;

	}
