import {Format} from "../../Format.js";

export class wad extends Format
{
	name       = "WAD";
	website    = "http://fileformats.archiveteam.org/wiki/Doom_WAD";
	ext        = [".wad"];
	magic      = ["id Software's DOOM Patch-WAD", "doom patch PWAD", "doom main IWAD", "id Software's DOOM Internal-WAD", "WAD3 game data", "Dungeon Keeper 2 game data archive", "application/x-doom-wad", /^Format: (Internal|Personal) WAD file/];
	idMeta     = ({macFileType, macFileCreator}) => (macFileType===".WAD" && ["Htic", "idSW"].includes(macFileCreator)) || (macFileType==="HXwd" && macFileCreator==="HEXN");
	converters = ["deark[module:wad]", "gamearch", "gameextractor"].map(v => `${v} & noesis[type:poly]`);
}
