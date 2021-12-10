import {Program} from "../../Program.js";

export class resource_dasm extends Program
{
	website   = "https://github.com/fuzziqersoftware/resource_dasm";
	package   = "app-arch/resource-dasm";
	bin       = "resource_dasm";
	args      = r => ["--data-fork", r.inFile(), r.outDir()];
	renameOut = {
		alwaysRename : true,
		regex        : /^[^_]+_(?<resid>.{4})_(?<rest>.+)$/,	// this regex assumes the input filename doesn't have an underscore
		renamer      :
		[
			({suffix}, {resid, rest}) => [resid, "_", suffix, rest]
		]
	};
}
