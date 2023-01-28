import {Format} from "../../Format.js";

export class vinylGoddessLBR extends Format
{
	name       = "Vinyl Goddess from Mars LBR Archive";
	website    = "https://moddingwiki.shikadi.net/wiki/LBR_Format";
	filename   = [/^goddess\.lbr$/i];
	converters = ["gamearch"];
}
