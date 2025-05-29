import {Format} from "../../Format.js";
import {TEXT_MAGIC} from "../../Detection.js";
import {_IMF_MAGIC} from "../text/imf.js";
import {flexMatch} from "../../identify.js";

export class ans extends Format
{
	name             = "ANSi Art File";
	website          = "http://fileformats.archiveteam.org/wiki/ANSI_Art";
	ext              = [".ans", ".drk", ".ice", ".ansi", ".asc", ".gbs"];
	weakExt          = [".drk", ".ice", ".asc"];	// .ANS was widely accepted as ANSI, but .drk and .ice less so. .asc is also not widely used.
	forbidExtMatch   = true;	// Sadly some .ice files like "2002 - 20 - tcf-0001.ice" won't get converted because they only identify as 'data' and since ansilove will convert any file you send it, we can't send these
	mimeType         = "text/x-ansi";
	priority         = this.PRIORITY.LOW;	// allow other image format detections to take priority
	magic            = ["ANSI escape sequence text", "ISO-8859 text, with escape sequences", "deark: ansiart", ...TEXT_MAGIC, /^data$/, ..._IMF_MAGIC];
	weakMagic        = [...TEXT_MAGIC, /^data$/, ..._IMF_MAGIC];
	confidenceAdjust = (inputFile, matchType, curConfidence, {detections}) =>
	{
		const magicMatches = detections.filter(detection => this.magic.some(m => flexMatch(detection.value, m)));

		// If all we've got for magic matches ia /^data$/ that's not a very confident match, so kick down the confidence level to '9' to allow other formats a shot at properly converting this first
		if(magicMatches.length===1 && magicMatches[0].value==="data")
			return -(curConfidence-9);
		
		return 0;
	};
	metaProvider = ["ansiloveInfo"];
	converters   = [
		"ansilove[format:ans]",
		dexState => (dexState.imageFailedTooTall ? null : "ffmpeg[format:tty][codec:ansi][outType:gif]"),	// if we failed a previous converter due to being too tall, then don't convert to an animated GIF (text/txt/Newsletter)
		"deark[module:ansiart][charOutType:image]"
	];
	notes = "Animated ANSI sequences such as KM-TRANSPORTER.ANS only get converted into a single image with ansilove. It would be nice to 'detect' that it's animated and use ffmpeg instead to convert it into an animated MP4";
}
