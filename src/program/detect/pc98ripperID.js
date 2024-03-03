import {Program} from "../../Program.js";
import {Detection} from "../../Detection.js";

export class pc98ripperID extends Program
{
	website = "https://gitlab.com/bunnylin/98ripper";
	package = "app-arch/98ripper";
	bin     = "98ripper";
	loc     = "local";
	args    = r => ["-i", `./${r.inFile()}`];
	post    = r =>
	{
		const matchValue = r.stdout.trim().split("]").at(-1).trim();
		r.meta.detections = matchValue?.length ? [Detection.create({value : `PC-98 ${matchValue}`, from : "pc98ripperID", file : r.f.input})] : [];
	};
	renameOut = false;
}
