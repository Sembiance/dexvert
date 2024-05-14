import {Program} from "../../Program.js";
import {Detection} from "../../Detection.js";

export class unp64ID extends Program
{
	website = "https://iancoog.altervista.org/";
	package = "app-arch/unp64";
	bin     = "unp64";
	loc     = "local";
	args    = r => ["-i", `./${r.inFile()}`];
	post    = r =>
	{
		let matchValue = r.stdout?.split(" : ").slice(1).join(" : ").trim();
		if(["(Unknown)"].includes(matchValue))
			matchValue = null;
		r.meta.detections = matchValue?.length ? [Detection.create({value : `P64 ${matchValue}`, from : "unp64ID", file : r.f.input})] : [];
	};
	renameOut = false;
}
