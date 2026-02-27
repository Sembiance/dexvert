import {Format} from "../../Format.js";

export class wad extends Format
{
	name       = "WAD";
	website    = "http://fileformats.archiveteam.org/wiki/Doom_WAD";
	ext        = [".wad"];
	magic      = [
		"id Software's DOOM Patch-WAD", "doom patch PWAD", "doom main IWAD", "id Software's DOOM Internal-WAD", "WAD3 game data", "Dungeon Keeper 2 game data archive", "application/x-doom-wad",
		/^Format: (Internal|Personal) WAD file/, "deark: wad", "WAD3 :wad:", /^geArchive: WAD_(IWAD|PWAD|WAD3)( |$)/, "dragon: WAD3 "
	];
	idMeta     = ({macFileType, macFileCreator}) => (macFileType===".WAD" && ["Htic", "idSW"].includes(macFileCreator)) || (macFileType==="HXwd" && macFileCreator==="HEXN");
	priority   = this.PRIORITY.LOW;
	converters = dexState =>
	{
		const r = [];
		if(dexState.hasMagics("WAD3 :wad:"))
			r.push("gameextractor[codes:WAD_WAD3,WAD_PWAD,WAD_IWAD]", "nconvert[extractAll][format:wad]");

		r.push("deark[module:wad]");
		if(!dexState.hasMagics("WAD3 :wad:"))
			r.push("gameextractor[codes:WAD_WAD3,WAD_PWAD,WAD_IWAD]");
		
		r.push("dragonUnpacker[types:WAD3]", "gamearch");
		return r.map(v => `${v} & noesis[type:poly]`);
	};
}
