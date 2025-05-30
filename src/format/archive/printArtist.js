import {Format} from "../../Format.js";

export class printArtist extends Format
{
	name           = "Print/Instant Artist";
	website        = "http://fileformats.archiveteam.org/wiki/Print_Artist";
	ext            = [".gfx"];
	forbidExtMatch = true;
	magic          = ["Print / Instant Artist"];
	idMeta         = ({macFileType, macFileCreator}) => ["GRFX", "LAYC", "LAYS", "QOTE"].includes(macFileType) && macFileCreator==="SOPa";
	converters     = ["printArtist"];
}
