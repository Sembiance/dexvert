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
		tinyProgPacked : {name : "TinyProg Packed", magic : ["16bit DOS EXE TinyProg compressed", "Packer: TinyProg"]}
	}
};

export const cup386 =
{
	archive :
	{
		ainexePacked                : {name : "AINEXE Packed", magic : ["AINEXE compressed 16bit DOS executable", "Packer: AINEXE"]},
		amisetupPacked              : {name : "Amisetup Packed", magic : ["Packer: Amisetup loader[by Robert Muchsel]"]},
		aPACKPacked                 : {name : "aPACK Packed", magic : ["Packer: aPACK", "16bit DOS EXE aPACK compressed"]},
		avPackPacked                : {name : "AVPACK Packed", magic : ["Packer: AVPACK"]},
		comRLEPackerPacked          : {name : "com RLE packer Packed", magic : ["Packer: com RLE packer"]},
		compressEXEPacked           : {name : "Compress-EXE Packed", magic : ["Packer: Compress-EXE"]},
		cruncherPacked              : {name : "Cruncher Packed", magic : ["Cruncher compressed DOS executable"]},
		dexEXEPacked                : {name : "DexEXE Packed",  magic : ["Packer: DexEXE"]},
		dnCOMCruncherPacked         : {name : "Dn.COM Cruncher Packed", magic : ["Packer: Dn.COM Cruncher"]},
		envelopePacked              : {name : "Envelope Packed", magic : ["Packer: envelope"]},
		exeLITEPacked               : {name : "ExeLITE Packed", magic : ["ExeLITE compressed 16bit DOS executable", "Packer: ExeLITE"]},
		fourKZIPPacked              : {name : "4kZIP Packed", magic : ["Packer: 4kZIP[by pascal //Digital Nightmare]"]},
		jamPacked                   : {name : "JAM Packed", magic : ["JAM compressed 16bit DOS executable"]},
		lglzPacked                  : {name : "LGLZ Packed", magic : ["Packer: LGLZ", "16bit DOS EXE LGLZ compressed", "LGLZ compressed DOS command"]},
		packPacked                  : {name : "Pack Packed", magic : ["Packer: Pack(1.0)[1987 by K.Kokkonen]"]},
		packerJESCOREPacked         : {name : "Packer JES //CORE Packed", magic : ["Packer: Packer[1997 by JES //CORE]"]},
		packerPacked                : {name : "Packer Packed", magic : ["Packer: Packer"]},
		pmwLitePacked               : {name : "PMWLite Packed", magic : ["Packer: PMWLite"]},
		rdtCompressorPacked         : {name : "RDT Compressor Packed", magic : ["Packer: RDT_Compressor"]},
		rjCrushPacked               : {name : "RJCrush Packed", magic : ["RJCrush compressed 16bit DOS executable", "Packer: RJcrush"]},
		rleCOMPackerPacked          : {name : "RLE com-packer Packed", magic : ["Packer: RLE com-packer"]},
		sixTwoFourPacked            : {name : "624 Packed", magic : ["Packer: Six-2-Fou", "Six-2-Four (624) packed DOS Command"]},
		shrinkerPacked              : {name : "Shrinker Packed", magic : ["16bit DOS Shrinker compressed Executable"]},
		spaceMakerPacked            : {name : "SpaceMaker Packed", magic : ["16bit DOS EXE Spacemaker compressed"]},
		tenthPlanetSoftPackerPacked : {name : "Tenth Planet Soft Packer Packed", magic : ["Packer: Tenth Planet Soft packer[1996]"]},
		tpackPacked                 : {name : "T-PACK Packed", magic : ["Packer: TPACK", "16bit DOS COM T-PACK compressed"]},
		tscrunchPacked              : {name : "TSCRUNCH Packed", magic : ["Packer: TSCRUNCH[by Clarion software]"]},
		xpackLZCOMPacked            : {name : "XPACK/LZCOM Packed", magic : ["Packer: XPACK/LZCOM"]}
	}
	
};

export const both =
{
	archive :
	{
		axePacked                 : {name : "AXE Packed", magic : ["16bit DOS AXE compressed Executable", "16bit DOS EXE AXE compressed", "Packer: SEA-AXE"]},
		cebeCompressExpandPacked  : {name : "CEBE Compress Expand Packed", magic : ["CEBE Compress Expand compressed DOS executable"]},
		cheatPackerPacked         : {name : "Cheat Packer Packed", magic : ["Packer: Cheat packer"]},
		dietPacked                : {name : "Diet Packed", magic : ["Packer: Diet", "16bit DOS EXE DIET compressed"]},
		executrixCompressorPacked : {name : "EXECUTRIX-COMPRESSOR Packed", magic : ["Packer: EXECUTRIX-COMPRESSOR[by Knowledge Dynamics Corp]"]},
		lmt2ePacked               : {name : "LM-T2E Packed", magic : ["16bit DOS LM-T2E executable"]},
		neobookPacked             : {name : "Neobook Packed", magic : ["Neobook compiled book executable"]},
		packwinPacked             : {name : "PACKWIN Packed", magic : ["16bit DOS EXE PACKWIN compressed", "16bit Win EXE PACKWIN compressed"]},
		pgmpakPacked              : {name : "PGMPAK Packed", magic : ["Packer: PGMPAK", "16bit DOS EXE PGMPAK compressed"]},
		pktinyPacked              : {name : "PKTINY Packed", magic : ["Packer: PKTINY", "16bit DOS EXE PKTINY compressed"]},
		proPackPackedExe          : {name : "Pro-Pack Packed Executable", magic : ["Packer: PRO-PACK", /^16bit DOS EXE R[MN]C \/ PRO-PACK compressed/]},
		scrnchPacked              : {name : "SCRNCH Packed", magic : ["Packer: SCRNCH", "SCRNCH compressed"]},
		shrinkPacked              : {name : "Shrink Packed", magic : ["Shrink packed", "Packer: SHRINK"]},
		ucexePacked               : {name : "UCEXE Packed", magic : ["Packer: UCEXE", "UCEXE compressed 16bit DOS executable"]},
		wwpackPacked              : {name : "WWPACK Packed", magic : ["Packer: WWPACK", "16bit DOS EXE WWPACK compressed"]}
	}
};
