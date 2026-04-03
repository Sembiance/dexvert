import {Format} from "../../Format.js";

export class prolineVoice extends Format
{
	name        = "Proline Voice";
	ext         = [".pvd"];
	magic       = ["Proline Voice Data"];
	unsupported = true;	// only 16 unique files on discmaster, small file size, unlikely to be sampled audio
}
