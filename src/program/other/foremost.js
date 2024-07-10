import {Program} from "../../Program.js";
import {path} from "std";

export class foremost extends Program
{
	website    = "http://foremost.sourceforge.net/";
	package    = "app-forensics/foremost";
	bruteFlags = { archive : {}, image : {} };
	bin        = "foremost";
	args       = r => [`-o${r.outDir()}`, r.inFile()];
	post       = async r =>
	{
		// leaves behind an audit.txt file, remove it
		await r.f.remove("new", r.f.files.new.find(file => file.base==="audit.txt"), {unlink : true});

		// check to see if we just have a single subdir output, if so, move all files in that one up one dir
		const dirNames = r.f.files.new.map(file => path.dirname(file.rel)).unique();
		if(dirNames.length===1 && dirNames[0].replace(/^(\.\.\/)+/, "").split("/").length===2)
			await r.f.files.new.parallelMap(async file => await file.moveUp(1));
	};
	renameOut = true;
}
