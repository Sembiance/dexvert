import {Format} from "../../Format.js";

export class vinylGoddessGameArchive extends Format
{
	name           = "Vinyl Goddess from Mars Game Archive";
	website        = "https://moddingwiki.shikadi.net/wiki/LBR_Format";
	filename       = [/^goddess\.lbr$/i];
	magic          = [/^geArchive: LBR( |$)/];
	converters     = ["gamearch", "gameextractor[codes:LBR]"];
}
