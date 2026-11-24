"""The writer's register. A missing public name means a private dwelling."""

HOME = [
    (
        "The blue coverlet",
        "Six patches of sailcloth, all different blues. The smallest has a mast stitched on backwards. Nobody has unpicked it.",
    ),
    (
        "The low shelf",
        "The underside is covered in pencil strokes. Each spring a child stood here in bare feet. One year the marks begin again at the bottom.",
    ),
    (
        "The butter crock",
        "Inside the lid someone scratched a little boat. Even with the crock full, the boat sits just above the butter.",
    ),
    (
        "The boot last",
        "A wooden foot with one heel worn flat. Folded inside its stocking is a receipt for two left boots, delivered to two different people.",
    ),
    (
        "The lamp book",
        "Every wick had a name in this household. A neat line beside Grandmother reads: still burns an hour on a thimble of oil.",
    ),
    (
        "The seed drawer",
        "The packet marked dry summer contains river beans. The packet marked flood contains the same beans, tied to corks.",
    ),
]
# layout, sign, object, inscription
BAKER = (
    "baker",
    "The First Loaf",
    "The bread tally",
    "Before the road had mileposts, runners carried a heel of bread to the next oven. The last baker to receive it rang the morning bell.",
)
MILL = (
    "mill",
    "The Borrowed Wind",
    "A miller's measure",
    "The smallest scoop is stamped WIDOW'S SHARE. Grain that fell between the floorboards belonged to the miller. Grain that fell in this scoop never did.",
)
BOOK = (
    "office",
    "The Binding Room",
    "A mended ledger",
    "Two hands repaired this book. One used fine thread. The other used fishing line and stitched through the first hand's signature.",
)
FERRY = (
    "pilot",
    "The Oar & Needle",
    "A notched oar",
    "Seven notches for crossings in thick fog. An eighth runs the whole length of the shaft. That morning the pilot walked the riverbed home.",
)
WATCH = (
    "watch",
    "The Last Lamp",
    "The lamp register",
    "One entry has no hour beside it: a light answered from beneath the water. The keeper trimmed the lamp and answered once.",
)
SCHOOL = (
    "school",
    "The Reed School",
    "A child's slate",
    "The pupils learned their letters from ferry wakes. An upright stroke meant a boat was coming home. A loop meant somebody had gone back for another passenger.",
)
GLASS = (
    "glass",
    "The Winter Glass",
    "A plant label",
    "A frost-cracked label reads: White nettle, brought upstairs the night the parish drowned. The handwriting underneath says: It took.",
)
FORGE = (
    "forge",
    "The Copper Measure",
    "A split bell mould",
    "The crack was plugged with a thumbprint. No bell cast here rings quite cleanly. The guild has rejected three offers to repair the mould.",
)
LOFT = (
    "pilot",
    "The Kite Loft",
    "A spool of kite line",
    "In fog the foresters flew paper birds above the branches. A red tail meant the path was open. A white tail meant wait for me.",
)
SALT = (
    "pilot",
    "Saltwake Chandlery",
    "A short length of chain",
    "Every ninth link is brass so a pilot can count it in the dark. The last one is gold. It was once somebody's wedding ring.",
)
SNOW = (
    "inn",
    "The Thawing Post",
    "A scorched boot rack",
    "Boots were dried toe-out for travellers going east and heel-out for those going west. The empty peg was always kept warm.",
)
PUMP = (
    "pump",
    "Swallow Pump House",
    "A brass shim",
    "The first pump clattered like a rook. Its makers slipped this shim under the bearing. The village birds kept answering it for another week.",
)
OFFICE = (
    "office",
    "Ada's Chart Office",
    "A chart weight",
    "The stone on Ada's maps came from the old river crossing. Turn it over and the slow green curve of the lost channel is still visible.",
)
THEATRE = (
    "theatre",
    "The Paper Playhouse",
    "A paper ticket",
    "A child punched two holes in this ticket. One admitted her. The other admitted her shadow, which had a speaking part.",
)


def home(i):
    obj, text = HOME[i % len(HOME)]
    return (("home", "home2", "home3")[i % 3], "", obj, text)


def renamed(record, name):
    return (record[0], name, *record[2:])


HALL_INSCRIPTIONS = {
    "KettleYard": "The cook kept the first bowl upside down until the last runner arrived. There is a ring in the table where it stood.",
    "PaperCourt": THEATRE[3],
    "SillwaterOffice": OFFICE[3],
    "GloamingPress": "Early editions printed the ferry times in red. A reader wrote beneath the last one: you can hear her oars from my kitchen.",
    "WeighHouse": "Alongside the iron weights hangs a little bag of buttons. Anyone short a penny could leave one here. The clerk never counted how many were left.",
    "FloodLedger": "The flooded streets were copied in blue ink. Families returned each spring to write their names in black beside a door they remembered.",
    "MouldLoft": "Three apprentices pressed their initials into the same mould. The middle one wrote backwards so the casting would carry her name the right way round.",
    "DrumHouse": "The duty roster calls for two drummers on a fog night. One played. The other listened along the floorboards for the answering beat.",
    "SignalLoom": "The first signal cloth was a striped apron. The weavers have saved one of its mother-of-pearl buttons in the shuttle drawer.",
    "SupperSteps": "A baker once fed both banks from these steps. Her soup recipe survives, except for the final line: keep adding water until everybody is here.",
    "Glasscut": "The glazier kept one crooked pane from every batch. Look through two together, her notebook says, and a straight road looks like a river.",
    "CinderLens": "In winter the lens keeper warmed the glass in both hands before polishing it. The cloth in the drawer has two patches worn thin.",
    "SumpHall": "When the pumps stopped, neighbours passed buckets hand to hand. There are still two sets of handles on the smallest bucket.",
    "ChainDock": "Pilots used to braid ribbons through the last link before sailing. A faded yellow knot sits just above the high-water mark.",
    "OrreryLoft": "The smallest wheel runs a little fast. A note by its pin reads: leave it. It keeps my brother’s ferry time.",
    "EchoRotunda": "A singer chalked a cross where an echo returned in tune. The floor has been laid three times. Someone always puts the cross back.",
    "LanternCourt": "Each family brought a lamp for the night crossing. One saucer has a saucer-sized patch beneath it where a child scrubbed away the soot every morning.",
    "StillBelfry": "The bell has two founders’ marks. One belongs to the caster. The other is a child’s palm pressed into the sand before the pour.",
    "LinenCourt": "The cloth kept for mending sails has a blue thread along one edge. In the flood, that thread was enough to find the way along a rope in the dark.",
    "SaffronKilns": "A potter left a row of thumb bowls for the night shift. Each fits a different hand. One has a hollow for a missing finger.",
    "TwinIntake": "Two keepers argued over which gate sang lower. Their tally ends with a diagram of two wet boots and the words: both wrong.",
    "CastingBed": FORGE[3],
    "RainCourt": "Someone measured a lean summer in cups of rain. Beside the smallest mark is a drawing of a pear, with five names around it.",
    "VellumWalk": "Look closely at the parchment offcuts. The mapmaker let children draw imaginary bridges on them. One bridge appears on a later survey.",
    "SoundingBay": "Soundings used to be called out in a singing voice. A pilot has written the deepest channel as four notes along the margin of the chart.",
    "MercySlip": "In the fare book the narrowest ferry is listed as a cradle. A seamstress paid its first crossing with three buttons and a very good needle.",
    "Wickwater": "The wick cutter measured a winter evening from thumb to elbow. Her left sleeve is embroidered with the short measure for summer.",
}

CHAPEL = (
    "chapel",
    "The Tide Chapel",
    "A wax boat",
    "Each spring the chapel sent a candle downriver in a little boat. The cupboard holds one boat for every year the river was too rough to launch it.",
)
POTTER = (
    "potter",
    "The Thumbprint Kiln",
    "A salt jar",
    "Customers could tell their pots apart by touch. The potter pressed each buyer’s thumb into the clay while the jar was still damp.",
)
WEAVER = (
    "weaver",
    "The Brass Shuttle",
    "A rescued selvedge",
    "In the lean winter a sail was cut into blankets. The weaver kept the blue selvedge and worked an inch of it into every new sail that year.",
)
HOSPITAL = (
    "office",
    "The Linen Ward",
    "A linen square",
    "A nurse sewed a blue corner onto each bandage washed in boiled water. When the dye ran out, she signed the corners with a single blue stitch.",
)
