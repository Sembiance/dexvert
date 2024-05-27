import {xu} from "xu";
import {Program} from "../../Program.js";
import {Detection} from "../../Detection.js";

export class detectItEasy extends Program
{
	website    = "https://github.com/horsicq/Detect-It-Easy";
	package    = "app-arch/Detect-It-Easy";
	bin        = "diec";
	loc        = "local";
	args       = r => ["--json", "--alltypes", r.inFile()];
	runOptions = ({timeout : xu.SECOND*20});	// not critical we perform this check at all, so timeout pretty quickly
	post       = r =>
	{
		r.meta.detections = [];

		const lines = r.stdout.split("\n");
		if(!lines.length)
			return;
		
		const jsonStartIdx = lines.findIndex(line => line.startsWith("{"));
		if(jsonStartIdx===-1)
			return;

		const dieData = xu.parseJSON(lines.slice(jsonStartIdx).join("\n")) || {};
		for(const detect of dieData.detects || [])
		{
			for(const value of detect?.values || [])
			{
				if(["Archive", "Format", "Installer", "Packer"].includes(value.type))
					r.meta.detections.push(Detection.create({value : value.string, confidence : 100, from : "detectItEasy", file : r.f.input}));
			}
		}
	};
	renameOut = false;
}

// Find out about detected packers from: https://github.com/packing-box/awesome-executable-packing
// More unpackers available in: /mnt/compendium/DevLab/dexvert/sandbox/app/unpackers
// It also has links to various unpackers too including:
// https://github.com/crackinglandia/fuu
// https://defacto2.net/f/a218ab4?dosmachine=svga&dosspeed=max&dosutils=true
// https://msfn.org/board/topic/62418-universal-extractor/page/49/
// https://www.portablefreeware.com/forums/viewtopic.php?t=21555
