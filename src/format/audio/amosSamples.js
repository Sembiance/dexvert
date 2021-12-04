
import {Format} from "../../Format.js";

export class amosSamples extends Format
{
	name         = "AMOS Samples Bank";
	website      = "http://fileformats.archiveteam.org/wiki/AMOS_Memory_Bank#AMOS_Samples_Bank";
	ext          = [".abk"];
	magic        = ["AMOS Samples Bank"];
	metaProvider = ["soxi"];
	converters   = ["amosbank"];
}
