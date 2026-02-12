import {Format} from "../../Format.js";

const WAD3_MAGICS = ["WAD3 :wad:", "geArchive: WAD_WAD3"];

export class wad extends Format
{
	name       = "WAD";
	website    = "http://fileformats.archiveteam.org/wiki/Doom_WAD";
	ext        = [".wad"];
	magic      = [
		"id Software's DOOM Patch-WAD", "doom patch PWAD", "doom main IWAD", "id Software's DOOM Internal-WAD", "WAD3 game data", "Dungeon Keeper 2 game data archive", "application/x-doom-wad",
		"geArchive: WAD_PWAD", "geArchive: WAD_IWAD",
		/^Format: (Internal|Personal) WAD file/, "deark: wad", ...WAD3_MAGICS
	];
	idMeta     = ({macFileType, macFileCreator}) => (macFileType===".WAD" && ["Htic", "idSW"].includes(macFileCreator)) || (macFileType==="HXwd" && macFileCreator==="HEXN");
	converters = dexState =>
	{
		const r = [];
		if(dexState.hasMagics(WAD3_MAGICS))
			r.push("nconvert[extractAll][format:wad]");

		r.push("deark[module:wad]", "gamearch", "gameextractor[codes:WAD_WAD3,WAD_PWAD,WAD_IWAD]");
		return r.map(v => `${v} & noesis[type:poly]`);
	};
}
