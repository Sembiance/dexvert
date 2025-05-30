import {Format} from "../../Format.js";

export class degasExtended extends Format
{
	name       = "Extended DEGAS Image";
	website    = "http://fileformats.archiveteam.org/wiki/Extended_DEGAS_image";
	magic      = ["deark: fpaint_pi9", "deark: atari_pi7", "deark: fpaint_pi4"];
	ext        = [".pi4", ".pi5", ".pi6", ".pi7", ".pi8", ".pi9"];
	fileSize   = {".pi4" : [77824, 154_114], ".pi5" : [38434, 153_634], ".pi7" : 308_224, ".pi9" : [77824, 65024]};
	byteCheck  = [{ext : ".pi5", offset : 0, match : [0x00, 0x04]}];
	converters = dexState =>
	{
		const r = ["recoil2png"];
		const originalExt = dexState.original.input.ext.toLowerCase();
		if(originalExt===".pi9")
			r.push("deark[module:fpaint_pi9]");
		if(originalExt===".pi7")
			r.push("deark[module:atari_pi7]");
		if(originalExt===".pi4")
			r.push("deark[module:fpaint_pi4]");
		return r;
	};
}
