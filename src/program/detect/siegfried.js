import {xu} from "xu";
import {Program} from "../../Program.js";
import {Detection} from "../../Detection.js";
import {base64Encode, path} from "std";
import {C} from "../../C.js";

const WARNINGS_SKIP = ["no match", "match on extension only", "empty source"];
const WARNINGS_ALLOW = ["extension mismatch", "match on text only"];

export class siegfried extends Program
{
	website = "https://github.com/richardlehane/siegfried";
	package = "app-arch/siegfried-bin";
	loc     = "local";
	exec    = async r =>
	{
		r.meta.detections = [];

		const rawText = await xu.tryFallbackAsync(async () => await (await fetch(`http://${C.SIEGFRIED_HOST}:${C.SIEGFRIED_PORT}/identify/${base64Encode(r.inFile({absolute : true}))}?base64=true&format=json`)).text());
		if(!rawText)
			return r.xlog.error`Failed to get siegfried data for file: ${r.f.input.base} got: ${rawText}`;
			
		const rawResult = xu.parseJSON(rawText.replaceAll("\t", ""));
		const matches = (rawResult?.files || []).find(({filename}) => path.basename(filename)===r.f.input.base)?.matches || [];
		if(matches.length===0)
			return r.xlog.warn`No siegfried matches for file, should always have 1 UNKNOWN match: ${rawResult}`;
		
		for(const {format, warning : warningRaw, version, id} of matches)
		{
			const warnings = warningRaw?.length ? warningRaw.split(";").map(v => v.trim()) : [];
			if(id==="UNKNOWN" || warnings.some(warning => WARNINGS_SKIP.includes(warning)))
				continue;
			
			const unknownWarnings = warnings.filter(warning => !WARNINGS_ALLOW.includes(warning));
			if(unknownWarnings.length)
				r.xlog.error`siegfried unknown warnings: ${unknownWarnings} on file: ${r.f.input.base}`;
			
			r.meta.detections.push(Detection.create({value : `${id}${format?.length ? ` ${format}` : ""}${version ? ` (${version})` : ""}`, from : "siegfried", confidence : 100, file : r.f.input}));
		}
	};
	renameOut = false;
}
