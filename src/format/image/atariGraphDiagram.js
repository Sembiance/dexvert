import {Format} from "../../Format.js";

export class atariGraphDiagram extends Format
{
	name        = "Atari ST Graph Diagram";	// by Hans-Christoph Ostendorf
	ext         = [".dia"];
	magic       = ["Graph Diagram"];
	weakMagic   = true;
	unsupported = true;	// Only 12 unique files on discmaster
}
