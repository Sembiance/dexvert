import {xu} from "xu";
import {Program} from "../../Program.js";
import {Detection} from "../../Detection.js";
import {base64Encode, path} from "std";

export class siegfried extends Program
{
	website = "https://github.com/richardlehane/siegfried";
	package = "app-arch/siegfried";
	loc     = "local";
	exec    = async r =>
	{
		r.meta.detections = [];

		const SIEGFRIED_HOST = "127.0.0.1";
		const SIEGFRIED_PORT = 15138;
		const rawResult = (await (await fetch(`http://${SIEGFRIED_HOST}:${SIEGFRIED_PORT}/identify/${base64Encode(r.inFile({absolute : true}))}?base64=true&format=json`)).json());
		const matches = (rawResult?.files || []).find(({filename}) => path.basename(filename)===r.f.input.base)?.matches || [];
		if(matches.length===0)
			return;
		
		for(const {format, warning, version, id} of matches)
		{
			if(id==="UNKNOWN" || warning==="no match")
				continue;
			
			r.meta.detections.push(Detection.create({value : `${id}${format?.length ? ` ${format}` : ""}${version ? ` (${version})` : ""}`, from : "siegfried", confidence : 100, file : r.f.input}));
		}
	};
	/*bin     = "sf";
	args    = r => ["-home", "/opt/siegfried-bin/siegfried", "-json", r.inFile()];
	post    = r =>
	{
		r.meta.detections = [];

		const o = (xu.parseJSON(r.stdout)?.files || []).find(({filename}) => filename===r.f.input.base);
		if(!o)
			return;
		
		const matches = o.matches || [];
		if(matches.length===0)
			return;
		
		for(const {format, warning, version, id} of matches)
		{
			if(id==="UNKNOWN" || warning==="no match")
				continue;
			
			r.meta.detections.push(Detection.create({value : `${id}${format?.length ? ` ${format}` : ""}${version ? ` (${version})` : ""}`, from : "siegfried", confidence : 100, file : r.f.input}));
		}
	};*/
	renameOut = false;
}
