// All of the formats in this file are game archive files that should just be handled with the 'gamearch' and/or 'gameextractor' programs and are not worthy of having their own file
// If you end the formatid with 'GameArchive' or 'GameDataArchive' then dexrecurse won't bubble up any warnings about needing more sample file formats
// Each entry also has the following properties added:
//	forbidExtMatch : true			(Only if ext is set)
//	converters     : ["gameextractor"] or ["gamearch"] or ["gamearch", "gameextractor"]
// SPECIAL properties only allowed in this file:
// allowExtMatch : true				(Set this is you want to allow ext matching for the format)
export const gameextractor =
{
	archive :
	{
		agonGameDataArchive                 : {name : "Agon game data archive", ext : [".sfl"], magic : ["Agon game data archive"], weakMagic : true},
		alienVsPredatorGameDataContainer    : {name : "Alien vs Predator game data container", ext : [".ffl"], magic : ["Alien vs Predator game data container"]},
		allods2RageOfMagesGameArchive       : {name : "Allods 2 Rage Of Mages game archive", ext : [".res"], magic : ["Allods 2 Rage Of Mages game data archive"]},
		americanConquest2GameArchvie        : {name : "American Conquest 2 game archvie", ext : [".gs1", ".gsc"], magic : ["American Conquest 2 game data archvie"]},
		ascaronEntertainmentGameArchive     : {name : "ASCARON Entertainment game archive", ext : [".cpr"], magic : ["ASCARON Entertainment game data archive"]},
		bankGameArchive                     : {name : "Bank Game Archive", ext : [".bnk"], magic : ["Bank game data archive"]},
		battlezone2GameDataPackage          : {name : "Battlezone 2 game data package", ext : [".pak"], magic : ["Battlezone 2 game data package"], weakMagic : true},
		bioWareEntityResourceFile           : {name : "BioWare Entity Resource File", ext : [".erf"], magic : ["BioWare Entity Resource File"]},
		bizarreCreationsBankFile            : {name : "Bizarre Creations Bank File", ext : [".baf"], magic : ["BAF (Bizarre Creations Bank File) (baf)"]},
		bloodrayneGameDataArchive           : {name : "Bloodrayne game data archive", ext : [".pod"], magic : ["Bloodrayne game data archive"], weakMagic : true},
		boltGameArchive                     : {name : "BOLT Game Archive", ext : [".blt"], magic : ["BOLT game data archive"]},
		broderbundMohawkGameArchive         : {name : "Broderbund Mohawk Game Archive", ext : [".mhk"], magic : ["Broderbund Mohawk game data archive", "Riven saved game"], idMeta : ({macFileType, macFileCreator}) => (macFileType==="MHK_" && macFileCreator==="MoRs") || (macFileType==="LBgP" && macFileCreator==="LBgP")},
		chasmGameArchive                    : {name : "Chasm Game Archive", ext : [".bin"], magic : ["Chasm BIN archive"]},
		ciGAMESGameDataArchive              : {name : "CI GAMES game data archive", ext : [".dpk"], magic : ["CI GAMES game data archive"], weakMagic : true},
		creativeAssemblyGameResourceData    : {name : "Creative Assembly game resource data", ext : [".pack"], magic : ["Creative Assembly game resource data"]},
		darkReignGameArchive                : {name : "Dark Reign Game Archive", ext : [".ftg"], magic : ["Dark Reign game data archive"], weakMagic : true, website : "http://fileformats.archiveteam.org/wiki/FTG_(Dark_Reign)"},
		darkReign2GameDataArchive           : {name : "Dark Reign 2 game data archive", ext : [".zwp"], magic : ["Dark Reign 2 game data archive"], weakMagic : true},
		destanGameDataArchive               : {name : "Destan game data archive", ext : [".3dn"], magic : ["Destan game data archive"]},
		digitalIllusionsGameArchive         : {name : "Digital Illusions game archive", ext : [".pdo", ".rmpublisher", ".rmlanguage", ".pdt", ".dta"], magic : ["Digital Illusions game data package"], weakMagic : true},
		dynamixGameArchive                  : {name : "Dynamix Game Archive", ext : [".dyn", ".rbx"], magic : ["Dynamix game data archive", "Dynamix Volume File game data archive"]},
		earthAndBeyondGameArchive           : {name : "Earth and Beyond Game Archive", ext : [".mix"], magic : ["Earth And Beyond game data archive"]},
		electronicArtsLibGameArchive        : {name : "Electronic Arts LIB Game Archive", ext : [".lib"], magic : ["Electronic Arts LIB container"]},
		empireEarth1GameArchive             : {name : "Empire Earth 1 Game Archive", ext : [".ssa"], magic : ["Empire Earth 1 game data", "Empire Earth Game Archive"], weakMagic : true},
		ensembleStudiosGameArchive          : {name : "Ensemble Studios Game Archive", ext : [".drs"], magic : ["Ensemble Studios Data Resource"]},
		etherlords2GameDataArchive          : {name : "Etherlords 2 game data archive", ext : [".res"], magic : ["Etherlords 2 game data archive"]},
		fearGameArchive                     : {name : "F.E.A.R. game archive", ext : [".arch00"], magic : ["F.E.A.R. game archive"]},
		finalFantasyGameArchive             : {name : "Final Fantasy Game Archive", ext : [".lgp"], magic : ["Final Fantasy Game Archive"]},
		finalLiberationGameArchive          : {name : "Final Liberation/Holistic Design game archive", ext : [".muk"], magic : ["Final Liberation: Warhammer Epic 40K game data archive", "Holistic Design game data archive (generic)"]},
		gabrielKnight3BarnGameArchive       : {name : "Gabriel Knight 3 barn game archive", ext : [".brn"], magic : ["Gabriel Knight 3 barn game data"]},
		gameMakerStudioGameDataArchive      : {name : "GameMaker Studio game data archive", ext : [".dat"], magic : ["GameMaker Studio game data archive"], weakMagic : true},
		godotPackageFormat                  : {name : "Godot Package format", ext : [".pck"], magic : ["Godot Package format", "Archive: Godot Pack"], weakMagic : true},
		haemimontGamesADGameDataArchive     : {name : "Haemimont Games AD game data archive", ext : [".hpk"], magic : ["Haemimont Games AD game data archive"], weakMagic : true},
		h2oGameDataArchive                  : {name : "Liquid Entertainment H2O game data archive", ext : [".h2o"], magic : ["Liquid Entertainment H2O game data archive"]},
		harryPotterQuidditchWorldCupArchive : {name : "Harry Potter: Quidditch World Cup archive", ext : [".ccd"], magic : ["Harry Potter: Quidditch World Cup game data archive"], weakMagic : true},
		highwayPursuitGameDataArchive       : {name : "Highway Pursuit game data archive", ext : [".hvd", ".hfd", ".hod", ".hsd", ".hmd", ".hgd"], magic : ["Highway Pursuit game data archive"], weakMagic : true},
		hmmPackfileGameArchive              : {name : "HMM Packfile Game Archive", ext : [".wdt", ".pak"], magic : ["Rising Kingdoms game data archive", /^fmt\/1876( |$)/]},
		hooligansGameDataArchive            : {name : "Hooligans game data archive", ext : [".x13"], magic : ["Hooligans game data archive"], weakMagic : true},
		howToSurviveSeriesGameArchive       : {name : "How to Survive series Game Archive", ext : [".rck"], magic : ["How to Survive series game data", "Format: RCK"], weakMagic : true},
		interstateGameArchive               : {name : "Interstate Series Game Archive", ext : [".zfs"], magic : ["Interstate serie game data archive", "Zork FileSystem game data archive"], weakMagic : true},
		jackedGameArchive                   : {name : "Jacked game archive", ext : [".dat", ".old"], magic : ["Jacked game data archive"], weakMagic : true},
		janesLongbow2GameArchive            : {name : "Jane's Longbow 2 Game Archive", ext : [".tre"], magic : ["Jane's Longbow 2 game data archive"]},
		lemmingsRevolutionGameArchive       : {name : "Lemmings Revolution game archive", ext : [".box"], magic : ["Lemmings Revolution game data archive"]},
		lionheadStudiosGameArchive          : {name : "Lionhead Studios game archive", ext : [".sad"], magic : ["Generic Lionhead Studios game data"]},
		lookingGlassGameArchive             : {name : "Looking Glass Game Archive", ext : [".res"], magic : ["Looking Glass Resource data", "LG Archiv gefunden"]},
		lucasArtsGameArchive                : {name : "Lucas Arts Game Archive", ext : [".gob"], magic : ["LucasArts Game data archive", "Dark Forces Game data archive"], idMeta : ({macFileType, macFileCreator}) => macFileType==="DATA" && ["dRfD", "dRfO", "PPUP"].includes(macFileCreator)},
		madsHAGGameArchive                  : {name : "MADS HAG Game Archive", ext : [".hag"], magic : ["MADS HAG game data archive"]},
		mallTycoonGameDataArchive           : {name : "Mall Tycoon game data archive", ext : [".muk"], magic : ["Mall Tycoon game data archive"], weakMagic : true},
		meyerGlassGameArchive               : {name : "Meyer/Glass Interactive Game Archive", ext : [".mgf"], magic : ["Meyer/Glass Interactive game data Format"]},
		mpakGameDataArchive                 : {name : "MPAK game data archive", ext : [".mpak"], magic : ["MPAK game data archive"]},
		nascarHeatGameArchive               : {name : "NASCAR Heat game archive", ext : [".trk", ".car"], magic : ["NASCAR Heat game data archive"]},
		novalogicGameArchive                : {name : "Novalogic Game Archive", ext : [".pff"], allowExtMatch : true, magic : ["Novalogic game data archive"]},
		obscureHVPackFileGameArchive        : {name : "Obscure HV PackFile game archive", ext : [".hvp"], magic : ["Obscure HV PackFile game data archive"]},
		pacmanAdventuresInTimeGameArchive   : {name : "Pacman - Adventures in Time game archive", ext : [".pac"], magic : ["Pacman - Adventures in Time game data archive"]},
		panzerEliteActionGameArchive        : {name : "Panzer Elite Action game archive", ext : [".x"], magic : ["Panzer Elite Action game data archive"], weakMagic : true},
		paxImperiaEminentDomainGameArchive  : {name : "Pax Imperia: Eminent Domain Game Archive", ext : [".img"], magic : ["Pax Imperia: Eminent Domain game data archive"], idMeta : ({macFileType, macFileCreator}) => macFileType==="Px2D" && macFileCreator==="Pax2"},
		pendulumaniaGameData                : {name : "Pendulumania game data", ext : [".qda"], magic : ["Pendulumania game data"], weakMagic : true},
		postalGameArchive                   : {name : "Postal game Archive", ext : [".sak"], magic : ["Postal game data Archive"]},
		quakePAK                            : {name : "Quake PAK", ext : [".pak"], allowExtMatch : true, magic : ["Quake archive", "Quake I or II world or extension", /^Archive: PACK$/], idMeta : ({macFileType, macFileCreator}) => (macFileType==="QDat" && macFileCreator==="Quak") || (macFileType===".pak" && macFileCreator==="HEX2") || (macFileType==="data" && macFileCreator==="Tmb4"), website : "http://fileformats.archiveteam.org/wiki/Quake_PAK"},
		realityBytesGameArchive             : {name : "Reality Bytes game archive", ext : [".rbd"], magic : ["Reality Bytes game Data archive"]},
		redengineGameArchive                : {name : "REDengine game Archive", ext : [".rda"], magic : ["REDengine game data Archive"]},
		riffBACKGameArchive                 : {name : "RIFF BACK Game Archive", ext : [".res"], magic : ["Generic RIFF file BACK"]},
		rumbleFighterGameDataArchive        : {name : "Rumble Fighter game data archive", ext : [".nsz"], magic : ["Rumble Fighter game data archive"]},
		scummDigitizedSoundsGameArchive     : {name : "SCUMM Digitized Sounds Game Archive", ext : [".sou"], magic : ["SCUMM digitized Sounds (v5-6)", "Lucasfilm Games VOC Sound"]},
		scraplandGameDataArchive            : {name : "Scrapland game data archive", ext : [".packed"], magic : ["Scrapland game data archive"]},
		sgaGameDataArchive                  : {name : "SGA game data archive", ext : [".sga", ".big"], magic : ["SGA game data archive", "SGA archive"], weakMagic : true},
		simsArchive                         : {name : "The Sims Archive", ext : [".far"], magic : ["The Sims Archive"], website : "http://fileformats.archiveteam.org/wiki/FAR_(The_Sims)"},
		simTexGameArchive                   : {name : "SimTex Game Archive", ext : [".lbx"], magic : ["SimTex LBX game data container"]},
		starsiegeGameArchive                : {name : "Starsiege Game Archive", ext : [".vol"], magic : ["Starsiege game data archive", "Starsiege Tribes game data archive"]},
		starTrekOnlineGameData              : {name : "Star Trek Online game data", ext : [".hogg"], magic : ["Star Trek Online game data"]},
		timeGateStudiosGameArchive          : {name : "TimeGate Studios game archive", ext : [".rwd"], magic : ["TimeGate Studios game data archive"], weakMagic : true},
		unrealEngine3Package                : {name : "Unreal Engine 3 Package", ext : [".u", ".uasset", ".utx", ".uax", ".umx", ".unr", ".ut3", ".upk"], magic : ["UE3 Unreal Package (LE)", "Format: UnrealEngine\\Unreal Package", /^Unreal (Audio|Engine) package/, /^Rune map$/], forbiddenMagic : ["Unreal Music"], idMeta : ({macFileType, macFileCreator}) => ["UnDt", "UnMp", "UnMu", "UnSn", "UnTx"].includes(macFileType) && ["DsEx", "Rune", "Unrl", "UnTn"].includes(macFileCreator)},
		vampireEngineMageSlayerGameArchive  : {name : "Vampire Engine MageSlayer game archive", ext : [".vpk"], magic : ["Vampire Engine MageSlayer game data archive"]},
		vivBIGF                             : {name : "VIV/BIGF/BIG4 EA Game Archive", ext : [".viv", ".big"], allowExtMatch : true, magic : ["VIV/BIGF Electronic Arts Game Archive", "Archive: BIGF", "BIG4 Electronic Arts game data archive"], website : "http://fileformats.archiveteam.org/wiki/VIV"},
		volitionPackageGameArchive          : {name : "Volition Package game archive", ext : [".vpp", ".vp"], magic : ["Volition Package - Red Faction game data archive", "Volition Package game archive data"]},
		warcraft2GameArchive                : {name : "Warcraft 2 Game Archive", ext : [".war"], magic : ["Warcraft game data archive"], weakMagic : true, idMeta : ({macFileType, macFileCreator}) => macFileType==="W2df" && macFileCreator==="W2dm"},
		wad2GameArchive                     : {name : "WAD2 Game Archive", ext : [".wad"], magic : ["WAD2 file", "Quake WAD"], website : "http://fileformats.archiveteam.org/wiki/Quake_WAD"},
		xcrArchive                          : {name : "XCR archive", ext : [".xcr"], magic : ["XCR archive", "Format: XCR"]},
		xenonautsGameArchive                : {name : "Xenonauts game archive", ext : [".pfp"], magic : ["Xenonauts game data archive"], weakMagic : true},
		youDontKnowJackGameArchive          : {name : "You Don't Know Jack Game Archive", ext : [".srf"], magic : ["You Don't Know Jack game data archive"], idMeta : ({macFileType, macFileCreator}) => (macFileType==="srf " && ["SRF ", "YDKJ"].includes(macFileCreator)) || (macFileType==="srf1" && macFileCreator==="SrfM") || (macFileType==="xSRF" && ["C2Bs", "Qbrw"].includes(macFileCreator))},
		warriorKingsGameData                : {name : "Warrior Kings game data", ext : [".bcp"], magic : ["Warrior Kings game data"]},
		wolfensteinGameData                 : {name : "Wolfenstein game data", ext : [".spk", ".mpk"], magic : ["Wolfenstein game data"]},
		zAxisGameSoundDataArchive           : {name : "Z-Axis game sound data archive", ext : [".zsd"], magic : ["Z-Axis game sound data archive"]}
	}
};

export const gamearch =
{
	archive :
	{
		buildEngineRFFGameArchive : {name : "Build Engine RFF Game Archive", ext : [".rff"], magic : ["Build Engine RFF encrypted container"], website : "https://moddingwiki.shikadi.net/wiki/RFF_Format"},
		cosmoVolumeGameArchive    : {name : "Cosmo Volume Game Archive", filename : [/^nukem2\.cmp$/i, /^volume\d[ab]\.ms\d$/i], website : "https://moddingwiki.shikadi.net/wiki/CMP_Format"},
		darkAgesMapGameArchive    : {name : "Dark Ages Map Game Archive", filename : [/^file05\.da\d$/i], website : "https://moddingwiki.shikadi.net/wiki/Dark_Ages_Map_Format"},
		drRiptideGameArchive      : {name : "Dr. Riptide Game Archive", ext : [".dat"], filename : [/^(riptide|ccedit)\.dat$/i, /^galvoice\.voc$/i], website : "https://moddingwiki.shikadi.net/wiki/DAT_Format_(Dr._Riptide)"},
		godOfThunderGameArchive   : {name : "God of Thunder Game Archive", ext : [".dat"], filename : [/^gotres\.dat$/i], website : "https://moddingwiki.shikadi.net/wiki/DAT_Format_(God_of_Thunder)"},
		highwayHunterGameArchive  : {name : "Highway Hunter Game Archive", ext : [".dat"], filename : [/^123\.dat$/i], website : "https://moddingwiki.shikadi.net/wiki/DAT_Format_(Highway_Hunter)"},
		homeBrewGameArchive       : {name : "HomeBrew Game Archive", ext : [".gw1", ".gw2", ".gw3"], magic : ["HomeBrew File Folder game data archive"], website : "https://moddingwiki.shikadi.net/wiki/HomeBrew_File_Folder_Format"},
		lostVikingsGameArchive    : {name : "The Lost Vikings Game Archive", ext : [".dat"], filename : [/^data\.dat$/i], website : "https://moddingwiki.shikadi.net/wiki/The_Lost_Vikings"},
		monsterBashGameArchive    : {name : "Monster Bash Game Archive", ext : [".dat"], filename : [/^bash\d\.dat$/i], website : "https://moddingwiki.shikadi.net/wiki/DAT_Format_(Monster_Bash)"},
		mysticTowersGameArchive   : {name : "Mystic Towers Game Archive", ext : [".dat"], filename : [/mystus\.dat$/i], website : "https://moddingwiki.shikadi.net/wiki/DAT_Format_(Mystic_Towers)"},
		mythosSoftwareGameArchive : {name : "Mythos Software Game Archive", ext : [".lib"], magic : ["Mythos Software LIB game data container"], website : "https://moddingwiki.shikadi.net/wiki/LIB_Format_(Mythos_Software)"},
		prehistorikGameArchive    : {name : "Prehistorik Game Archive", filename : [/^files[ab]\.(cur|vga)$/i], website : "https://moddingwiki.shikadi.net/wiki/CUR_Format"},
		sangoFighterGameArchive   : {name : "Sango Fighter Game Archive", filename : [/^backgd\.pic$/i, /^(bonus|color|pather)\.dat$/i, /^engpic\.pcx$/i, /^(eopen|story|workpage)\.pbn$/i, /^(hunt|stosay)\.pcp$/i, /^music\.mid$/i, /^voice\.pcm$/i, /^br.+\.rlc$/i, /^vs1\.rlc$/i, /message\.pxb$/i], website : "https://moddingwiki.shikadi.net/wiki/DAT_Format_(Sango_Fighter)"},
		stargunnerGameArchive     : {name : "Stargunner Game Archive", filename : [/^stargun\.dlt$/i], magic : ["DLT game data archive"], website : "https://moddingwiki.shikadi.net/wiki/DLT_Format"},
		stellar7GameArchive       : {name : "Stellar 7 Game Archive", ext : [".res"], filename : [/^(stellar|cockpit|draxon|voice|stelart|scenex|level\d+)\.res$/i], website : "https://moddingwiki.shikadi.net/wiki/RES_Format_(Stellar_7)"},
		vinylGoddessGameArchive   : {name : "Vinyl Goddess from Mars Game Archive", filename : [/^goddess\.lbr$/i], website : "https://moddingwiki.shikadi.net/wiki/LBR_Format"},
		wackyWheelsGameArchive    : {name : "Wacky Wheels Game Archive", filename : [/^wacky\.(dat|lid)$/i], magic : [/^Wacky Wheels Archive$/], website : "https://moddingwiki.shikadi.net/wiki/DAT_Format_(Wacky_Wheels)"}
	}
	
};

export const both =
{
	archive :
	{
		buildEngineGroupGameArchive : {name : "Build Engine Group Game Archive", ext : [".grp", ".dat"], magic : ["Build engine group file", "Build Engine GRP container"], idMeta : ({macFileType, macFileCreator}) => macFileType==="data" && ["Duke", "ShdW"].includes(macFileCreator), website : "http://fileformats.archiveteam.org/wiki/GRP_(Duke_Nukem_3D)"},
		descentGameArchive          : {name : "Descent Game Archive", ext : [".hog"], magic : ["Descent game data archive"], idMeta : ({macFileType, macFileCreator}) => macFileType==="HOG " && ["DCNT", "DCT2"].includes(macFileCreator)},
		epfGameArchive 			    : {name : "EPF Game Archive", ext : [".epf"], magic : ["EPF game data archive"], website : "https://moddingwiki.shikadi.net/wiki/EPF_Format"}
	}
};
