import {Program} from "../../Program.js";
import {Detection} from "../../Detection.js";

export class ancientID extends Program
{
	website = "https://github.com/temisu/ancient_format_decompressor";
	package = "app-arch/ancient";
	bin     = "ancient";
	loc     = "local";
	args    = r => ["identify", r.inFile()];
	post    = r =>
	{
		const {matchType} = (r.stdout.trim().match(/^Compression of .+ is (?<matchType>.+)$/) || {groups : {}}).groups;
		r.meta.detections = matchType ? [Detection.create({value : matchType, from : "ancientID", file : r.f.input})] : [];
	};
	renameOut = false;
}
