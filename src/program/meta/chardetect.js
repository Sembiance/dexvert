import {xu} from "xu";
import {Program} from "../../Program.js";

export class chardetect extends Program
{
	website    = "https://github.com/chardet/chardet";
	package    = "dev-python/chardet";
	bin        = "chardetect";
	args       = r => [r.inFile()];
	runOptions = ({timeout : xu.MINUTE});	// Can get hung up on certain files and just spin forever
	post       = r =>
	{
		let detectedCharSet = r.stdout.trim().substring(r.inFile().length + 2);
		if(detectedCharSet!=="no result")
		{
			detectedCharSet = detectedCharSet.substring(0, detectedCharSet.indexOf(" "));
			if(detectedCharSet.length>0)
				r.meta.charSet = detectedCharSet;
		}
	};
}
