import {Format} from "../../Format.js";
import {fileUtil, encodeUtil} from "xutil";

export class thetaMusicComposer extends Format
{
	name         = "Theta Music Composer";
	website      = "http://atariki.krap.pl/index.php/TMC_%28format_pliku%29";
	ext          = [".tm8", ".tmc", ".tm2"];
	magic        = ["Theta Music Composer 1.x", "Theta Music Composer 2.x"];
	idCheck      = async (inputFile, detections) =>
	{
		if(!detections.some(detection => detection.value==="Theta Music Composer 1.x"))
			return true;

		const songTitleRaw = await fileUtil.readFileBytes(inputFile.absolute, 30, 6);
		if(songTitleRaw.every(v => (v>=32 && v<=126) || (v===9) || (v===13) || (v===10)))
			return true;

		const songTitleText = await encodeUtil.decode(songTitleRaw, "ATARI-ST");
		if(!(/^[ -~\t\r\n]*$/).test(songTitleText))
			return false;

		return true;
	};
	metaProvider = ["musicInfo"];
	converters   = ["asapconv"];
}
