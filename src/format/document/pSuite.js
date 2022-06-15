import {Format} from "../../Format.js";

export class pSuite extends Format
{
	name        = "P-Suite";
	magic       = ["P-Suite format (compressed)"];	// There is also an Uncompressed version, which I have not yet encountered
	unsupported = true;
}
