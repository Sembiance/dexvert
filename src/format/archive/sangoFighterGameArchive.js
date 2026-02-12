import {Format} from "../../Format.js";

export class sangoFighterGameArchive extends Format
{
	name           = "Sango Fighter Game Archive";
	website        = "https://moddingwiki.shikadi.net/wiki/DAT_Format_(Sango_Fighter)";
	filename       = [/^backgd\.pic$/i, /^(bonus|color|pather)\.dat$/i, /^engpic\.pcx$/i, /^(eopen|story|workpage)\.pbn$/i, /^(hunt|stosay)\.pcp$/i, /^music\.mid$/i, /^voice\.pcm$/i, /^br.+\.rlc$/i, /^vs1\.rlc$/i, /message\.pxb$/i];
	converters     = ["gamearch"];
}
