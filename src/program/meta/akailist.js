import {xu} from "xu";
import {Program} from "../../Program.js";

export class akailist extends Program
{
	website    = "https://www.lsnl.jp/~ohsaki/software/akaitools/";
	package    = "app-arch/akaitools";
	bin        = "akailist";
	args       = r => ["-l", "-f", r.inFile()];
	runOptions = ({timeout : xu.SECOND*10, timeoutSignal : "SIGKILL"});
	post       = r =>
	{
		const meta = {files : []};
		for(const line of r.stdout?.trim()?.split("\n")?.slice(1) || [])
		{
			const {type, size, blockLocation, name} = (/^(?<type>.*)\s\s+(?<size>\d+)\s+(?<blockLocation>\d+)\s+(?<name>.+)$/).exec(line)?.groups || {};
			if(type)
				meta.files.push({type : type.trim(), size : +size, blockLocation : +blockLocation, name});
		}

		// akailist will read almost ANY file and output gibberish, so only include listings if at least 80% of the files are *VOLUME*
		if((meta.files.map(o => (o.type.toLowerCase().includes("volume") ? 1 : 0)).sum()/meta.files.length)<0.8)
			meta.files = [];
		Object.assign(r.meta, meta);
	};
	renameOut  = false;
}
