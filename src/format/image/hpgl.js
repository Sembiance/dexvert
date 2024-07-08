import {xu} from "xu";
import {Format} from "../../Format.js";
import {TextLineStream} from "std";

export class hpgl extends Format
{
	name           = "Hewlett-Packard Graphics Language";
	website        = "http://fileformats.archiveteam.org/wiki/HP-GL";
	ext            = [".hpgl", ".hpg", ".hp", ".plt"];
	forbidExtMatch = [".hp", ".plt"];
	magic          = ["Hewlett-Packard Graphics Language"];
	idCheck = async (inputFile, detections, {extMatch}) =>
	{
		// the magic above is kinda weak, but it doesn't have a good extension either. Some things convert as garbage
		// we allow in if the extension is a non-weak extension match
		if(extMatch)
			return true;

		if(inputFile.size>(xu.MB*3))	// discmaster has never encountered an HPGL file larger than 1.4MB so this is probably pretty safe
			return false;

		for await(const line of (await Deno.open(inputFile.absolute)).readable.pipeThrough(new TextDecoderStream()).pipeThrough(new TextLineStream()))
		{
			if(!line?.trim()?.length)
				continue;

			// from: https://web.archive.org/web/20170227192501/http://www.sxlist.com/techref/language/hpgl/commands.htm
			// commands must be terminated by semi-colon or line feed
			// so we check the first non-empty line and pass if we find a semi-colon or if the first 2 chars are a valid command and the third letter is a space
			const VALID_COMMANDS = ["aa", "ar", "ca", "ci", "cp", "cs", "dc", "dp", "df", "dr", "di", "dt", "ea", "er", "ft", "im", "ip", "in", "iw", "lb", "oa", "oc", "od", "oe", "of", "ph", "oi", "oo", "op", "os", "pa", "pd", "pr", "ps", "pt", "pu", "ra", "ro", "rr", "sa", "sc", "si", "sl", "sm", "sp", "sr", "ss", "tl", "uc", "vs"];
			return line?.trim().includes(";") || (VALID_COMMANDS.includes(line?.substring(0, 2).toLowerCase() && line.charAt(2)===" "));
		}

		return false;
	};
	idMeta         = ({macFileType}) => macFileType==="HPGL";
	converters     = [
		// svg
		"viewCompanion",

		// png
		"corelPhotoPaint",
		
		// svg, but super slow, so we only do it if we have both ext and magic match
		"canvas[strongMatch][hasExtMatch][nonRaster]"
		
		// "irfanView" // this will just output a PNG, but it'll take almost anything and output garbage
	];
}
