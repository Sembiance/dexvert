import {xu} from "xu";
import {fileUtil} from "xutil";
import {Format} from "../../Format.js";
import {csvParse} from "std";

export class csv extends Format
{
	name         = "Comma Seperated Value File";
	website      = "http://fileformats.archiveteam.org/wiki/CSV";
	ext          = [".csv"];
	mimeType     = "application/json";
	magic        = ["CSV text", "CSV ASCII text"];
	priority     = this.PRIORITY.LOW;
	untouched    = dexState => dexState.meta.entryCount;
	metaProvider = ["text"];
	meta         = async inputFile =>
	{
		// anything 25MB or larger skip parsing
		if(inputFile.size>xu.MB*25)
			return {};

		const m = {};
		const csvResult = await xu.tryFallbackAsync(async () => await csvParse(await fileUtil.readTextFile(inputFile.absolute)));
		if(csvResult?.length)
			m.entryCount = csvResult.length;

		return m;
	};
}
