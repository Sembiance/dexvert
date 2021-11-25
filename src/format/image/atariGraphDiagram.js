import {Format} from "../../Format.js";

export class atariGraphDiagram extends Format
{
	name        = "Atari ST Graph Diagram";
	ext         = [".dia"];
	magic       = ["Graph Diagram"];
	weakMagic   = true;
	unsupported = true;
	notes       = "No known converter. Atari ST graphing program by Hans-Christoph Ostendorf.";
}
