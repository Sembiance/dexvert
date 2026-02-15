import {Format} from "../../Format.js";
import {RUNTIME} from "../../Program.js";
import {TEXT_MAGIC_STRONG} from "../../Detection.js";

export class printfox extends Format
{
	name           = "Printfox/Pagefox Bitmap";
	website        = "http://fileformats.archiveteam.org/wiki/Printfox_bitmap";
	ext            = [".gb", ".bs", ".pg"];
	magic          = ["PrintFox/Pagefox bitmap", "PrintFox/Pagefox WEAK", "Printfox/Pagefox :prx:"];
	trustMagic     = true;
	forbiddenMagic = TEXT_MAGIC_STRONG;

	// Since this is such a weak match, only allow if we are an extMatch OR we have explicitly set an environment variable as commodore
	idCheck = (inputFile, detections, {extMatch}) => extMatch || RUNTIME.globalFlags?.osHint?.commodore;

	// We used to allow .bin as well, but the 'magic' is so totally weak (just a single character at the start of the file) that we simply can't allow it out in the wild
	// The following two lines can be re-instated if you want to add .bin back as an extension above, assuming you can figure out a way further identify the file
	// .bin doesn't convert correctly with nconvert, so if we detect it in a filename like shark.gb.bin then we check to see if .gb is a valid ext, otherwise we just use .gb
	//safeExt    : state => (state.input.ext.toLowerCase()===".bin" ? (exports.meta.ext.find(v => v===path.extname(state.input.name).toLowerCase()) || ".gb") : state.input.ext.toLowerCase()),

	converters = ["nconvert[format:prx]", "recoil2png[format:BS,GB,PG]"];
}
