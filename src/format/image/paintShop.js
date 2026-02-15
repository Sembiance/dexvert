import {Format} from "../../Format.js";

export class paintShop extends Format
{
	name       = "PaintShop";
	website    = "http://fileformats.archiveteam.org/wiki/PaintShop_(Atari_ST)";
	ext        = [".da4", ".psc"];
	magic      = ["PaintShop plus Compressed bitmap", /^fmt\/1733( |$)/];
	converters = dexState =>
	{
		const r = ["recoil2png[format:PSC,DA4]"];
		if(dexState.original.input.ext.toLowerCase()===".da4")
			r.push("wuimg[format:da4][matchType:magic]");
		return r;
	};
}
