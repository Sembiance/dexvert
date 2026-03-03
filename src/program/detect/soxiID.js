import {Program} from "../../Program.js";
import {Detection} from "../../Detection.js";

// soxi will match against file extension which would be BAD since that would mean extensions get converted to stronger 'magic', so we copy it to a tmp file (with a random.tmp name) and run trid against that
// HOWEVER, some formats are not 'checked' by soxi UNLESS the extension is set, so we allow certain extensions in
const ALLOWED_EXTS =
[
	".snd"		// audio/sounder
];

export class soxiID extends Program
{
	website = "http://sox.sourceforge.net";
	package = "media-sound/sox";
	bin     = "soxi";
	loc     = "local";
	args    = r => ["-t", ALLOWED_EXTS.includes(r.f.input.ext?.toLowerCase()) ? r.inFile() : r.flags.detectTmpFilePath];
	post    = r =>
	{
		r.meta.detections = [];

		for(const line of r.stdout.trim().split("\n"))
		{
			if(line.trim().length)
				r.meta.detections.push(Detection.create({value : `soxi: ${line.trim()}`, confidence : 100, from : "soxiID", file : r.f.input}));
		}
	};
	renameOut = false;
}
