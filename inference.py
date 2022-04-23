#! /home/user/anaconda3/envs/billy/bin/python
# -*- coding: utf-8 -*-
from rating.model import RatingModel
import mysql.connector
from bert_serving.client import BertClient
import re
import numpy as np
import math
import time
from collections import defaultdict
import sys

BATCH_SIZE = 1000
count = 0
last_id = 38457636
if len(sys.argv) > 1:
    if sys.argv[1] != '-f':
        last_id = int(sys.argv[1])
print('start from:', last_id)

rm = RatingModel()

con = mysql.connector.connect(
    host= '140.114.53.129',        	# 主機名稱
	database= 'smart_restaurant_NewYork',		# 資料庫名稱
	user= 'smartuser',            	# 帳號
	password= 'pp253&$@'  			# 密碼
)

bc = BertClient(check_length=False)

KEYWORDS = {
    'atmosphere': [
        "cheerful", "locations", "ultraviolet", "foregrounds", "rotor", "venue", "radio", 
        "venues", "mosaics", "location", "forest", "magic", "expression", "marne", "seascapes", 
        "gloom", "nature", "environments", "techno", "pedal", "surround", "weather", "tumble", 
        "ghost", "promotional", "odor", "ambiance's", "bliss", "pacing", "surrounds", "wallpapering", 
        "screen", "occult", "scent", "tenant", "ambulatories", "settings", "aura", "health", 
        "agitation", "pipe", "ventilation", "stereo", "sphere", "radiance", "atmosphere", "airspace", 
        "soils", "mixer", "agricultural", "forest", "terrestrial", "stance", "ambiances", "programming", 
        "landscape", "console", "fox", "fusion", "session", "stimulation", "lairs", "vicinity", 
        "environment", "visuals", "acoustic", "medley", "lace", "installation", "intellectual", "feedback", 
        "harmonic", "fluctuations", "nutrition", "utilization", "edifices", "arctic", "script", "lifestyle", 
        "shipping", "veranda", "proportions", "outsider", "auras", "halo", "surroundings", "scheduling", 
        "countryside", "bisector", "site", "postscripts", "mood", "aerial", "gazebo", "temperament", 
        "kitchenette", "pop", "amulet", "paste", "exhume", "landscaping", "flavor", "seraglios", 
        "morale", "ecosystems", "views", "airline", "casting", "graphic", "glamour", "benefices", 
        "terrain", "dioramas", "outstations", "organism", "scented", "supernatural", "infrastructure", "flight", 
        "emission", "drum", "posture", "sentiment", "demeanor", "behavioral", "effects", "spice", 
        "illusion", "environs's", "mystic", "stench", "tone", "ceramic", "accelerator", "wallpapers", 
        "rhythm", "infrared", "fox", "aroma", "aural", "facility", "operational", "footage", 
        "eyed", "spaciousness", "pictorials", "depiction", "ambiance", "ambience's", "exhumes", "airs", 
        "scenery", "tactic", "mix", "sea", "temper", "lowlands", "waterfronts", "spray", 
        "strings", "sample", "blur", "resonance", "orb", "airship", "greeting", "armories", 
        "arctic", "sunlight", "culture", "stroll", "spirit", "pupil", "ambiences", "seashores", 
        "dangers", "location's", "diversity", "environs", "lipstick", "air", "signal", "kite", 
        "curiosities", "loops", "ambience", "condor", "racecourse", "racing", "salty", "paranormal", 
        "smoky", "fresh", "apogees", "somber", "locality", "recreations", "ambient", "talents", 
        "innovation", "fragrance", "amplifier", "moodiness", "porn", "attitude", "ink", "sweetness", 
        "lushness", "disrepair", "vinyl", "seraglio", "sirius"
    ],
    'food': [
        "earwig", "cuisines", "fruitless", "drive", "substrate", "concentrate", "bean", "vine", 
        "braid", "fruiting", "nitrogen", "oyster", "scrumptious", "flowers", "fastidious", "pasta", 
        "licking", "leaves", "sugar", "cheeseburger", "smelling", "pigeon", "eatables", "tumble", 
        "rice", "cheeses", "sweet", "fitch", "glare", "nutrient", "round", "nutritional", 
        "champagnes", "seductive", "soups", "bleeding", "rice", "impious", "alluring", "tasting", 
        "slurpee", "yummy", "drinks", "fuzzy", "fabulous", "cheese", "dish", "devastating", 
        "healed", "capricious", "hospitality", "dimension", "sensual", "fished", "calcium", "whiskey", 
        "schedule", "seriousness", "egg", "baking", "toasty", "doggie", "yucky", "shady", 
        "pigmies", "cracking", "hamburgers", "yuppies", "bean", "pleasurable", "pasties", "climbing", 
        "mane", "pigmies", "wines", "homemade", "sausages", "supercilious", "eating", "terrifying", 
        "treated", "recipes", "fabrics", "tongue", "chocolates", "unexpected", "supper", "hot", 
        "doughnuts", "moisture", "embryo", "cheeseburgers", "delightful", "walsh", "seized", "wave", 
        "picking", "tooth", "delectable", "sexy", "enticing", "jiffy", "syrupy", "punching", 
        "lifestyle", "stroking", "tasteless", "iced", "cry", "delicious", "cocktails", "sweet", 
        "chammy", "chewing", "schedules", "stems", "kicking", "enjoy", "captivating", "speak", 
        "amusing", "food", "sweetish", "martini", "barbecue", "yuppy", "appetizer's", "gems", 
        "game", "spicy", "tasteful", "addictive", "onion", "championship", "sour", "ladles", 
        "doctrines", "damnable", "cursing", "fruits", "scotch", "slaughtered", "shrill", "behavioral", 
        "kissing", "stripped", "breakfast", "brightness", "litigiousness", "glucose", "salads", "blurred", 
        "tunes", "pollen", "seize", "flavorful", "unpleasant", "freeze", "bizarre", "rhythm", 
        "sauces", "fruitful", "educate", "fried", "halibuts", "burger", "cupcakes", "tantalized", 
        "dinner", "flower", "suppers", "academies", "bribe", "roasted", "appliances", "freezing", 
        "boar", "markets", "playoff", "preposterous", "fruition", "drink", "sugary", "cuckoo", 
        "title", "sarcastic", "living", "sobbing", "bitter", "champagne", "fixture", "bagels", 
        "fries", "grainy", "solitude", "vicarious", "seafood", "haunting", "cabbage", "slapping", 
        "sipping", "steak", "stews", "stingy", "breathable", "chilling", "foods", "wry", 
        "thermal", "worshipped", "chicken", "vanilla", "fighting", "communicate", "paperboy", "pizza", 
        "outlets", "sweetener", "signal", "washing", "sweetened", "beverage", "berries", "peas", 
        "desserts", "regional", "fresh", "dreadful", "incurious", "spiced", "somber", "series", 
        "rancorous", "swinging", "appetizers", "takeout", "talents", "wonderful", "saturated", "pigtails", 
        "cold", "sniffing", "foliage", "porn", "petals", "horrific", "exquisite", "season", 
        "blowing", "cleaned", "juicy", "impressionable", "appetizing", "playoffs", "gratifying", "soured", 
        "teach", "feathered", "highboy", "paypal", "powder", "diet", "luscious", "dancing", 
        "lusciousness", "soulful", "cocktail", "looney", "lustful", "celebrate", "soaking", "stale", 
        "cuisine", "frozen", "sultry", "voracious", "parsimonious", "deliver", "fruitcakes", "learn", 
        "thrown", "voltage", "gloom", "tablets", "spite", "learning", "integrate", "consume", 
        "embarrassing", "fruity", "jelly", "flavors", "deciduous", "lizard", "feisty", "canned", 
        "stem", "leger", "league", "investing", "intriguing", "hamburger", "flowers", "lobster", 
        "wax", "optimizer", "sticky", "juice", "rubbing", "onion", "biting", "hormone", 
        "boiled", "dough", "lusciously", "beguiling", "seasons", "nipple", "cooking", "litigious", 
        "tuna", "amazing", "steaks", "polymer", "crisp", "croissants", "splendid", "budweiser's", 
        "chummy", "takeout's", "inspected", "greasy", "stance", "tummy", "seasoning", "conference", 
        "hilarious", "bathed", "lustrous", "eat", "swell", "examine", "noise", "toothed", 
        "watery", "brainteaser", "breathtaking", "fanboy", "bread", "salsa", "driving", "bosom", 
        "acid", "licentious", "sweetbreads", "pizzas", "tasty", "burgers", "sensuous", "year", 
        "blueberries", "sucking", "silky", "pugilistic", "dessert", "harvested", "fusty", "liquor", 
        "buying", "manners", "carbon", "tantalizing", "demeaning", "cutter", "avaricious", "flavor", 
        "pleasuring", "ministries", "recipe", "flowering", "mushroom", "cheesecakes", "wrappers", "sweets", 
        "toast", "broomstick", "brisk", "fascinate", "salt", "downs", "tournament", "explore", 
        "sauce", "flowery", "stings", "semiconscious", "owning", "swabs", "tones", "snacks", 
        "disturbing", "demeanor", "irritating", "prettifying", "laughable", "wine", "cured", "pastries", 
        "multifarious", "oats", "hungry", "shortbread", "spice", "distracting", "grape", "sweetbread", 
        "pernicious", "dye", "grapes", "clumsy", "tone", "sinuous", "ceramic", "pastry", 
        "delicious", "cooks", "veggies", "pancakes", "refreshing", "peppercorns", "tapeworm", "tubular", 
        "stinger", "oven", "lethal", "occlusive", "ringlet", "ferocious", "dishes", "cakes", 
        "billing", "crackers", "grill", "boozy", "experiencing", "temper", "shimmy", "hoarse", 
        "sulfate", "taste", "omelets", "fascinating", "toothless", "flavored", "puddings", "knotted", 
        "touching", "peppers", "danes", "cereal", "tuneful", "resin", "popcorn", "flavorless", 
        "shrimp", "downs", "cooked", "donuts", "toothsome", "sausage", "jumpy", "apron", 
        "exciting", "fruit", "riveting", "scoop", "interesting", "drinking", "tequila", "face", 
        "organic", "offerings", "custards", "season's", "glue", "toothy", "baked", "mocked", 
        "custard", "leaf", "womb", "week", "mint", "feathering", "banquets", "wholesome", 
        "oils", "intoxicating", "contumacious", "heal", "chasing", "aromatic", "snacked", "salty", 
        "eater", "wingnut", "smoky", "stealing", "buffets", "massage", "vegetables", "eaten", 
        "nutrients", "appetizer", "creations", "behave", "pizzazz", "chewy", "kiddie", "plank", 
        "donut", "droplet", "brands", "angles", "bender", "nectar", "bender", "budweiser", 
        "scotch", "chips", "burger", "cake", "fruited", "configurations", "dining", "scary", 
        "hunted", "cherries", "milked", "waffles", "roast", "adorable", "chaffinches", "stuffing", 
        "pudding"
    ],
    'value': [
        "extremely", "sleek", "woodsy", "suppliers", "overpriced", "measure", "hurtle", "pilfered", 
        "voltage", "payments", "manufactured", "soiled", "pressures", "costly", "brainy", "predictions", 
        "value", "compensate", "authorized", "velocity", "elaborate", "rents", "bulky", "pricing", 
        "unvoiced", "undersized", "costed", "harmless", "rate", "tarmacked", "market", "bike", 
        "torque", "fortune", "prized", "valuation", "cute", "costing", "dimension", "gap", 
        "blowsy", "whiskey", "horsepower", "expenses", "revenue", "dangerous", "neat", "pious", 
        "pruned", "proportion", "greasy", "marketed", "terrifying", "funding", "wealth", "fabrics", 
        "riches", "subsidies", "dollar", "trajectory", "pricey", "mortgaged", "quality", "fun", 
        "overstocked", "expensive", "fined", "pearson", "fee", "nominal", "overprinted", "timer", 
        "inexpensive", "clever", "radius", "useless", "overprice", "cash", "calculated", "energetic", 
        "quantity", "assessed", "trusty", "unbosomed", "accursed", "importance", "measurement", "dollars", 
        "priced", "menacing", "mandate", "counterfeited", "flyer", "glide", "booked", "gamey", 
        "unique", "flashy", "price", "bias", "trained", "wages", "endurance", "instructional", 
        "worthless", "shipped", "dicey", "cone", "artsy", "skinny", "prices", "tariffs", 
        "clumsy", "overprices", "bizarre", "price", "gap", "balance", "cash", "costs", 
        "installed", "clearance", "labelled", "affordable", "configured", "intense", "priceless", "coin", 
        "excess", "tactic", "equipped", "markets", "money", "asset", "advertised", "momentum", 
        "appealing", "dewy", "tuition", "esteem", "palmy", "conditions", "trendy", "financing", 
        "powerful", "invoiced", "bullet", "fishy", "expense", "impressive", "lofty", "values", 
        "overpaid", "cheap", "income", "unrealized", "profit", "rates", "subsidy", "cost", 
        "heavier", "filmy", "boring", "sturdy", "tariff", "sugarcoated", "expenditure", "yarn", 
        "amount", "balls", "daley", "valued", "dealers", "salary", "friction", "leaky", 
        "overpricing", "slam", "buyer", "tough", "instruction", "constant", "compensation", "comfortable", 
        "cheaper", "weighty", "shiny", "scary", "punishments", "formulated", "quantities"
    ],
    'service': [
        "supplier", "processors", 
        "advising", "stools", "cocktail", "user", "aid", "venue", "participant", "combat", 
        "healers", "management", "goals", "managerial", "housekeepers", "hostesses", "journalism", "serving", 
        "build", "carry", "managing", "practicing", "fisherman", "secretary", "stimulate", "spectator", 
        "tailors", "software", "hostlers", "coaches", "trainer", "participating", "volunteer", "serviceman", 
        "consultation", "sponsor", "nurse", "programmer", "jealous", "feeder", "interruption", "provide", 
        "sacks", "serves", "interface", "cast", "waitresses", "waitress", "participants", "coaching", 
        "appearing", "butchers", "entertain", "assist", "residing", "casuals", "waiters", "organizer", 
        "porters", "tablet", "consultants", "use", "implementations", "logistics", "army", "enlisted", 
        "mobile", "servicemen", "leadership", "instructor", "assurance", "coach", "bartender", "feminine", 
        "working", "claiming", "exhibiting", "illustrating", "smartphone", "position", "commentator", "marketing", 
        "browsers", "finance", "gardeners", "guidance", "feedback", "napkins", "absorb", "distraction", 
        "goal", "developer", "kernel", "serve", "nutrition", "counseling", "hostess", "training", 
        "tool", "assistance", "pass", "fly", "comprise", "preach", "ensign", "services", 
        "keeper", "suffering", "auxiliary", "hosts", "organizers", "dessert", "drones", "fridges", 
        "playing", "patron", "forward", "fairy", "clerk", "support", "trainers", "brisk", 
        "enhancement", "donors", "simulator", "functionality", "promoter", "switches", "compiler", "employ", 
        "technician", "general", "oracle", "maid", "instructional", "covering", "allowance", "brunette", 
        "fulfill", "bodyguard", "waiter", "illustrate", "announcer", "host", "developers", "displaying", 
        "assisting", "goalkeeper", "accounting", "contestants", "attending", "depict", "grooms", "missions", 
        "duties", "valets", "paranoid", "managers", "outreach", "goaltender", "bakery", "apps", 
        "operational", "unit", "undertake", "browser", "servers", "shelter", "intervention", "finishing", 
        "historian", "attendant", "vocal", "mobile", "therapist", "supervision", "assists", "confuse", 
        "teacher", "receptionists", "housekeeper", "choreography", "steals", "commemorating", "provision", "server", 
        "pharmacy", "secretary", "headmaster", "navy", "wartime", "service", "format", "portraying", 
        "successively", "modeling", "controllers", "scoring", "maids", "contribution", "mechanic", "ethernet", 
        "linux", "longtime", "winger", "desktop", "infantry", "specializing", "witch", "involvement", 
        "query", "law", "strategy", "accompaniment", "cache", "cadet", "served", "flashlights", 
        "engineering", "host's", "clones", "arrogant", "duty", "hardware", "diners", "operate", 
        "referee", "military", "modems", "oracle", "manager", "bartenders", "receptionist", "striker"
    ],
    'cleanliness': [
        "soil", "unbecoming", "scoping", 
        "hidden", "lively", "vicious", "garlicky", "scouring", "cleanses", "brush", "smog", 
        "disgusting", "hubby", "nosey", "humid", "secure", "lousy", "soiled", "sober", 
        "sludge", "pesky", "docility", "untouched", "stuffiness", "neatly", "big", "tumble", 
        "righteousness", "imprudent", "contaminants", "sweet", "tubby", "canny", "uncleanly", "waxed", 
        "carbs", "limbered", "contaminating", "unwieldiest", "grimier", "scavenging", "pestered", "powdered", 
        "fuzzy", "bored", "dish", "spooled", "safekeeping", "brutal", "smeared", "punch", 
        "tardy", "gloominess", "destructive", "honest", "cube", "cleared", "convincing", "libel", 
        "puddled", "whipple", "chrome", "immaculateness", "weak", "massey", "vinegary", "pebbly", 
        "wastewater", "cesarean", "drain", "neat", "messy", "plums", "chestnut", "grey", 
        "boggled", "scourging", "negligent", "honeyed", "meek", "confident", "bale", "sprawling", 
        "moisture", "cage", "wormy", "moldered", "rubbery", "cleanse", "contaminate", "theft", 
        "catalyzing", "bonding", "complicated", "pestering", "housecleaned", "ungrateful", "woozy", "coppery", 
        "fraction", "houseclean", "crabbier", "tilt", "stanchion", "brassy", "wasted", "jaggedness", 
        "horsey", "joke", "cramped", "cauterize", "slanderous", "unwarranted", "iced", "delicious", 
        "orderliness", "cleans", "uncontaminated", "assimilate", "pollinating", "neighborliness", "fouled", "loveliness", 
        "sweet", "lubber", "bad", "courtliness", "joycean", "oxidizing", "gambling", "scavenges", 
        "tainted", "food", "drag", "foully", "shuffle", "luxuriousness", "dumping", "sandbagged", 
        "tidied", "bothersome", "sour", "footman", "adultery", "foley", "tailored", "pebble", 
        "posy", "cotton", "carbonate", "cool", "insure", "chamberlain", "grimy", "repellent", 
        "maddened", "cutesy", "vacuumed", "scavenge", "salted", "uncleaner", "baffling", "blessedness", 
        "scrounge", "blackened", "cleanliness", "strip", "sterilizing", "bizarre", "simian", "muted", 
        "untrustworthy", "savaged", "clearer", "muddied", "mcconnell", "lumbered", "plumbs", "brave", 
        "worrisome", "slime's", "dusty", "tease", "scraped", "bribe", "lick", "acidifying", 
        "cemented", "excess", "stateliness", "costliness", "neatness", "irresponsible", "ungovernable", "reedy", 
        "humble", "nasty", "incinerate", "dummy", "greenhorn", "sordid", "grunge", "spirited", 
        "stretchy", "bitter", "damp", "compacted", "depleting", "white", "polite", "whiter", 
        "peroxiding", "singleton", "ivory", "scavenger", "scrounged", "bumbled", "stringy", "untruthful", 
        "gassy", "nicely", "plummet", "soot", "tidy", "paint", "cursed", "muddled", 
        "homeliness", "sordidness's", "unrealized", "fighting", "doughy", "shale", "weeded", "shrink", 
        "horny", "scavengers", "fresh", "unwashed", "horrify", "filthy", "peat", "gentles", 
        "ivory", "materials", "defective", "chlorinating", "plumb", "clean", "comfortable", "questionable", 
        "grimness", "cesarean", "definite", "buttock", "patterned", "dishonest", "uncle", "blanks", 
        "flirting", "elegant", "straightforward", "respectable", "sordidly", "sleek", "deposits", "woodsy", 
        "pathetic", "safe", "housecleaning's", "unintelligent", "loopy", "chamberlain", "stale", "contaminant", 
        "selfless", "sordidness", "slime", "hilly", "footsore", "ugly", "scrounges", "anderson", 
        "fraud", "mean", "swamped", "corrosion", "fight", "shapeliness", "tarbell", "manipulation", 
        "striven", "ungracious", "blue", "scenic", "slippery", "spying", "sticky", "jump", 
        "cotton", "cooky", "plodded", "cute", "strips", "serene", "discount", "copying", 
        "chanter", "stack", "grimed", "roadhouse", "white", "holman", "cooking", "balanced", 
        "cleansed", "crisp", "soils", "glitter", "miserable", "greasy", "wipe", "spunky", 
        "stowing", "volcanic", "tap", "watery", "spitting", "hobbs", "scavenged", "recycling", 
        "flinty", "housecoat", "muddy", "horridly", "cobs", "risqu\u00e9", "drip", "petroleum", 
        "timer", "clever", "bedrock", "lumpy", "switching", "warder", "sister", "purple", 
        "blubbered", "sisterly", "smoking", "gritty", "sandman", "cheating", "hateful", "pigment", 
        "crumbling", "fusty", "falconer", "dishonestly", "temperament", "bather", "unsportsmanlike", "mineral", 
        "cob", "pink", "bullock", "precise", "dandy", "cleanness", "grime's", "bamboozled", 
        "trading", "misery", "glide", "raw", "flashy", "mousey", "crusted", "creel", 
        "herbicide", "loyaler", "kid", "horrid", "sanded", "dingy", "crisped", "strawed", 
        "swanky", "grime", "disturbing", "carboy", "sealed", "punch", "wet", "singleton", 
        "sister", "grey", "unfriendly", "delicious", "tooled", "rummy", "slash", "wicked", 
        "refreshing", "woodiness", "soaked", "bullock", "bemoan", "graveled", "vaporizing", "unclean", 
        "blank", "barbs", "sediment", "orderly", "straight", "crawford", "cement", "tawdry", 
        "boozy", "scatter", "dirty", "poker", "chipped", "plumb's", "alike", "contaminates", 
        "lockean", "resin", "weedy", "lowliness", "twisted", "appealing", "healthy", "metal", 
        "clear", "jumpy", "excreting", "cleanser", "uncleanest", "housecleans", "pureness", "brother", 
        "incompetent", "lock", "foul", "drinking", "asphalted", "fishy", "ironed", "uncleanlier", 
        "ancestor", "pollution", "battered", "perfumed", "cheap", "haunted", "healthiness", "freshly", 
        "crumpled", "deceitful", "liveliness", "basalt", "sturdy", "scavenger's", "friendliness", "sandstone", 
        "oiled", "shriveled", "nerdier", "shameful", "stealing", "colored", "cleanly", "lone", 
        "warped", "muddles", "unethical", "cosy", "crabby", "sensible", "tormented", "defecate", 
        "thread", "muffed", "polluting", "detoxification", "fills", "cousin", "constant", "plumbed", 
        "shiny", "dusted", "unexpected", "uncleanliest", "brotherly", "seasoned"
    ]
}

ASPECTS = ['atmosphere', 'service', 'food', 'cleanliness', 'value']


def is_aspect(aspect, sentence):
    global KEYWORDS
    for keyword in KEYWORDS[aspect]:
        if keyword in sentence:
            return True
    return False

def split_review_text_iter(review_text):
    if review_text is None:
        return
    for line in review_text.splitlines():
        stripped_line = line.strip()
        if len(stripped_line) == 0:
            continue

        for sep_line in re.split('。|，|；|﹐|！|\!|,|\?|？|；|;|\t|:|：', stripped_line):
            sep_line = sep_line.strip()
            if len(sep_line) > 20 or len(sep_line) <= 2:
                continue
            yield sep_line

print('starting...')

while True:
    st = time.time()
    cur = con.cursor(dictionary=True, buffered=True)
    cur.execute(f'''
    SELECT
        A.`id`, B.`text`, A.`is_atmosphere`,
        A.`is_service`, A.`is_food`, A.`is_cleanliness`, A.`is_value`
    FROM `reviews_aspect` AS A
    LEFT JOIN `reviews` AS B ON A.`id` = B.`id`
    WHERE
        A.`id` > {last_id} AND
        (
            A.`is_atmosphere` = 1 OR
            A.`is_service` = 1 OR
            A.`is_food` = 1 OR
            A.`is_cleanliness` = 1 OR
            A.`is_value` = 1
        )
    LIMIT {BATCH_SIZE};
    ''')
    reviews = cur.fetchall()
    if reviews is None or len(reviews) == 0:
        print('finish')
        break
    last_id = reviews[-1]['id']
    cur.close()
    
    splitted_sen = []
    sid = 0
    for review in reviews:
        text = review['text']
        review['aspects'] = defaultdict(list)
        review_aspects = tuple(filter(lambda v: review[f'is_{v}'] == 1, ASPECTS))
        for sen in split_review_text_iter(text):
            s_aspects = tuple(filter(lambda v: is_aspect(v, sen), review_aspects))
            if not any(s_aspects):
                continue
            splitted_sen.append(sen)
            
            for a in s_aspects:
                review['aspects'][a].append(sid)
            
            sid += 1
    
    if len(splitted_sen) == 0:
        print('skip!')
        print('count:', count, '\t', 'last index:', last_id)
        count += BATCH_SIZE
        continue
    
    splitted_emb = bc.encode(splitted_sen)
    splitted_rating = rm.predict_classes_embeddings(splitted_emb)
    
    results = []
    for review in reviews:
        ra = review['aspects']
        ar = list(np.average([splitted_rating[v] for v in ra[a]]) for a in ASPECTS)
        
        results.append(tuple(None if math.isnan(r) else r for r in ar) + (review['id'],))
    
    
    cur = con.cursor()
    cur.executemany(f'''
    UPDATE `reviews_aspect`
    SET
        `atmosphere_rating` = %s,
        `service_rating` = %s,
        `food_rating` = %s,
        `cleanliness_rating` = %s,
        `value_rating` = %s
    WHERE
        `id` = %s
    ;''', results)
    con.commit()
    cur.close()
    
    count += BATCH_SIZE
    
    et = time.time()
    print('count:', count, '\t', 'last index:', last_id, '\t', 'time:', et - st)
    
    del splitted_emb
    del splitted_rating
    del splitted_sen
    del results
