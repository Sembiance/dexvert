import {Program} from "../../Program.js";
import {path} from "std";

export class ptf_extract extends Program
{
	website       = "https://github.com/GeofrontTeam/LibPSPThemes";
	bin           = "python3";
	args          = r => [path.join(Program.binPath("ptf_extract"), "ptf.py"), "-c", r.inFile({absolute : true})];
	cwd           = r => r.outDir();
	mirrorInToCWD = true;
	post          = async r =>
	{
		r.f.files.new.filter(file => file.ext===".gim").map(async file => await r.f.remove("new", file, {unlink : true}));
		const dirNames = r.f.files.new.map(file => path.dirname(file.rel)).unique();
		if(dirNames.length===1 && dirNames[0].replace(/^(\.\.\/)+/, "").split("/").length===2)
			await r.f.files.new.parallelMap(async file => await file.moveUp(1));
	};
	renameOut     = false;
}
