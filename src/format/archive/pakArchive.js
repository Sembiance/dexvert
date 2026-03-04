import {Format} from "../../Format.js";

export class pakArchive extends Format
{
	name           = "PAK Archive";
	ext            = [".pak"];
	forbidExtMatch = true;
	magic          = [
		/^geArchive: PAK_PACK_4( |$)/,
		/^geArchive: PAK_(37|57)( |$)/,
		/^geArchive: PAK_(46|48)( |$)/	// These identify for ICON.PAK, WARI.PAK, WINDOWS.PAK but actually extract as PAK_57, which is why these are not listed below as codes, as I haven't encountered true archives as these yet
	];
	converters = ["gameextractor[codes:PAK_37,PAK_57,PAK_PACK_4]"];
}
