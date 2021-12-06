import {xu} from "xu";
import {Program} from "../../Program.js";
import {runUtil} from "xutil";
import {path} from "std";

export class sidInfo extends Program
{
	website = "https://github.com/Sembiance/dexvert/bin/svgInfo.js";
	exec    = async r =>
	{
		const {stderr : sidInfoRaw} = await runUtil.run("sidplay2", ["-w/dev/null", "-t1", r.inFile()], {cwd : r.f.root, timeout : xu.MINUTE});
		r.meta.sidSubSongCount = +(sidInfoRaw.match(/Playlist.*\(tune \d+\/(?<subSongCount>\d+)/) || {groups : {}}).groups.subSongCount;

		const songLengthsRaw = await Deno.readTextFile(path.join(xu.dirname(import.meta), "..", "..", "..", "music", "sid", "Songlengths.txt"));
		const songLengths = [];
		
		let nextLine=false;
		songLengthsRaw.trim().split(songLengthsRaw.includes("\n") ? "\n" : "\r").forEach(line =>
		{
			if(nextLine)
			{
				songLengths.push(...line.split("=")[1].trim().split(" "));
				nextLine = false;
			}
			else if(line.startsWith(";") && line.trim().toLowerCase().endsWith(`/${r.f.input.base.toLowerCase()}`))	// we compare original filename, because the md5sum is too fragile, anything minor can modify it
			{
				nextLine = true;
			}
		});

		if(songLengths.length>0)
			r.meta.sidSongLengths = songLengths;
	};
}
