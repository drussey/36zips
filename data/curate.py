"""Hand-curated entries. Each row: (year, artist_credit, song_title_substring, performer_or_None,
quote, price_k, kind, currency, city, confidence, flags, note).
kind: sell | buy | quoted | profit.  price_k in thousands. flags: list of strings.
Genius URL/id joined from raw hit dumps by song title."""
import json, glob, re, csv

E = []
def add(year, artist, song, performer, quote, price, kind="quoted", cur="USD", city=None, conf="high", flags=(), note=None, src="lyric_search"):
    E.append(dict(year=year, artist=artist, song=song, performer=performer, quote=quote,
                  price_k=price, kind=kind, currency=cur, city=city, confidence=conf,
                  flags=list(flags), note=note, source=src))

# ---- 1990s
add(1992,"Pooh-Man","Niggas Ain't Playin'",None,"Drop a key for twenty five like they was hot",25,"sell","USD","Oakland, CA","medium")
add(1992,"UGK","Pocket Full of Stones","Pimp C","17-5, I got a bird on they ass",17.5,"quoted","USD","Port Arthur, TX","medium",note="17.5 read as $17,500 for the bird (kilo)")
add(1994,"Kokane","All Bark No Bite","Kokane","Cause I gotta slang my funk at 17-5 a ki",17.5,"sell","USD","Los Angeles, CA")
add(1995,"Master P","Dead Presidents","Master P","25 G's for a key",25,"quoted","USD","New Orleans, LA / Richmond, CA")
add(1995,"Raekwon","Striving for Perfection","Raekwon","Fuck all this twenty for a brick shit, man",20,"buy","USD","New York, NY")
add(1995,"TRU","That's How We Break Bread",None,"Cap a key for 10 and 12, my Mexican friends",11,"buy","USD","New Orleans, LA","medium",note="range 10-12; midpoint used")
add(1996,"Pimp Daddy","Pimp'n Ain't E-Z",None,"For twenty two five, an ki for eleven five",11.5,"quoted","USD","New Orleans, LA","low",note="ambiguous; 11.5 taken as kilo price")
add(1997,"Hot Boys","Get it How U Live!!",None,"Is you bout that white sauce, 10 a keys the cost",10,"quoted","USD","New Orleans, LA")
add(1997,"TRU","Swamp Nigga","Master P","I got birds 16-5 a muthafuckin ki / Fool, when ya hit me, it's 18-5 / I gotta tax ya 2 G's",18.5,"sell","USD","New Orleans, LA",note="buys at 16.5, sells at 18.5")
add(1997,"The Notorious B.I.G.","Niggas Bleed","The Notorious B.I.G.","I got a hundred bricks, 14.5 a piece",14.5,"quoted","USD","Brooklyn, NY",note="bulk (100 bricks) price")
# ---- 2000s
add(2000,"504 Boyz","Moving Things",None,"I mean an ounce into a brick / Get it for sixteen five",16.5,"buy","USD","New Orleans, LA")
add(2001,"JAY-Z","U Don't Know","JAY-Z","Could make forty off a brick, but one rhyme could beat that",40,"profit","USD","Brooklyn, NY","high",["profit_not_price"],"profit per brick, not price; excluded from price charts by default")
add(2002,"50 Cent","Too Hot",None,"I got what you need, nineteen-five a key",19.5,"sell","USD","New York, NY")
add(2002,"Fabolous","Young'n","Fabolous","30 a gram 28 on the keys",28,"quoted","USD","Brooklyn, NY")
add(2004,"Boosie Badazz & Webbie","Hustlin'",None,"That whole slab sixteen five you got a profit",16.5,"quoted","USD","Baton Rouge, LA")
add(2005,"Gucci Mane","Hustle","Gucci Mane","A nigga gotta get the whole thing / Nineteen-five every time my phone ring",19.5,"sell","USD","Atlanta, GA")
add(2005,"D4L","I'm Da Man",None,"Seventeen five, same color t-shirt",17.5,"quoted","USD","Atlanta, GA","medium",note="echoes the Jeezy '17.5' figure")
add(2006,"Jeezy","Mr. 17.5","Jeezy","It's ya boy, Mr. 17.5",17.5,"quoted","USD","Atlanta, GA",note="Jeezy's nickname; $17,500 per kilo")
add(2006,"Jeezy","J.E.E.Z.Y.","Jeezy","Keep a plug on the white / Mr. 17-5, you niggas know the name",17.5,"quoted","USD","Atlanta, GA")
add(2006,"Rick Ross","Hustlin'","Rick Ross","Sat it on them twenty-twos, birds go for twenty-two",22,"sell","USD","Miami, FL")
add(2007,"Pimp C","True Stories","Pimp C","So I hit the fuckin' slab for the 16.5",16.5,"buy","USD","Houston, TX")
add(2007,"Andre Nickatina","7 Letters Coked Out (Intro)","Andre Nickatina","My homie said his go for eighteen five",18.5,"sell","USD","San Francisco, CA")
add(2007,"DJ Khaled","I'm So Hood (Remix)","Young Jeezy","Seventeen-five, yeah, nigga, I said it",17.5,"quoted","USD","Atlanta, GA","medium")
add(2008,"Jeezy","24 - 23","Jeezy","I used to pay Kobe, but now I pay LeBron",23,"buy","USD","Atlanta, GA",note="Kobe = 24, LeBron = 23; price fell from $24k to $23k. Album The Recession, Sept 2008")
add(2008,"Gucci Mane","Feel Like Cookin'","Gucci Mane","Give a brick for the cash charge you seventeen bands",17,"sell","USD","Atlanta, GA")
add(2008,"Gucci Mane","In the Trap",None,"Cop a bird for the twenty nigga all ten",20,"buy","USD","Atlanta, GA")
add(2008,"2 Pistols","Gettin' Money Mane","2 Pistols","Whole blocks of Anna White for twenty-two-five",22.5,"sell","USD","Tampa, FL")
add(2009,"JAY-Z","Empire State of Mind","JAY-Z","If Jeezy's payin' LeBron, I'm payin' Dwyane Wade",3,"buy","USD","Brooklyn, NY","high",["outlier","hyperbole","homage"],"Answer to Jeezy's 24-23: LeBron = 23 (i.e. $23k), Dwyane Wade = 3 => $3k a kilo. Boast, not a market price")
add(2009,"Kendrick Lamar","Best Rapper Under 25","Kendrick Lamar","Heard about eighteen rappers say that a bird can go for seventeen-point-five",17.5,"quoted","USD","Compton, CA","medium",["meta"],"commentary on other rappers' figure")
add(2009,"Ab-Soul","Introduction","Ab-Soul","Like I'm wrapped in vaseline and go for 18 5 a key",18.5,"quoted","USD","Carson, CA")
add(2009,"French Montana","Bricks & Walls","French Montana","Nah it ain't ten a key / Look homey it's 35",35,"sell","USD","Bronx, NY")
add(2009,"Gucci Mane","Time To Eat",None,"21 a key, 10 five a half a key, 55 a quarter key",21,"sell","USD","Atlanta, GA")
add(2009,"Lil' Flip & Gudda Gudda","I Keep It Street All Day",None,"The bricks go for sixteen, five if I know ya",16.5,"sell","USD","Houston, TX")
add(2009,"Raekwon","Ill Figures",None,"Brick a white nowadays is forty grand invested",40,"quoted","USD","New York, NY")
add(2009,"Jeezy","Done It","Jeezy","One nigga ooh wee, Mr. 17.5",17.5,"quoted","USD","Atlanta, GA","medium",["repeat_nickname"])
# ---- 2010s
add(2010,"Gucci Mane","Swing My Door","Gucci Mane","I count 18-5 every time they swing my door",18.5,"sell","USD","Atlanta, GA","medium",["implied_unit"],"Burrrprint 2 (2010); Genius page lists 2006. Kilo is implied, never named in the line")
add(2010,"Jeezy","Whippin All of Dat","Jeezy","Man, niggas want thirty for a brick, man",30,"buy","USD","Atlanta, GA")
add(2010,"Meek Mill","Bricks","Meek Mill","Thirty thousand, nigga that's a brick",30,"quoted","USD","Philadelphia, PA")
add(2010,"Roc Marciano","Whateva Whateva","Roc Marciano","Twenty five thousand a key",25,"quoted","USD","Hempstead, NY")
add(2011,"D. King (rapper)","Supposed to Be","D. King","'Cause bricks go for 11-5 in Dade County",11.5,"quoted","USD","Miami, FL","medium")
add(2011,"Future","We On Top",None,"Brick on top of brick they go for 28",28,"sell","USD","Atlanta, GA")
add(2011,"Money Gang","Work",None,"Thirty for a brick and ten percent",30,"sell","USD",None,"medium")
add(2012,"Meek Mill","Dreams and Nightmares (Intro)","Meek Mill","With them bricks, they go for forty, ain't no ten a key",40,"sell","USD","Philadelphia, PA")
add(2012,"Jeezy","The Motto (Remix)",None,"Birds for the thirty-three, I got my Larry on",33,"sell","USD","Atlanta, GA")
add(2012,"Gunplay","Bible on the Dash","Gunplay","When a brick was seventeen and you ain't have to rob your plug",17,"quoted","USD","Miami, FL","high",["retrospective"],"looking back at an earlier era")
add(2012,"Yo Gotti","Ain't No Turning Around",None,"Hit em' with a key again / For eighteen five, young nigga go live",18.5,"sell","USD","Memphis, TN")
add(2012,"Fredo Santana","Up Them Poles",None,"Two keys for the forty",20,"buy","USD","Chicago, IL",note="2 for 40 => 20 each")
add(2012,"Alpoko Don Aka Don Dada","Married to the Game","Alpoko Don","Eight brick full / Fifteen a piece",15,"sell","USD","Greenville, SC","medium")
add(2013,"Pusha T","Millions","Rick Ross","Got a kilo for 20, my choppas say I'm the shit",20,"buy","USD","Miami, FL")
add(2013,"Boldy James","For the Birds","Boldy James","Thirty-six for the birds and I need a brick",36,"quoted","USD","Detroit, MI")
add(2013,"Casino","Communication",None,"Thirty-six for a brick, that's the calculation",36,"quoted","USD","Atlanta, GA")
add(2013,"Doe B","30 Piece","Doe B","Bricks go for 30",30,"sell","USD","Montgomery, AL")
add(2013,"Doe B","Don't Want It",None,"But if you bring 23, you can get a whole key",23,"sell","USD","Montgomery, AL")
add(2013,"E-40","Tree in the Load",None,"Twenty four five for a brick, man",24.5,"quoted","USD","Vallejo, CA")
add(2013,"Meek Mill","I'm Leanin'",None,"Got birds for the twenty five K",25,"quoted","USD","Philadelphia, PA")
add(2013,"Tracy T","16",None,"Whole thing for 33, that's Patrick Ewing nigga",33,"sell","USD","Atlanta, GA")
add(2013,"Waka Flocka Flame","Fast Forward","Waka Flocka Flame","The bricks go for 35, that's KD",35,"sell","USD","Atlanta, GA")
add(2013,"Waka Flocka Flame","Murda She Wrote",None,"I'm 'bout to up the price / 65,000 for a brick of white",65,"sell","USD","Atlanta, GA","medium")
add(2013,"Wale","Bricks",None,"Now 16, getting them bricks for the 16",16,"buy","USD",None,"medium",["wordplay"])
add(2013,"SBOE","Money Cars Clothes",None,"I fronted 2, charging 45 each brick",45,"sell","USD","Queens, NY","medium")
add(2013,"Joey Fatts","PushaMan",None,"Five for the O and fifteen for the whole thing",15,"sell","USD","Long Beach, CA")
add(2014,"O.T. Genasis","Funk Flex Freestyle","O.T. Genasis","Plug said, \"Thirty for a brick now\"",30,"buy","USD","Long Beach, CA")
add(2014,"Dave East","In Some Shit (Part 1)","Dave East","Always used to have the bricks at 19-5, that's taxin'",19.5,"sell","USD","Harlem, NY",flags=["retrospective"])
add(2014,"E-40","Same Since '88",None,"Thirty-eight a brick on a hundred flip",38,"quoted","USD","Vallejo, CA")
add(2014,"KXNG Crooked","Fallen Rap Gods","KXNG Crooked","For 22 a key, let me know if it's a go",22,"sell","USD","Long Beach, CA")
add(2014,"TREY CHOPS","Stickers","TREY CHOPS","Yeah, it's probably 40 for a key",40,"quoted","USD",None,"medium")
add(2014,"SpaceGhostPurrp & Dough2x","MunnieTrain7264",None,"Stuntman bricks, 17.5, you know I got 'em",17.5,"sell","USD","Miami, FL","medium")
add(2015,"Gucci Mane","Still Selling Dope","Gucci Mane","When a brick was twenty-six, it got me goddamn rich",26,"quoted","USD","Atlanta, GA","high",["retrospective"])
add(2015,"French Montana & Chris Brown","Antidote (Remix)","French Montana","Talkin' back when bricks was fifteen",15,"quoted","USD","Bronx, NY","high",["retrospective"])
add(2015,"Jadakiss","Critical",None,"Bought me two bricks call me 60 thou'",30,"buy","USD","Yonkers, NY",note="2 for 60 => 30 each")
add(2015,"Rick Ross","Neighborhood Drug Dealer (Remix)","Rick Ross","I charge 90 a brick for a nigga",90,"sell","USD","Miami, FL","low",["outlier","hyperbole"])
add(2016,"Killer Mike","Saks Fifth","Killer Mike","I don't really give a fuck they charging 30 for a key",30,"buy","USD","Atlanta, GA")
add(2016,"Westside Gunn","Summerslam 88","Westside Gunn","Two bricks for 50, that's a good look",25,"buy","USD","Buffalo, NY",note="2 for 50 => 25 each")
add(2016,"Yo Gotti","Mitch","Yo Gotti","'Cause I'm money making Mitch, I want 30 for a brick",30,"sell","USD","Memphis, TN")
add(2016,"K.I.D GuacamoleGodd","100 Clip",None,"Thirty K for a brick and we might make a route",30,"quoted","USD","Chicago, IL","medium")
add(2016,"Baby E","Bando",None,"Sell a whole thing for 32 like magic",32,"sell","USD",None,"medium")
add(2017,"Migos","T-Shirt","Migos","Seventeen five, same color T-shirt",17.5,"quoted","USD","Atlanta, GA","high",["homage"],"nod to Jeezy's 17.5")
add(2017,"Future","Scrape","Future","Throw half a brick at Magic / 18-5 on a Monday",18.5,"quoted","USD","Atlanta, GA","medium")
add(2017,"Philthy Rich","Another One","Philthy Rich","Thirty thou for a brick of soft, man fuck it",30,"quoted","USD","Oakland, CA")
add(2017,"Hoodrich Pablo Juan","Servin & Swervin","Hoodrich Pablo Juan","Sell you a bird for the 30",30,"sell","USD","Atlanta, GA")
add(2017,"Loso Loaded","Shot Callin",None,"Thirty-six for a brick",36,"sell","USD","Atlanta, GA")
add(2017,"SprngBrk","Tuh","O.T. Genasis","Thirty for a brick, low (Real low, tuh)",30,"sell","USD","Long Beach, CA","medium")
add(2017,"Juicy J","One Of Them","Juicy J","Three 6 for the whole thing",36,"sell","USD","Memphis, TN",note="pun on Three 6 Mafia")
add(2018,"Young Scooter","No Features",None,"Twenty-six a brick, you can them LeVeon",26,"quoted","USD","Atlanta, GA")
add(2018,"Deniro Farrar","Key To The Door","Deniro Farrar","Whole thing for the 41, just bought a choppa",41,"quoted","USD","Charlotte, NC")
add(2019,"Freddie Gibbs & Madlib","Fake Names","Freddie Gibbs","They was getting shit for seventeen / Tossin' shit to me for twenty-eight / Bricks go for thirty-one",31,"sell","USD","Gary, IN",note="supply chain: 17 -> 28 -> 31")
add(2019,"LOM Rudy","Fuck Rap",None,"How I'ma eat? I heard the bricks went up to 38",38,"quoted","USD","Detroit, MI")
add(2019,"Leeky Bandz","Picasso",None,"It's thirty-five for a brick",35,"quoted","USD","Atlanta, GA")
add(2019,"OJ da Juiceman","Bricks & Pots","OJ da Juiceman","36 cost 30 flat, chopping bricks like lumberjacks",30,"buy","USD","Atlanta, GA")
add(2019,"Peso Peso","Da Bottom","Peso Peso","Got it for twenty-five, then I charge thirty for the brick",30,"sell","USD","Houston, TX",note="buys at 25, sells at 30")
add(2019,"Stack Bundles","Stand Up","Stack Bundles","Twenty-two a brick, twenty-two on whips",22,"quoted","USD","Queens, NY","medium",["posthumous"],"Stack Bundles died in 2007; recorded before then")
add(2019,"Westside Gunn","Never Give Up",None,"Used to pay eighteen-five for the whole thing",18.5,"buy","USD",None,"high",["retrospective"])
add(2019,"Cookie Money","No Forfeit","Cookie Money","Twenty dollars for a solid, 30 thousand a key",30,"quoted","USD","Oakland, CA")
# ---- 2020s
add(2020,"Westside Gunn","Allah Sent Me",None,"Ayo, I miss the days when bricks was only nineteen",19,"quoted","USD","Buffalo, NY","high",["retrospective"])
add(2020,"EST Gee","Members Only","EST Gee","Thirty bricks for thirty-three a piece, I'm tryna grab",33,"buy","USD","Louisville, KY")
add(2020,"EST Gee","Get Money",None,"Say 'Forty', I ain't talkin' bout a strap, but a key",40,"quoted","USD","Louisville, KY")
add(2020,"Haftbefehl & Gucci Mane","Ice","Gucci Mane","Bricks go for thirty-three, my bricks still in puberty",33,"sell","USD","Atlanta, GA")
add(2020,"ILL BILL","WATCH THE CITY BURN",None,"Fluffy duffel bags, eighteen thousand a brick",18,"quoted","USD","Brooklyn, NY","medium")
add(2020,"Nuk & Rio Da Yung OG","Opioid",None,"A hundred pack, twenty for a brick, plug from Lebanese",20,"quoted","USD","Flint, MI")
add(2020,"Yo Gotti","Stay Ur Distance","Yo Gotti","Bricks, spent forty a piece",40,"buy","USD","Memphis, TN")
add(2020,"38 Spesh","Home Game","38 Spesh","I still pay 38 for the whole thing",38,"buy","USD","Rochester, NY")
add(2020,"GrindHard E","Against The Wall",None,"You said thirty-six for a brick",36,"quoted","USD","Flint, MI","medium")
add(2020,"Fate Gryndhouse","Don't Run Off On The Plug","Fate Gryndhouse","Say u wanna brick 33 the price",33,"sell","USD",None,"medium")
add(2020,"Future","Life Is Good (Remix)","Lil Baby","Spent thirty racks on a rap bitch, could've went and bought a brick, woah",30,"quoted","USD","Atlanta, GA","medium",["derived"],"30 racks equated to a brick; price implied by the comparison, not stated outright")
add(2021,"Icewear Vezzo","5 Mill","Icewear Vezzo","Fetti takin' two, can get a brick for twenty-one",21,"buy","USD","Detroit, MI")
add(2021,"Rick Ross","Little Havana","Rick Ross","Thirty-six a brick, baby, here it is",36,"sell","USD","Miami, FL")
add(2021,"Westside Gunn","Peri Peri","Rome Streetz","When bricks was thirty-five, mines was thirty-two firm",32,"sell","USD","New York, NY","high",["retrospective"],"market 35, his 32")
add(2021,"3MFrench","Lizzie McGuire",None,"The plug, he told me, \"That price is regular, forty thousand for a brick\"",40,"buy","USD",None)
add(2021,"Call Me Schosa","Schotivation","Call Me Schosa","That's plug talk on vacations for 28 a key",28,"quoted","USD",None,"medium")
add(2021,"Peezy","I'm Good, Pt. 6","Peezy","Forty on the watch, that's a motherfuckin' square (A brick)",40,"quoted","USD","Detroit, MI","medium")
add(2021,"Fredo","I Miss","Fredo","I miss when them bricks were twenty-eight",28,"quoted","GBP","London, UK","high",["retrospective"])
add(2021,"ArrDee","Plugged In Freestyle","ArrDee","Me and Mitch was splitting up a key for thirty",30,"buy","GBP","Brighton, UK","medium")
add(2021,"Country Dons","Daily Duppy",None,"40 for a key, and you know I ain't a locksmith",40,"quoted","GBP","London, UK")
add(2021,"ACE (UK Drill) & Kwengface","Slowly",None,"Fifty on a brick, that's overpriced",50,"quoted","GBP","London, UK",note="rapper calls it overpriced")
add(2022,"Yo Gotti, 42 Dugg & EST Gee","Cold Gangsta",None,"The price went high, it's thirty a brick",30,"quoted","USD","Memphis, TN")
add(2022,"Drego & Beno","Slatt Season 5",None,"I paid twenty thousand for the brick",20,"buy","USD","Detroit, MI")
add(2022,"Real Boston Richey","Dawggy","Real Boston Richey","But birds go for thirty-two",32,"sell","USD","Tallahassee, FL")
add(2022,"Knowledge The Pirate & Big Ghost Ltd","Sweetwater","Knowledge The Pirate","Bricks of that raw for thirty",30,"sell","USD","New York, NY")
add(2022,"3MFrench","Gaza",None,"Thirty a brick if you really get two off",30,"sell","USD",None,"medium")
add(2022,"Lil Jairmy","SRT",None,"Back when bricks was seventy-K",70,"quoted","USD","Baytown, TX","low",["retrospective","outlier"])
add(2023,"M Huncho","where you been?","M Huncho","Twenty-nine thousand for a brick, today",29,"quoted","GBP","London, UK")
add(2023,"Conway the Machine & Wun Two","Bianca","Conway the Machine","My nigga got 10 bricks, 33 a piece",33,"quoted","USD","Buffalo, NY")
add(2023,"Fatt Macc","Box God","Fatt Macc","Twenty-five a brick, exotic bags got my line hot",25,"sell","USD",None,"medium")
add(2023,"YOUNG JR","On Babies",None,"My brick cost twenty-five, shoes 850",25,"buy","USD",None,"medium")
add(2023,"Young Shiners & EST DonWon","One of One",None,"Twenty for a brick and it was raw",20,"quoted","USD",None,"medium")
add(2023,"Why G, Bundog & Money Musik","Expendables",None,"Twenty-two for that snow",22,"quoted","CAD","Toronto, ON","medium")
add(2024,"Dimiko","Leave The Door Open","Dimiko","I can make it snow 20.5 for a key",20.5,"sell","USD",None,"medium")
add(2024,"YN Jay","US 23",None,"Plugged in, twenty-seven for a brick in Houston",27,"buy","USD","Flint, MI")
add(2024,"Meekz","Manny","Meekz","Thirty for a brick, couple milli' for a tape",30,"quoted","GBP","Manchester, UK")
add(2024,"Morrisson","Daily Duppy (2024)","Morrisson","Give me thirty for a brick of sniff",30,"sell","GBP","London, UK")
add(2024,"Aystar","Hands On","Aystar","Boss the price is twenty-five if you're copping a brick",25,"sell","GBP","Liverpool, UK")
add(2024,"Wiz Khalifa","Dress Like This","Hardo","Twenty for a brick, but want five thousand for the vocals (Skrrt)",20,"quoted","USD","Pittsburgh, PA","medium")
add(2024,"Hackle & Buckshot (IRL)","AIN'T WORTH IT","Buckshot (IRL)","Thirty K a brick shipped if you got the fucking links (Links)",30,"sell","USD",None,"medium")
add(2024,"Tyno Got It","Uncle Drive","Tyno Got It","Food price went up last week / Now it's 17 5th for a half a brick",35,"quoted","USD",None,"medium",["derived"],"17.5 per half => 35 per kilo")
add(2024,"Westside Gunn & DJ Drama","Duran Duran","Westside Gunn","Niggas know me, when bricks was twenty-two a pot",22,"quoted","USD","Buffalo, NY","high",["retrospective"])
add(2024,"Řezník & Non Phixion","Groupie",None,"Twenty-five a brick",25,"quoted","USD","New York, NY","medium")
add(2024,"BloodHound Q50","King Draco","BloodHound Q50","Sixteen-five if you want you a brick",16.5,"sell","USD",None,"medium")
add(2025,"AgnsBill","Trap Fame","AgnsBill","Thirty-six a brick, I sold him three",36,"sell","USD",None,"medium")
add(2025,"Young Nudy","SNAKE","Young Nudy","That's when bricks was goin' for thirty-six",36,"quoted","USD","Atlanta, GA","high",["retrospective"])
add(2025,"Slim (UK)","24","Slim","Some things never change, thirty for a brick of yay",30,"quoted","GBP","London, UK")
add(2025,"Street Certified & ShredGang","Back To Back",None,"Thirty for a brick",30,"quoted","USD",None,"medium")
add(2025,"bdifferent & Hotboii","LMDS",None,"Let them birds go for thirty-three like Boston Celtics",33,"sell","USD","Orlando, FL")
add(2026,"Why G","Where Ya Mans?",None,"Eighteen-five just for the brick",18.5,"quoted","CAD","Toronto, ON","medium")

# ---- additions from retry sweep (2026-09-02)
add(1996,"Silkk the Shocker","I Ain't Takin No Shorts","Silkk the Shocker","Mr. I gives a fuck, I gots this D 17, 5 a key",17.5,"sell","USD","New Orleans, LA")
add(1998,"La The Darkman","Gun Rule","La The Darkman","Stole four bricks, a hundred G's / Twenty-five a piece straight",25,"quoted","USD","New York, NY")
add(2005,"AZ","The Truth","AZ","And when coke went up, we had it for 27",27,"sell","USD","Brooklyn, NY",flags=["retrospective"])
add(2008,"Wiley","Taliban","Wiley","The price of coke's going up / It's thirty four gram for a key",34,"quoted","GBP","London, UK")
add(2010,"Jeezy","Porsche Music","Jeezy","That's thirty-k, for a whole brick of sheetrock",30,"quoted","USD","Atlanta, GA")
add(2012,"Gucci Mane","Put on a Show","Gucci Mane","Selling bricks for 35, if I know [ya]",35,"sell","USD","Atlanta, GA")
add(2012,"Webbo","Young Nigga Ballin",None,"When them birds was going for the 17",17,"quoted","USD","Detroit, MI","high",["retrospective"])
add(2013,"Lantana","All Hustle, No Luck (Remix)",None,"I want thirty for a bird, 22 for a duck",30,"sell","USD",None,"medium")
add(2014,"D. Chamberz","On My 1, 2","Fred the Godson","Forty for a key, seventy if you want two",40,"sell","USD","Bronx, NY","medium")
add(2015,"Deniro Farrar","So Long","Deniro Farrar","Real street nigga 35 for a brick / Sell it for the forty one",41,"sell","USD","Charlotte, NC",note="buys at 35, sells at 41")
add(2015,"Westside Gunn & Conway the Machine","Pray for Buffalo",None,"Coke prices so-so, forty for a whole dough",40,"quoted","USD","Buffalo, NY")
add(2016,"Jimmy Wopo","Prime Time","Jimmy Wopo","And it's forty for a key nigga, ask AZ",40,"quoted","USD","Pittsburgh, PA")
add(2016,"Westside Gunn","Free Chapo","Conway the Machine","Dump the work in the acid, forty for a brick",40,"quoted","USD","Buffalo, NY","medium")
add(2017,"Baby Ahk","Marathon","Baby Ahk","18 5 for the half a key",37,"sell","USD",None,"medium",["derived"],"18.5 per half => 37 per kilo")
add(2017,"No Plug","Groceries",None,"Bricks is thirty-five, that's too high",35,"quoted","USD","Atlanta, GA")
add(2018,"Westside Gunn","Ric Martel",None,"Whole brick for 28, look like we bleached it",28,"quoted","USD","Buffalo, NY","medium")
add(2018,"sKitz Kraven","Propaganda","sKitz Kraven","Thirty for a key / Now that's a piece",30,"quoted","USD",None,"medium")
add(2019,"Wanski","5.Am","Veeze","Thirty-five for a white bird like Larry",35,"quoted","USD","Detroit, MI","medium")
add(2019,"Slim (UK)","Picture This","Slim","Yo it's forty bags for a brick / It's gettin' drastic",40,"quoted","GBP","London, UK")
add(2020,"42 Dugg","Ride With Me","42 Dugg","Thirty-five a key, buss her down and lean",35,"quoted","USD","Detroit, MI")
add(2020,"Burna Bandz","Let The Racks Speak","Burna Bandz","Bricks going for the forty-three",43,"quoted","CAD","Toronto, ON")
add(2020,"Jeezy","Back","Jeezy","I want twenty for a half, forty for a slab (Bricks)",40,"sell","USD","Atlanta, GA")
add(2020,"K-Trap","Probably",None,"Fifty-four a brick, I need a better price",54,"buy","GBP","London, UK")
add(2020,"Lil Wayne","I Don't Sleep",None,"Text message from my Memphis bitch, she get 'em ten a key",10,"quoted","USD","New Orleans, LA","low",["outlier"])
add(2020,"Ronin Gray","GET DOWN","Ronin Gray","Them birds I used to flip / Twenty-one five",21.5,"quoted","USD",None,"medium",["retrospective"])
add(2020,"SupaWassi","Gucci","SupaWassi","I could get a bird for thirty-three like Larry (Bird)",33,"buy","USD",None,"medium")
add(2021,"BandGang Lonnie Bands & Cypress Moreno","Where Is Marshall","BandGang Lonnie Bands","I just paid fifty for a bird, this nigga taxin' me",50,"buy","USD","Detroit, MI",note="rapper says he was overcharged")
add(2021,"Pop Smoke","Tell the Vision","Pusha T","When a brick is thirty-six, bitch, how could I not?",36,"quoted","USD","Virginia Beach, VA")
add(2021,"Struggle Mike & Smoke Bulga","John Gotti",None,"Only thirty for a bird, I know the real de[al]",30,"sell","USD","Buffalo, NY","medium")
add(2021,"Tee Grizzley","White Dior Tee","Tee Grizzley","Forty-eight a key, thirty-eight a P, nigga (Work)",48,"quoted","USD","Detroit, MI","medium")
add(2022,"42 Dugg, Coi Leray & CMG The Label","Hold Me Down","42 Dugg","Forty for a verse, I want fifty for a brick",50,"sell","USD","Detroit, MI")
add(2022,"Al-Doms & Pusha T","HAHA","Pusha T","My yellow brick road was twenty-five a key",25,"quoted","USD","Virginia Beach, VA","high",["retrospective"])
add(2022,"Blac Youngsta","Money","Blac Youngsta","Forty for a brick, eating Winnup since back in the day",40,"quoted","USD","Memphis, TN")
add(2022,"Kenzo Str8Drop","Trap Flow","Kenzo Str8Drop","Nuttin' less than thirty five and you can cop this brick",35,"sell","USD",None,"medium")
add(2022,"Tye Henney","PM","Tye Henney","Twenty for a bird, if it's good, I need that shit",20,"buy","USD",None,"medium")
add(2023,"Boldy James & ChanHays","Trust Issues","Boldy James","Twenty-six a blue, thirty for the brick",30,"quoted","USD","Detroit, MI")
add(2024,"Poody Gordy, Babyface Ray, Drego & Beno & ShredGang Mone","Break a Bitch",None,"'Bout twenty, yeah, for this half a brick",40,"sell","USD","Detroit, MI","medium",["derived"],"20 per half => 40 per kilo")
add(2025,"Boldy James & V Don","Bobert Horry","Boldy James","Back when they used to charge you seventeen for the whole brick",17,"quoted","USD","Detroit, MI","high",["retrospective"])
add(2026,"Conway the Machine & DJ Whoo Kid","TV OFF","Conway the Machine","Fifteen and a half for a key slab",15.5,"quoted","USD","Buffalo, NY","medium")
add(2026,"Nickoe","The Peoples Choice","Nickoe","I just sold a brick at forty",40,"sell","USD",None,"medium")

# ---- additions from Genius annotation crawl (2026-09-03): fans decoded the unit or the number
A="annotation"
add(2000,"Three 6 Mafia","Sippin' on Some Syrup","Pimp C","If you got sixteen, you can get a bizzird",16,"sell","USD","Port Arthur, TX",note="annotation: Pimp C sells birds for $16,000",src=A)
add(2003,"G-Unit","Stunt 101","Young Buck","Buck, he from Cashville, Ten-a-key nigga / We getting them ten a ki'",10,"buy","USD","Nashville, TN",src=A)
add(2005,"Bun B","Get Throwed","Young Jeezy","Snowman, 16.5 a piece, nigga, USDA",16.5,"buy","USD","Atlanta, GA",note="annotation notes Jeezy has also used 17.5 and 19.5",src=A)
add(2006,"Clipse","Wamp Wamp (What It Do)","Malice","Seventeen a brick, yeah, run and tell 'em that",17,"sell","USD","Virginia Beach, VA",src=A)
add(2007,"OJ da Juiceman","Kop a Chicken","OJ da Juiceman","Cop a chicken, dog, for the 18",18,"buy","USD","Atlanta, GA","medium",["implied_unit"],"chicken = bird = kilo; annotation misreads it as a pound",src=A)
add(2008,"Gucci Mane","Bricks","Gucci Mane","Drought season in, charged your ass a whole thirty",30,"sell","USD","Atlanta, GA",flags=["drought"],note="annotation: drought price, normally ~25",src=A)
add(2010,"Jeezy","Ill'in","Jeezy","Got some redbones to go out to Phoenix, get that Amare",1,"buy","USD","Atlanta, GA","medium",["outlier","hyperbole","homage","implied_unit"],"Amar'e Stoudemire wore #1 => $1k a kilo; answers Jay-Z's Dwyane Wade line",src=A)
add(2012,"Rick Ross","So Sophisticated","Rick Ross","Breaking news and we still get them for ten a key",10,"buy","USD","Miami, FL","low",["outlier","hyperbole"],src=A)
add(2013,"Ace Hood","Bugatti","Rick Ross","That's why I hustle for half a key, that's twelve G's",24,"sell","USD","Miami, FL","high",["derived"],"12 per half => 24 per kilo",src=A)
add(2013,"Payroll Giovanni","Pure White","Payroll Giovanni","I had 'em for the 2-3, nigga, just like new J's",23,"sell","USD","Detroit, MI","medium",["implied_unit"],"Jordan's 23 => $23k",src=A)
add(2013,"Gucci Mane","Jugg Finesse","Gucci Mane","1017, that's a brick wit' a extra 10",17,"sell","USD","Atlanta, GA",note="1017 Bricksquad wordplay: 17 for the brick",src=A)
add(2014,"Rick Ross","War Ready","Rick Ross","Seventeen, I was chargin' niggas seventeen",17,"sell","USD","Miami, FL","high",["retrospective"],"at age 17",src=A)
add(2015,"Yo Gotti","Rihanna","Yo Gotti","Got bricks of Madonna / Twenty two for that thirty six",22,"sell","USD","Memphis, TN",src=A)
add(2019,"Griselda","Chef Dred's","Benny the Butcher","I double up if the brick clean / But now I get that for a sixteen",16,"buy","USD","Buffalo, NY","medium",src=A)
add(2024,"Conway the Machine","Mutty","Conway the Machine","If you got a half a bird for nine, and water whipped it all the way 'round",18,"buy","USD","Buffalo, NY","high",["derived"],"9 per half => 18 per kilo",src=A)
add(2007,"Gorilla Zoe","Money Man","Gorilla Zoe","We got bricks of the flake, Justin Timberlake / Last year was 24, this year is 28",28,"quoted","USD","Atlanta, GA","high",["implied_unit"],"price move stated in the line: 24 in 2006, 28 in 2007")
add(2007,"Gorilla Zoe","Money Man","Gorilla Zoe","We got bricks of the flake, Justin Timberlake / Last year was 24, this year is 28",24,"quoted","USD","Atlanta, GA","high",["implied_unit","retrospective","companion"],"the 'last year' half of the line: 24 in 2006; dated to 2006 in build.py. Companion row to the 28 (2007) entry")
add(2007,"Gucci Mane","Truck Loaded","Gucci Mane","Eighteen bands, I done sold another thing / Ten grand cash, that'll get you 'bout a half",18,"sell","USD","Atlanta, GA","high",["implied_unit"],"full price list: 18 for the whole thing, 10 for a half; re-recorded as 'Do The Math' (2009)")

# ---- additions from ranked candidates (2026-09-05), see data/candidates_ranked.tsv
add(2016,"Snap Capone","Pay 4 It / Picture Me Rolling","Snap Capone","Charge thirty for a key, that's the price of my watch",30,"sell","GBP","London, UK","medium")  # https://genius.com/Snap-capone-pay-4-it-picture-me-rolling-lyrics
add(2019,"Fee Gonzales","Slatt","Fee Gonzales","I just paid like 40 for the brick",40,"buy","GBP","London, UK","medium")  # https://genius.com/Fee-gonzales-slatt-lyrics
add(2013,"Doughboyz Cashout","Numbers",None,"2 for 60 for the bricks",30,"sell","USD","Detroit, MI","medium",["derived"],"2 for 60 => 30 per brick")  # https://genius.com/Doughboyz-cashout-numbers-lyrics
add(2014,"Smerker","Stars In The Wraith (Remix)",None,"Thirty on my wrist, wan' pay thirty for a brick",30,"buy","GBP","London, UK","medium")  # https://genius.com/Smerker-stars-in-the-wraith-remix-lyrics
add(2006,"Styles P","Institutionalized","Styles P","Twenty for a brick, but if you caught, it's twenty-five",20,"quoted","USD","Yonkers, NY","high",note="25 is the sentence in years, not a price")  # https://genius.com/Styles-p-institutionalized-lyrics
add(2001,"E.S.G. & Slim Thug","Mash For Our Cash",None,"Sixteen-five for a bird, so nigga quit hating",16.5,"sell","USD","Houston, TX")  # https://genius.com/Esg-tx-and-slim-thug-mash-for-our-cash-lyrics
add(2023,"GooseByTheWay, SK Da King, 7xvethegenius & Lucky Seven","Take It Back",None,"Before niggas started payin' thirty for a whole thing",30,"buy","USD","Buffalo, NY","medium",["implied_unit","retrospective"],"'whole thing' = kilo; line looks back to before fentanyl")  # https://genius.com/Goosebytheway-sk-da-king-7xvethegenius-and-lucky-seven-take-it-back-lyrics
add(2019,"Ameer Vann","All I Know","Ameer Vann","Thirty for a brick and a hunnid in the trunk",30,"quoted","USD","Houston, TX","medium")  # https://genius.com/Ameer-vann-all-i-know-lyrics
add(1998,"Kane & Abel","Greens, Cornbread, and Cabbage",None,"Fifteen five for a key now I'm",15.5,"sell","USD","New Orleans, LA","medium",note="trim quote to the line")  # https://genius.com/Kane-and-abel-greens-cornbread-and-cabbage-lyrics
add(2021,"Rx Papi","Daisy Lane","Rx Papi","Study for a ten, thirty for a brick",30,"quoted","USD","Rochester, NY","medium")  # https://genius.com/Rx-papi-daisy-lane-lyrics
add(2015,"Big Ghost Ltd, Conway the Machine & Westside Gunn","If I Ruled the World '15",None,"I take it back to '05 when coke prices was eighteen a key",18,"quoted","USD","Buffalo, NY","high",["retrospective"],"line dates the price to 2005; set performer once checked (Conway or Westside Gunn)")  # https://genius.com/Big-ghost-ltd-conway-the-machine-and-westside-gunn-if-i-ruled-the-world-15-lyrics
add(2021,"Erick the Architect","Self Made","Erick the Architect","I'll tell you why the white sell like 10 a key",10,"quoted","USD","Brooklyn, NY","medium")  # https://genius.com/Erick-the-architect-self-made-lyrics
add(2019,"Cookie Money","Street Visions","Cookie Money","Thirty for a brick, I ain't never",30,"quoted","USD","Oakland, CA","medium",note="trim quote to the line")  # https://genius.com/Cookie-money-street-visions-lyrics
add(2019,"Emoney X JC","prada","Sir Flex-A-Lot","I got twenty fucking thousand for a brick",20,"quoted","USD",None,"medium")  # https://genius.com/Emoney-x-jc-prada-lyrics
add(2019,"Lil Lyko","Lean",None,"Spend 10 grand on a bitch, spend six on a brick",6,"buy","USD",None,"low",["outlier"],"6 is far below market, likely a bar not a price")  # https://genius.com/Lil-lyko-lean-lyrics
add(2018,"Young Scooter","Plug Lingo","Young Scooter","Like how I sell a bird for twenty and they cost three-oh",20,"sell","USD","Atlanta, GA","medium",note="sells at 20, says they cost 30; sell price used")  # https://genius.com/Young-scooter-plug-lingo-lyrics
add(2014,"Millyz & The Colombians","The Plug Remix",None,"Sixty for the whole thing / Thirty for the half",60,"sell","USD","Boston, MA","medium",["implied_unit"],"'whole thing' = kilo; check whether Millyz or Jadakiss raps the line")  # https://genius.com/Millyz-and-the-colombians-the-plug-remix-lyrics
add(2020,"Florence Sinclair","Hard food",None,"But how much? / Well it's forty grand a key",40,"quoted","GBP","London, UK","medium")  # https://genius.com/Florence-sinclair-hard-food-lyrics
add(2020,"Zaytoven","EA LEGENDS",None,"No more pain, sold the bricks for twenty-eight",28,"sell","USD","Atlanta, GA","medium",note="set performer once checked (OJ da Juiceman, Yung LA or Yung Ralph)")  # https://genius.com/Zaytoven-ea-legends-lyrics
add(2020,"Ice City","Street Therapy",None,"Re-up on the brick, that's thirty-six, half a brick, eighteen",36,"buy","GBP","London, UK","medium",note="36 read as price since the half is priced at 18")  # https://genius.com/Ice-city-street-therapy-lyrics
add(2019,"Corleone (UK)","Poor Little Rich Kid",None,"Heard that sniff shit, 35 a brick prick",35,"quoted","GBP","London, UK","medium",note="Snap Capone features, check who raps the line")  # https://genius.com/Corleone-uk-poor-little-rich-kid-lyrics
add(2016,"Lil Pump","30 Bitches (2016)","Lil Pump","Forty thousand on a brick",40,"quoted","USD","Miami, FL","medium",note="year from title; confirm on Genius")  # https://genius.com/Lil-pump-30-bitches-2016-lyrics
add(2016,"Chubbie Baby","Thank the Plug",None,"Brick at 15 and a half / Now a half a brick cost you 15 and a half",15.5,"buy","USD","Atlanta, GA","medium",["retrospective"],"line contrasts old price (15.5 per brick) with now (15.5 per half => 31); old price used, consider a second derived row at 31")  # https://genius.com/Chubbie-baby-thank-the-plug-lyrics
add(2017,"Snap Capone","Man Down","Snap Capone","I'm in the hood where the bricks go for thirty",30,"quoted","GBP","London, UK","medium")  # https://genius.com/Snap-capone-man-down-lyrics
add(2005,"D-Block","Yayo","Jadakiss","Your bricks cost 24, mine 60 something",24,"quoted","USD","Yonkers, NY","medium",note="24 taken as the market price; 60 is a boast about his own being uncut")  # https://genius.com/D-block-yayo-lyrics
add(2020,"Geny Luv","Oak",None,"On my shit thirty dollars on a brick",30,"quoted","USD",None,"low",["implied_unit"],"'thirty dollars' read as 30K")  # https://genius.com/Geny-luv-oak-lyrics
add(2024,"RX HECTOR","Any Occasion",None,"I spent a twenty on a brick, sent it to Cincinnati",20,"buy","USD",None,"medium",note="check whether RX HECTOR or YTB Fatt raps the line")  # https://genius.com/Rx-hector-any-occasion-lyrics
add(2024,"Victor Rashad","Wartime Ready","Victor Rashad","I wanna break down a brick at twenty-four",24,"buy","USD",None,"medium")  # https://genius.com/Victor-rashad-wartime-ready-lyrics
add(2012,"AR-AB","North 2 West","AR-AB","Bring 32 grand if you need a brick",32,"sell","USD","Philadelphia, PA","high")  # https://genius.com/Ar-ab-north-2-west-lyrics
add(2018,"Dion Lekeith","How You Trying to Roll","Bobby Gore","Got me feeling like a key / 30 grand I'll pay the fee",30,"quoted","USD",None,"low",["implied_unit","wordplay"],"30 grand is 'the fee' in a rhyme with 'key'; kilo price by association only")  # https://genius.com/Dion-lekeith-how-you-trying-to-roll-lyrics
add(2018,"JayDaYoungan","Wake Up","JayDaYoungan","Stepped out and I look like a brick / Thirty bands, I put that on my wrist",30,"quoted","USD","Bogalusa, LA","low",["implied_unit","wordplay"],"thirty bands is the watch; equates himself to a brick, so 30 = brick price only by implication")  # https://genius.com/Jaydayoungan-wake-up-lyrics

# ---- locations the lyric itself names
LYRIC_LOC={
 "D. King (rapper)|Supposed to Be":"Dade County, FL",
 "YN Jay|US 23":"Houston, TX",
 "French Montana|Bricks & Walls":"Canal Street, New York, NY",
 "Lil Wayne|I Don't Sleep":"Memphis, TN",
 "Westside Gunn & Conway the Machine|Pray for Buffalo":"Buffalo, NY (title)",
 "Rick Ross|Little Havana":"Little Havana, Miami, FL (title)",
 "G-Unit|Stunt 101":"Nashville, TN (Cashville)",
 "Jeezy|Ill'in":"Phoenix, AZ",
}
# ---- join to raw hits for URLs
hits=[]
for f in glob.glob("data/raw_hits*.json"):
    try: hits+=json.load(open(f))
    except Exception: pass
def norm(s): return re.sub(r"[^a-z0-9]","",s.lower())
idx={}
for h in hits:
    idx.setdefault(norm(h["title"]),h)
for l in open("data/annot_hits.jsonl"):
    a=json.loads(l)
    idx.setdefault(norm(a["song"]+" by "+a["artist"]),dict(url=a["url"],id=a["song_id"],year=a["year"],title=a["song"]))
import os
WIKI_BAD={'Slim','Peezy','Kokane','Bobby Gore'}  # Wikipedia article is a different artist with the same name
WIKI=json.load(open('data/rapper_places.json')) if os.path.exists('data/rapper_places.json') else {}
LINKS=json.load(open('data/annotation_links.json')) if os.path.exists('data/annotation_links.json') else {}
FIX=json.load(open('data/url_fixups.json')) if os.path.exists('data/url_fixups.json') else {}
IMAGES=json.load(open('data/images.json')) if os.path.exists('data/images.json') else {}  # artist|song -> site-relative image path (hand picks, win)
AUTO_IMG=json.load(open('data/images_auto.json')) if os.path.exists('data/images_auto.json') else {}  # from data/fetch_images.py
INFER=json.load(open('data/inferred_places.json')) if os.path.exists('data/inferred_places.json') else {}  # artist|song -> {city,basis,url,confidence}
# Stable ids: data/ids.json maps artist|song|quote[:40]|price_k -> id. A new row takes the next number above the
# highest ever issued; a deleted row's number is retired, never reused. So #e<id> links survive inserts and deletes.
IDS_PATH="data/ids.json"
IDS=json.load(open(IDS_PATH)) if os.path.exists(IDS_PATH) else {}
next_id=max(IDS.values(),default=0)+1
out=[]
for e in E:
    idk=f'{e["artist"]}|{e["song"]}|{e["quote"][:40]}|{e["price_k"]}'
    if idk not in IDS:
        IDS[idk]=next_id; next_id+=1; print("NEW ID:",IDS[idk],idk)
    key=norm(e["song"]+" by "+e["artist"])
    h=idx.get(key)
    if not h:
        # fallback: title starts with song
        cands=[v for k,v in idx.items() if k.startswith(norm(e["song"])) and norm(e["artist"].split(",")[0].split(" &")[0]) in k]
        h=cands[0] if cands else None
    e["id"]=IDS[idk]
    e["genius_url"]=h["url"] if h else None
    e["genius_id"]=h["id"] if h else None
    e["genius_year"]=h["year"] if h else None
    fix=FIX.get(f'{e["artist"]}|{e["song"]}')
    if not h and fix: e["genius_url"],e["genius_id"],e["genius_year"]=fix
    elif not h: print("NO MATCH:",e["artist"],"-",e["song"])
    elif h["year"] and h["year"]!=e["year"]: print("YEAR DIFF:",e["artist"],e["song"],e["year"],"vs genius",h["year"])
    e["lyric_location"]=LYRIC_LOC.get(f'{e["artist"]}|{e["song"]}')
    # Wikipedia placement of the performer (or first credited artist)
    who=e["performer"] or re.split(r" & |, | \(Ft\.",e["artist"])[0].strip()
    w=WIKI.get(who) or {}
    if who in WIKI_BAD: w={}
    toks=[t for t in re.findall(r"[a-z0-9]+",who.lower()) if len(t)>=3]
    if not w.get("title") or not any(t in w["title"].lower() for t in toks): w={}
    e["wiki_title"]=w.get("title"); e["wiki_birth_place"]=w.get("birth_place"); e["wiki_origin"]=w.get("origin")
    e["wiki_top_city"]=(w.get("top_cities") or [[None]])[0][0]
    lk=LINKS.get(f'{e["artist"]}|{e["song"]}|{e["quote"][:40]}') or {}
    e["annotation_url"]=lk.get("annotation_url"); e["annotation_text"]=lk.get("annotation"); e["annotation_votes"]=lk.get("votes")
    ai=AUTO_IMG.get(f'{e["artist"]}|{e["song"]}') or {}
    e["image"]=IMAGES.get(f'{e["artist"]}|{e["song"]}') or ai.get("image")
    e["image_source"]="manual" if IMAGES.get(f'{e["artist"]}|{e["song"]}') else next((k for k in ("artist_photo","song_art") if ai.get(k)==ai.get("image") and ai.get("image")),None)
    e["song_art"]=ai.get("song_art")
    inf=INFER.get(f'{e["artist"]}|{e["song"]}') or {}
    e["inferred_city"]=inf.get("city"); e["inferred_basis"]=inf.get("basis"); e["inferred_url"]=inf.get("url"); e["inferred_confidence"]=inf.get("confidence")
    for src,val in (("lyric",e["lyric_location"]),("curated",e["city"]),("wiki_origin",e["wiki_origin"]),("wiki_top_city",e["wiki_top_city"]),("wiki_birth_place",e["wiki_birth_place"]),("inferred",e["inferred_city"])):
        if val: e["home_city"],e["home_city_source"]=val,src; break
    else: e["home_city"],e["home_city_source"]=None,None
    out.append(e)
assert len({e["id"] for e in out})==len(out), "duplicate id: two rows share artist, song, quote start and price"
json.dump(IDS,open(IDS_PATH,"w"),indent=1,ensure_ascii=False)
json.dump(out,open("data/kilo_prices.json","w"),indent=1,ensure_ascii=False)
with open("data/kilo_prices.csv","w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=list(out[0].keys()))
    w.writeheader()
    for e in out:
        e2=dict(e); e2["flags"]=";".join(e["flags"]); w.writerow(e2)
print(len(out),"entries written")
