// All of the formats in this file are 'packed' files that should just be handled with the 'unp' and/or 'cup386' programs and are not worthy of having their own file
// Each entry also has the following properties added:
//             ext : [".exe", ".com"]
//	forbidExtMatch : true
//          packed : true
//	converters     : ["unp[renameKeepFilename]"] or ["cup386[renameKeepFilename]"] or ["unp[renameKeepFilename]", "cup386[renameKeepFilename]"]
export const unp =
{
	archive :
	{
		compackPacked  : {name : "COMPACK Packed", magic : ["Packer: COMPACK", "16bit DOS EXE COMPACK compressed"]},
		icePacked      : {name : "ICE Packed", magic : ["ICE compressed/scrambled DOS Command", "Packer: ICE"]},
		optlinkPacked  : {name : "OPTLINK Packed", magic : ["Packer: Optlink"]},
		tinyProgPacked : {name : "TinyProg Packed", magic : ["16bit DOS EXE TinyProg compressed"]}
	}
};

export const cup386 =
{
	archive :
	{
		ainexePacked        : {name : "AINEXE Packed", magic : ["AINEXE compressed 16bit DOS executable", "Packer: AINEXE"]},
		amisetupPacked      : {name : "Amisetup Packed", magic : ["Packer: Amisetup loader[by Robert Muchsel]"]},
		aPACKPacked         : {name : "aPACK Packed", magic : ["Packer: aPACK", "16bit DOS EXE aPACK compressed"]},
		avPackPacked        : {name : "AVPACK Packed", magic : ["Packer: AVPACK(1.22)[Andrei Volkov]"]},
		comRLEPackerPacked  : {name : "com RLE packer Packed", magic : ["Packer: com RLE packer[by NOP/PC]"]},
		cruncherPacked      : {name : "Cruncher Packed", magic : ["Cruncher compressed DOS executable"]},
		exeLITEPacked       : {name : "ExeLITE Packed", magic : ["ExeLITE compressed 16bit DOS executable"]},
		fourKZIPPacked      : {name : "4kZIP Packed", magic : ["Packer: 4kZIP[by pascal //Digital Nightmare]"]},
		lglzPacked          : {name : "LGLZ Packed", magic : ["16bit DOS EXE LGLZ compressed"]},
		packerJESCOREPacked : {name : "Packer JES //CORE Packed", magic : ["Packer: Packer[1997 by JES //CORE]"]},
		packerPacked        : {name : "Packer Packed", magic : ["Packer: Packer"]},
		pktinyPacked        : {name : "PKTINY Packed", magic : ["16bit DOS EXE PKTINY compressed"]},
		rdtCompressorPacked : {name : "RDT Compressor Packed", magic : ["Packer: RDT_Compressor"]},
		rjCrushPacked       : {name : "RJCrush Packed", magic : ["RJCrush compressed 16bit DOS executable"]},
		rleCOMPackerPacked  : {name : "RLE com-packer Packed", magic : ["Packer: RLE com-packer"]},
		sixTwoFourPacked    : {name : "624 Packed", magic : ["Packer: Six-2-Fou", "Six-2-Four (624) packed DOS Command"]},
		spaceMakerPacked    : {name : "SpaceMaker Packed", magic : ["16bit DOS EXE Spacemaker compressed"]},
		tpackPacked         : {name : "T-PACK Packed", magic : ["Packer: TPACK", "16bit DOS COM T-PACK compressed"]},
		xpackLZCOMPacked    : {name : "XPACK/LZCOM Packed", magic : ["Packer: XPACK/LZCOM"]}
	}
	
};

export const both =
{
	archive :
	{
		axePacked                : {name : "AXE Packed", magic : ["16bit DOS AXE compressed Executable", "16bit DOS EXE AXE compressed"]},
		cebeCompressExpandPacked : {name : "CEBE Compress Expand Packed", magic : ["CEBE Compress Expand compressed DOS executable"]},
		cheatPackerPacked        : {name : "Cheat Packer Packed", magic : ["Packer: Cheat packer"]},
		dietPacked               : {name : "Diet Packed", magic : ["Packer: Diet", "16bit DOS EXE DIET compressed"]},
		neobookPacked            : {name : "Neobook Packed", magic : ["Neobook compiled book executable"]},
		packwinPacked            : {name : "PACKWIN Packed", magic : ["16bit DOS EXE PACKWIN compressed"]},
		pgmpakPacked             : {name : "PGMPAK Packed", magic : ["Packer: PGMPAK", "16bit DOS EXE PGMPAK compressed"]},
		proPackPackedExe         : {name : "Pro-Pack Packed Executable", magic : ["Packer: PRO-PACK", /^16bit DOS EXE R[MN]C \/ PRO-PACK compressed/]},
		scrnchPacked             : {name : "SCRNCH Packed", magic : ["Packer: SCRNCH", "SCRNCH compressed"]},
		shrinkPacked             : {name : "Shrink Packed", magic : ["Shrink packed", "Packer: SHRINK"]},
		ucexePacked              : {name : "UCEXE Packed", magic : ["Packer: UCEXE", "UCEXE compressed 16bit DOS executable"]},
		wwpackPacked             : {name : "WWPACK Packed", magic : ["Packer: WWPACK", "16bit DOS EXE WWPACK compressed"]}
	}
};
