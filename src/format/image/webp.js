import {Format} from "../../Format.js";

export class webp extends Format
{
	name          = "WebP Image";
	website       = "http://fileformats.archiveteam.org/wiki/Webp";
	ext           = [".webp"];
	mimeType      = "image/webp";
	magic         = ["WebP bitmap", /^WebP$/, /^RIFF.* Web\/P image$/];
	untouched     = true;
	metaProvider = ["image", "webpinfo"];
}

/*

exports.inputMeta = (state0, p0, cb) => p0.util.flow.serial([
	(state, p) => p.family.supportedInputMeta,
	() => ({program : "webpinfo"}),
	(state, p) =>
	{
		if(p.util.program.getMeta(state, "webpinfo"))
			state.input.meta.webp = p.util.program.getMeta(state, "webpinfo");

		return p.util.flow.noop;
	}
])(state0, p0, cb);

*/
