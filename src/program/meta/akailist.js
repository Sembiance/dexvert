import {xu} from "xu";
import {Program} from "../../Program.js";

export class akailist extends Program
{
	website    = "https://www.lsnl.jp/~ohsaki/software/akaitools/";
	package    = "app-arch/akaitools";
	bin        = "akailist";
	args       = r => ["-l", "-f", r.inFile()];
	runOptions = ({timeout : xu.SECOND*10});
	post       = r =>
	{
		const meta = {files : []};
		for(const line of r.stdout?.trim()?.split("\n")?.slice(1) || [])
		{
			const {type, size, blockLocation, name} = (/^(?<type>.*)\s\s+(?<size>\d+)\s+(?<blockLocation>\d+)\s+(?<name>.+)$/).exec(line)?.groups || {};
			if(type)
				meta.files.push({type : type.trim(), size : +size, blockLocation : +blockLocation, name});
		}
		if(meta.files.every(o => o.type==="UNKNOWN"))
			meta.files = [];
		Object.assign(r.meta, meta);
	};
	renameOut  = false;
}
