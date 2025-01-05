import {Program} from "../../Program.js";

export class pdsTransformTool extends Program
{
	website    = "https://nasa-pds.github.io/transform/";
	package    = "app-arch/pds-transform-tool";
	bin        = "pds-transform-tool";
	args       = r => ["--target", r.inFile(), "--format-type", "png", "--output-dir", r.outDir()];
	renameOut  = true;
}
