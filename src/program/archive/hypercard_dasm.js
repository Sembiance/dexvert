import {Program} from "../../Program.js";

export class hypercard_dasm extends Program
{
	website = "https://github.com/fuzziqersoftware/resource_dasm";
	package = "app-arch/resource-dasm";
	bin     = "hypercard_dasm";
	args    = r => [r.inFile(), r.outDir()];
}
